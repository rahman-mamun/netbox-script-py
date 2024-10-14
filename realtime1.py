import requests
import subprocess
import ipaddress
import time

# Configuration
NETBOX_API_URL = 'http://94.237.37.172:8000/api/ipam/ip-addresses/'  # Replace with your NetBox API URL
NETBOX_TOKEN = ''  # Replace with your NetBox API token
NETWORK = '10.71.42.90/30'  # Adjust to scan the entire 10.71.42.x range

# Set up headers for the API request
headers = {
    'Authorization': f'Token {NETBOX_TOKEN}',
    'Content-Type': 'application/json',
}

# Function to ping an IP address
def ping_ip(ip):
    """Ping an IP address and return True if it's active."""
    try:
        print(f"Pinging IP: {ip}")  # Debug output
        output = subprocess.run(['ping', '-S', '10.71.42.148', '-n', '1', str(ip)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0  # Return True if the ping was successful
    except Exception as e:
        print(f"Error pinging {ip}: {e}")
        return False

# Function to check if an IP address already exists in NetBox
def ip_exists_in_netbox(ip):
    """Check if an IP address already exists in NetBox."""
    response = requests.get(f'{NETBOX_API_URL}?address={ip}/32', headers=headers)
    return response.status_code == 200 and response.json().get('count', 0) > 0

# Function to add IP address to NetBox
def add_ip_to_netbox(ip):
    """Add an active IP address to NetBox."""
    if ip_exists_in_netbox(ip):
        print(f'IP address {ip} already exists in NetBox.')
        return

    data = {
        'address': str(ip) + '/32',  # Use /32 for a single host
        'status': 'active',  # Adjust status as needed (active, reserved, etc.)
    }

    # Make the API request to add the IP
    response = requests.post(NETBOX_API_URL, headers=headers, json=data)

    # Log details of the request and response
    print(f"Request to add IP: {data}")
    print(f"Response Code: {response.status_code}")
    if response.status_code == 201:
        print(f'Successfully added IP address: {ip}')
    else:
        print(f'Failed to add {ip}: {response.status_code} - {response.content.decode("utf-8")}')

# Main execution
if __name__ == "__main__":
    # Create an IP network object from the defined range
    network = ipaddress.ip_network(NETWORK, strict=False)

    print("Scanning network...")
    # Iterate through all host addresses in the network
    for ip in network.hosts():
        if ping_ip(ip):
            print(f"Active IP: {ip}")  # Log active IP
            add_ip_to_netbox(ip)  # Add the active IP to NetBox in real-time
        else:
            print(f"No response from {ip}")  # Log inactive IPs

        time.sleep(0.1)  # Optional: pause briefly to avoid overwhelming the network
