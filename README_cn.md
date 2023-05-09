# Terminal-Agent-X

## 安装

TBD.

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

使用`tax -h`来获得更多信息。

## 支持

目前仅在 Windows 10/11(cmd) 和 Ubuntu 22.04上进行了测试，理论上也支持其他平台。

目前的版本不支持在Windows Powershell运行，也不能在早于Windows 10的系统运行。对于这些用户，你可以安装 `curl on Windows` 以使用此工具。

## 注意

你可能会在生成的命令后面看到一行命令
```
Do you want to execute the command? (y/n)
```
请自行决定执行与否。我对生成的命令的后果不负责任。
