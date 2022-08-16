# Systems Security Project

The aim of the project is to secure our web application against the [OWASP Top 10 Vulnerabilities].

### Team Member and chosen vulnerabilities:
- Cheng Yu Xun: Identity and Authentication Failures, Denial Of Service
- Toh Kit Hou Kenneth: Cross-Site Scripting Forgery, Forgot Password
- Poh Jian Yang Darrek: Broken Access Control, Security Logging & Monitoring Failures
- Situ Xuan Hao Vannsar: Account Enumeration and Guessable User account

Setting up production environment:
```
python -m venv .venv (for Windows) / python3 -m venv .venv (for macOS)
.venv\scripts\activate (for Windows) / source .venv/bin/activate (for macOS)
pip install -r requirements.txt
python run.py (to run the file)
```

TODO:
- Change the MYSQL_USER and MYSQL_PASSWORD accordingly to your own credentials in the .env file
- In healthcheck() function in healthcheck_ep.py, change the email in the send_danger_email() parameter to the email you wish to receive the notification.
- Run the Ip Address of the Flask App within 10 secs [If failed to do so, please delete the database in healthcheck_data folder and redo this step.]

Setting up MySQL DB:
1. open sql script in mysql workbench
2. create a database schema named 'secprj'
3. ctrl + shift + enter to run the script

[OWASP Top 10 Vulnerabilities]: <https://owasp.org/www-project-top-ten/>