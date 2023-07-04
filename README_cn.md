# Terminal-Agent-X

[EN](README.md) / [中文](https://github.com/LyuLumos/Terminal-Agent-X/blob/main/README_cn.md) / [Wiki](https://github.com/LyuLumos/Terminal-Agent-X/wiki)


## Features

- 👻 一键安装运行
- 🎈 体积极小，不需要任何依赖
- 🐼 支持中英文，能够运行在Windows和Linux多类型终端上
- 🤖 兼容OpenAI GPT-3.5/4s、DALL·E以及 Claude API，可在世界各地使用


## 安装

```bash
pip install terminal-agent-x
```

## 配置

你需要首先配置环境变量 `OpenAI_KEY`。

```bash
# Linux系统
vim ~/.bashrc
# 在文件的末尾添加
export OpenAI_KEY=sk-xxx
# 保存并执行
source ~/.bashrc

# 对于Windows，你可以搜索如何在Windows上设置环境变量。
```

使用 `python -c "import os;print(os.environ.get('OpenAI_KEY'))"` 进行测试。

`OpenAI_KEY` 可以从 [OpenAI](https://platform.openai.com/account/api-keys) 获得。


## 开始使用

可以使用 `tax <prompt>` 开始，例如：

```
tax 用Python写一个计算斐波那契数列的程序
```

使用`tax -h`来查看更多信息。

## 注意

你可能会在生成的命令后面看到一行命令
```
Do you want to execute the command? (y/n)
```
请自行决定执行与否。我对生成的命令的后果不负责任。
