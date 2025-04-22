import pytest
from album import Album


class DummyPhoto:
    def __init__(self, path):
        self.path = path

    def format(self):
        return {'name': self.path.name}


@pytest.fixture
def album_dir_with_miniatures(tmp_path, monkeypatch):
    # Create image and miniature files
    (tmp_path / "image1.jpg").write_text("real image")
    (tmp_path / "image2.min.jpg").write_text("miniature image")
    (tmp_path / "image3.jpeg").write_text("real image")

    # Patch Photo to DummyPhoto so we skip any real processing
    import album
    monkeypatch.setattr(album, "Photo", DummyPhoto)

    return tmp_path


def test_album_excludes_min_files(album_dir_with_miniatures):
    album = Album(album_dir_with_miniatures, "TestAlbum", 0)
    result = album.format()

    # Extract file names from result dictionary
    photo_names = result.get("items", {}).get("order", [])
    
    assert "image1.jpg" in photo_names
    assert "image3.jpeg" in photo_names
    assert "image2.min.jpg" not in photo_names
