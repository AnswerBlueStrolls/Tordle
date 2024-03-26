import utils.db_connection as database, utils.ao3 as ao3
import yaml, os, csv
class Loader:
    config = {}
    debug_mode = False
    base_path = ""
    lang = ""
    db = None
    output_dir = ""
    def __init__(self, config_file):
        self.base_path = os.path.dirname(config_file)
        self.output_dir = os.path.join(self.base_path, "output")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.config = yaml.safe_load(open(config_file))
        self.config["db_name"] = os.path.join(self.base_path, self.config["db_name"])
        lang = self.config.get("language")
        if lang != None:
            self.lang = lang
        if self.config["debug"] == True:
            self.debug_mode = True
        self.db = database.AODatabase()
        self.db.init_from_config(self.config)
        
    def load_to_file(self, id):
        output_path = os.path.join(self.output_dir, "{}.csv".format(str(id)))
        with open(output_path, 'w', newline='') as csvfile:
            length = ao3.get_fic_from_ao3(id, csvfile, self.lang)
            if length > 0:
                csvfile.close()
                return output_path
            else:
                return ""
    def load_one_fic(self, id):
        if len(self.db.get_fic_by_id(id)) > 0:
            print("Fanfic already exist, skip ...")
            return False
        csvfile =  self.load_to_file(id)
        if csvfile != "":
            self.db.load_csv(csvfile)
        os.remove(csvfile)
        return True
    
    def load_batch_fics(self, limit):
        batch_dir = os.path.join(self.base_path, "loader")
        loaded_count = 0
        for file_name in os.listdir(batch_dir):
            if loaded_count > limit:
                print("Reach limit, finish loading.")
                return
            full_file_name = os.path.join(batch_dir, file_name)
            with open(full_file_name, 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                for row in csv_reader:
                    res = self.load_one_fic(row[0])
                    if res:
                        loaded_count += 1
                csvfile.close()
            print("Delete file", full_file_name)
            os.remove(full_file_name)           
