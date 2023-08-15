import sqlite3

class SQLiteDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def execute(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.conn.commit()

    def fetch_all(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchone()

    def total(self, query, params=None):
        if params:
            result = self.fetch_one(query, params)
        else:
            result = self.fetch_one(query)
        return result[0] if result else 0

    def delete(self, query, params=None):
        if params:
            self.execute(query, params)
        else:
            self.execute(query)


class Model:
    db = None

    @classmethod
    def initialize(cls, db):
        cls.db = db

    @classmethod
    def create_table(cls):
        columns = ', '.join([f"{column} {data_type}" for column,
                            data_type in cls.__dict__.items() if not column.startswith('__')])
        create_table_query = f"CREATE TABLE IF NOT EXISTS {cls.__name__} (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns},create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        
        cls.db.execute(create_table_query)

    def save(self):
        columns = ', '.join(self.__dict__.keys())
        placeholders = ', '.join(['?' for _ in self.__dict__.values()])
        insert_query = f"INSERT INTO {self.__class__.__name__} ({columns}) VALUES ({placeholders})"
        values = tuple(self.__dict__.values())
        self.db.execute(insert_query, values)

    def update(self):
        update_query = f"UPDATE {self.__class__.__name__} SET " + ', '.join(
            [f"{column} = ?" for column in self.__dict__.keys() if column != 'id']) + " WHERE id = ?"
        values = tuple(value for column, value in self.__dict__.items()
                       if column != 'id') + (self.id,)
        self.db.execute(update_query, values)

    def save_or_update(self):
        if hasattr(self, 'id') and self.id:
            self.update()
        else:
            self.save()

    def delete(self):
        delete_query = f"DELETE FROM {self.__class__.__name__} WHERE id=?"
        self.db.delete(delete_query, (self.id,))

    @classmethod
    def fetch_one(cls, where='1=1', params=None):
        sql = f"""SELECT * FROM {cls.__name__} WHERE {where}"""
        if params:
            result = cls.db.fetch_one(sql, params)
        else:
            result = cls.db.fetch_one(sql)

        if result:
            instance = cls()
            instance.__dict__.update(result)
            return instance
        else:
            return None

    @classmethod
    def total(cls, where='1=1', params=None):
        sql = f"""SELECT count(1) FROM {cls.__name__} WHERE {where}"""
        return cls.db.total(sql,params)

    @classmethod
    def fetch_all(cls, where='1=1', params=None):
        sql = f"""SELECT * FROM {cls.__name__} WHERE {where}"""
        if params:
            results = cls.db.fetch_all(sql, params)
        else:
            results = cls.db.fetch_all(sql)

        instances = []
        for result in results:
            instance = cls()
            instance.__dict__.update(result)
            instances.append(instance)

        return instances


class VitsHistory(Model):
    user_id = "INTEGER"
    content = "TEXT"

class User(Model):
    access_token = "TEXT"


if __name__ == "__main__":

    db = SQLiteDB('new.sqlite')
    Model.initialize(db)
    # Message.create_table()
    # flag = Message.fetch_one("msg_id = '123456'")
    # message = Message()
    # message.context = 'msg.text'
    # message.message_id = 'msg.MsgId'
    # message.toUserName = 'msg.NickName or ''ME'''
    # message.fromUserName = 'msg.ActualNickName or msg.user.NickName'
    # message.save()
