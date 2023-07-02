import signal
import subprocess
import os
import argparse
import re
import json
from typing import Tuple
import psutil


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


def fetch_code(openai_key: str, model: str, prompt: str, url_option: str) -> str:
    url, headers, terminal_headers, data = req_info(openai_key, model, prompt, url_option)
    if os.name == 'nt':  # Windows
        if check_terminal() == 'powershell':
            wt_command = f'Invoke-WebRequest -Uri "{url}" -Method POST -Headers @{{{terminal_headers[0]};{terminal_headers[1]}}} -Body \'{data}\' -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | Select-Object -ExpandProperty choices | Select-Object -First 1 | Select-Object -ExpandProperty message | Select-Object -ExpandProperty content'
            print(
                f'Current version does not fully support Windows PowerShell. Please copy command below and paste:\n\n{wt_command}')
            return ''
        # Windows cmd
        headers = [h.replace('"', '\\"') for h in headers]
        data = data.replace('"', '\\"')
        command = f'curl -s "{url}" -H "{headers[0]}" -H "{headers[1]}" -d "{data}"'
        command = f'{command} --ipv4' if model == 'claude' else command  # The claude API worker is not IPv6 compatible
    else:  # Linux
        command = f"curl -s --location '{url}' --header '{headers[0]}' --header '{headers[1]}' --data '{data}'"
    # print(command)

    try:
        res, err = run_command_with_timeout(command, 60)
        # print(res, err)
        # res = os.popen(command).read().encode('utf-8').decode('utf-8', 'ignore')
        if model.lower() == 'dalle':
            return json.loads(res)['data'][0]['url']
        return json.loads(res)['choices'][0]['message']['content']
    except KeyError:
        assert False, 'This is most likely due to poor internet or invalid key. Please retry.'
    except json.decoder.JSONDecodeError:
        assert False, 'This URL may be invalid or the response cannot be parsed'


def req_info(openai_key: str, model: str, prompt: str, url_option: str) -> Tuple[str, str, str, str]:
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
        # 'claude': 'https://claude-api.lyulumos.space/v1/chat/completions'
    }
    # url_option = 'claude' if model == 'claude' else url_option
    # claude API is not accessible
    if model == 'claude':
        assert False, 'Claude API is not accessible now. Please use OpenAI API instead.'
    url = urls[url_option] if url_option in urls else url_option

    if model.lower() == 'dalle':
        url = 'https://api.openai-proxy.com/v1/images/generations' if url_option == 'openai_gfw' else 'https://api.openai.com/v1/images/generations'
        data = f'{{"prompt": "{prompt}"}}'
    else:
        data = f'{{"model": "{model}","messages": [{{"role": "user", "content": "{prompt}"}}]}}'
    return url, headers, terminal_headers, data


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


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Tax: A terminal agent using OpenAI/Claude API')
    parser.add_argument("prompt", nargs='+', type=str, help="Prompt")
    parser.add_argument('-k', '--key', type=str,
                        help='Your key for OpenAI/Claude.')
    parser.add_argument('--model', type=str,
                        default='gpt-3.5-turbo', help='Model name. Choose from gpt-3.5/4s or DALLE.')
    parser.add_argument('-i', '--input', type=str,
                        help='Input file. If specified, the prompt will be read from the file.')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file. If specified, the response will be saved to the file.')
    parser.add_argument('--url', type=str, default='openai',
                        help="URL for API request. Choose from ['openai_gfw', 'openai', 'claude'] or your custom url.")
    parser.add_argument('--show_all', action='store_true',
                        help='Show all contents in the response.')
    args = parser.parse_args()

    prompt = ' '.join(args.prompt)
    prompt = f'{prompt}\\n{load_file(args.input)}' if args.input else prompt

    key = args.key or os.environ.get('OpenAI_KEY')
    if not key:
        assert False, 'Error: OpenAI key not found. Please specify it in system environment variables or pass it as an argument.'

    # res = get_model_response(openai_key, args.model, prompt)
    res = fetch_code(key, args.model, prompt, args.url)

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
