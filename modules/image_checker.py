import httpx
import io
import urllib.parse
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def _get_exif_data(image):
    """Extracts and decodes EXIF data from an image object."""
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data

def _convert_to_degrees(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degrees."""
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)

async def analyze_image(image_path):
    """Analyzes an image from a local path or URL for EXIF data and provides reverse search links."""
    print(f"\n--- 🖼️ Image OSINT Analysis for {image_path} ---")
    image_obj = None
    is_url = image_path.startswith('http')

    try:
        if is_url:
            print("Downloading image from URL...")
            async with httpx.AsyncClient() as client:
                response = await client.get(image_path, follow_redirects=True)
                response.raise_for_status()
                image_obj = Image.open(io.BytesIO(response.content))
        else:
            print("Reading local image file...")
            image_obj = Image.open(image_path)
    except FileNotFoundError:
        print(f"❌ Error: Local file not found at '{image_path}'")
        return
    except Exception as e:
        print(f"❌ Error: Could not load image. {e}")
        return

    # 1. EXIF Data Analysis
    print("\n[+] Analyzing EXIF Metadata...")
    exif = _get_exif_data(image_obj)

    if not exif:
        print("  - No EXIF data found in this image.")
    else:
        for key, val in exif.items():
            if key == "GPSInfo":
                continue # We'll handle GPS separately
            print(f"  - {key}: {val}")

        if "GPSInfo" in exif:
            print("\n[+] GPS Information Found!")
            gps_info = exif["GPSInfo"]
            lat_ref = gps_info.get("GPSLatitudeRef")
            lat = gps_info.get("GPSLatitude")
            lon_ref = gps_info.get("GPSLongitudeRef")
            lon = gps_info.get("GPSLongitude")

            if lat and lat_ref and lon and lon_ref:
                lat_deg = _convert_to_degrees(lat)
                lon_deg = _convert_to_degrees(lon)
                if lat_ref == "S":
                    lat_deg = -lat_deg
                if lon_ref == "W":
                    lon_deg = -lon_deg

                print(f"  - Latitude: {lat_deg}")
                print(f"  - Longitude: {lon_deg}")
                print(f"  - Google Maps Link: https://www.google.com/maps/search/?api=1&query={lat_deg},{lon_deg}")

    # 2. Reverse Image Search Links
    print("\n[+] Reverse Image Search Links:")
    if is_url:
        encoded_url = urllib.parse.quote_plus(image_path)
        print(f"  - Google: https://images.google.com/searchbyimage?image_url={encoded_url}")
        print(f"  - Yandex: https://yandex.com/images/search?rpt=imageview&url={encoded_url}")
        print(f"  - Bing: https://www.bing.com/images/search?view=detailv2&iss=sbi&q=imgurl:{encoded_url}")
    else:
        print("  - Upload this local file to the services above to perform a reverse image search.")
