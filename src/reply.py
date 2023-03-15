import discord
import openai
from message_history import MessageHistory


class OpenAIReply():

    def __init__(self, token: str):
        openai.api_key = token

    # conversation map (channel ID: list of MessageHistory objects)
    conversations = dict()

    # initial prompt
    initial_prompt = """
    You are Jane, a helpful AI who pretends to be a human. Messages are from
    multiple users, so message content begins with their name and a colon.
    When replying to users, do not include the 4 numbers in their name after
    the # symbol. If someone asks for your opinion on a subject, create an
    opinion. If someone is mean to you, kindly let them know that continued
    aggressive behavior will result in disciplinary measures. It's a casual
    server environment, so feel free to include slang and not always capitalize
    your letters.
    """

    def __reply_without_memory(self, message: str, channel_id: int) -> str:

        # Generate response
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': self.initial_prompt},
                {'role': 'user', 'content': message}
            ]
        )

        # Append new value into conversations
        history = MessageHistory(channel_id)
        self.conversations.update({channel_id: history})

        # Append latest message and reply
        reply = response['choices'][0]['message']['content']
        history.append_message(message, reply)

        return reply

    def __reply_with_memory(self, history: MessageHistory, message: str):
        messages = [{'role': 'system', 'content': self.initial_prompt}]
        for k, v in dict(history.get_map()).items():
            messages.append({'role': 'user', 'content': k})
            messages.append({'role': 'system', 'content': v})
        messages.append({'role': 'user', 'content': message})

        # Generate response
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages
        )

        # Append latest message and reply
        reply = response['choices'][0]['message']['content']
        history.append_message(message, reply)

        return reply

    def generate_reply(self, message: discord.Message, client: discord.Client) -> str:
        """Uses OpenAI to generate a reply

        Keyword arguments:
            message -- The message to be replied token

        Returns:
            OpenAI chat model response
        """

        message_content = message.content.strip()
        prepared_message = f'{message.author}:' + str(message_content)
        reply = None

        if message_content == f'<@{client.user.id}>':
            return 'pong!'

        if len(message_content) > 1000:
            return "Sorry, I don't answer messages longer than 1000 characters!"

        # Pull from conversations
        if message.channel.id in self.conversations:
            history = self.conversations.get(message.channel.id)
            reply = self.__reply_with_memory(history, prepared_message)
        else:
            # No conversation data, generate plain reply without memory
            reply = self.__reply_without_memory(prepared_message, message.channel.id)

        return reply
