import requests
url = 'https://maker.ifttt.com/trigger/test/with/key/cdWvZpM0bM84ydmsi41QnI'
#parameters = {
# 'username': 'username',
# 'password': 'password',
# 'keeploggedin': 'true'
#}

session = requests.Session()
req = session.post(url)
print(req.status_code)


