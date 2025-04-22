from photo import Photo
from conf import CONFIG, write_json


class Album:
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif'}

    def __init__(self, path, name, root):
        self.path = path
        self.name = name
        self.root = root or 0
        self.items_order = []
        self.items_dict = {}

    def _get_sorted_paths(self, entries, type_):
        def sort_key(entry):
            order_by_map = {
                'access': 'st_atime',
                'modify': 'st_mtime',
                'create': 'st_ctime',
            }

            conf_map = {
                'album': {
                    'order_by': CONFIG.ORDER_ALBUMS_BY_LAST_DO,
                    'sort_by_time': CONFIG.SORT_ALBUMS_BY_TIME,
                    'reverse': CONFIG.REVERSE_ALBUMS_ORDER,
                },
                'photo': {
                    'order_by': CONFIG.ORDER_PHOTOS_BY_LAST_DO,
                    'sort_by_time': CONFIG.SORT_PHOTOS_BY_TIME,
                    'reverse': CONFIG.REVERSE_PHOTOS_ORDER,
                }
            }

            if conf_map[type_]['sort_by_time']:
                attr = order_by_map[conf_map[type_]['order_by']]
                return getattr(entry.stat(), attr)
            return entry.name

        reverse = CONFIG.REVERSE_ALBUMS_ORDER if type_ == 'album' else CONFIG.REVERSE_PHOTOS_ORDER
        return sorted(entries, key=sort_key, reverse=reverse)

    def _is_image(self, path):
        # Reject miniature images like 'photo.min.jpg'
        return (
            path.is_file()
            and path.suffix.lower() in self.IMAGE_EXTENSIONS
            and '.min.' not in path.name.lower()
        )

    def _get_album_metadata(self):
        parts = self.path.parts
        return parts[-self.root:] if self.root > 0 else []

    def format(self):
        print(f"Processing album: {self.name}")
        album_metadata = {
            'name': self.name,
            'type': 'album',
            'root': self.root,
            'parents': self._get_album_metadata()
        }

        image_paths = []
        sub_album_paths = []

        for entry in self.path.iterdir():
            if entry.is_dir():
                sub_album_paths.append(entry)
            elif self._is_image(entry):
                image_paths.append(entry)

        photo_list = self._get_sorted_paths(image_paths, 'photo')
        album_list = self._get_sorted_paths(sub_album_paths, 'album')

        has_child_album = False

        for photo_path in photo_list:
            photo = Photo(photo_path)
            photo_conf = photo.format()
            if photo_conf:
                self.items_order.append(photo_path.name)
                self.items_dict[photo_path.name] = photo_conf

        for album_path in album_list:
            sub_album = Album(album_path, album_path.name, self.root + 1)
            self.items_order.append(album_path.name)
            self.items_dict[album_path.name] = sub_album.format()
            has_child_album = True

        items = {'order': self.items_order, 'dict': self.items_dict}

        if has_child_album:
            return {**album_metadata, 'items': items}
        else:
            # No sub-albums; write config
            filename = '-'.join(album_metadata['parents']) + '.json'
            output_path = CONFIG.ALBUMS_PATH / filename
            print("Writing album config to", output_path)
            write_json(output_path, items)
            return {
                **album_metadata,
                'path': './' + str(output_path.relative_to(CONFIG.DIR_PATH)),
                'no_sub_album': True
            }
