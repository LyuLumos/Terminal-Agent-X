# Terminal-Agent-X

[EN](README.md) / [中文](https://github.com/LyuLumos/Terminal-Agent-X/blob/main/README_cn.md) / [Wiki](https://github.com/LyuLumos/Terminal-Agent-X/wiki)

## Install

```bash
pip install terminal-agent-x
```

## Config

You need to add the environment variable `OpenAI_KEY` to the path.

```bash
# On Linux
vim ~/.bashrc
# add this line to the end of the file
export OpenAI_KEY=sk-xxx
# save and execute
source ~/.bashrc

# For Windows, you can google how to set environment variables on Windows.
```

Use `python -c "import os;print(os.environ.get('OpenAI_KEY'))"` for testing.

You can get your `OpenAI_KEY` from [OpenAI](https://platform.openai.com/account/api-keys).


## Get Started

You can use the `tax <prompt>` to interact with the model, like this:

```
tax write a python code for fibonacci
```

Use `tax -h` to get more information.
```bash
usage: tax.py [-h] [--openai_key OPENAI_KEY] [--model MODEL] [--file FILE] [--url URL] [--default_url] [--claude] [--show_all] prompt [prompt ...]

Description of your program

positional arguments:
  prompt                Prompt

options:
  -h, --help            show this help message and exit
  --openai_key OPENAI_KEY
                        Your key for OpenAI, only for one-time request
  --model MODEL         Model name. You can use all OpenAI models.
  --file FILE           Output file. If specified, the output will be written to this file. Tax will act like ChatGPT
  --url URL             URL for API request which can be accessd under GFW. When your network environment is NOT under GFW, you can use OpenAI API directly.
  --default_url         Use default OpenAI API URL for request.
  --claude              Use Claude API for request.
  --show_all            Show all contents in the response
```

## Support

I have tested on Windows 10/11(cmd) and Ubuntu 22.04, it should work on other platforms.

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

