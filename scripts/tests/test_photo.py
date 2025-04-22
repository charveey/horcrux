from pathlib import Path
import tempfile
import shutil
import pytest
from PIL import Image
from photo import Photo  # Assuming Photo class is in photo.py

# Fixture to create a temporary image file for testing
@pytest.fixture
def temp_image():
    temp_dir = tempfile.mkdtemp()  # Creates a temporary directory
    image_path = Path(temp_dir) / "test_image.jpg"
    # Create an image and save it
    image = Image.new("RGBA", (800, 600), (255, 0, 0, 255))
    image.save(image_path)
    yield image_path
    shutil.rmtree(temp_dir)  # Clean up temporary directory after test

# Mock configuration settings for testing purposes
@pytest.fixture
def mock_conf(monkeypatch):
    class MockConf:
        SIGN_ORIGINAL = True
        SIGN_THUMBNAIL = True
        MIN_WIDTH = 400
        FONT_SIZE = 20
        COPYRIGHT = "Test ©"
        FONT_FAMILY = "arial.ttf"
        WATERMARK_ROTATE = 0
        DEBUG = False
        DIR_PATH = Path.cwd()

    monkeypatch.setattr("photo.conf", MockConf)
    return MockConf


# Test the is_min property (checks if file is a "min" version of the image)
def test_is_min_property(temp_image):
    min_path = temp_image.with_name("test_image.min.jpg")  # Simulate a 'min' version of the file
    photo = Photo(min_path)
    assert photo.is_min is True  # Check if it returns True for 'min' image


# Test the has_min property (checks if 'min' file exists)
def test_has_min_property(temp_image):
    photo = Photo(temp_image)
    assert photo.has_min is False  # Check that 'has_min' is False initially

    # Create the min file
    photo.min_path.touch()  # Create the min file
    assert photo.has_min is True  # Check that 'has_min' is now True


# Test the format method to ensure it creates a thumbnail and processes the image
def test_format_creates_thumbnail(temp_image, mock_conf):
    photo = Photo(temp_image)
    result = photo.format()

    assert result is not None  # Ensure the result is not None
    assert photo.min_path.exists()  # Check if the 'min' version file exists
    assert result["type"] == "photo"  # Check the 'type' is 'photo'
    assert result["width"] == 800  # Check that the width of the original image is retained
    assert "min_path" in result  # Check if 'min_path' is included in the result


# Test the format method to ensure it skips processing if a 'min' file exists
def test_format_skips_if_min_file_given(temp_image, mock_conf):
    min_path = temp_image.with_name("test_image.min.jpg")
    min_path.touch()  # Simulate that the 'min' file already exists
    photo = Photo(min_path)
    assert photo.format() is None  # It should return None as the 'min' file exists


# Test that Photo raises an error when a non-existent image file is provided
def test_raises_error_for_missing_image():
    non_existent_path = Path("nonexistent.jpg")
    
    with pytest.raises(FileNotFoundError):
        Photo(non_existent_path)  # Should raise a FileNotFoundError


# Test that Photo raises an error if the specified font is missing
def test_fallback_or_error_on_missing_font(temp_image, monkeypatch):
    class MockConf:
        SIGN_ORIGINAL = True
        SIGN_THUMBNAIL = False
        MIN_WIDTH = 400
        FONT_SIZE = 20
        COPYRIGHT = "Test ©"
        FONT_FAMILY = "missing_font.ttf"  # Simulate missing font
        WATERMARK_ROTATE = 0
        DEBUG = False
        DIR_PATH = Path.cwd()
    
    monkeypatch.setattr("photo.conf", MockConf)

    photo = Photo(temp_image)

    # Patch ImageFont.truetype to simulate missing font
    monkeypatch.setattr("photo.ImageFont.truetype", lambda *args, **kwargs: (_ for _ in ()).throw(IOError("Font not found")))

    with pytest.raises(IOError, match="Font not found"):
        photo.mark_image(photo.pil_image, MockConf.FONT_SIZE)  # Should raise an IOError because font is missing
