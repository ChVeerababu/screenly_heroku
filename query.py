import pymysql as p
from dotenv import load_dotenv
import os
load_dotenv()



host = os.environ.get('RDS_URL')
user = os.environ.get('RDS_USER')
password = os.environ.get('RDS_PASS')
database = os.environ.get('RDS_DB')


# connect database here
def db():
    dbcon=p.connect(host=host,user=user,password=password,database=database)
    return dbcon
# query execution block
def query_db(query, args=(), one=False):
    cur = db().cursor()
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.connection.close()
    return (r[0] if r else None) if one else r





















'''class DB:
    def __init__(self,host,user,password,database):
        self.host=host
        self.user=user
        self.password=password
        self.database=database

    def db(self):

        dbcon=p.connect(host=self.host,user=self.user,password=self.password,database=self.database)
        return dbcon.cursor()
    # query execution block
    def query_db(self,query, args=(), one=False):
        cur = db()
        cur.execute(self.query, self.args)
        r = [dict((cur.description[i][0], value) \
                for i, value in enumerate(row)) for row in cur.fetchall()]
        cur.connection.close()
        return (r[0] if r else None) if one else r

cur=DB(host,user,password,database)'''
