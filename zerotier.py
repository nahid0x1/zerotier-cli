import requests
import argparse
from datetime import datetime, timezone, timedelta
import re

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
        print(f"An error occurred: {e}")
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
        print(f"Member {address} updated successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error updating member {address}: {e}")

def format_time_difference(last_seen_dt):
    delta = datetime.now(timezone.utc) - last_seen_dt
    seconds = delta.total_seconds()

    if seconds < 60:
        return f"{int(seconds)} sec"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minute"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hour"
    elif seconds < 2592000:
        return f"{int(seconds // 86400)} day"
    elif seconds < 31104000:
        return f"{int(seconds // 2592000)} month"
    else:
        return f"{int(seconds // 31104000)} year"

def fetch_member_info(address):
    member_url = f'{url}/{address}'
    try:
        response = requests.get(member_url, headers=headers)
        response.raise_for_status()
        member = response.json()
        print("\nDevice Information:")
        print(f"Address: {member.get('nodeId', 'N/A')}")
        print(f"Name: {member.get('name', 'N/A')}")
        print(f"Description: {member.get('description', 'N/A')}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching info for member {address}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Manage ZeroTier network members.")
    parser.add_argument('--address', type=str)
    parser.add_argument('--edit', action='store_true')
    parser.add_argument('--auth', type=str, choices=['true', 'false'])
    parser.add_argument('--name', type=str)
    parser.add_argument('--description', type=str)
    parser.add_argument('--info', action='store_true')
    args = parser.parse_args()

    if args.address:
        if args.info:
            fetch_member_info(args.address)
        elif args.edit and (args.name or args.description):
            update_member(args.address, name=args.name, description=args.description)
        elif args.auth is not None:
            update_member(args.address, authorized=args.auth.lower() == 'true')
        else:
            print("Specify --edit with --name/--description, --auth, or --info.")
    else:
        members = fetch_members()
        if members:
            print(f"Network ID: {NETWORK_ID}\n")
            print(f"{'Address':<18} | {'Device Name':<25} | {'Managed IPs':<18} | {'Last Seen':<15} | {'Status':<8} | {'Version':<8} | {'Authorization':<12}")
            print("-" * 120)
            for m in members:
                address = m.get('nodeId', 'N/A')
                name = m.get('name', 'N/A')
                ips = ', '.join(m.get('config', {}).get('ipAssignments', [])) or 'N/A'
                last_seen_dt = datetime.fromtimestamp(m.get('lastSeen', 0) / 1000, tz=timezone.utc)
                last_seen = format_time_difference(last_seen_dt)
                status = 'Online' if (datetime.now(timezone.utc) - last_seen_dt).total_seconds() < 600 else 'Offline'
                version = m.get('clientVersion', 'N/A')
                auth = 'Authorized' if m.get('config', {}).get('authorized', False) else 'Unauthorized'
                print(f"{address:<18} | {name:<25} | {ips:<18} | {last_seen:<15} | {status:<8} | {version:<8} | {auth:<12}")
        else:
            print("No members found or an error occurred.")

if __name__ == '__main__':
    main()
