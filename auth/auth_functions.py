import uuid
import requests

def get_mac_address():
    id = uuid.getnode()
    mac = ':'.join(("%012X" % id)[i:i+2] for i in range(0, 12, 2))
    return mac

def auth(username, password):
    mac = get_mac_address()
    res = requests.post('https://tellurium.ejae8319.workers.dev/api/users/auth', json={
        "project": "네이버자동포스팅-신공간",
        "username": username,
        "password": password,
        "code": mac,
    })
    return res.ok