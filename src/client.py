import os
from reply import OpenAIReply
from dotenv import load_dotenv
import discord

# load from .env
load_dotenv()
token = os.getenv("DISCORD_TOKEN")


def should_reply(client: discord.Client, message: discord.Message) -> bool:
    message_content = message.content.strip()

    # Return true if message is a reply to bot
    if message.reference and message.reference.cached_message:
        return message.reference.cached_message.author.id == client.user.id

    return message_content.__contains__(f'<@{client.user.id}') or message_content.lower().__contains__(client.user.name.lower())


class Client(discord.Client):
    async def on_ready(self: discord.Client):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('----------------------------------------------')

    async def on_message(self, message: discord.Message):
        if should_reply(self, message):
            openai_reply = OpenAIReply(os.getenv("OPENAI_TOKEN"))
            reply = openai_reply.generate_reply(message, self)
            await message.reply(reply, mention_author=False)


def main():
    intents = discord.Intents.default()
    intents.message_content = True

    client = Client(intents=intents)
    client.run(token)


if __name__ == "__main__":
    main()
