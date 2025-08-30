import httpx
import io
import urllib.parse
import numpy as np
from PIL import Image, ImageChops
from stegano import lsb

# --- FORENSIC FUNCTIONS ---

def perform_ela(image_obj):
    """Performs Error Level Analysis on an image."""
    try:
        # Save the original image to a temporary in-memory file at 95% quality
        temp_buffer = io.BytesIO()
        image_obj.save(temp_buffer, format='JPEG', quality=95)
        temp_buffer.seek(0)

        # Re-open the saved image
        resaved_img = Image.open(temp_buffer)

        # Find the difference between the original and the re-saved version
        ela_img = ImageChops.difference(image_obj, resaved_img)

        # Enhance the ELA image to make differences more visible
        extrema = ela_img.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1 # Avoid division by zero
        scale = 255.0 / max_diff

        ela_img = ImageChops.multiply(ela_img, Image.new('RGB', ela_img.size, (int(scale),) * 3))

        # Save the result to a file
        ela_filename = "ela_result.jpg"
        ela_img.save(ela_filename, "JPEG")
        print(f"  - ELA image saved as '{ela_filename}'. Areas with high contrast may have been manipulated.")
    except Exception as e:
        print(f"  - ELA could not be performed: {e}")


def check_steganography(image_path, is_url):
    """Checks for hidden LSB steganography in an image."""
    if is_url:
        print("  - Steganography check can only be run on local files.")
        return
    try:
        # Attempt to reveal hidden data from the image
        secret_message = lsb.reveal(image_path)
        if secret_message:
            print(f"  - 🚨 Potential Hidden Data Found: {secret_message}")
        else:
            print("  - No obvious LSB steganography data found.")
    except Exception:
        print("  - No obvious LSB steganography data found.")


# --- ORIGINAL OSINT FUNCTIONS (MODIFIED) ---

def _get_exif_data(image):
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                from PIL.ExifTags import GPSTAGS
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data

def _convert_to_degrees(value):
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)

async def analyze_image(image_path, do_ela=False, do_stega=False):
    """Main function to analyze an image."""
    print(f"\n--- 🖼️ Image OSINT Analysis for {image_path} ---")
    image_obj = None
    is_url = image_path.startswith('http')

    try:
        if is_url:
            print("Downloading image from URL...")
            async with httpx.AsyncClient() as client:
                response = await client.get(image_path, follow_redirects=True)
                response.raise_for_status()
                image_data = io.BytesIO(response.content)
                image_obj = Image.open(image_data)
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
    from PIL.ExifTags import TAGS
    exif = _get_exif_data(image_obj)

    if not exif:
        print("  - No EXIF data found.")
    else:
        # (EXIF data processing code remains the same as before)
        for key, val in exif.items():
            if key == "GPSInfo": continue
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
                if lat_ref == "S": lat_deg = -lat_deg
                if lon_ref == "W": lon_deg = -lon_deg
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

    # 3. Manual Analysis Checklist
    print("\n[+] Manual Analysis Checklist:")
    print("  - Look for text (street signs, logos, posters).")
    print("  - Analyze architecture (building style, materials).")
    print("  - Check for unique landmarks or natural features (mountains, coastlines).")
    print("  - Examine vehicles (license plates, models).")
    print("  - Note weather, shadows (time of day), and vegetation (climate).")

    # 4. Perform Advanced Forensic Checks if requested
    if do_ela:
        print("\n[+] Performing Error Level Analysis (ELA)...")
        perform_ela(image_obj.convert('RGB'))

    if do_stega:
        print("\n[+] Checking for Hidden Steganographic Data...")
        check_steganography(image_path, is_url)
