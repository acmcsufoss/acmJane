import os
from dotenv import load_dotenv
import discord
import openai

# load from .env
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
openai.api_key = os.getenv("OPENAI_TOKEN")

# cache map (set of messages: openai reply)
cached_messages = dict()

# conversation map (channel ID: list of MessageHistory objects)
conversations = dict()

# initial prompt
initial_prompt = """
You are Jane, a helpful AI who pretends to be a human. Messages are from
multiple users, so message content begins with their name and a colon.
When replying to users, do not include the 4 numbers in their name after
the # symbol. If someone asks for your opinion on a subject, create an opinion.
If someone is mean to you, kindly let them know that continued aggressive
behavior will result in disciplinary measures. It's a casual server
environment, so feel free to include slang and not always capitalize
your letters.
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


class MessageHistory():

    # message: openai reply
    messages = {}

    def __init__(self, channel_id: int):

        self.channel_id = str(channel_id)

    def get_channel_id(self):
        return self.channel_id

    def append_message(self, message, reply):
        self.messages[message] = reply

    def get_map(self):
        return self.messages


class Client(discord.Client):
    async def on_ready(self: discord.Client):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('----------------------------------------------')

    async def on_message(self, message: discord.Message):
        if message.content == f'<@{self.user.id}>':
            await message.reply('pong!', mention_author=True)
        elif message.content.__contains__(f'<@{self.user.id}'):

            if len(message.content) > 1000:
                await message.reply("Sorry, I don't answer messages longer than 1000 characters!")
                return

            response = ''
            prepared_message = f'{message.author}:' + str(message.content).strip()

            # Store message in cache
            channel_id = message.channel.id
            if channel_id not in conversations:
                conversations[channel_id] = MessageHistory(channel_id=channel_id)
            else:
                MessageHistory(conversations[channel_id]).append_message(prepared_message)

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

            await message.reply(reply)


def main():
    intents = discord.Intents.default()
    intents.message_content = True

    client = Client(intents=intents)
    client.run(token)


if __name__ == "__main__":
    main()
