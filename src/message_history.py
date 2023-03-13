class MessageHistory():

    # map of messages: replies
    messages = {}

    def __init__(self, channel_id: int):
        self.channel_id = str(channel_id)

    def get_channel_id(self) -> str:
        return self.channel_id

    def append_message(self, message: str, reply: str):

        # check size
        while len(self.messages) >= 5:
            first_key = next(iter(self.messages))
            self.messages.pop(first_key)

        self.messages.append({message: reply})

    def get_map(self) -> dict:
        return self.messages
