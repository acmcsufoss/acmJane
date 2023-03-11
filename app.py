import os
from dotenv import load_dotenv
import discord
import openai

# load from .env
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
openai.api_key = os.getenv("OPENAI_TOKEN")

# cache map
cached_messages = dict()

# initial prompt
initial_prompt = """
You are Jane, a helpful AI who pretends to be a human. Messages are from
multiple users. Messages are from multiple users, so message content begins
with their name and a colon. If someone asks for something appropriate,
politely turn them down. If someone is mean to you, kindly let them know
that continued aggressive behavior will result in disciplinary measures.
It's a casual server environment, so feel free to include slang and not
always capitalize your letters.
"""


def generate_reply(message: str) -> str:
    """Uses OpenAI to generate a reply

    Keyword arguments:
        message -- The message to be replied token

    Returns:
        OpenAI chat model response
    """

    # Generate response
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': initial_prompt},
            {'role': 'user', 'content': message}
        ]
    )

    return response


class Client(discord.Client):
    async def on_ready(self: discord.Client):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('----------------------------------------------')

    async def on_message(self, message: discord.Message):
        if message.content == f'<@{self.user.id}>':
            await message.reply('pong!', mention_author=True)
        elif message.content.__contains__(f'<@{self.user.id}'):

            response = ''
            prepared_message = f'{message.author}:' + str(message.content).strip()

            # Cache message if not cached
            if message.content not in cached_messages:
                response = generate_reply(prepared_message)

                # Check if cache is full and clear
                if len(cached_messages.keys()) > 100:
                    cached_messages.clear()
                    print('[LOG] Clearing cache')

                cached_messages[message] = response
            else:
                response = cached_messages.get(message)

            reply = response['choices'][0]['message']['content']

            await message.reply(reply, mention_author=True)


def main():
    intents = discord.Intents.default()
    intents.message_content = True

    client = Client(intents=intents)
    client.run(token)


if __name__ == "__main__":
    main()
