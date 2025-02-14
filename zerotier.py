import requests
import argparse
from datetime import datetime, timezone

API_TOKEN = '' #api
NETWORK_ID = '' #network id

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

def main():
    parser = argparse.ArgumentParser(description="Manage ZeroTier network members.")
    parser.add_argument('--address', type=str)
    parser.add_argument('--edit', action='store_true')
    parser.add_argument('--auth', type=str, choices=['true', 'false'])
    parser.add_argument('--name', type=str)
    parser.add_argument('--description', type=str)
    args = parser.parse_args()

    if args.address:
        if args.edit and (args.name or args.description):
            update_member(args.address, name=args.name, description=args.description)
        elif args.auth is not None:
            update_member(args.address, authorized=args.auth.lower() == 'true')
        else:
            print("Specify --edit with --name/--description or --auth.")
    else:
        members = fetch_members()
        if members:
            print(f"Network ID: {NETWORK_ID}\n")
            print(f"{'Address':<18} | {'Device Name':<25} | {'Managed IPs':<18} | {'Last Seen':<22} | {'Status':<8} | {'Version':<8} | {'Authorization':<12}")
            print("-" * 130)
            for m in members:
                if m.get('config', {}).get('authorized', False):
                    address = m.get('nodeId', 'N/A')
                    name = m.get('name', 'N/A')
                    ips = ', '.join(m.get('config', {}).get('ipAssignments', [])) or 'N/A'
                    last_seen_dt = datetime.fromtimestamp(m.get('lastSeen', 0) / 1000, tz=timezone.utc)
                    last_seen = last_seen_dt.strftime('%I:%M:%S %p %m-%d-%Y')
                    status = 'Online' if (datetime.now(timezone.utc) - last_seen_dt).total_seconds() < 600 else 'Offline'
                    version = m.get('clientVersion', 'N/A')
                    auth = 'Authorized' if m.get('config', {}).get('authorized', False) else 'Unauthorized'
                    print(f"{address:<18} | {name:<25} | {ips:<18} | {last_seen:<22} | {status:<8} | {version:<8} | {auth:<12}")
        else:
            print("No members found or an error occurred.")

if __name__ == '__main__':
    main()
