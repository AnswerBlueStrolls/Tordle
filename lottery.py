import aesthetic.face_off as face
import sys, logging, os
import argparse
import crawler.loader as loader
from utils.fandom_config import FandomConfig

def lottery(config_file, id):
    result = False
    config = FandomConfig(config_file)
    while True:
        lottery = face.FaceOff(config, id)
        result = lottery.repeat_face_off()
        if result == 0:
            print("Continue ...")
        if result == -1:
            print("Start a new one")
            lottery.reset()
        else:
            return

def web_lottery(fandom, language, id, text_length):
    config = FandomConfig.create_from_web(fandom, language)
    faceoff = face.FaceOff(config, id, text_length)
    result, mappings, all_characters = faceoff.get_face_off_content()
    if len(result) == 0:
        print("Could not get result")
    return result, mappings, all_characters

def load(config_file, id, limit):
    config = FandomConfig(config_file)
    load = loader.Loader(config)
    if id > 0:
        load.load_one_fic(id)
    else:
        load.load_batch_fics(limit)

def save_file(config_file, id):
    config = FandomConfig(config_file)
    load = loader.Loader(config)
    if id > 0:
        load.load_to_file(id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--config', type=str, help='config file of your fandom')
    parser.add_argument('--action', type=str, help="action to do (load, draw, file)")
    parser.add_argument('--id', type=int, default=0, help="the id of fanfic")
    parser.add_argument('--limit', type=int, default=-1, required=False, help="the max number of fanfic to load")
    parser.add_argument('--file', type=str, help='local file to un-sensitive')
    args = parser.parse_args()
    if args.action == "load":
        load(args.config, args.id, args.limit)
    if args.action == "draw":
        lottery(args.config, args.id)
    if args.action == "file":
        save_file(args.config, args.id)
