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


def fetch_code(openai_key, model, prompt):
    command = "curl -s"
    url = "https://api.lyulumos.space/v1/chat/completions"
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
            webrequest_pwsh = f'Invoke-WebRequest -Uri "{url}" -Method POST -Headers '
            f'@{{{terminal_headers[0]};{terminal_headers[1]}}} -Body \'{data}\' -UseBasicParsing | '
            'Select-Object -ExpandProperty Content | ConvertFrom-Json | Select-Object -ExpandProperty '
            'choices | Select-Object -First 1 | Select-Object -ExpandProperty message | Select-Object '
            '-ExpandProperty content'
            print(webrequest_pwsh)

        else:  # Windows cmd
            headers = [h.replace('"', '\\"') for h in headers]
            data = data.replace('"', '\\"')
            command += f' "{url}" -H "{headers[0]}" -H "{headers[1]}" -d "{data}"'
    else:  # Linux
        command += f" --location '{url}' --header '{headers[0]}' --header '{headers[1]}' --data '{data}'"
    print(command)

    try:
        res = json.loads(os.popen(command).read())[
            'choices'][0]['message']['content']
    except KeyError:
        assert False, 'This is most likely due to poor internet. Please retry.'
    return str(res)


def find_code(text):
    pattern = r"```(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return delete_prefix(match.group(0))  # with ``` pairs
    else:
        return None
        # assert False, f'Error: No code found in text. Please retry.'
    # return None


def delete_prefix(text):
    # text: ```python\nprint('Hello, world!')\n``` or ```\nprint('Hello, world!')\n```
    s_new = re.sub(r'```[\w-]*\n', '```', text)
    return s_new.strip('`').strip()

# # ATTENTION: Python requests is very slow. Use curl instead.
# import requests
# def get_model_response(OpenAI_KEY, model, prompt):
#     url = 'https://api.lyulumos.space/v1/chat/completions'
#     headers = {
#         'Authorization': f'Bearer {OpenAI_KEY}',
#         'Content-Type': 'application/json',
#     }
#     json_data = {
#         'model': 'gpt-3.5-turbo',
#         'messages': [
#             {
#                 'role': 'user',
#                 'content': '{}'.format(prompt),
#             },
#         ],
#     }
#     # print(json_data)
#     response = requests.post(url, headers=headers, json=json_data)
#     # print(response.text)
#     # {"id":"chatcmpl-7DcBBzkbUMUZTxbzigCiajz4u5PCE","object":"chat.completion","created":1683479381,"model":"gpt-3.5-turbo-0301","usage":{"prompt_tokens":10,"completion_tokens":10,"total_tokens":20},"choices":[{"message":{"role":"assistant","content":"Hello there! How can I assist you today?"},"finish_reason":"stop","index":0}]}
#     try:
#         res = json.loads(response.text)['choices'][0]['message']['content']
#     except Exception as e:
#         assert False, f'Error: {e}'
#     return str(res)


def main():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument("prompt", nargs='+', type=str, help="Prompt")
    parser.add_argument('--openai_key', type=str,
                        help='Your key for OpenAI, only for one-time request')
    parser.add_argument('--model', type=str,
                        default='gpt-3.5-turbo', help='Model name')
    parser.add_argument(
        '--file', type=str, help='Output file. If specified, the output will be written to this file. Tax will act like ChatGPT')
    parser.add_argument('--url', type=str, default='https://api.lyulumos.space/v1/chat/completions',
                        help='URL for API request. When your network environment is NOT under GFW, you can use OpenAI API directly.')
    args = parser.parse_args()

    prompt = ' '.join(args.prompt)
    prompt = f'{prompt}. Answer me with markdown'
    openai_key = args.openai_key or os.environ.get('OpenAI_KEY')
    if not openai_key:
        assert False, 'Error: OpenAI key not found. Please specify it in system environment variables or pass it as an argument.'

    # res = get_model_response(openai_key, args.model, prompt)
    res = fetch_code(openai_key, args.model, prompt)

    if args.file:
        with open(args.file, 'w', encoding='utf-8') as f:
            f.write(res)
        f.close()
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
