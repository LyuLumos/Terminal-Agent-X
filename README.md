# Terminal-Agent-X

## Install

TBD.

You need to the environment variable `OpenAI_KEY` to the path.

```bash
# On Linux
vim ~/.bashrc

# add this line to the end of the file
export OpenAI_KEY=sk-xxx

# save and excute
source ~/.bashrc
```


Use `python -c "import os;print(os.environ.get('OpenAI_KEY'))"` for testing.

You can get your `OpenAI_KEY` from [OpenAI](https://platform.openai.com/account/api-keys).




## Get Started

You can use the `tax` command to interact with the model, like this:

```
tax write a python code for fibonacci
```

Use `tax -h` to get more information.

## Support

I have tested on Windows 10/11(cmd) and Ubuntu 22.04, but it should work on other platforms.

Current version does not support Windows Powershell, or run on Windows systems early than Windows 10. For these users, you can install `curl on Windows` in cmd to use this tool.

## Attention

You can see a directive after the generated command that says
```
Do you want to excute the command? (y/n)
```
Please execute it or not at your own discretion. I am not responsible for the consequences of generated commands.