# Terminal-Agent-X

[EN](README.md) / [中文](https://github.com/LyuLumos/Terminal-Agent-X/blob/main/README_cn.md) 

## Features

- 👻 一键安装运行
- 🎈 体积极小，不需要任何依赖
- 🐼 支持中英文，能够运行在Windows和Linux多类型终端上
- 🤖 兼容GPT-3.5/4s、DALL·E、 Claude API以及各种第三方API

## 安装

```bash
pip install terminal-agent-x
```


## 配置

您需要添加以下环境变量：

```bash
export tax_key=sk-xxx
export tax_base_url=YOUR_BASE_URL # 可选，默认值: https://api.openai.com
```

从[OpenAI](https://platform.openai.com/account/api-keys)获取您的OpenAI密钥，或者从[Anthropic](https://www.anthropic.com/claude/)获取您的Claude API密钥，并将其设置为`tax_key`。


## 开始使用

可以使用 `tax <prompt>` 开始，例如：

```
tax 用Python写一个计算斐波那契数列的程序
```

使用`tax -h`来查看更多信息。

## 用法

| 模型 | 命令 | 描述 |
| :--- | :--- | :--- |
| ChatGPT | `tax <提示>` | 使用 `gpt-3.5-turbo` 生成内容。 |
| ChatGPT | `tax <提示> --code` | 使用 `gpt-3.5-turbo` 生成代码。如果只生成1行代码，将在您的许可下自动执行。 |
| GPT-4o-mini | `tax <提示> -m gpt-4o-mini` | 使用 GPT-4 生成内容。 |
| GPT-4o | `tax -i <图片路径> -m gpt-4o <提示>` | 上传一张图片并使用 GPT-4 Vision Preview 进行对话。 |
| DALL·E 3 | `tax <提示> -m dalle` | 使用 DALL·E 3 生成图像。目前一次只能生成一张 `1024x1024` 的图像。 |
| Claude | `tax <提示> -m claude` | 使用 Claude 生成代码。如果已在环境变量中设置了 密钥，则使用 `-k your_claude_key`。 |
| Gemini Pro |  `tax <提示> -m gemini-pro` | 使用 Gemini Pro 生成内容。支持 `-k google_api_key`。目前只支持单次对话。 |
| Gemini Pro Vision | `tax -i <图片路径> -m gemini-pro-vision <提示>` | 上传一张图片并使用 Gemini Vision 进行对话。支持 `-k google_api_key`。 |


| 模式 | 命令 | 描述 |
| :--- | :--- | :--- |
| 与模型对话 | `tax -m model_name -c` | 与选定的模型进行对话。 |
| 使用第三方基础 URL 和密钥 | `tax <提示> -u <base_url> -k <key>`| 在环境变量之前使用指定的 URL 和密钥。 |
| 将结果保存到文件 | `tax <提示> -o <output_file>` | 将响应保存到文件中。 |
| 从文件中读取提示| `tax --prompt_file <prompt_file>` | 从文件中读取提示，每行一个提示。请确保您有足够的配额。 |
| 并行处理 | `tax -p --prompt_file input.txt -o output.txt --option max_workers=3 --option chat_mode=openai` | 设置并行处理的更多选项。例如，`--option max_workers=3` 表示可以同时运行 3 个进程。 |


## 注意

你可能会在生成的命令后面看到一行命令
```
Do you want to execute the command? (y/n)
```
请自行决定执行与否。作者对生成的命令的后果不负责任。

## 许可证

[GNU通用公共许可证 v3.0](LICENSE)
