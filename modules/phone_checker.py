import phonenumbers
from phonenumbers import geocoder, carrier, timezone

def analyze_phone_number(phone_number_str):
    """Analyzes a phone number and returns basic information."""
    print(f"\n--- 📞 Phone Number Analysis for {phone_number_str} ---")
    try:
        parsed_number = phonenumbers.parse(phone_number_str)
        if not phonenumbers.is_valid_number(parsed_number):
            print("❌ Invalid phone number.")
            return

        print(f"✅ International Format: {phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}")
        print(f"🌍 Location: {geocoder.description_for_number(parsed_number, 'en')}")
        print(f"📡 Carrier: {carrier.name_for_number(parsed_number, 'en')}")

        time_zones = timezone.time_zones_for_number(parsed_number)
        if time_zones:
            print(f"⏳ Time Zone(s): {', '.join(time_zones)}")

    except Exception as e:
        print(f"An error occurred: {e}")
