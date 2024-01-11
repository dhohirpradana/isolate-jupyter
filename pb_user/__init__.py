import os
import requests
from flask import Flask, request, jsonify

from pb_token import token_get
from dotenv import load_dotenv

load_dotenv()

pb_user_url = os.environ.get('PB_USER_URL')
pb_login_url = os.environ.get('PB_ADMIN_LOGIN_URL')
print(pb_user_url)
def user_create(j_port, username, password, email, first_name, last_name):
    print({
        "email": email,
        "password": password,
        "username": username,
        "passwordConfirm": password,
        "firstName": first_name,
        "lastName": last_name,
        "role": "authenticated",
        "jToken": "test-token-123",
        "jPort": j_port
    })
    pb_token = token_get()
    try:
        r = requests.post(pb_user_url,
                        json={
                            "email": email,
                            "password": password,
                            "username": username,
                            "passwordConfirm": password,
                            "firstName": first_name,
                            "lastName": last_name,
                            "role": "authenticated",
                            "jToken": "test-token-123",
                            "jPort": j_port
                        },
                        headers={
                            "Authorization": "Bearer " + pb_token
                        }
        )
        r.raise_for_status()
        data = r.json()
        status_code = r.status_code
        return (True, None)
    
    except Exception as e:
        status_code = r.status_code
        print(str(e))
        return (False, "Error create PB user.")
    
def user_remove(username):
    pb_token = token_get()
    # get list of users
    try:
        r = requests.get(pb_user_url, headers={"Authorization": "Bearer " + pb_token})
        r.raise_for_status()
        data = r.json()
        users = data["items"]
        
        # check if user exists and get id
        for user in users:
            if user["username"] == username:
                user_id = user["id"]
                try:
                    r = requests.delete(pb_user_url + f"/{user_id}", headers={"Authorization": "Bearer " + pb_token})
                    r.raise_for_status()
                    data = r.json()
                    status_code = r.status_code
                    print(data)
                except Exception as e:
                    status_code = r.status_code
                    print(str(e))
                break
            else:
                pass
    except Exception as e:
        print(str(e))
        pass

# check connection
def check_connection():
    try:
        r = requests.get(pb_login_url)
        print("pb conn success")
        return True
    except Exception as e:
        print(str(e))
        print("pb conn failed")
        return False
    
# check if user already exists
def user_check(email, username):
    pb_token = token_get()
    try:
        r = requests.get(pb_user_url, headers={"Authorization": "Bearer " + pb_token})
        r.raise_for_status()
        data = r.json()
        users = data["items"]
        
        # check if user not exists
        for user in users:
            if user["email"] == email or user["username"] == username:
                return False
        return True
    except Exception as e:
        print('An exception occurred')
        return jsonify({"message": "Error check user."}), 400