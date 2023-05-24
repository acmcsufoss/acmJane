import os
from reply import OpenAIReply
from dotenv import load_dotenv
from datetime import date, datetime
import tiktoken
import discord

# load from .env
load_dotenv()
token = os.getenv("DISCORD_TOKEN")


def count_tokens(text: str) -> int:
    """String tokenizer

    Keyword arguments:
    text -- Text [string]
    Return: Number of tokens [int]
    """

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))


def should_reply(client: discord.Client, message: discord.Message) -> bool:
    """Decides if Client should reply to a message

    Keyword arguments:
    client -- Discord Client
    message -- Discord message
    Return: Boolean if Client should reply
    """

    message_content = message.content.strip()

    # Check permissions
    if not message.channel.permissions_for(message.guild.me).send_messages:
        return False

    return client.user.mentioned_in(message)

# TODO: Add token value of all messages sent in API call


def at_limit(d: dict) -> bool:
    """Checks daily character limit

    Keyword arguments:
    d -- Dictionary of token count per day
    Return: Boolean value of current date being over limit
    """

    monthly_usd_limit = 5
    daily_usd_limit = monthly_usd_limit / 30
    cost_per_1k_token = 0.002
    token_cost_today = (d.get(date.today(), 0) / 1000) * cost_per_1k_token
    return token_cost_today >= daily_usd_limit


class Client(discord.Client):

    tokens_per_day = dict()
    last_message_per_guild = dict()
    last_message_per_guild_per_channel = dict()
    GUILD_RATE_LIMIT_SECONDS = 2
    CH_RATE_LIMIT_SECONDS = 4

    async def on_ready(self: discord.Client):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('----------------------------------------------')

    async def on_message(self, message: discord.Message):
        if should_reply(self, message):
            now = datetime.now()
            current = (now.hour * 60 * 60) + (now.minute * 60) + now.second

            # prepare and add to limit
            prepared_message = f'{message.author}: {str(message.content).strip()}'
            self.tokens_per_day[date.today()] = count_tokens(
                prepared_message) + self.tokens_per_day.get(date.today(), 0)

            # check for token limit and rate limit
            if at_limit(self.tokens_per_day):
                await message.reply("I'm currently sleeping, but check back later!", mention_author=False)
            else:
                # check on channel then guild level
                ch_diff = current - \
                    self.last_message_per_guild_per_channel.get(
                        message.channel.id, 0)
                guild_diff = current - \
                    self.last_message_per_guild.get(message.channel.id, 0)

                if message.guild.id in self.last_message_per_guild and (ch_diff < self.CH_RATE_LIMIT_SECONDS or guild_diff < self.GUILD_RATE_LIMIT_SECONDS):
                    return

            # update last message time
            self.last_message_per_guild[message.guild.id] = current
            self.last_message_per_guild_per_channel[message.channel.id] = current

            # reply
            try:
                openai_reply = OpenAIReply(
                    os.getenv("OPENAI_TOKEN"), self.user.display_name)
                reply = await openai_reply.generate_reply(message, self)

                if reply.startswith(f'{self.user.display_name}: '):
                    reply = reply.split(f'{self.user.display_name}: ')[1]

                await message.reply(reply, mention_author=False)
            except Exception as e:
                print(e)
                error = "Uh oh, looks like something went wrong, try again later!"
                await message.reply(error, mention_author=False)


def main():
    intents = discord.Intents.default()
    intents.message_content = True

    client = Client(intents=intents)
    client.run(token)


if __name__ == "__main__":
    main()
