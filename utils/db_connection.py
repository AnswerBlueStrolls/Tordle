import sqlite3, pandas
language_map = {"English": "English", "Chinese": "Zhong Wen"}
class AODatabase:
    db_name = ""
    table_name = ""
    language = ""
    fanfic_index = 0
    def __init__(self):
        pass

    def init_from_config(self, config):
        self.db_name = config["db_name"]
        self.table_name = config["table_name"]
        lang = config.get("language")
        if lang != None:
            self.language = lang
        self.fanfic_index = config["fanfic_index"]

    def get_one_fic_randomly(self):
        if self.language == "":
            sql = "SELECT * FROM {} ORDER BY RANDOM() LIMIT 1".format(self.table_name)
        else:
            sql = "SELECT * FROM {} WHERE language = '{}' ORDER BY RANDOM() LIMIT 1".format(self.table_name, self.language)
        conn = sqlite3.connect(self.db_name)
        crsr = conn.cursor()
        crsr.execute(sql)
        result = crsr.fetchall()
        id = result[0][0]
        body = result[0][self.fanfic_index]
        conn.close()
        return id, body

    def get_fic_by_id(self, id):
        sql = "SELECT * FROM {} WHERE work_id = {} LIMIT 1".format(self.table_name, id)
        conn = sqlite3.connect(self.db_name)
        crsr = conn.cursor()
        crsr.execute(sql)
        result = crsr.fetchall()
        if len(result) == 0:
            conn.close()
            return ""
        id = result[0][0]
        body = result[0][self.fanfic_index]
        conn.close()
        return body
    
    def load_csv(self, csv_file):
        conn = sqlite3.connect(self.db_name)
        col_names = ['work_id', 'title', 'author', 'rating', 'category', 'fandom', 'relationship', 'character', 'additional tags', 'language', 'published', 'status', 'status date', 'words', 'chapters', 'comments', 'kudos', 'bookmarks', 'hits', 'all_kudos', 'all_bookmarks', 'body']
        df = pandas.read_csv(csv_file, names=col_names)
        df.to_sql(self.table_name, conn, if_exists='append', index=False)
        conn.close()