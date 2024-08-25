import psycopg2
import os
from pytz import timezone
from dotenv import load_dotenv
load_dotenv()

DATABASE=os.getenv("DATABASE")
DATABASE_USER=os.getenv("DATABASE_USER")
DATABASE_PASSWORD=os.getenv("DATABASE_PASSWORD")
DATABASE_HOST=os.getenv("DATABASE_HOST")
DATABASE_PORT=os.getenv("DATABASE_PORT")

class DataAccessObject:
    def __init__(self, tableName) -> None:
        self.tableName = tableName
    def connect(self):
        conn = psycopg2.connect(database=DATABASE,
                            user=DATABASE_USER,
                            password=DATABASE_PASSWORD,
                            host=DATABASE_HOST,
                            port=DATABASE_PORT)
        cursor = conn.cursor()
        return conn, cursor

    def close(self, conn, cursor):
        conn.close()
        cursor.close()
        
    def query(self, values):
        conn, cursor = self.connect()
        command = f''' SELECT * FROM "{self.tableName}" WHERE channel_id = '{values['channel_id']}' '''
        cursor.execute(command)
        row = cursor.fetchall()
        self.close(conn=conn, cursor=cursor)
        return row
        
    def insert(self, values):
        try:
            conn, cursor = self.connect()
            command = f'''
            INSERT INTO public."{self.tableName}"(
            name, subs, total_views, avg_engagement_rate, search_term, creation_date, update_date, channel_id)
            VALUES ('{self.formatString(values['name'])}', {values['subs']}, {values['total_views']}, {values['avg_engagement_rate']}, '{self.formatString(values['search_term'])}', '{values['creation_date']}', '{values['update_date']}', '{values['channel_id']}');
            '''
            cursor.execute(command)
            conn.commit()
            self.close(conn=conn, cursor=cursor)
        except Exception as e:
            print(e)
        
    def update(self, values):
        try:
            conn, cursor = self.connect()
            command = f'''
            UPDATE public."{self.tableName}"
            SET name={values['name']}, subs={values['subs']}, total_views={values['total_views']}, avg_engagement_rate={values['avg_engagement_rate']}, search_term={values['search_term']}, creation_date={values['creation_date']}, update_date={values['update_date']}, channel_id={values['channel_id']}
            WHERE youtube_channel_id = {values['youtube_channel_id']};
            '''
            cursor.execute(command)
            conn.commit()
            self.close(conn=conn, cursor=cursor)
        except Exception as e:
            print(e)
    def formatString(self, string: str):
        return string.replace("'","''")