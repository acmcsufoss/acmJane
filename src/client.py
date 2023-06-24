from collections import defaultdict
import os
import palm
from dotenv import load_dotenv
from datetime import datetime
import discord

# load from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
channel_history = defaultdict(list)  # key: channel id, value: list of messages


def should_reply(client: discord.Client, message: discord.Message) -> bool:
    """Decides if Client should reply to a message

    Keyword arguments:
    client -- Discord Client
    message -- Discord message
    Return: Boolean if Client should reply
    """

    # Check permissions
    if not message.channel.permissions_for(message.guild.me).send_messages:
        return False

    return client.user.mentioned_in(message)


class Client(discord.Client):
    async def on_ready(self: discord.Client):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("----------------------------------------------")

    async def on_message(self, message: discord.Message):
        if should_reply(self, message):
            current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

            # prepare and add to limit
            prepared_message = (
                f"{message.author} ({current_time}): {message.content.strip()}"
            )

            # insert into channel history
            channel_history[message.channel.id].append(prepared_message)

            try:
                reply = palm.reply(channel_history[message.channel.id])

                await message.reply(reply, mention_author=False)

            except Exception as e:
                print(e)
                await message.reply(
                    "Uh oh, something went wrong, try again later!",
                    mention_author=False,
                )


def main():
    intents = discord.Intents.default()
    intents.message_content = True

    client = Client(intents=intents)
    client.run(TOKEN)


if __name__ == "__main__":
    main()
