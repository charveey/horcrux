from conf import CONFIG
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS, GPSTAGS, IFD
from fractions import Fraction

def _format_exposure_fraction(self, value):
    try:
        exposure = float(value)
        if exposure == 0:
            return "Unknown"
        frac = Fraction(exposure).limit_denominator(10000)
        return f"1/{int(1/frac)}s" if exposure < 1 else f"{int(exposure)}s"
    except (ValueError, ZeroDivisionError, TypeError):
        return "Unknown"


## HEIC and AVIF support
#from pillow_heif import register_heif_opener
#import pillow_avif
#register_heif_opener()

class Photo():
    def __init__(self, path):
        self.path = path
        self.min_path = path.with_name(path.stem + '.min.webp')

        # Open the image
        self.pil_image = Image.open(self.path).convert('RGBA')
        self.width, self.height = self.pil_image.size
        self.size = self.pil_image.size

        # Extract EXIF data
        self.exif_data = self._extract_exif()

        # Set standard attributes
        self.camera = self.exif_data.get('Make', 'Unknown')
        self.model = self.exif_data.get('Model', 'Unknown')
        self.aperture = self.exif_data.get('FNumber', 'Unknown')
        self.exposure = self.exif_data.get('ExposureTime', 'Unknown')
        self.iso = self.exif_data.get('ISOSpeedRatings', 'Unknown')
        self.focal = self.exif_data.get('FocalLength', 'Unknown')

    def _extract_exif(self):
        exif = {}
        try:
            raw_exif = self.pil_image.getexif()

            # Base IFD
            for k, v in raw_exif.items():
                tag = TAGS.get(k, k)
                exif[tag] = self._handle_exif_value(v)

            # Extended IFDs (GPS, etc.)
            for ifd_id in IFD:
                try:
                    ifd = raw_exif.get_ifd(ifd_id)
                    tags = GPSTAGS if ifd_id == IFD.GPSInfo else TAGS
                    for k, v in ifd.items():
                        tag = tags.get(k, k)
                        exif[tag] = self._handle_exif_value(v)
                except KeyError:
                    continue
        except Exception as e:
            print(f"Error extracting EXIF data: {e}")
        
        return exif

    def _format_exif_value(self, value, digits=2, as_type=float):
        try:
            value = as_type(value)
            return round(value, digits)
        except (TypeError, ValueError):
            return "Unknown"

    def _format_exposure_fraction(self, value):
        try:
            exposure = float(value)
            if exposure == 0:
                return "Unknown"
            frac = Fraction(exposure).limit_denominator(10000)
            return f"1/{int(1/frac)}s" if exposure < 1 else f"{int(exposure)}s"
        except (ValueError, ZeroDivisionError, TypeError):
            return "Unknown"

    def _handle_exif_value(self, value):
        """Helper method to convert EXIF values to JSON serializable types."""
        if isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], int) and isinstance(value[1], int):
            # If the value is a tuple of two integers (IFDRational), convert it to a float
            return float(value[0]) / value[1]
        return value

    @property
    def is_min(self):
        return self.path.suffix.lower() == '.webp' and '.min.' in self.path.name
    
    @property
    def has_min(self):
        return self.min_path.exists()
    
    def format(self):
        if self.is_min:
            return None
        
        if not self.has_min:
            if CONFIG.SIGN_ORIGINAL:
                signed_image = self.mark_image(self.pil_image, CONFIG.FONT_SIZE)
                self.save_image(signed_image, self.path)

            # Resize the image
            ratio = float(CONFIG.MIN_WIDTH) / self.size[0]
            new_image_size = tuple([int(x * ratio) for x in self.size])

            if CONFIG.SIGN_THUMBNAIL:
                if not CONFIG.SIGN_ORIGINAL:
                    signed_image = self.mark_image(self.pil_image, CONFIG.FONT_SIZE)
                signed_image.thumbnail(new_image_size, Image.Resampling.LANCZOS)
                self.save_image(signed_image, self.min_path)
            else:
                min_image = self.pil_image.copy()
                min_image.thumbnail(new_image_size, Image.Resampling.LANCZOS)
                self.save_image(min_image, self.min_path)

        relative_path = str(self.path.with_suffix('.webp').relative_to(CONFIG.DIR_PATH))
        
        return {
            "type": 'photo',
            'width': self.size[0],
            'height': self.size[1],
            'camera': f"{self.camera} {self.model}".strip(),
            'aperture': self._format_exif_value(self.aperture, digits=1),
            'exposure': self._format_exposure_fraction(self.exposure),
            'iso': self._format_exif_value(self.iso, as_type=int),
            'focal': self._format_exif_value(self.focal, digits=1),
            'path': './' + relative_path,
            'min_path': './' + str(self.min_path.relative_to(CONFIG.DIR_PATH))
        }
    
    def save_image(self, img, path):
        output_path = path.with_suffix('.webp')

        if CONFIG.DEBUG:
            img.show()
        else:
            img.convert('RGB').save(output_path, 'WEBP', quality=95)

            # Optionally remove the original
            if path.suffix.lower() != '.webp':
                try:
                    path.unlink()  # Deletes the original file
                    print(f"Deleted original: {path}")
                except Exception as e:
                    print(f"Failed to delete original: {path} — {e}")

    def mark_image(self, img, fontsize):
        width, height = img.size
        transparent_image = Image.new('RGBA', img.size, (255, 255, 255, 0))
        font = ImageFont.truetype('./assets/font/' + CONFIG.FONT_FAMILY, CONFIG.FONT_SIZE)
        draw = ImageDraw.Draw(transparent_image)

        t_size = font.getbbox(CONFIG.COPYRIGHT)
        t_w = t_size[2]
        t_h = t_size[3]

        x = (width - t_w) / 2
        y = height - 2 * t_h
        draw.text((x, y), CONFIG.COPYRIGHT, font=font, fill=(255, 255, 255, 125))
        transparent_image = transparent_image.rotate(CONFIG.WATERMARK_ROTATE)
        signed_image = Image.alpha_composite(img, transparent_image)
        return signed_image