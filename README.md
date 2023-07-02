# Terminal-Agent-X

[EN](README.md) / [中文](https://github.com/LyuLumos/Terminal-Agent-X/blob/main/README_cn.md) / [Wiki](https://github.com/LyuLumos/Terminal-Agent-X/wiki)

## Install

```bash
pip install terminal-agent-x
```

## Config

You need to add the environment variable `OpenAI_KEY` to the path. Please get your `OpenAI_KEY` from [OpenAI](https://platform.openai.com/account/api-keys).

Use `python -c "import os;print(os.environ.get('OpenAI_KEY'))"` for testing.


## Get Started

You can use the `tax <prompt>` to interact with the model, like:

```
$ tax write a python code for fibonacci
```

Use `tax -h` to get more information.
```bash
usage: tax.py [-h] [-k KEY] [--model MODEL] [-i INPUT] [-o OUTPUT] [--url URL] [--show_all] prompt [prompt ...]

Tax: A terminal agent using OpenAI/Claude API

positional arguments:
  prompt                Prompt

options:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     Your key for OpenAI/Claude.
  --model MODEL         Model name. Choose from gpt-3.5/4s or DALLE.
  -i INPUT, --input INPUT
                        Input file. If specified, the prompt will be read from the file.
  -o OUTPUT, --output OUTPUT
                        Output file. If specified, the response will be saved to the file.
  --url URL             URL for API request. Choose from ['openai_gfw', 'openai', 'claude'] or your custom url.
  --show_all            Show all contents in the response.
```

## Attention

You can see a directive after the generated command that says
```
Do you want to execute the command? (y/n)
```
Please execute it or not at your own discretion. I am not responsible for the consequences of generated commands.

Anthropic Claude API in not available since July 2023. Please use OpenAI API instead.

## License

[GNU General Public License v3.0](LICENSE)

## Development Logs

<details>
<summary>0.1.0</summary>

- Implement basic functions
- Support for Windows cmd and Linux shell
- Add `--file` option for saving the response to a file
</details>

<details>
<summary>0.1.1</summary>

- Add `--show_all` option for showing all contents of the response.
- Add `--url` option for users not under GFW.
- Add support for Windows Powershell
</details>

<details>
<summary>0.1.2</summary>

- Add Anthropic Claude API Support. Thanks to [jtsang4/claude-to-chatgpt](https://github.com/jtsang4/claude-to-chatgpt).
- Add Support for Chinese on Linux and Windows. (also add a temporary solution for VSCode Terminal on Windows).
- Add a timeout function.
- Fix: C++ code block prefix.
</details>

<details>
<summary>0.1.3</summary>

- Fix: code block prefix bug (tax will act maybe a little faster).
- Modify: simplify the code.
- Test: test for multi-process. Now you can use tax more efficiently in terminal.
</details>

<details>
<summary>0.1.4</summary>

- Feat: Add support for reading prompt from file.
- Feat: Add support for OpenAI DALL·E.
- Fix: Resolve the bug of curl command on Windows platform using IPv6 address to access Claude.
</details>

<details>
<summary>0.1.5</summary>

- Fix: Change api to a third-party proxy. Affected by GFW's DNS domain pollution, the original proxy is temporarily unavailable.
</details>