import re

# s = "```\nprint('Hello, world!')\n```"
s = "There are a few steps that need to be followed to install Docker on Ubuntu:1. Update the system package index:```sdfdgfhgjhkjlk;```l'jhghfgdsa"

pattern = r"```(.*?)```"
match = re.search(pattern, s, re.DOTALL)
print(match.group(0), match.group(1))

# s_new = re.sub(r'```[\w-]*\n', '```', s)
# print(s_new)
