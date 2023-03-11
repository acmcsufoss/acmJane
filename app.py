import os
from discord.message import Message

from dotenv import load_dotenv
import discord

# load from .env
load_dotenv()
token = os.getenv("DISCORD_TOKEN")


class Client(discord.Client):
    async def on_ready(self: discord.Client):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('----------------------------------------------')

    async def on_message(self, message: discord.Message):
        if message.content == f'<@{self.user.id}>':
            await message.reply('pong!', mention_author=True)


intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run(f'{token}')
