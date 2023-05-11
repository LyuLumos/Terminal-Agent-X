import os
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
            webrequest_pwsh = f'$res = Invoke-WebRequest -Uri "{url}" -Method POST -Headers @{{{terminal_headers[0]};{terminal_headers[1]}}} -Body \'{data}\' -UseBasicParsing'
            get_res_pwsh = '$res.Content | ConvertFrom-Json | Select-Object -ExpandProperty choices | Select-Object -First 1 | Select-Object -ExpandProperty message | Select-Object -ExpandProperty content'
            os.system(webrequest_pwsh)
            res = os.popen(get_res_pwsh).read()
            return res
        
        else: # Windows cmd
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
    # "There are a few steps that need to be followed to install Docker on Ubuntu:\n\n1. Update the system package index:\n\n```\nsudo apt-get update\n```\n\n2. Install the necessary packages to allow apt to use a repository over HTTPS:\n\n```\nsudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common\n```\n\n3. Add the official GPG key of Docker:\n\n```\ncurl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -\n```
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
