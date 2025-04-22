import sys
from album import Album
from nest import Nest
from conf import CONFIG,write_json

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class log():
    def info(text):
        print(bcolors.HEADER + text + bcolors.ENDC)
    
    def ok(text):
        print(bcolors.OKBLUE + text + bcolors.ENDC)

def main():
    log.info('Start processing the gallery...')
    horcrux = Album(CONFIG.PHOTOS_PATH, 'Horcrux', 0)
    config = horcrux.format()
    log.info('Now writing the config file to ' + str(CONFIG.HORCRUX_PATH))
    write_json(CONFIG.HORCRUX_PATH, config)
    Nest().main()
    log.ok('Success! Enjoy~')

if __name__ == '__main__':
    sys.exit(main())
