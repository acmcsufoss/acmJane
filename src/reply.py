import discord
import openai


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

    def __reply_without_memory(self, message: str) -> str:

        # Generate response
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': self.initial_prompt},
                {'role': 'user', 'content': message}
            ]
        )

        return response

    def generate_reply(self, message: discord.Message, client: discord.Client) -> str:
        """Uses OpenAI to generate a reply

        Keyword arguments:
            message -- The message to be replied token

        Returns:
            OpenAI chat model response
        """

        message_content = message.content.strip()
        reply = ''

        if message_content == f'<@{client.user.id}>':
            return 'pong!'

        if len(message_content) > 1000:
            return "Sorry, I don't answer messages longer than 1000 characters!"

        # Pull from conversations
        if message.channel.id in self.conversations:
            # TODO: Create new reply helper function that
            # takes MessageHistory parameters
            print("[LOG] Retrieving conversation context")
        else:

            # No conversation data, generate plain reply without memory
            prepared_message = f'{message.author}:' + str(message_content)
            reply = self.__reply_without_memory(prepared_message)

            # TODO: Append new value into conversations

        return reply
