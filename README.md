# acmJane

> A ChatGPT based conversational Discord bot

## About

acmJane currently utilizes `gpt-3.5-turbo` and is setup to maintain
short conversations with users, with a current maximum conversation
length of 5 messages with each message being capped at 1000 characters.

## Setup

1. Clone the repo

   ```terminal
   git clone https://github.com/acmcsufoss/acmJane.git
   ```

2. Create a virtual environment

   ```terminal
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies

   ```terminal
   pip install -r ./requirements.txt
   ```

4. Setup env according to env.example

5. Run bot

   ```terminal
   python3 src/client.py
   ```

## Resources

- [discord.py docs](https://discordpy.readthedocs.io/en/stable)
