import signal
import subprocess
import os
import argparse
import re
import json
from typing import Tuple
import datetime
import concurrent.futures
import base64
import http.client
import psutil


def check_terminal() -> str:
    # check the terminal type
    parent_process_name = psutil.Process(os.getppid()).name()
    if parent_process_name in ['pwsh', 'powershell', 'powershell.exe']:
        return 'powershell'
    if parent_process_name in ['cmd', 'cmd.exe']:
        return 'cmd'


def run_command_with_timeout(command: str, timeout: int, stream_flag: bool) -> Tuple[str, str]:
    p = subprocess.Popen(command, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    try:
        if stream_flag:
            full_res = ''
            while True:
                output = p.stdout.readline()
                if output.strip() == '[DONE]' and p.poll() is not None:
                    break
                if output.strip():
                    response = output.decode('utf-8', 'ignore')
                    response = response[6:] if response.startswith('data:') else response
                    res_json = json.loads(response)
                    if res_json['choices'][0]['finish_reason'] == 'stop':
                        break
                    single_line_res = res_json['choices'][0]['delta']['content']
                    print(single_line_res, end='')
                    full_res += single_line_res
            print()
        else:
            full_res, _ = p.communicate(timeout=timeout)
            full_res = full_res.decode('utf-8', 'ignore')
        return full_res
    except subprocess.TimeoutExpired as timeout_e:
        p.terminate()
        if os.name == 'nt':
            kill_process_tree(p.pid)
        else:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        raise subprocess.TimeoutExpired(
            p.args, timeout, output=full_res) from timeout_e


def kill_process_tree(pid: int) -> None:
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass


def fetch_code(openai_key: str, model: str, prompt: str, url_option: str, chat_flag: bool, stream_flag=True) -> str:
    # print(f'fetch_code has been called with {openai_key}, {model}, {prompt}, {url_option}, {chat_flag}')
    url, headers, terminal_headers, data = req_info(
        openai_key, model, prompt, url_option, chat_flag, stream_flag=stream_flag)
    if os.name == 'nt':  # Windows
        if check_terminal() == 'powershell':
            wt_command = f'Invoke-WebRequest -Uri "{url}" -Method POST -Headers @{{{terminal_headers[0]};{terminal_headers[1]}}} -Body \'{data}\' -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | Select-Object -ExpandProperty choices | Select-Object -First 1 | Select-Object -ExpandProperty message | Select-Object -ExpandProperty content'
            print(
                f'Current version does not fully support Windows PowerShell. Please copy command below and paste:\n\n{wt_command}')
            return ''
        # Windows cmdtax
        headers = [h.replace('"', '\\"') for h in headers]
        data = data.replace('"', '\\"')
        command = f'curl -s "{url}" -H "{headers[0]}" -H "{headers[1]}" -d "{data}"'
        # The claude API worker is not IPv6 compatible
        command = f'{command} --ipv4' if model == 'claude' else command
    else:  # Linux
        command = f"curl -s --location '{url}' --header '{headers[0]}' --header '{headers[1]}' --data '{data}'"
    # print(command)

    try:
        res = run_command_with_timeout(command, 60, stream_flag=stream_flag)
        # print('res=', res)

        if 'dalle' in model.lower() or 'dall-e' in model.lower():
            return json.loads(res)['data'][0]['url']
        if not stream_flag:
            return json.loads(res)['choices'][0]['message']['content']
        else:
            return res
    except Exception as e:
        return 'Error', e


def chat_data_wrapper(model: str, prompt: str, chat_flag: bool, stream_flag: bool) -> str:
    if chat_flag:
        return f'{{"model": "{model}","messages":{prompt}}}'  # 组装数据的部分在函数之外完成
    if 'dalle' in model.lower() or 'dall-e' in model.lower():
        return f'{{"prompt": "{prompt}", "n": 1, "model": "dall-e-3", "size": "1024x1024"}}'
    # if input_image and model.lower() == 'gpt-4-vision-preview':
    #     base64_image = encode_image(input_image)
    #     content = f'[{{"type": "text","text": "{prompt}"}},{{"type": "image_url","image_url": {{"url": "data:image/jpeg;base64,{base64_image[-1]}"}}}}]'
    #     return f'{{"model": "{model}","messages": [{{"role": "user", "content": "{content}"}}], "max_tokens": 300}}'
    stream_flag = 'true' if stream_flag else 'false'
    return f'{{"model": "{model}", "messages": [{{"role": "user", "content": "{prompt}"}}], "stream": {stream_flag}}}'


def req_info(openai_key: str, model: str, prompt: str, url_option: str, chat_flag: bool, stream_flag: bool) -> Tuple[str, str, str, str]:
    headers = [
        f"Authorization: Bearer {openai_key}",
        "Content-Type: application/json"
    ]
    terminal_headers = [
        f"Authorization='Bearer {openai_key}'",
        "'Content-Type'='application/json'"
    ]
    urls = {
        'openai_gfw': 'https://api.openai-proxy.com',
        'openai': 'https://api.openai.com',
    }
    url = urls[url_option] if url_option in urls else url_option

    # if model.lower() == 'dalle':
    #     url = 'https://api.openai-proxy.com/v1/images/generations' if url_option == 'openai_gfw' else 'https://api.openai.com/v1/images/generations'
    
    if '.' in url[:-1].split('/')[-1]:
        url = url+'/' if url[-1] != '/' else url
        if 'dalle' in model.lower() or 'dall-e' in model.lower():
            url += "v1/images/generations"
        else:
            url += "v1/chat/completions"

    data = chat_data_wrapper(model, prompt, chat_flag, stream_flag=stream_flag)
    return url, headers, terminal_headers, data


def single_claude(anthropic_api_key: str, model: str, prompt: str) -> str:
    url = 'https://api.anthropic.com/v1/complete'
    model = 'claude-1' if model == 'claude' else model
    headers = [
        "anthropic-version: 2023-06-01",
        "content-type: application/json",
        f"x-api-key: {anthropic_api_key}"
    ]
    terminal_headers = [
        "'anthropic-version'='2023-06-01'",
        "'content-type'='application/json'",
        f"'x-api-key'='{anthropic_api_key}'"
    ]
    data = f'{{"model": "{model}","prompt": "\\n\\nHuman: {prompt}\\n\\nAssistant:","max_tokens_to_sample": 256,"stream": false}}'
    if os.name == 'nt':
        if check_terminal() == 'powershell':
            wt_command = f'Invoke-WebRequest -Uri "{url}" -Method POST -Headers @{{{terminal_headers[0]};{terminal_headers[1]};{terminal_headers[2]}}} -Body \'{data}\' -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | Select-Object -ExpandProperty completion'
            print(
                f'Current version does not fully support Windows PowerShell. Please copy command below and paste:\n\n{wt_command}')
            return ''
        # Windows cmd
        headers = [h.replace('"', '\\"') for h in headers]
        data = data.replace('"', '\\"')
        command = f'curl -s {url} -H "{headers[0]}" -H "{headers[1]}" -H "{headers[2]}" -d "{data}"'
    else:
        command = f"curl --request POST --url '{url}' --header '{headers[0]}' --header '{headers[1]}' --header '{headers[2]}' --data '{data}'"
    # print(command)
    try:
        res = run_command_with_timeout(command, 60, stream_flag=False)
        # print(res)
        return json.loads(res)['completion']
    except Exception as e:
        err = str(e)
        return 'Error', res, err



def find_code(text: str) -> str:
    pattern = r"```(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        codes = match.group(0)
        first_n = codes.find('\n')
        return codes[first_n+1:-3].strip()  # without ``` pairs
    return None


def load_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def chat(openai_key: str, model: str, url_option: str):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    conversation = [
        {"role": "system", "content": f"You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: 2021-09\nCurrent date: {current_date}"},
    ]
    # print(conversation)

    while True:
        user_input = input("> ")
        if user_input == "exit":
            break
        conversation.append({"role": "user", "content": user_input})
        response = fetch_code(openai_key, model, json.dumps(conversation), url_option, chat_flag=True, stream_flag=False)
        print(f'Tax: {response}')
        conversation.append({"role": "assistant", "content": response.encode(
            'unicode-escape').decode('utf8').replace("'", "")})
        # The bash command sent cannot contain single quotes, escaping has no effect. So the single quotes in the conversation will be deleted and the user will not see it.
        # print(conversation)


def parallel_ask(data_prompts, chat_mode, api_key, url, max_workers, output_file, model, **args):
    with concurrent.futures.ThreadPoolExecutor(max_workers=int(max_workers)) as executor:
        if chat_mode == 'openai':
            future_to_prompt = {executor.submit(fetch_code, **args, openai_key=api_key, url_option=url, prompt=prompt, model=model, chat_flag=False, stream_flag=False): prompt for prompt in data_prompts}
        results = []
        for future in concurrent.futures.as_completed(future_to_prompt):
            try:
                data = future.result()
            except Exception as exc:
                data = str(type(exc))
            results.append(repr(data))
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join((results)))
        f.close()


