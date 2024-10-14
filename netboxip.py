import requests
import subprocess
import socket
import ipaddress
import time

# Configuration
NETBOX_API_URL = 'http://94.237.37.172:8000/api/ipam/ip-addresses/'  # Replace with your NetBox API URL
NETBOX_TOKEN = ''  # Replace with your NetBox API token
NETWORK = '172.1.1.0/24'  # Adjust to your network range


# Set up headers for the API request
headers = {
    'Authorization': f'Token {NETBOX_TOKEN}',
    'Content-Type': 'application/json',
}

# Function to ping an IP address
def ping_ip(ip):
    try:
        # Using subprocess to ping the IP
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
        print(f'Failed to add {ip}: {response.content}')

# Main execution
if __name__ == "__main__":
    network = ipaddress.ip_network(NETWORK, strict=False)
    ip_addresses = []

    print("Scanning network...")
    for ip in network.hosts():  # Get all host addresses in the network
        if ping_ip(ip):
            print(f"Active IP: {ip}")
            ip_addresses.append(ip)

    for ip in ip_addresses:
        add_ip_to_netbox(ip)

    # After scanning the network
    print("Discovered IPs:")
    for ip in ip_addresses:
        print(ip)
