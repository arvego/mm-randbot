from time import sleep
from models import db, User


from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import Channel, ChannelParticipantsRecent


# Those constants are aviable on https://my.telegram.org/apps. Just create new app if needed
API_ID = 666666
API_HASH = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
PHONE = '+1234567890'


class FetcherClient(TelegramClient):
    def __init__(self, session_user_id, user_phone, api_id, api_hash):
        super().__init__(session_user_id, api_id, api_hash)

        # Проверка соеденения с сервером. Проверка данных приложения
        print('Connecting to Telegram servers...')
        if not self.connect():
            print('Initial connection failed. Retrying...')
            if not self.connect():
                print('Could not connect to Telegram servers.')
                return

        # Проверка авторизирован ли юзер под сессией
        if not self.is_user_authorized():
            print('First run. Sending code request...')
            self.send_code_request(user_phone)

            self_user = None
            while self_user is None:
                code = input('Enter the code you just received: ')
                try:
                    self_user = self.sign_in(user_phone, code)

                # Two-step verification may be enabled
                except SessionPasswordNeededError:
                    pw = input('Two step verification is enabled. Please enter your password: ')
                    self_user = self.sign_in(password=pw)

    def run(self):
        # Запрос выбора чата для сканирования
        peer = self.choose_peer()
        users = self.get_user_list(peer)
        self.insert_users_into_database(users, peer.id)
        return users

    def choose_peer(self):
        dialogs = self.get_dialogs(limit=10)
        s = ''
        entities = [dialog.entity for dialog in dialogs if isinstance(dialog.entity, Channel)]
        entities = [entity for entity in entities if entity.megagroup]

        for i, entity in enumerate(entities):
            s += '{}. {}\t | {}\n'.format(i, entity.title, entity.id)

        print(s)
        num = input('Choose group: ')
        print('Chosen: ' + entities[int(num)].title)

        return entities[int(num)]

    @staticmethod
    def get_user_list(peer):
        participants = client(GetParticipantsRequest(peer, ChannelParticipantsRecent(), offset=0, limit=200, hash=0))
        users = participants.users

        while participants.count > len(users):
            participants = client(GetParticipantsRequest(peer,
                                                         ChannelParticipantsRecent(),
                                                         offset=len(users),
                                                         limit=200, hash=0))
            users.extend(participants.users)
            sleep(0.5)

        return users

    @staticmethod
    def insert_users_into_database(users, chat_id):
        users = [{'chat_id': chat_id,
                  'user_id': user.id,
                 'first_name': user.first_name,
                 'last_name': user.last_name,
                  'is_member': True} for user in users if user.first_name]

        with db.atomic():
            User.insert_many(users).on_conflict_replace().execute()


# Client creates session so code and password is needed once
client = FetcherClient('fetcher', PHONE, API_ID, API_HASH)
client.run()

