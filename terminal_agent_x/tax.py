import signal
import subprocess
import os
import argparse
import psutil
import re
import json


def check_terminal():
    # check the terminal type
    parent_process_name = psutil.Process(os.getppid()).name()
    if parent_process_name in ['pwsh', 'powershell', 'powershell.exe']:
        return 'powershell'
    elif parent_process_name in ['cmd', 'cmd.exe']:
        return 'cmd'


def run_command_with_timeout(command, timeout):
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


def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass


def fetch_code(openai_key, model, prompt, args):
    url = "https://api.lyulumos.space/v1/chat/completions" if not args.default_url else "https://api.openai.com/v1/chat/completions"
    url = "https://claude-api.lyulumos.space/v1/chat/completions" if args.claude else url
    headers = [
        f"Authorization: Bearer {openai_key}",
        "Content-Type: application/json"
    ]
    terminal_headers = [
        f"Authorization='Bearer {openai_key}'",
        "'Content-Type'='application/json'"
    ]
    data = f'{{"model": "{model}","messages": [{{"role": "user", "content": "{prompt}"}}]}}'

    if os.name == 'nt':  # Windows
        if check_terminal() == 'powershell':
            wt_command = f'Invoke-WebRequest -Uri "{url}" -Method POST -Headers @{{{terminal_headers[0]};{terminal_headers[1]}}} -Body \'{data}\' -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | Select-Object -ExpandProperty choices | Select-Object -First 1 | Select-Object -ExpandProperty message | Select-Object -ExpandProperty content'
            print(
                f'Current version does not fully support Windows PowerShell. Please copy command below and paste:\n\n{wt_command}')
            return ''
        else:  # Windows cmd
            headers = [h.replace('"', '\\"') for h in headers]
            data = data.replace('"', '\\"')
            command = f'curl -s "{url}" -H "{headers[0]}" -H "{headers[1]}" -d "{data}"'
    else:  # Linux
        command = f"curl -s --location '{url}' --header '{headers[0]}' --header '{headers[1]}' --data '{data}'"
    # print(command)

    try:
        res, err = run_command_with_timeout(command, 60)
        # print(res, err)
        # res = os.popen(command).read().encode('utf-8').decode('utf-8', 'ignore')
        return json.loads(res)['choices'][0]['message']['content']
    except KeyError:
        assert False, 'This is most likely due to poor internet. Please retry.'


def find_code(text):
    pattern = r"```(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return delete_prefix(match.group(0))  # with ``` pairs
    return None


def delete_prefix(text):
    # text: ```python\nprint('Hello, world!')\n``` or ```\nprint('Hello, world!')\n```
    s_new = re.sub(r'```[\w-]*[+]*\n', '```', text)
    return s_new.strip('`').strip()


def main():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument("prompt", nargs='+', type=str, help="Prompt")
    parser.add_argument('--openai_key', type=str,
                        help='Your key for OpenAI, only for one-time request')
    parser.add_argument('--model', type=str,
                        default='gpt-3.5-turbo', help='Model name. You can use all OpenAI models.')
    parser.add_argument(
        '--file', type=str, help='Output file. If specified, the output will be written to this file. Tax will act like ChatGPT')
    parser.add_argument('--url', type=str, default='https://api.lyulumos.space/v1/chat/completions',
                        help='URL for API request which can be accessd under GFW. When your network environment is NOT under GFW, you can use OpenAI API directly.')
    parser.add_argument('--default_url', action='store_true',
                        help='Use default OpenAI API URL for request.')
    parser.add_argument('--claude', action='store_true',
                        help='Use Claude API for request.')
    parser.add_argument('--show_all', action='store_true',
                        help='Show all contents in the response')
    args = parser.parse_args()

    prompt = ' '.join(args.prompt)
    prompt = f'{prompt}. Answer me with markdown'
    openai_key = args.openai_key or os.environ.get('OpenAI_KEY')
    if not openai_key:
        assert False, 'Error: OpenAI key not found. Please specify it in system environment variables or pass it as an argument.'

    # res = get_model_response(openai_key, args.model, prompt)
    res = fetch_code(openai_key, args.model, prompt, args)

    if args.file:
        with open(args.file, 'w', encoding='utf-8') as f:
            f.write(res)
        f.close()
    elif args.show_all:
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
