import pytest
from nest import Nest
from pathlib import Path
from unittest.mock import MagicMock, mock_open


@pytest.fixture
def mock_conf(monkeypatch, tmp_path):
    class MockConf:
        DIR_PATH = tmp_path
        HORCRUX_PATH = Path("horcrux.json")
        CONFIG_PATH = tmp_path / "final_config.json"

        @staticmethod
        def write_json(path, data):
            path.write_text("written")

    monkeypatch.setattr("nest.conf", MockConf)
    return MockConf


def test_read_json_reads_file(monkeypatch, mock_conf):
    dummy_data = {"test": 1}
    json_str = '{"test": 1}'

    m = mock_open(read_data=json_str)
    monkeypatch.setattr("builtins.open", m)

    nest = Nest()
    result = nest.read_json(Path("horcrux.json"))

    assert result == dummy_data


def test_convert_child_items_orders_correctly():
    nest = Nest()
    items = {
        'dict': {'a': 1, 'b': 2, 'c': 3},
        'order': ['b', 'c', 'a']
    }

    result = nest.convert_child_items(items)
    assert result == [2, 3, 1]


def test_append_album_adds_photos():
    nest = Nest()
    dummy_album = {'name': 'Test', 'parents': [], 'type': 'album'}
    dummy_photos = [{'type': 'photo', 'name': 'x.jpg'}]

    nest.append_album(dummy_album, photos=dummy_photos)

    assert len(nest.resources) == 1
    assert nest.resources[0]['type'] == 'photos'
    assert nest.resources[0]['list'] == dummy_photos


def test_nest_photos_reads_and_converts(monkeypatch):
    nest = Nest()
    dummy_album = {'name': 'Album', 'parents': [], 'type': 'album'}
    dummy_items = {
        'dict': {'img1': {'type': 'photo'}, 'img2': {'type': 'photo'}},
        'order': ['img1', 'img2']
    }

    monkeypatch.setattr(nest, "read_json", lambda _: dummy_items)
    monkeypatch.setattr(nest, "append_album", MagicMock())

    nest.nest_photos(dummy_album, "some_path.json")

    nest.append_album.assert_called_once_with(dummy_album, [
        {'type': 'photo'},
        {'type': 'photo'}
    ])


def test_nest_album_handles_nested(monkeypatch):
    nest = Nest()
    dummy = {
        'type': 'album',
        'name': 'root',
        'parents': [],
        'items': {
            'dict': {
                'img1': {'type': 'photo'},
                'sub': {
                    'type': 'album',
                    'no_sub_album': True,
                    'name': 'sub',
                    'path': 'sub.json',
                    'parents': ['root']
                }
            },
            'order': ['img1', 'sub']
        }
    }

    monkeypatch.setattr(nest, "read_json", lambda path: {
        'dict': {'pic1': {'type': 'photo'}},
        'order': ['pic1']
    })
    monkeypatch.setattr(nest, "append_album", MagicMock())

    nest.nest_album(dummy)

    # Two albums added: one for img1, one from sub.json
    assert nest.append_album.call_count == 2
