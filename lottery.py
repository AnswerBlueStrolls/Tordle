import aesthetic.face_off as face
import sys

def lottery(argv, arc):
    config_name = argv[1]
    print(argv, arc)
    lottery = face.FaceOff(config_name)
    lottery.face_off()

if __name__ == '__main__':
    lottery(sys.argv, len(sys.argv))