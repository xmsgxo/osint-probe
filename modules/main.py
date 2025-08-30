import argparse
import asyncio
from colorama import init, Fore, Style
from modules.username_checker import find_username
from modules.email_checker import check_email_breaches
from modules.phone_checker import analyze_phone_number
import config
init(autoreset=True)

def print_banner():
    banner = """
    ██████╗ ███████╗██╗ █████╗ ████████╗
    ██╔══██╗██╔════╝██║██╔══██╗╚══██╔══╝
    ██████╔╝███████╗██║███████║   ██║   
    ██═══╝ ╚════██║██║██╔══██║   ██║   
    ██║     ███████║██║██║  ██║   ██║   
    ╚═╝     ╚══════╝╚═╝╚═╝  ╚═╝   ╚═╝   
    OSINT-Probe v1.0
    """
    print(Fore.CYAN + banner)
    print(Style.RESET_ALL)

async def main():
    parser = argparse.ArgumentParser(description="OSINT-Probe: A modular OSINT tool.")
    parser.add_argument("-u", "--username", help="Username to search for.")
    parser.add_argument("-e", "--email", help="Email address to check for breaches.")
    parser.add_argument("-p", "--phone", help="Phone number to analyze (in international format, e.g., +14158586273).")
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.print_help()
        return
    print_banner()
    if args.username:
        await find_username(args.username)
    if args.email:
        await check_email_breaches(args.email, config.HIBP_API_KEY)
    if args.phone:
        analyze_phone_number(args.phone)

if __name__ == "__main__":
    asyncio.run(main())
