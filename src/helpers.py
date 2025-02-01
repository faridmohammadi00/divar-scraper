import os
import json
import csv
from datetime import datetime


def list_and_select_province():
    with open('./data/provinces.json', 'r', encoding='utf-8') as file:
        provinces = json.load(file)
    
    print("Select a province by entering its number:")
    for idx, province in enumerate(provinces, start=1):
        print(f"{idx}. {province['name']} ({province['abr']})")
    
    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(provinces):
                selected_province = provinces[choice - 1]
                print(f"You selected: {selected_province['name']} ({selected_province['abr']})")
                return selected_province['abr']
            else:
                print(f"Please enter a number between 1 and {len(provinces)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
            
def list_or_enter_phone_number():
    tokens_file = "./data/tokens.json"
    phone_numbers = []

    if os.path.exists(tokens_file):
        with open(tokens_file, "r", encoding="utf-8") as file:
            tokens_data = json.load(file)
            phone_numbers = list(tokens_data.keys())

    if phone_numbers:
        print("Select a phone number from the list, or enter a new one:")
        for idx, phone in enumerate(phone_numbers, start=1):
            print(f"{idx}. {phone}")
        print(f"{len(phone_numbers) + 1}. Enter a new phone number")

        while True:
            try:
                choice = int(input(f"Enter the number of your choice (1-{len(phone_numbers) + 1}): "))
                if 1 <= choice <= len(phone_numbers):
                    return phone_numbers[choice - 1]
                elif choice == len(phone_numbers) + 1:
                    return input("Enter your new phone number: ").strip()
                else:
                    print(f"Please enter a valid number (1-{len(phone_numbers) + 1}).")
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        print("No phone numbers found. Please enter a new phone number.")
        return input("Enter your phone number: ").strip()
    
    
def save_tokens(phone, access_token, refresh_token, token):
    tokens_file = "./data/tokens.json"
    if os.path.exists(tokens_file):
        with open(tokens_file, "r", encoding="utf-8") as file:
            tokens_data = json.load(file)
    else:
        tokens_data = {}

    tokens_data[phone] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token": token
    }

    with open(tokens_file, "w", encoding="utf-8") as file:
        json.dump(tokens_data, file, indent=4, ensure_ascii=False)

    print("Tokens saved successfully.")
    

def load_token(phone):
    tokens_file = "./data/tokens.json"
    if os.path.exists(tokens_file):
        with open(tokens_file, "r", encoding="utf-8") as file:
            tokens_data = json.load(file)
            return tokens_data.get(phone)
    return None


def set_basic_token(driver, token):
    driver.execute_cdp_cmd("Network.enable", {})

    driver.execute_cdp_cmd(
        "Network.setExtraHTTPHeaders",
        {
            "headers": {
                "Authorization": f"Basic {token}"
            }
        }
    )
    
    
def initiating_provinces():
    with open('./data/provinces.json', 'r', encoding='utf-8') as provinces:
        provinces_data = json.load(provinces)
        
    for province in provinces_data:
        dir_name = province["abr"]
        os.makedirs('./static/' + dir_name, exist_ok=True)

        print(f"It's Done. initiating provinces")
        
        
def save_data_to_csv(data, province, folder="./static"):
    if not os.path.exists(folder + '/' + province):
        os.makedirs(folder)
    
    filename = f"{folder}/{province}/data_{province}_{datetime.now().strftime('%Y-%m-%d')}.csv"
    file_exists = os.path.exists(filename)
    
    if not data:
        print("No data to save.")
        return
    header = data[0].keys()
    
    try:
        with open(filename, mode='a' if file_exists else 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            if not file_exists:
                writer.writeheader()
            
            writer.writerows(data)
            
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"An error occurred while saving data to CSV: {e}")