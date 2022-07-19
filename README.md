# System Security Project

The aim of the project is to secure our web application against the [OWASP Top 10 Vulnerabilities].

### Team Member and chosen vulnerabilities:
- Cheng Yu Xun: Identity and Authentication Failures, Denial Of Service
- Toh Kit Hou Kenneth: Cross-Site Scripting Forgery, Forgot Password
- Poh Jian Yang Darrek: Broken Access Control, Security Logging & Monitoring Failures
- Situ Xuan Hao Vannsar: Account Enumeration and Guessable User account

Setting up production environment:
```
python -m venv .venv (for windows) / python3 -m venv .venv (for macOS)
.venv\scripts\activate (for Windows) / source .venv/bin/activate (for macOS)
pip install -r requirements.txt
python run.py
```
Setting up MySQL DB:
1. open sql script in mysql workbench
2. create a database schema named 'secprj'
3. ctrl + shift + enter to run the script