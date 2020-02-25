import pymysql
import requests


# path = 'https://172.16.10.1'
# with requests.Session() as session:
#     data = {"username": 'admin', "password": 'admin'}
#     url = f'{path}/api/auth/login'
#     response = session.post(url, json=data, verify=False)
#     json = response.json()
#     print(json)

# Open database connection
db = pymysql.connect("198.51.100.12", "root", "coldplay", "apollo")

# prepare a cursor object using cursor() method
cursor = db.cursor()

# execute SQL query using execute() method.
cursor.execute("SELECT VERSION()")
