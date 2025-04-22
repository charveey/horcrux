import pytest
from unittest.mock import MagicMock
from album import Album


@pytest.fixture
def mock_conf(monkeypatch, tmp_path):
    class MockConf:
        ORDER_ALBUMS_BY_LAST_DO = 'modify'
        ORDER_PHOTOS_BY_LAST_DO = 'modify'
        SORT_ALBUMS_BY_TIME = True
        SORT_PHOTOS_BY_TIME = True
        REVERSE_ALBUMS_ORDER = False
        REVERSE_PHOTOS_ORDER = False
        ALBUMS_PATH = tmp_path / "albums"
        DIR_PATH = tmp_path
        ALBUMS_PATH.mkdir(parents=True, exist_ok=True)

        @staticmethod
        def write_json(path, data):
            path.write_text("written")

    monkeypatch.setattr("album.conf", MockConf)
    monkeypatch.setattr("album.Photo", MagicMock())  # Mock Photo class
    return MockConf


@pytest.fixture
def temp_album_dir(tmp_path):
    # Create a dummy album directory with a sub-album and an image
    album_dir = tmp_path / "album"
    sub_album = album_dir / "sub_album"
    image = album_dir / "photo.jpg"
    sub_album.mkdir(parents=True)
    image.write_bytes(b"fake image data")
    return album_dir


def test_album_with_sub_album_and_photo(temp_album_dir, mock_conf):
    album = Album(temp_album_dir, temp_album_dir.name, root=1)
    result = album.format()

    assert result["type"] == "album"
    assert "items" in result
    assert "sub_album" in result["items"]["dict"]
    assert "photo.jpg" in result["items"]["order"]


def test_album_without_sub_album(tmp_path, mock_conf):
    album_path = tmp_path / "empty_album"
    album_path.mkdir()
    image_path = album_path / "image.jpg"
    image_path.write_bytes(b"image")

    album = Album(album_path, album_path.name, root=0)
    result = album.format()

    assert result["no_sub_album"] is True
    assert result["type"] == "album"
    assert result["path"].startswith("./")
    config_file = mock_conf.ALBUMS_PATH / f"{album_path.name}.json"
    assert config_file.exists()
    assert config_file.read_text() == "written"
