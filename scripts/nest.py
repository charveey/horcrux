import sys
import json
from conf import CONFIG, write_json


class Nest:
    def __init__(self):
        self.resources = []

    def read_json(self, relative_path):
        abs_path = CONFIG.DIR_PATH.joinpath(relative_path)
        print('Reading from:', abs_path)
        with open(abs_path, 'r') as f:
            return json.load(f)

    def append_album(self, album, photos=None):
        """
        If photos are given, convert album to a photo list container.
        """
        if photos is not None:
            album = {
                'name': album['name'],
                'type': 'photos',
                'parents': album.get('parents', []),
                'list': photos
            }

        self.resources.append(album)

    def convert_child_items(self, items):
        """
        Reorder children according to the given 'order' list.
        """
        return [items['dict'][key] for key in items['order'] if key in items['dict']]

    def nest_photos(self, album, list_path):
        items = self.read_json(list_path)
        photos = self.convert_child_items(items)
        self.append_album(album, photos)

    def nest_album(self, album):
        if album['type'] != 'album':
            return

        if album.get('no_sub_album'):
            self.nest_photos(album, album['path'])
        else:
            children = self.convert_child_items(album['items'])
            photos = [item for item in children if item['type'] == 'photo']
            if photos:
                self.append_album(album, photos)

            for child in children:
                self.nest_album(child)

    def main(self):
        horcrux = self.read_json(CONFIG.HORCRUX_PATH)
        self.nest_album(horcrux)
        write_json(CONFIG.CONFIG_PATH, self.resources)


if __name__ == '__main__':
    nest = Nest()
    sys.exit(nest.main())
