# Navigation
- [Limit overrun race conditions](#limit-overrun-race-conditions)
- [Bypassing rate limits via race conditions](#bypassing-rate-limits-via-race-conditions)
- [Multi-endpoint race conditions](#multi-endpoint-race-conditions)
- [Single-endpoint race conditions](#single-endpoint-race-conditions)
- [Exploiting time-sensitive vulnerabilities](#exploiting-time-sensitive-vulnerabilities)
# Limit overrun race conditions
1. Authenticate to store
2. Put "l33t" jacket in cart
3. Page says get 20% off using promo code `PROMO20`
4. Enter promotion code and intercept request > Send to repeater
5. Create new tab group and put POST request containing promotion code inside
6. Right click request > Duplicate > 30 times
7. Go to settings > Tools > Proxy > disable "Use keep-alive for HTTP/1 if the server supports it"
8. Repeater tab > Right-click drop down arrow next to send > Select "Send group in parallel (single-packet attack)"
9. Send request
10. Refresh cart and discount coupon should be applied multiple times
- **Note:** Remove coupon and attempt process multiple times if coupon is not applied enough times to complete the lab
# Bypassing rate limits via race conditions
1. Intercept login request as Carlos > Send request to repeater
2. Select the password text > Right-click > Extensions > Turbo Intruder
3. Select the `race-single-packet-attack.py` example
4. Change the `for i in range` code to use the password list and stack all requests inside a single request i.e. `gate='race1'`
- Code will look like the following
```python
def queueRequests(target, wordlists):

    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2
                           )
    for word in open('C:\\repos\\BSCP\\1.0 Lab Lists\\passwords.txt'):
        engine.queue(target.req, word.rstrip(), gate='race1')

    # once every 'race1' tagged request has been queued
    # invoke engine.openGate() to send them in sync
    engine.openGate('race1')

def handleResponse(req, interesting):
    table.add(req)
```
5. Send attack
6. Identify the `302` status code indicating successful login
7. Copy `set-cookie` value from response and paste into browser
8. Go to `/admin` > Delete Carlos
# Multi-endpoint race conditions
1. Authenticate
2. Add gift-card to cart and checkout saving both requests in repeater
3. Edit `POST /cart` requests and make the `productId=1` so you purchase the "l33t" jacket
4. Put the two requests into a tab group in the following order
	1. Add jacket
	2. Checkout
5. Send group in sequence (single connection)
	1. You will notice the first request has a high response time ~`600`ms and the subsequent requests have similar ~`350`ms
	2. Checkout will error saying "INSUFFICIENT FUNDS"
6. Reset cart so just one gift-card is in the cart ready to make a purchase
7. Add an additional `GET /` request as the first request in the tab group so the order is:
	1. `GET /`
	2. Add jacket
	3. Checkout
8. Send group (single connection)
	1. Same pattern follows ~`600`ms first request and ~`350`ms for the subsequent requests
		- This indicates "**connection warming**" will work to prime our subsequent requests
9. Reset cart to just one gift-card
10. Send group in parallel (single-packet attack)
- "l33t" jacket will be purchased
	- Note: If it does not work straight away, reset the cart and try again
# Single-endpoint race conditions
1. Authenticate
2. Changing email will send a link to exploit server with a link
3. Copy POST request to change email `POST /my-account/change-email`
4. Create a tab group in the following format:
	1. Carlos email
	2. Exploit server email
	3. 8 more requests that are the Carlos email
5. **Send group in parallel (single-packet attack type)**
6. Check exploit server and confirm there is a link for Carlos (if it does not appear, try multiple times)
	1. This link will likely be invalid/expired
7. Create a second tab group in the following format:
	1. Carlos email
	2. Exploit server email
8. Use the first tab group to send a group of emails
9. Use the second tab group to send just the two emails
- **Always use the single-packet request**
10. If you do not get it straight away, keep trying
11. Verify email for Carlos > Admin Panel > Delete Carlos
# Exploiting time-sensitive vulnerabilities
1. Login page > Reset password
2. Enter username wiener and see reset link is sent to email address
3. Send request to repeater and make a tab group with two requests
4. **Send group in parallel (single-packet attack)**
5. In the response times, notice each subsequent request is staggered ~`300` ms. Note the email client also receives two separate password reset links with different tokens
6. Note that the cookie is `phpsessionid` indicating PHP is being used
7. Create a second session and request password reset
	1. Delete cookie from browser and issue new request to reset password
8. Now in your tab group should be two separate sessions and CSRF tokens to reset the password
9. **Send group in parallel (single-packet attack)**
10. Both requests receive close to the exact same response time
11. Keep going until you have two requests the get **the exact same response time**
12. In the email client you receive two links with the exact same token
	- This confirms that the time the request is submitted is influencing the token generation
13. Change one of the requests to reset the password to target user `carlos`
14. **Send group in parallel (single-packet attack)**
	1. You will notice that the requests will have largely differing response times but this does not matter
15. Use the password reset link and change the `username` parameter to `carlos`
16. Repeat until you get a valid link
17. Reset password for Carlos > Authenticate as Carlos > Delete Carlos