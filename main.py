import argparse
import asyncio
from colorama import init, Fore, Style

from modules.username_checker import find_username
from modules.email_checker import check_email_breaches
from modules.phone_checker import analyze_phone_number
from modules.image_checker import analyze_image
import config

init(autoreset=True)

def print_banner():
    banner = """
    ██████╗ ███████╗██╗ █████╗ ████████╗
    ██╔══██╗██╔════╝██║██╔══██╗╚══██╔══╝
    ██████╔╝███████╗██║███████║   ██║   
    ██╔═══╝ ╚════██║██║██╔══██║   ██║   
    ██║     ███████║██║██║  ██║   ██║   
    ╚═╝     ╚══════╝╚═╝╚═╝  ╚═╝   ╚═╝   
    OSINT-Probe v2.0
    """
    print(Fore.CYAN + banner)
    print(Style.RESET_ALL)

async def main():
    parser = argparse.ArgumentParser(description="OSINT-Probe: A modular OSINT tool.")
    parser.add_argument("-u", "--username", help="Username to search for.")
    parser.add_argument("-e", "--email", help="Email address to check for breaches.")
    parser.add_argument("-p", "--phone", help="Phone number to analyze (in international format).")

    image_group = parser.add_argument_group("Image Analysis Options")
    image_group.add_argument("-i", "--image", help="Path or URL to an image for analysis.")
    image_group.add_argument("--ela", action="store_true", help="Perform Error Level Analysis on the image.")
    image_group.add_argument("--stega", action="store_true", help="Check for hidden steganographic data in the image.")

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return

    print_banner()

    if args.username:
        await find_username(args.username)
    if args.email:
        await check_email_breaches(args.email)
    if args.phone:
        analyze_phone_number(args.phone)
    if args.image:
        await analyze_image(args.image, do_ela=args.ela, do_stega=args.stega)

if __name__ == "__main__":
    asyncio.run(main())
