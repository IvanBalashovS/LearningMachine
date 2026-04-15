class ChatRoom:
    
    def __init__(self):
        self._users = [] 
    
    def add_user(self, user):
        self._users.append(user)
        user.set_chat_room(self)
    
    def send_message(self, sender, message):
        print(f"Чат: сообщение от {sender.name}")
        for user in self._users:
            if user != sender:
                user.receive(sender.name, message)


class User:
    def __init__(self, name: str):
        self.name = name
        self._chat_room = None
    
    def set_chat_room(self, chat_room):
        self._chat_room = chat_room
    
    def send(self, message: str):
        print(f"{self.name} пишет: '{message}'")
        if self._chat_room:
            self._chat_room.send_message(self, message)
    
    def receive(self, sender_name: str, message: str):
        print(f"{self.name} получил от {sender_name}: '{message}'")


if __name__ == "__main__":
    chat = ChatRoom()

    alice = User("Олеся")
    bob = User("Ваня")
    charlie = User("Саша")
    
    chat.add_user(alice)
    chat.add_user(bob)
    chat.add_user(charlie)
    
    alice.send("Всем привет!")
    bob.send("Привет, Алиса!")
    charlie.send("Как дела?")