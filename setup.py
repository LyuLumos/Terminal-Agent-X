from setuptools import setup

setup(
    name='terminal_agent_x',
    version='0.1',
    packages=['terminal_agent_x'],
    entry_points={
        'console_scripts': [
            'tax = terminal_agent_x.tax:main'
        ]
    },
    author='LyuLumos',
    install_requires=['requests'],
)