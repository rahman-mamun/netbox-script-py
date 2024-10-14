import requests
import subprocess
import ipaddress
import time
from collections import defaultdict

# Configuration
NETBOX_API_URL = 'http://94.237.37.172:8000/api/ipam/ip-addresses/'  # Replace with your NetBox API URL
NETBOX_TOKEN = ''  # Replace with your NetBox API token
NETWORK = '10.71.42.0/24'  # Adjust to your desired network range to scan multiple IPs

# Set up headers for the API request
headers = {
    'Authorization': f'Token {NETBOX_TOKEN}',
    'Content-Type': 'application/json',
}

# Function to ping an IP address
def ping_ip(ip):
    try:
        output = subprocess.run(['ping', '-n', '1', str(ip)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0  # Return True if the ping was successful
    except Exception as e:
        print(f"Error pinging {ip}: {e}")
        return False

# Function to add IP address to NetBox
def add_ip_to_netbox(ip):
    data = {
        'address': str(ip) + '/32',  # Use /32 for a single host
        'status': 'active',  # Adjust as needed
    }

    response = requests.post(NETBOX_API_URL, headers=headers, json=data)

    if response.status_code == 201:
        print(f'Successfully added IP address: {ip}')
    else:
        print(f'Failed to add {ip}: {response.status_code} - {response.content.decode("utf-8")}')

# Main execution
if __name__ == "__main__":
    network = ipaddress.ip_network(NETWORK, strict=False)
    ip_addresses = defaultdict(list)

    print("Scanning network...")
    for ip in network.hosts():  # Get all host addresses in the network
        print(f"Pinging IP: {ip}")
        if ping_ip(ip):
            print(f"Active IP: {ip}")
            # Grouping IP addresses based on the last octet
            last_octet = str(ip).split('.')[-1]
            ip_addresses[last_octet].append(ip)

    # Add scanned IPs to NetBox and print groups
    for group, ips in ip_addresses.items():
        print(f"\nGroup {group}:")
        for ip in ips:
            add_ip_to_netbox(ip)
            time.sleep(1)  # Wait for 1 second between requests

    # After scanning the network
    print("\nDiscovered IPs:")
    for group, ips in ip_addresses.items():
        print(f"Group {group}: {', '.join(map(str, ips))}")
