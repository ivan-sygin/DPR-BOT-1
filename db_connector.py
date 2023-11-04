import psycopg2
from users import User
class DB_Handler:
    def fetch_data(self,req):
        self.cursor.execute(req)
        self.results = self.cursor.fetchall()
        return self.results
    def close(self):
        self.cursor.close()
    def getUsers(self):
        tmp = self.fetch_data(
            """SELECT * FROM public.admins
            ORDER BY id_chat ASC 
            """)
        users = []
        for item in tmp:
            users.append(User(*item))
        return users

    def __init__(self,host,port,db,user,passw):

        db_params = {
            'host': host,
            'port': port,
            'database': db,
            'user': user,
            'password': passw,
        }
        self.connection = psycopg2.connect(**db_params)
        self.cursor = self.connection.cursor()


