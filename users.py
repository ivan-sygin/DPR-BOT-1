class User:
    chat_id:str
    name:str
    surname:str
    isAdmin:bool
    notificationsEnabled:bool

    def __init__(self,chat_id,name,surname,isAdmin,notificationsEnabled):
        self.chat_id = chat_id
        self.name = name
        self.surname = surname
        self.isAdmin = isAdmin
        self.notificationsEnabled = notificationsEnabled

    def __str__(self):
        return f"{self.chat_id}|{self.name}|{self.surname}|{'+' if self.isAdmin else '-'}|{'+' if self.notificationsEnabled else '-'}"

    def __repr__(self):
        return f"{self.chat_id}|{self.name}|{self.surname}|{'+' if self.isAdmin else '-'}|{'+' if self.notificationsEnabled else '-'}"