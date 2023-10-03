import csv
import smtplib
import base64
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from termcolor import colored

def send_bulk_emails():
    # Step 1: Ask for SMTP server file
    smtp_file = input("Enter the path to the SMTP server file (format: 'server|port|user|pass'): ")

    # Step 2: Ask for email list file
    email_file = input("Enter the path to the email list file (one email per line): ")

    # Step 3: Ask for sender name and subject
    sender_name = input("Enter the sender name: ")
    encoded_name = base64.b64encode(sender_name.encode()).decode()
    subject = input("Enter the subject: ")
    subject += f" [{time.strftime('%Y-%m-%d %H:%M:%S')}]"
    encoded_subject = base64.b64encode(subject.encode()).decode()




    # Read SMTP server file
    smtp_servers = []
    with open(smtp_file, 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            smtp_servers.append({
                'server': row[0],
                'port': int(row[1]),
                'username': row[2],
                'password': row[3]
            })

    # Read email list file
    with open(email_file, 'r') as file:
        emails = file.read().splitlines()
    
    # Step 4: Count the number of emails in the list
    total_emails = len(emails)
    print(f"Total emails in the list: {total_emails}")

    # Step 5: Ask for the path to the HTML file
    html_file_path = input("Enter the path to the HTML file: ")

    # Read HTML content from the file
    with open(html_file_path, 'r', encoding='utf-8') as html_file:
        html_letter = html_file.read()

    # Step 6: Rotate between SMTP servers for every 50 emails sent
    smtp_index = 0
    email_count = 0

    # Step 7: Use coloring in the output
    def print_colored(message, color):
        print(colored(message, color))

    # Step 8: Save success and error emails to separate files
    success_file = "result/success.txt"
    error_file = "result/errors.txt"

    # Step 9: Count the number of emails sent for each SMTP server
    count_file = "result/email_counts.txt"
    email_counts = {}

    # Define headers
    headers = {
        'X-Priority': '1',
        'X-MSMail-Priority': 'High',
        'Importance': 'High',
        'X-Mailer': 'Python SMTP Client'
    }

    for email in emails:
        smtp_server = smtp_servers[smtp_index]
        server = smtp_server['server']
        port = smtp_server['port']
        username = smtp_server['username']
        password = smtp_server['password']
        sender_email = f"=?UTF-8?B?{encoded_name}?= <{username}>"

        # Create the email message
        msg = MIMEMultipart('alternative')
        msg['From'] = Header(sender_email)
        msg['To'] = email
        msg['Subject'] = f"=?UTF-8?B?{encoded_subject}?="

        # Add the HTML content
        msg.attach(MIMEText(html_letter, 'html'))

        # Add headers to the message
        for key, value in headers.items():
            msg.add_header(key, value)

        # Connect to the SMTP server
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(username, password)

            # Send the email
            try:
                smtp.send_message(msg)
                print_colored(f"Email sent to {email} via {server}:{port}", "green")

                # Save successful emails to a file
                with open(success_file, "a") as f:
                    f.write(email + "\n")

                # Count the number of emails sent for each SMTP server
                email_counts[server] = email_counts.get(server, 0) + 1

            except smtplib.SMTPException as e:
                print_colored(f"Failed to send email to {email} via {server}:{port} - Error: {str(e)}", "red")

                # Save failed emails to a file
                with open(error_file, "a") as f:
                    f.write(email + "\n")

        email_count += 1

        # Calculate and print the remaining emails
        remaining_emails = total_emails - email_count
        print(f"Remaining emails: {remaining_emails}")

        # Rotate between SMTP servers every 50 emails sent
        if email_count % 50 == 0:
            smtp_index = (smtp_index + 1) % len(smtp_servers)

    # Step 10: Print the summary of sent emails
    for server, count in email_counts.items():
        print(f"{server} has sent {count} emails")

# Example usage
send_bulk_emails()
