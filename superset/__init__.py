import os
import requests
from dotenv import load_dotenv

load_dotenv()

superset_api_url = os.environ.get(
    'SUPERSET_API_URL')
# 10.1.111.18:3003/register


def register(username, first_name, last_name, email, password):
    body_j = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "roles": [1]
    }

    print(body_j)

    try:
        response = requests.post(superset_api_url, timeout=5, json=body_j)
        response.raise_for_status()
        print("response", response.json())
        return True
    except Exception as e:
        print(f"Register error {e}")
        return False
