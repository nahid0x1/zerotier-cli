import requests
import argparse
from datetime import datetime, timezone
from colorama import init, Fore, Back, Style

init(autoreset=True)

API_TOKEN = ''
NETWORK_ID = ''

headers = {'Authorization': f'token {API_TOKEN}'}
url = f'https://api.zerotier.com/api/v1/network/{NETWORK_ID}/member'

def fetch_members():
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"An error occurred: {e}")
        return []

def update_member(address, name=None, description=None, authorized=None):
    member_url = f'{url}/{address}'
    data = {}
    if name: data['name'] = name
    if description: data['description'] = description
    if authorized is not None: data['config'] = {'authorized': authorized}
    try:
        response = requests.post(member_url, headers=headers, json=data)
        response.raise_for_status()
        print(Fore.GREEN + f"Member {address} updated successfully.")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error updating member {address}: {e}")

def delete_member(address):
    member_url = f'{url}/{address}'
    try:
        response = requests.delete(member_url, headers=headers)
        response.raise_for_status()
        print(Fore.GREEN + f"Member {address} deleted successfully.")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error deleting member {address}: {e}")

def format_time_difference(last_seen_dt):
    delta = datetime.now(timezone.utc) - last_seen_dt
    seconds = delta.total_seconds()
    if seconds < 60:
        return Fore.CYAN + f"{int(seconds)} sec"
    elif seconds < 3600:
        return Fore.BLUE + f"{int(seconds // 60)} min"
    elif seconds < 86400:
        return Fore.MAGENTA + f"{int(seconds // 3600)} hr"
    elif seconds < 2592000:
        return Fore.YELLOW + f"{int(seconds // 86400)} day"
    elif seconds < 31104000:
        return Fore.MAGENTA + f"{int(seconds // 2592000)} month"
    else:
        return Fore.RED + f"{int(seconds // 31104000)} year"

def fetch_member_info(address):
    member_url = f'{url}/{address}'
    try:
        response = requests.get(member_url, headers=headers)
        response.raise_for_status()
        member = response.json()
        print(Back.CYAN + "\nDevice Information:")
        print(f"{Fore.GREEN}Address: {member.get('nodeId', 'N/A')}")
        print(f"{Fore.GREEN}Name: {member.get('name', 'N/A')}")
        print(f"{Fore.GREEN}Description: {member.get('description', 'N/A')}")
        print(f"{Fore.GREEN}Physical IP: {member.get('physicalAddress', 'N/A')}")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error fetching info for member {address}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Manage ZeroTier network members.")
    parser.add_argument('--address', type=str)
    parser.add_argument('--edit', action='store_true')
    parser.add_argument('--auth', type=str, choices=['true', 'false'])
    parser.add_argument('--name', type=str)
    parser.add_argument('--description', type=str)
    parser.add_argument('--info', action='store_true')
    parser.add_argument('--delete', action='store_true', help="Delete the specified member.")
    args = parser.parse_args()

    if args.address:
        if args.info:
            fetch_member_info(args.address)
        elif args.delete:
            delete_member(args.address)
        elif args.edit and (args.name or args.description):
            update_member(args.address, name=args.name, description=args.description)
        elif args.auth is not None:
            update_member(args.address, authorized=args.auth.lower() == 'true')
        else:
            print(Fore.RED + "Specify --edit with --name/--description, --auth, --info, or --delete.")
    else:
        members = fetch_members()
        if members:
            print(Back.BLACK + Fore.YELLOW + Style.BRIGHT + f"Network ID: {NETWORK_ID}\n")
            print(Fore.GREEN + f"{'Address':<10} | {'Device Name':<25} | {'Managed IPs':<15} | {'Last Seen':<10} | {'Status':<7} | {'Version':<6} | {'Authorization':<15}")
            print(Fore.GREEN + "-" * 104)
            for m in members:
                address = m.get('nodeId', 'N/A')
                name = m.get('name', 'N/A')
                ips = ', '.join(m.get('config', {}).get('ipAssignments', [])) or 'N/A'
                last_seen_dt = datetime.fromtimestamp(m.get('lastSeen', 0) / 1000, tz=timezone.utc)
                last_seen = format_time_difference(last_seen_dt)
                status = 'Online ' if (datetime.now(timezone.utc) - last_seen_dt).total_seconds() < 600 else 'Offline'
                version = m.get('clientVersion', 'N/A')
                auth = Back.GREEN+'authorized' if m.get('config', {}).get('authorized', False) else Back.RED+'unauthorized'
                
                print(Fore.GREEN + f"{address:<10} {Fore.GREEN}| {Fore.YELLOW}{name:<25} {Fore.GREEN}| {Fore.CYAN}{ips:<15} {Fore.GREEN}| {Fore.MAGENTA}{last_seen:<15} {Fore.GREEN}| "
                      f"{(Fore.GREEN if status == 'Online ' else Fore.RED)}{status:<6} {Fore.GREEN}| {Fore.WHITE}{version:<7} {Fore.GREEN}| {Fore.WHITE if auth == 'authorized' else Fore.WHITE}{auth:<15}")
        else:
            print(Fore.RED + "No members found or an error occurred.")

if __name__ == '__main__':
    main()
