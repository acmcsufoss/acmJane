from collections import deque


class MessageHistory():

    # queue of messages: replies
    messages = deque()

    def __init__(self, channel_id: int):
        self.channel_id = str(channel_id)

    def get_channel_id(self) -> str:
        return self.channel_id

    def append_message(self, message: str, reply: str):

        # check size
        if len(self.messages) >= 5:
            self.messages.popleft()

        self.messages.append({message: reply})

    def get_queue(self) -> deque:
        return self.messages
