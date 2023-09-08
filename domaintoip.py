import socket
import sys
from termcolor import colored
from tqdm import tqdm

def get_ip_addresses(websites):
    ip_addresses = {}
    
    for website in tqdm(websites, desc="Processing", unit="website"):
        try:
            # Remove "http://" or "https://" if present in the website URL
            website = website.replace("http://", "").replace("https://", "")
            
            # Remove trailing "/" from the website URL
            website = website.rstrip("/")
            
            ip_address = socket.gethostbyname(website)
            ip_addresses[website] = ip_address
            print(f"{colored(website, 'blue')}: {colored(ip_address, 'green')}")
        except socket.gaierror as e:
            ip_addresses[website] = str(e)
            print(f"{colored(website, 'blue')}: {colored('Error: ' + str(e), 'red')}")
    
    return ip_addresses

def save_ips_to_file(ip_addresses, output_file_name):
    with open(output_file_name, "w") as output_file:
        for ip_address in ip_addresses.values():
            output_file.write(f"{ip_address}\n")

# Display a logo
logo = """
  ______   ______   .__   __.  __  .___________.    _______ .______       __       __  .___________. __    ______ 
 /  __  \ /  __  \  |  \ |  | |  | |           |   /  _____||   _  \     |  |     |  | |           ||  |  /  __  \
|  |  |  |  |  |  | |   \|  | |  | `---|  |----`  |  |  __  |  |_)  |    |  |     |  | `---|  |----`|  | |  |  |  |
|  |  |  |  |  |  | |  . `  | |  |     |  |       |  | |_ | |   ___/     |  |     |  |     |  |     |  | |  |  |  |
|  `--'  |  `--'  | |  |\   | |  |     |  |       |  |__| | |  |         |  `----.|  |     |  |     |  | |  `--'  |
 \______/ \______/  |__| \__| |__|     |__|        \______| | _|         |_______||__|     |__|     |__|  \______/ 
"""

print(colored(logo, 'cyan'))

# Prompt the user for the filename containing the list of websites
input_file_name = input("Enter the filename containing the list of websites: ")
output_file_name = input("Enter the filename to save the IP addresses: ")

try:
    with open(input_file_name, "r") as input_file:
        websites = [line.strip() for line in input_file.readlines()]

    num_websites = len(websites)
    print(f"Number of websites in the file: {num_websites}")

    ip_addresses = get_ip_addresses(websites)
    save_ips_to_file(ip_addresses, output_file_name)

    print(f"IP addresses saved to '{output_file_name}'")

except FileNotFoundError:
    print(colored(f"Error: File '{input_file_name}' not found.", 'red'))
except Exception as e:
    print(colored(f"An error occurred: {e}", 'red'))