def load_prompts_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.readlines()
    return [line.strip() for line in text]


def process_image(api_key, url, prompt, image_path, model):
    url = url.replace('https://', '')
    GOOGLE_ENDPOINT = 'generativelanguage.googleapis.com'
    if 'gemini' in model:
        url = GOOGLE_ENDPOINT
    conn = http.client.HTTPSConnection(url)

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def openai_gpt4_v(api_key, prompt, image_path, model, conn, encode_image):
        payload = json.dumps({
            "model": f'{model}',
            "stream": False,
            "messages": [
            {        
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f'{prompt}'
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f'data:image/jpeg;base64,{encode_image(image_path)}'
                        }
                    }
                ]
            }],
            "max_tokens": 400
        })
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        data = res.read()
        # print(data.decode("utf-8"))
        ans = json.loads(data.decode("utf-8"))['choices'][0]['message']['content']
        return ans
    
    def google_gemini_v(api_key, prompt, image_path, model, conn, encode_image):
        payload = json.dumps({
            "contents": [
                {
                    "parts": [
                        {
                            "text": f'{prompt}'
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": f'{encode_image(image_path)}'
                            }
                        }
                    ]
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json'
        }
        conn.request("POST", f"/v1beta/models/{model}:generateContent?key={api_key}", payload, headers)
        res = conn.getresponse()
        data = res.read()
        ans = json.loads(data.decode("utf-8"))['candidates'][0]['content']['parts'][0]['text']
        return ans

    if 'gpt' in model:
        ans = openai_gpt4_v(api_key, prompt, image_path, model, conn, encode_image)
    elif 'gemini' in model:
        ans = google_gemini_v(api_key, prompt, image_path, model, conn, encode_image)

    return ans


# TODO: openai requests will gradually be migrated to this.
def https_chat_openai_request(url, api_key, model, prompt):
    url = url.replace('https://', '')
    url = url[:-1] if url[-1] == '/' else url
    conn = http.client.HTTPSConnection(url, timeout=240)
    headers = {
      'Accept': 'application/json',
      'Authorization': f'Bearer {api_key}',
      'Content-Type': 'application/json'
    }
    payload = {
        "model": f'{model}',
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": f'{prompt}'
            }
        ]
    }
    if not model.startswith('o1'):
        payload["max_tokens"] = 1024
    payload = json.dumps(payload)
    conn.request("POST", "/v1/chat/completions", payload, headers)
    data = conn.getresponse().read()
    ans = json.loads(data.decode("utf-8"))['choices'][0]['message']['content']
    return ans


