import smtplib
import argparse
import socket
from email.message import EmailMessage
from termcolor import colored
import time
import ssl

def test_smtp_server(server_info, target_email):
    server, port, username, password = server_info.split('|')
    port = int(port)

    try:
        with smtplib.SMTP(server, port, timeout=5) as smtp:
            smtp.set_debuglevel(0)

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            smtp.starttls(context=context)

            smtp.login(username, password)

            msg = EmailMessage()
            msg.set_content(f"This is a test message.\nServer: {server}\nPort: {port}\nUsername: {username}\nPassword: {password}")
            msg['Subject'] = "SMTP Test"
            msg['From'] = username
            msg['To'] = target_email

            smtp.send_message(msg)
            return True
    except (smtplib.SMTPException, socket.timeout, ssl.SSLError) as e:
        print(colored(f"Error while testing server {server}:{port} ({username}): {str(e)}", "red"))
        return False
    except socket.gaierror as e:
        print(colored(f"DNS resolution error for server {server}:{port} ({username}): {str(e)}", "red"))
        return False
    except ConnectionRefusedError as e:
        print(colored(f"Connection refused for server {server}:{port} ({username}): {str(e)}", "red"))
        return False

def main():
    parser = argparse.ArgumentParser(description="Check validity of SMTP servers and save valid ones.")
    parser.add_argument("smtp_list", type=str, help="Path to the file containing SMTP server list")
    parser.add_argument("target_email", type=str, help="Your email to send test message to")

    args = parser.parse_args()

    with open(args.smtp_list, 'r') as f:
        smtp_servers = f.read().splitlines()

    valid_servers = []

    print(colored(f"Checking {len(smtp_servers)} SMTP servers...\n", "blue"))

    for index, server_info in enumerate(smtp_servers, start=1):
        fields = server_info.split('|')
        if len(fields) != 4:
            print(colored(f"Invalid server info format: {server_info}", "red"))
            continue

        server, port, username, password = fields
        port = int(port)
        
        print(colored(f"Checking server {index}/{len(smtp_servers)}: {server}:{port} ({username})", "yellow"), end='\r')
        
        if test_smtp_server(server_info, args.target_email):
            valid_servers.append(server_info)
            with open("smtp-khdam.txt", 'a') as f:
                f.write(server_info + '\n')
            
            print(colored(f"Server {index}/{len(smtp_servers)} is valid: {server_info}", "green"))
        else:
            print(colored(f"Server {index}/{len(smtp_servers)} is not valid: {server_info}", "red"))

        time.sleep(1)  # Add a delay to avoid spamming the servers

    print(colored(f"\n{len(valid_servers)} valid servers saved to valid_send.txt", "blue"))


if __name__ == "__main__":
    main()
