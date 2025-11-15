import time
import requests

for i in range(10):
    try:
        r = requests.post('http://127.0.0.1:5000/chat', json={'message':'hello from test'})
        print('attempt', i, 'status', r.status_code)
        print(r.text)
        break
    except Exception as e:
        print('wait', i, e)
        time.sleep(0.5)
