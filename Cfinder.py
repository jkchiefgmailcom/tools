import requests
import urllib3
import argparse

# Suppress only the specific InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ASCII Art Header
def print_header():
    header = r"""
 ██████╗███████╗██╗███╗   ██╗██████╗ ███████╗██████╗ 
██╔════╝██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗
██║     █████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝
██║     ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
╚██████╗██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║
 ╚═════╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝
                                                     
    """
    print(header)
    print("CFINDER - What are you hiding behind your Cloudflare?\n")

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Script to check HTTP/HTTPS services behind Cloudflare.')
    parser.add_argument(
        '-i', '--ip_ports', 
        required=True, 
        help='File containing a list of IP:port combinations, one per line.'
    )
    parser.add_argument(
        '-u', '--url_hosts', 
        required=True, 
        help='File containing a list of hostnames, one per line.'
    )
    return parser.parse_args()

# Function to read lists from files
def read_list_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Dictionary to store results for grouping
results = {}

# Function to perform the HTTP request
def check_host(ip_port, url_host):
    ip, port = ip_port.split(':')
    protocol = 'https' if port in ['443', '8443'] else 'http'
    url = f"{protocol}://{ip}:{port}"

    headers = {
        'Host': url_host
    }

    # Indication of the current processing
    print(f"Processing IP: {ip}, Port: {port}, Host: {url_host}...")

    try:
        response = requests.get(url, headers=headers, timeout=5, verify=False)
        status_code = response.status_code
        response_size = len(response.content)
        
        # Grouping key based on IP and Port
        key = (ip, port)
        if key not in results:
            results[key] = []
        results[key].append((url_host, status_code, response_size))
    except Exception as e:
        # Handle errors separately using a unique key for errors
        key = (ip, port)
        if key not in results:
            results[key] = []
        results[key].append((url_host, 'Error', str(e)))

# Main function
def main():
    # Print header
    print_header()

    args = parse_arguments()

    # Read IP:ports and hostnames from files
    ip_ports = read_list_from_file(args.ip_ports)
    url_hosts = read_list_from_file(args.url_hosts)

    # Iterate over the IP:ports and URLs
    for ip_port in ip_ports:
        for url_host in url_hosts:
            check_host(ip_port, url_host)

    # Print grouped results
    print("\nFinal Grouped Results:\n")
    divider = "=" * 50  # Divider for separating different IP:port groups
    for key, hosts in results.items():
        ip, port = key
        print(f"{divider}")
        print(f"IP: {ip:<15} Port: {port:<5}")
        print(f"{divider}")
        for host_info in hosts:
            host, status, size = host_info
            print(f"Host: {host:<30} Status: {status:<6} Size: {size}")
        print("\n")

if __name__ == "__main__":
    main()
