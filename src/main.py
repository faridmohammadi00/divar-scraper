import os
import csv
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from auth import authenticate_user, confirm_auth
from helpers import *
import time

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def start_process(province='tehran', token=None, scroll_count=2):
    try:
        if token:
            set_basic_token(driver, token)
        
        url = f"https://divar.ir/s/{province}/services"
        driver.get(url)
        time.sleep(3)

        for _ in range(scroll_count):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

        service_listings = driver.find_elements(By.TAG_NAME, "article")
        print(len(service_listings))
        
        data = []
        for listing in service_listings:
            try:
                title = listing.find_element(By.CLASS_NAME, "kt-post-card__title").text
                link = listing.find_element(By.CLASS_NAME, "kt-post-card__action").get_attribute("href")
                data.append({"title": title, "link": link})
            except Exception as e:
                print(f"Error extracting a listing: {e}")

        directory = f"./static/{province}"
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = f"{directory}/{province}_{datetime.now().strftime('%Y-%m-%d')}.csv"
        
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["title", "link"])
            writer.writeheader()
            for item in data:
                writer.writerow(item)
        print(f"Data saved to {filename}")
        
        open_links_from_csv(driver, province, filename)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()


def open_links_from_csv(driver, province, filename):
    file_path = f"{filename}"

    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return

    links = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            links.append(row["link"])

    if not links:
        print("No links found in the CSV file.")
        return

    data_list = []
    for link in links:
        try:
            data = {
                'group': '',
                'sub_group': '',
                'third_group': '',
                'province': province,
                'phone': '',
                'title': '',
                'description': '',
            }

            print(f"Opening link: {link}")
            driver.get(link)
            time.sleep(10)

            breadcrumb_padd = driver.find_element(By.CLASS_NAME, 'kt-breadcrumbs--padded')
            breadcrumbs = breadcrumb_padd.find_elements(By.TAG_NAME, 'li')

            for index, breadcrumb in enumerate(breadcrumbs):
                if index == 0:
                    data['group'] = breadcrumb.text.strip()
                elif index == 1:
                    data['sub_group'] = breadcrumb.text.strip()
                elif len(breadcrumbs) > 2:
                    if index == 2:
                        data['third_group'] = breadcrumb.text.strip()
                        
            title = driver.find_element(By.CLASS_NAME, 'kt-page-title__title').text.strip()
            data['title'] = title
            
            post_page_section_pad = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div/main/article/div/div[1]/section[2]/div')
            kt_base_row = post_page_section_pad.find_elements(By.CLASS_NAME, 'kt-description-row')
            
            description_wrapper = kt_base_row[-1]
            description = description_wrapper.find_element(By.TAG_NAME, 'p').text.strip()
            data['description'] = description
            
            phone_number = get_phone_number(driver)
            if phone_number:
                data['phone'] = phone_number
            else:
                print("Phone number not found.")
                data['phone'] = '***'

            data_list.append(data)
            print(f"Data: {data}")

        except Exception as e:
            print(f"Failed to open {link}. Error: {e}")
    save_data_to_csv(data_list, province)
    print("Finished opening all links.")


def get_phone_number(driver):
    try:
        post_actions = driver.find_element(By.CLASS_NAME, "post-actions")
        post_actions_btn = post_actions.find_elements(By.TAG_NAME, 'button')
        print('post actions: ', len(post_actions_btn))
        contact_btn = post_actions_btn[0]
        contact_btn.click()
        time.sleep(3)
        
        try:
            copy_row = driver.find_element(By.CLASS_NAME, "copy-row")

            phone_link = copy_row.find_element(By.TAG_NAME, "a")
            phone_number = phone_link.text.strip()

            print(f"Phone number: {phone_number}")
            return phone_number
        
        except NoSuchElementException as e:
            print(f"Failed to retrieve phone number. Error: {e}")
            return None

    except Exception as e:
        print(f"Failed to retrieve phone number. Error: {e}")
        return None
    

if __name__ == "__main__":
    phone_number = list_or_enter_phone_number()

    if authenticate_user(phone_number):
        auth_code = input("Enter the authentication code sent to your phone: ").strip()
        access_token, refresh_token, token = confirm_auth(phone_number, auth_code)

        if access_token:
            save_tokens(phone_number, access_token, refresh_token, token)
        else:
            print("Failed to authenticate user.")
            exit()
    else:
        print("Authentication process failed.")
        exit()

    province_name = list_and_select_province()
    
    while True:
        try:
            scroll_count = int(input("Enter the number of times to scroll the page: ").strip())
            if scroll_count > 0:
                break
            else:
                print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    start_process(province_name, access_token, scroll_count)
