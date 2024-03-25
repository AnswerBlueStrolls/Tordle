import sqlite3
class AODatabase:
    db_name = ""
    table_name = ""
    language = "English"
    fanfic_index = 0
    def __init__(self):
        pass

    def init_from_config(self, config):
        self.db_name = config["db_name"]
        self.table_name = config["table_name"]
        self.language = config["language"]
        self.fanfic_index = config["fanfic_index"]

    def get_one_fic_randomly(self):
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
        sql = "SELECT * FROM {} WHERE language = '{}' AND work_id = {} ORDER BY RANDOM() LIMIT 1".format(self.table_name, self.language, id)
        conn = sqlite3.connect(self.db_name)
        crsr = conn.cursor()
        crsr.execute(sql)
        result = crsr.fetchall()
        if len(result) == 0:
            return ""
        id = result[0][0]
        body = result[0][self.fanfic_index]
        conn.close()
        return body