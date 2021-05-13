#!/bin/bash

# Run discord bot with virtual environment

run_discord_bot () {
    source venv/bin/activate
    pip install install -r requirements.txt
    pip install -e .
    python bool_bot
}


echo source venv/bin/activate
if [ $? -eq 0 ]; then
    echo Found venv directory;
    run_discord_bot
else
    echo No venv directory. Installing one now;
    python3 -m venv venv;
    run_discord_bot
fi