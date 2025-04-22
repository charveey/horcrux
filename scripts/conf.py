from types import SimpleNamespace
from pathlib import Path
import json
import yaml

# Core paths
REPO_DIR = Path.cwd()
DIR_PATH = Path(__file__).parent.parent
PHOTOS_PATH = DIR_PATH.joinpath('photos/')
ALBUMS_PATH = DIR_PATH.joinpath('_data/albums')
HORCRUX_PATH = DIR_PATH.joinpath('_data/Horcrux.json')
CONFIG_PATH = DIR_PATH.joinpath('_data/config.json')
CONF_YAML_PATH = DIR_PATH.joinpath('_config.yml')

# Ensure albums path exists
ALBUMS_PATH.mkdir(parents=True, exist_ok=True)

# Default config values
DEFAULT_CONFIG = {
    'DEBUG': False,
    'MIN_WIDTH': 600,
    'COPYRIGHT': '@im_kveen',
    'FONT_SIZE': 40,
    'FONT_FAMILY': 'Eczar-Medium.ttf',
    'WATERMARK_ROTATE': 0,
    'SIGN_THUMBNAIL': False,
    'SIGN_ORIGINAL': True,
    'SORT_ALBUMS_BY_TIME': True,
    'REVERSE_ALBUMS_ORDER': True,
    'ORDER_ALBUMS_BY_LAST_DO': 'access',
    'SORT_PHOTOS_BY_TIME': False,
    'REVERSE_PHOTOS_ORDER': True,
    'ORDER_PHOTOS_BY_LAST_DO': 'access',
    'KEEP_ORDER': False,

    # Paths in config for unified access
    'REPO_DIR': REPO_DIR,
    'DIR_PATH': DIR_PATH,
    'PHOTOS_PATH': PHOTOS_PATH,
    'ALBUMS_PATH': ALBUMS_PATH,
    'HORCRUX_PATH': HORCRUX_PATH,
    'CONFIG_PATH': CONFIG_PATH,
    'CONF_YAML_PATH': CONF_YAML_PATH,
}

# Load and apply _config.yml values
with open(CONF_YAML_PATH, 'r') as config_file:
    site_conf = yaml.load(config_file, Loader=yaml.FullLoader)

DEFAULT_CONFIG['COPYRIGHT'] = '@' + site_conf.get('instagram', 'unknown')

process = site_conf.get('process', {})
album_conf = process.get('album', {})
photo_conf = process.get('photo', {})
watermark_conf = photo_conf.get('watermark', {})

DEFAULT_CONFIG.update({
    'MIN_WIDTH': photo_conf.get('min_width', DEFAULT_CONFIG['MIN_WIDTH']),
    'FONT_SIZE': watermark_conf.get('fontsize', DEFAULT_CONFIG['FONT_SIZE']),
    'FONT_FAMILY': watermark_conf.get('fontfamily', DEFAULT_CONFIG['FONT_FAMILY']),
    'WATERMARK_ROTATE': watermark_conf.get('rotate', DEFAULT_CONFIG['WATERMARK_ROTATE']),
    'SIGN_THUMBNAIL': watermark_conf.get('thumbnail', DEFAULT_CONFIG['SIGN_THUMBNAIL']),
    'SIGN_ORIGINAL': watermark_conf.get('original', DEFAULT_CONFIG['SIGN_ORIGINAL']),
    'SORT_ALBUMS_BY_TIME': album_conf.get('sort_by_time', DEFAULT_CONFIG['SORT_ALBUMS_BY_TIME']),
    'REVERSE_ALBUMS_ORDER': album_conf.get('reverse', DEFAULT_CONFIG['REVERSE_ALBUMS_ORDER']),
    'ORDER_ALBUMS_BY_LAST_DO': album_conf.get('order_by', DEFAULT_CONFIG['ORDER_ALBUMS_BY_LAST_DO']),
    'SORT_PHOTOS_BY_TIME': photo_conf.get('sort_by_time', DEFAULT_CONFIG['SORT_PHOTOS_BY_TIME']),
    'REVERSE_PHOTOS_ORDER': photo_conf.get('reverse', DEFAULT_CONFIG['REVERSE_PHOTOS_ORDER']),
    'ORDER_PHOTOS_BY_LAST_DO': photo_conf.get('order_by', DEFAULT_CONFIG['ORDER_PHOTOS_BY_LAST_DO']),
    'KEEP_ORDER': process.get('keep_order', DEFAULT_CONFIG['KEEP_ORDER']),
})

# Enable attribute-style access everywhere
CONFIG = SimpleNamespace(**DEFAULT_CONFIG)

# --- Utility functions ---

def merge_list(list_keep_order, list_new) -> list:
    print('Merge old order:', list_keep_order)
    print('The new order is:', list_new)
    right = None
    left = None
    for item in list_keep_order:
        if item in list_new:
            idx = list_new.index(item)
            if left is None or idx < left:
                left = idx
            if right is None or idx > right:
                right = idx

    if left is not None and right is not None and (right - left + 1) == len(list_keep_order):
        list_new[left:right + 1] = list_keep_order

    print('Merged order:', list_new)
    return list_new

def merge_json(path, data):
    try:
        with open(path, 'r') as f:
            original_config = json.load(f)
            if 'items' in original_config and 'items' in data:
                data['items']['order'] = merge_list(original_config['items']['order'], data['items']['order'])
            if 'order' in original_config:
                data['order'] = merge_list(original_config['order'], data['order'])
    except Exception:
        pass
    return data

def write_json(path, data):
    if CONFIG.KEEP_ORDER:
        data = merge_json(path, data)
    with open(path, 'w') as f:
        f.write(json.dumps(data, indent=2, separators=(',', ': ')))
        