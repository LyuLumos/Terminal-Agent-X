import signal
import subprocess
import os
import argparse
import re
import json
from typing import Tuple
import psutil
import datetime


def check_terminal() -> str:
    # check the terminal type
    parent_process_name = psutil.Process(os.getppid()).name()
    if parent_process_name in ['pwsh', 'powershell', 'powershell.exe']:
        return 'powershell'
    if parent_process_name in ['cmd', 'cmd.exe']:
        return 'cmd'


def run_command_with_timeout(command: str, timeout: int) -> Tuple[str, str]:
    p = subprocess.Popen(command, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    try:
        stdout, stderr = p.communicate(timeout=timeout)
        return stdout.decode('utf-8', 'ignore'), stderr.decode('utf-8', 'ignore')
    except subprocess.TimeoutExpired as timeout_e:
        p.terminate()
        if os.name == 'nt':
            kill_process_tree(p.pid)
        else:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        raise subprocess.TimeoutExpired(
            p.args, timeout, output=stdout, stderr=stderr) from timeout_e


def kill_process_tree(pid: int) -> None:
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass


def fetch_code(openai_key: str, model: str, prompt: str, url_option: str, chat_flag: bool) -> str:
    url, headers, terminal_headers, data = req_info(
        openai_key, model, prompt, url_option, chat_flag)
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
        res, err = run_command_with_timeout(command, 60)
        # res = os.popen(command).read().encode('utf-8').decode('utf-8', 'ignore')
        if model.lower() == 'dalle':
            return json.loads(res)['data'][0]['url']
        return json.loads(res)['choices'][0]['message']['content']
    except:
        return 'Error', res, err


def chat_data_wrapper(model: str, prompt: str, chat_flag: bool) -> str:
    if chat_flag:
        return f'{{"model": "{model}","messages":{prompt}}}'  # 组装数据的部分在函数之外完成
    if model.lower() == 'dalle':
        return f'{{"prompt": "{prompt}"}}'
    return f'{{"model": "{model}","messages": [{{"role": "user", "content": "{prompt}"}}]}}'


def req_info(openai_key: str, model: str, prompt: str, url_option: str, chat_flag: bool) -> Tuple[str, str, str, str]:
    headers = [
        f"Authorization: Bearer {openai_key}",
        "Content-Type: application/json"
    ]
    terminal_headers = [
        f"Authorization='Bearer {openai_key}'",
        "'Content-Type'='application/json'"
    ]
    urls = {
        'openai_gfw': 'https://api.openai-proxy.com/v1/chat/completions',
        'openai': 'https://api.openai.com/v1/chat/completions',
    }
    url = urls[url_option] if url_option in urls else url_option

    if model.lower() == 'dalle':
        url = 'https://api.openai-proxy.com/v1/images/generations' if url_option == 'openai_gfw' else 'https://api.openai.com/v1/images/generations'
    data = chat_data_wrapper(model, prompt, chat_flag)
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
        res, err = run_command_with_timeout(command, 60)
        return json.loads(res)['completion']
    except:
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
        response = fetch_code(openai_key, model, json.dumps(
            conversation), url_option, True)
        print(f'Tax: {response}')
        conversation.append({"role": "assistant", "content": response.encode(
            'unicode-escape').decode('utf8').replace("'", "")})
        # The bash command sent cannot contain single quotes, escaping has no effect. So the single quotes in the conversation will be deleted and the user will not see it.
        # print(conversation)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Tax: A terminal agent using OpenAI/Claude API')
    parser.add_argument("prompt", nargs='*', type=str, help="Prompt")
    parser.add_argument('-k', '--key', type=str,
                        help='Your key for OpenAI/Claude.')
    parser.add_argument('-m', '--model', type=str,
                        default='gpt-3.5-turbo', help='Model name. Choose from gpt-3.5/4s, Claude API or DALLE.')
    parser.add_argument('-i', '--input', type=str,
                        help='Input file. If specified, the prompt will be read from the file.')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file. If specified, the response will be saved to the file.')
    parser.add_argument('-c', '--chat', action='store_true',
                        help='Chat mode. Tax will act like ChatGPT. Enter "exit" to quit.')
    parser.add_argument('-u', '--url', type=str, default='openai',
                        help="URL for API request. Choose from ['openai_gfw', 'openai', 'claude'] or your custom url.")
    parser.add_argument('-a', '--show_all', action='store_true',
                        help='Show all contents in the response.')
    args = parser.parse_args()

    prompt = ' '.join(args.prompt)
    prompt = f'{prompt}\\n{load_file(args.input)}' if args.input else prompt

    key = args.key or os.environ.get('OpenAI_KEY')
    if not key:
        assert False, 'Error: OpenAI key not found. Please specify it in system environment variables or pass it as an argument.'
    if args.chat:
        chat(key, args.model, args.url)
        return

    if args.model.lower() == 'claude' or args.url == 'claude':
        res = single_claude(key, 'claude-1', prompt)
        print(res)
        return

    # res = get_model_response(openai_key, args.model, prompt)
    res = fetch_code(key, args.model, prompt, args.url, False)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(res)
        f.close()
    elif args.show_all or args.model.lower() == 'dalle':
        print(res)
    else:
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


if __name__ == '__main__':
    main()
