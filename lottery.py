import aesthetic.face_off as face
import sys, logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(message)s')

def lottery(argv, arc):
    config_name = argv[1]
    result = False
    id = 0
    if arc > 2:
        id = int(argv[2])
    while True:
        lottery = face.FaceOff(config_name, id)
        result = lottery.face_off()
        if not result:
            print("Failed, retry.")
        else:
            return


if __name__ == '__main__':
    lottery(sys.argv, len(sys.argv))