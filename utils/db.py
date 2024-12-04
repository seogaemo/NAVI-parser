import os
import psycopg2


class DB:
    def __init__(self):
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")

        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

        self.cur = self.conn.cursor()

        if self.checkTableIsExist():
            confirm = input("Do you want to drop the table? (Y/n): ")
            if confirm == "y" or confirm == "":
                self.dropTable()

            self.createTable()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def checkTableIsExist(self):
        check_table_query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'road_data'
        )
        """
        self.cur.execute(check_table_query)
        return self.cur.fetchone()[0]

    def dropTable(self):
        drop_table_query = """
        DROP TABLE IF EXISTS road_data
        """
        self.cur.execute(drop_table_query)
        self.conn.commit()

    def createTable(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS road_data (
            id TEXT PRIMARY KEY,
            lat FLOAT,
            lng FLOAT,
            ele FLOAT,
            time TIMESTAMP WITH TIME ZONE,
            duration FLOAT,
            speed FLOAT,
            video TEXT
        )
        """
        self.cur.execute(create_table_query)
        self.conn.commit()

    def insertData(self, data):
        insert_data_query = """
        INSERT INTO road_data (id, lat, lng, ele, time, duration, speed, video)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cur.execute(
            insert_data_query,
            (
                data["id"],
                data["lat"],
                data["lng"],
                data["ele"],
                data["time"],
                data["duration"],
                data["speed"],
                data["video"],
            ),
        )
        self.conn.commit()
