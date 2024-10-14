import requests
import subprocess
import ipaddress

# Configuration
NETBOX_API_URL = 'http://94.237.37.172:8000/api/ipam/ip-addresses/'  # Replace with your NetBox API URL
NETBOX_TOKEN = ''  # Replace with your NetBox API token
NETWORK = '10.71.42.40'  # Adjust to your network range

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
        # Use subprocess to ping the IP
        output = subprocess.run(['ping', '-n', '1', str(ip)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0  # Return True if the ping was successful
    except Exception as e:
        print(f"Error pinging {ip}: {e}")
        return False

# Function to add IP address to NetBox
def add_ip_to_netbox(ip):
    """Add an active IP address to NetBox."""
    data = {
        'address': str(ip) + '/32',  # Use /32 for a single host
        'status': 'active',  # Adjust status as needed (active, reserved, etc.)
    }

    # Make the API request to add the IP
    response = requests.post(NETBOX_API_URL, headers=headers, json=data)

    # Check the response status code
    if response.status_code == 201:
        print(f'Successfully added IP address: {ip}')
    else:
        print(f'Failed to add {ip}: {response.status_code} - {response.content.decode("utf-8")}')

# Main execution
if __name__ == "__main__":
    # Create an IP network object from the defined range
    network = ipaddress.ip_network(NETWORK, strict=False)
    ip_addresses = []  # List to hold active IP addresses

    print("Scanning network...")
    # Iterate through all host addresses in the network
    for ip in network.hosts():
        if ping_ip(ip):
            print(f"Active IP: {ip}")  # Log active IP
            ip_addresses.append(ip)
        else:
            print(f"No response from {ip}")  # Log inactive IPs

    # Attempt to add discovered active IPs to NetBox
    for ip in ip_addresses:
        add_ip_to_netbox(ip)

    # Final output of discovered IPs
    print("Discovered IPs:")
    for ip in ip_addresses:
        print(ip)
