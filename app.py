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
            {'role': 'system', 'content': "You're Jane; a helpful assistant."},
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

            # Cache message if not cached
            if message not in cached_messages:
                response = generate_reply(message.content)

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
