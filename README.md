# Eric-Bot

A discord eric bot. It will be eric's worst nightmare. 

# Installation

First check out the documentation here: https://discordpy.readthedocs.io/en/latest/intro.html

For linux/mac users (in the command line):

1. pip3 install -r requirements.txt
(Installs everything in requirements.txt, feel free to add it if you find other packages you want to use)
2. touch .env 
3. touch google-drive-credentials.json
(For steps 2-3, ask Justin or go onto the test server to find the files)
4. pip3 install -e . 
(Loads the bool_bot as its own library. Need to do this for tests)
5. python3 bool_bot 
(To start the app)

# Tests

Type "pytest" to run tests

All tests are located in bool_bot/tests directory.

[Pytest](https://docs.pytest.org/en/stable/)
[Pytest-mocker](https://pypi.org/project/pytest-mock/)
[Pytest-mocker-tutorial](https://changhsinlee.com/pytest-mock/)

**NOTE**
When making a new test file, make sure to put test in the name of the file or else it won't work.

# Contributing

For contributing/code of conduct go [here](./CONTRIBUTING.md)

# Features

For now feature list will be localized to this [GoogleDoc](https://docs.google.com/document/d/1NiyKNi84mMjQg219-CK9Bu_EmCaqTWaEj1crirnnbxM/edit?usp=sharing)

# Test Server

Here is the [test_server](https://discord.gg/qsmZYek)