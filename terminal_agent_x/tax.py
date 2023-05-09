import os
import argparse
import json
import re

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


def fetch_code(openai_key, model, prompt):
    command = "curl -s"
    url = "https://api.lyulumos.space/v1/chat/completions"
    headers = [
        f"Authorization: Bearer {openai_key}",
        "Content-Type: application/json"
    ]
    data = f'{{"model": "{model}","messages": [{{"role": "user", "content": "{prompt}"}}]}}'

    if os.name == 'nt':  # Windows
        headers = [h.replace('"', '\\"') for h in headers]
        data = data.replace('"', '\\"')
        command += f' "{url}" -H "{headers[0]}" -H "{headers[1]}" -d "{data}"'
    else:  # Linux
        command += f" --location '{url}' --header '{headers[0]}' --header '{headers[1]}' --data '{data}'"
    # print(command)

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


def main():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument("prompt", nargs='+', type=str, help="Prompt")
    parser.add_argument('--openai_key', type=str,
                        help='Your key for OpenAI, only for one-time request')
    parser.add_argument('--model', type=str,
                        default='gpt-3.5-turbo', help='Model name')
    parser.add_argument(
        '--file', type=str, help='Output file. If specified, the output will be written to this file. Tax will act like ChatGPT')
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
                if answer == 'y' or answer == 'Y' or answer == 'yes' or answer == 'Yes' or answer == 'YES':
                    os.system(first_code)


if __name__ == '__main__':
    main()
