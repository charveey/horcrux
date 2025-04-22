import json
import yaml
from conf import (
    merge_list, merge_json, CONFIG
)

# --- Test Helpers for simulating YAML reload ---

def load_yaml_config(path):
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def apply_config(config_data):
    # Mimic the config initialization logic in conf.py
    process = config_data.get('process', {})
    album_conf = process.get('album', {})
    photo_conf = process.get('photo', {})
    watermark_conf = photo_conf.get('watermark', {})

    CONFIG.COPYRIGHT = '@' + config_data['instagram']
    CONFIG.MIN_WIDTH = photo_conf.get('min_width', CONFIG.MIN_WIDTH)
    CONFIG.FONT_SIZE = watermark_conf.get('fontsize', CONFIG.FONT_SIZE)
    CONFIG.FONT_FAMILY = watermark_conf.get('fontfamily', CONFIG.FONT_FAMILY)
    CONFIG.WATERMARK_ROTATE = watermark_conf.get('rotate', CONFIG.WATERMARK_ROTATE)
    CONFIG.SIGN_THUMBNAIL = watermark_conf.get('thumbnail', CONFIG.SIGN_THUMBNAIL)
    CONFIG.SIGN_ORIGINAL = watermark_conf.get('original', CONFIG.SIGN_ORIGINAL)
    CONFIG.SORT_ALBUMS_BY_TIME = album_conf.get('sort_by_time', CONFIG.SORT_ALBUMS_BY_TIME)
    CONFIG.REVERSE_ALBUMS_ORDER = album_conf.get('reverse', CONFIG.REVERSE_ALBUMS_ORDER)
    CONFIG.ORDER_ALBUMS_BY_LAST_DO = album_conf.get('order_by', CONFIG.ORDER_ALBUMS_BY_LAST_DO)
    CONFIG.SORT_PHOTOS_BY_TIME = photo_conf.get('sort_by_time', CONFIG.SORT_PHOTOS_BY_TIME)
    CONFIG.REVERSE_PHOTOS_ORDER = photo_conf.get('reverse', CONFIG.REVERSE_PHOTOS_ORDER)
    CONFIG.ORDER_PHOTOS_BY_LAST_DO = photo_conf.get('order_by', CONFIG.ORDER_PHOTOS_BY_LAST_DO)
    CONFIG.KEEP_ORDER = process.get('keep_order', CONFIG.KEEP_ORDER)

# --- Actual tests ---

def test_merge_list_correct():
    keep_order = ['a', 'b', 'c']
    new_order = ['b', 'a', 'c']
    merged = merge_list(keep_order, new_order.copy())
    assert merged == ['a', 'b', 'c']


def test_merge_list_partial_match():
    keep_order = ['a', 'b']
    new_order = ['b', 'c', 'a']
    merged = merge_list(keep_order, new_order.copy())
    assert merged == ['b', 'c', 'a']


def test_merge_json(tmp_path):
    original = {
        "items": {
            "order": ["a", "b", "c"]
        },
        "order": ["a", "b", "c"]
    }
    new_data = {
        "items": {
            "order": ["b", "a", "c"]
        },
        "order": ["b", "a", "c"]
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(original))
    result = merge_json(path, new_data)
    assert result['order'] == ["a", "b", "c"]
    assert result['items']['order'] == ["a", "b", "c"]


def test_yaml_config_parsing(tmp_path):
    yaml_path = tmp_path / "_config.yml"
    yaml_path.write_text("""
instagram: testuser
process:
  keep_order: true
  album:
    sort_by_time: false
    reverse: true
    order_by: create
  photo:
    sort_by_time: true
    reverse: false
    order_by: modify
    watermark:
      fontsize: 48
      fontfamily: Fancy.ttf
      rotate: 10
      thumbnail: true
      original: false
""")
    config_data = load_yaml_config(yaml_path)
    apply_config(config_data)

    assert CONFIG.COPYRIGHT == '@testuser'
    assert CONFIG.FONT_SIZE == 48
    assert CONFIG.FONT_FAMILY == 'Fancy.ttf'
    assert CONFIG.KEEP_ORDER is True
    assert CONFIG.ORDER_PHOTOS_BY_LAST_DO == 'modify'
    assert CONFIG.REVERSE_PHOTOS_ORDER is False
