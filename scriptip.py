import socket
import argparse
import requests
import netifaces

NETBOX_URL = "http://94.237.37.172:8000/api/ipam/ip-addresses/"
API_TOKEN = ""

def get_hostnames(ip, ports):
    hostnames = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)  # Adjust timeout as needed
                if s.connect_ex((ip, port)) == 0:
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                        hostnames.append((ip, hostname))
                    except socket.herror:
                        hostnames.append((ip, None))
        except Exception as e:
            print(f"Error: {e}")
    return hostnames

def add_ip_address(ip, hostname):
    data = {
        "address": ip,
        "status": "active",
        "dns_name": hostname
    }
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(NETBOX_URL, json=data, headers=headers)
    if response.status_code == 201:
        print(f"Successfully added {ip} with hostname {hostname} to NetBox")
    else:
        print(f"Failed to add {ip} with hostname {hostname} to NetBox")

def main():
    parser = argparse.ArgumentParser(description="Discover IP addresses and hostnames from the Internet")
    parser.add_argument("ports", metavar="PORT", type=int, nargs="+", help="List of ports to scan")
    args = parser.parse_args()

    network = "77.240.10.0/24"
    for i in range(1, 255):
        ip = f"{network[:-4]}{i}"
        hostnames = get_hostnames(ip, args.ports)
        for ip, hostname in hostnames:
            add_ip_address(ip, hostname)

if __name__ == "__main__":
    main()

# Remember to add prefix to interface example  http://127.0.0.1:8000/ . Change network ip or add more in this script. Also check API token key
# on the begining of this script that it match what is generated on Netbox interface. Example run this script python3 netboxtestscan.py 80 2087  