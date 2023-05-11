import os
import argparse

from utils import fetch_code, find_code, delete_prefix, check_terminal, request_pwsh


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
                if answer in ['y', 'Y', 'yes', 'Yes', 'YES']:
                    os.system(first_code)


if __name__ == '__main__':
    main()