def https_gemini_request(api_key, model, prompt):
    url = 'generativelanguage.googleapis.com'

    conn = http.client.HTTPSConnection(url)
    headers = {
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f'{prompt}'
                    }
                ]
            }
        ]
    })
    conn.request("POST", f"{url}/v1/models/{model}:generateContent?key={api_key}", payload, headers)
    data = conn.getresponse().read()
    ans = json.loads(data.decode("utf-8"))['candidates'][0]['content']['parts'][0]['text']
    return ans


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Tax: A terminal agent using OpenAI/Claude API')
    parser.add_argument("prompt", nargs='*', type=str, help="Prompt")
    parser.add_argument('-k', '--key', type=str,
                        help='Your key for OpenAI/Claude.')
    parser.add_argument('-m', '--model', type=str,
                        default='gpt-4o-mini', help='Model name. Choose from gpt-3.5/4, Claude, Gemini or DALLE series.')
    parser.add_argument('-i', '--input_image', type=str,
                        help='Input image for OpenAI GPT-4-vision and Google Gemini Pro Vision [Beta Feature].')
    parser.add_argument('--prompt_file', type=str,
                        help='Input file. If specified, the prompt will be read from the file.')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file. If specified, the response will be saved to the file.')
    parser.add_argument('-c', '--chat', action='store_true',
                        help='Chat mode. Tax will act like ChatGPT. Enter "exit" to quit.')
    parser.add_argument('-u', '--url', type=str,
                        help="URL for API request. Choose from ['openai_gfw', 'openai', 'claude'] or your custom url such as 'https://api.openai.com'.")
    parser.add_argument('--code', action='store_true',
                        help='Only show the code.')
    parser.add_argument('-p', '--parallel', action='store_true',
                        help='Parallel mode. If specified, the input file will be read line by line and the responses will be saved to the output file.')
    parser.add_argument('--not_stream', action='store_true',
                        help='The text response is streamed by default. If specified, the response will not be streamed.')
    # parser.add_argument('--plugin', type=str, choices=['git_commit'],
    #                     help='Plugins with the third-party software or API.')
    parser.add_argument('--option', metavar='KEY=VALUE', action='append', help='Custom option')
    args = parser.parse_args()

    prompt = ' '.join(args.prompt)
    prompt = f'{prompt}\\n{load_file(args.prompt_file)}' if args.prompt_file and not args.parallel else prompt

    key = args.key or os.environ.get('tax_key')
    url = args.url or os.environ.get('tax_base_url')

    if not key:
        assert False, 'Error: tax_key not found. Please specify it in system environment variables or pass it as an argument.'
    if not url:
        url = 'https://api.openai.com'

    url = url[:-1] if url[-1] == '/' else url

    # input_args = sys.stdin.readlines()
    # prompt = f'{prompt}\\n{repr("".join(input_args))}' if input_args else prompt
    # if input_args:
    #     res = https_chat_openai_request(args.url, args.key, args.model, prompt)
    #     print(res)
    #     return

    # if args.plugin == 'git_commit':
    #     command = f'git diff | python terminal_agent_x/tax.py -k {key} -m {args.model} -u {args.url} {prompt}\\n 根据git diff结果写出git commit message'
    #     res = run_command_with_timeout(command, 30)
    #     print(res)
    #     return
    # https_chat_openai_request(args.url, args.key, args.model, prompt)

    if args.chat:
        chat(key, args.model, url)
        return

    if args.model.lower() == 'claude' or url == 'claude':
        res = single_claude(key, 'claude-1', prompt)
        print(res)
        return
    elif 'gemini-pro' == args.model.lower():
        res = https_gemini_request(key, args.model, prompt)
        print(res)
        return
    elif args.model.startswith('o1'):
        res = https_chat_openai_request(url, key, args.model, prompt)
        print(res)
        return

    if args.option and args.parallel:
        custom_options = {option.split('=')[0]: option.split('=')[1]
                          for option in args.option}

        parallel_ask(data_prompts=load_prompts_file(args.prompt_file), output_file=args.output, model=args.model, api_key=key, url=url, **custom_options)
        print(f'The results have been saved to {args.output}')
        return

    if args.input_image:
        print('[TAX HINT]: This feature is still in beta. Please use it with caution.')
        res = process_image(key, url, prompt, args.input_image, args.model)
        print(res)
        return

    # stream is only supported by OpenAI gpt-* models
    stream_flag = True if args.model.startswith('gpt') else False
    stream_flag = False if args.not_stream else stream_flag

    res = fetch_code(key, args.model, prompt, url, chat_flag=False, stream_flag=stream_flag)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.code:
                res = find_code(res) or res
            f.write(res)
        f.close()
    elif args.code:
        first_code = find_code(res)
        if not first_code:
            print(res)
        else:
            print(first_code + '\n')
            # only run for single code
            if first_code and len(first_code.split('\n')) == 1:
                answer = input('Do you want to execute the command? (y/n)  ')
                if answer in ['y', 'Y', 'yes', 'Yes', 'YES']:
                    os.system(first_code)
    else:
        if not stream_flag:
            print(res)


if __name__ == '__main__':
    main()
