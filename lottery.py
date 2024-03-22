import aesthetic.face_off as face
import sys

def lottery(argv, arc):
    config_name = argv[1]
    result = False
    
    while True:
        lottery = face.FaceOff(config_name)
        result = lottery.face_off()
        if not result:
            print("Failed, retry.")
        else:
            return


if __name__ == '__main__':
    lottery(sys.argv, len(sys.argv))