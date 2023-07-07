# Terminal-Agent-X

[EN](README.md) / [中文](https://github.com/LyuLumos/Terminal-Agent-X/blob/main/README_cn.md) / [Wiki](https://github.com/LyuLumos/Terminal-Agent-X/wiki)

## Features

- 👻 Easy installation and usage with a single command.
- 🎈 Small size, no additional dependencies required.
- 🐼 Supports English and Chinese on Windows CMD, Powershell, Linux shell, etc.
- 🤖 Compatible with OpenAI GPT-3.5/4s, DALL·E, and Claude API in Chinese Mainland and other countries.


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

or use `tax --chat` to chat with the model.
```
$ tax --chat
> hi
Tax: Hello! How can I assist you today?
```

Use `tax -h` to get more information.

## Attention

You can see a directive after the generated command that says
```
Do you want to execute the command? (y/n)
```
Please execute it or not at your own discretion. I am not responsible for the consequences of generated commands.

## License

[GNU General Public License v3.0](LICENSE)

## Development Logs

<details>
<summary>0.1.x</summary>

#### 0.1.0

- Implement basic functions
- Support for Windows cmd and Linux shell
- Add `--file` option for saving the response to a file

#### 0.1.1

- Add `--show_all` option for showing all contents of the response.
- Add `--url` option for users not under GFW.
- Add support for Windows Powershell

#### 0.1.2

- Add Anthropic Claude API Support. Thanks to [jtsang4/claude-to-chatgpt](https://github.com/jtsang4/claude-to-chatgpt). (deprecated in 0.1.5) 
- Add Support for Chinese on Linux and Windows. (also add a temporary solution for VSCode Terminal on Windows).
- Add a timeout function.
- Fix: C++ code block prefix.

#### 0.1.3

- Fix: code block prefix bug (tax will act maybe a little faster).
- Modify: simplify the code.
- Test: test for multi-process. Now you can use tax more efficiently in terminal.

#### 0.1.4

- Feat: Add support for reading prompt from file.
- Feat: Add support for OpenAI DALL·E.
- Fix: Resolve the bug of curl command on Windows platform using IPv6 address to access Claude.

#### 0.1.5

- Fix: Change api to a third-party proxy. Affected by GFW's DNS domain pollution, the original proxy is temporarily unavailable. `claude-to-chatgpt` is unavailable.

#### 0.1.6

- Feat: Add support for **Chat** on Linux. Now you can use tax as **ChatGPT CLI**!
- Feat: Add support for native Anthropic Claude API on Linux Shell, Windows cmd and Powershell.

</details>