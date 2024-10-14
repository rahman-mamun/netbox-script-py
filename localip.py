import socket
import argparse
import requests
import netifaces

NETBOX_URL = "http://94.237.37.172:8000/api/ipam/ip-addresses/"
API_TOKEN = ""

def get_local_network():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        ifaddresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in ifaddresses:
            for address in ifaddresses[netifaces.AF_INET]:
                ip = address['addr']
                netmask = address['netmask']
                if ip != '172.18.218.7':  # Ignore loopback address
                    return ip, netmask

    return None, None

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

    local_ip, netmask = get_local_network()
    if not local_ip:
        print("Could not detect local network")
        return

    # Adjust the network range based on the detected IP and netmask
    network_prefix = '.'.join(local_ip.split('.')[:-1])
    for i in range(1, 255):
        ip = f"{network_prefix}.{i}"
        hostnames = get_hostnames(ip, args.ports)
        for ip, hostname in hostnames:
            add_ip_address(ip, hostname)

if __name__ == "__main__":
    main()
