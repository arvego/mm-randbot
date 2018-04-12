from peewee import SqliteDatabase, Model, IntegerField, TextField, BooleanField


db = SqliteDatabase('gen/data.db')


class User(Model):
    user_id = IntegerField(unique=True)
    chat_id = IntegerField()
    first_name = TextField()
    last_name = TextField(null=True)
    is_member = BooleanField()  # Current status of user (member/left)

    class Meta:
        database = db


db.create_tables([User], safe=True)
