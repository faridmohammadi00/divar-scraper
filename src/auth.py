import requests


def authenticate_user(phone):
    url = "https://api.divar.ir/v5/auth/authenticate"
    payload = {"phone": phone}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("Authentication request sent successfully.")
        return True
    else:
        print(f"Error during authentication: {response.status_code}, {response.text}")
        return False
    
    
def confirm_auth(phone, code):
    url = "https://api.divar.ir/v5/auth/confirm"
    payload = {
        "phone": phone,
        "code": code
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("Authentication confirmed successfully.")
        return data["access_token"], data["refresh_token"], data["token"]
    else:
        print(f"Error during confirmation: {response.status_code}, {response.text}")
        return None, None, None
