from re import M
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.common.exceptions import (
    ElementNotVisibleException,
    ElementClickInterceptedException,
    WebDriverException,
    TimeoutException,
)

import time
from selenium.webdriver.common.action_chains import ActionChains
import sys
import os
from twocaptcha import TwoCaptcha
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])


def solveCaptcha(url):

    api_key = os.getenv('APIKEY_2CAPTCHA', 'c862f1c33bcc20c8f16e2d060c75d7f9')

    solver = TwoCaptcha(api_key)

    try:
        result = solver.hcaptcha(
            sitekey='33f96e6a-38cd-421b-bb68-7806e1764460',
            url=url,
        )

        return result
    except Exception as e:
        print(e)

    else:
        return result

search_query = input("Enter search query :")
place_name = input("Enter place name :")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.pagesjaunes.fr/")
driver.maximize_window()

time.sleep(10)

result = solveCaptcha(driver.current_url)
print(result)

captcha_code = result['code']
# WebDriverWait(driver, 25).until(
#         EC.presence_of_element_located(
#             (By.ID, "//*[contains(@id,'h-captcha-response')]")
#         )
#     )

container = driver.find_element(By.ID,"cf-hcaptcha-container")
# driver.execute_script("arguments[0].removeChild(arguments[0].firstElementChild);", container)
# driver.execute_script("document.querySelector('[title= \"Main content of the hCaptcha challenge\"]').remove();")

driver.execute_script("document.querySelector(`[id^=h-captcha-response]`).innerHTML = " +"'"+ captcha_code +"'")

driver.execute_script("document.getElementById('challenge-form').submit()")

time.sleep(10)

driver.find_element(By.ID,"didomi-notice-agree-button").click()
time.sleep(2)

driver.find_element(By.ID,"quoiqui").click()
driver.find_element(By.ID,"quoiqui").send_keys(search_query)


driver.find_element(By.ID,"ou").click()
driver.find_element(By.ID,"ou").send_keys(place_name)

driver.find_element(By.XPATH,"//*[@id='form_motor_pagesjaunes']/div[1]/div[2]/div[2]/button").click()

time.sleep(5)

name_scrap = []
address_scrap = []
tel_scrap = []

names_for_csv = []
address_scrap_csv = []
tel_scrap_csv = []

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#Start extracting
html = driver.page_source
soup = BeautifulSoup(html, features="html.parser")

result_section = soup.find("section", {"id": "listResults"})

for ultag in soup.find_all('ul', {"class" : "bi-list"}):
    for litag in ultag.find_all('li'):
        name_tag = litag.find('h3')
        if name_tag!= None:
            name_scrap.append(name_tag.text)
            print(name_tag.text)
        else:
            name_scrap.append(None)
        a_tag = litag.find('a', {'title' : 'Voir le plan'})
        if a_tag != None:
            # print(a_tag.text.strip())
            address_scrap.append(a_tag.text.strip())
        else:
            address_scrap.append(None)
        phone_number_div = litag.find('div', {'class' : 'number-contact txt_sm'})
        if phone_number_div!= None:
            phone_number_span = phone_number_div.find_all('span')
            print(phone_number_span)
            if(len(phone_number_span)>0):
                tel_scrap.append(phone_number_span[len(phone_number_span)-1])
            else:
                tel_scrap.append(None)
        else:
            tel_scrap.append(None)





while(True):
    try:
        element = driver.find_element(By.ID,"pagination-next")
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        driver.find_element(By.ID,"pagination-next").click()

        time.sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, features="html.parser")

        result_section = soup.find("section", {"id": "listResults"})

        for ultag in soup.find_all('ul', {"class" : "bi-list"}):
            for litag in ultag.find_all('li'):
                name_tag = litag.find('h3')
                if name_tag!= None:
                    name_scrap.append(name_tag.text)
                    print(name_tag.text)
                else:
                    name_scrap.append(None)
                a_tag = litag.find('a', {'title' : 'Voir le plan'})
                if a_tag != None:
                    # print(a_tag.text.strip())
                    address_scrap.append(a_tag.text.strip())
                else:
                    address_scrap.append(None)
                phone_number_div = litag.find('div', {'class' : 'number-contact txt_sm'})
                if phone_number_div!= None:
                    phone_number_span = phone_number_div.find_all('span')
                    print(phone_number_span)
                    if(len(phone_number_span)>0):
                        tel_scrap.append(phone_number_span[len(phone_number_span)-1])
                    else:
                        tel_scrap.append(None)
                else:
                    tel_scrap.append(None)

    except:
        break


for i in range(len(name_scrap)):
    if name_scrap[i] != None:
        names_for_csv.append(name_scrap[i])
        address_scrap_csv.append(address_scrap[i])
        if tel_scrap[i] == None:
            tel_scrap_csv.append(None)
        else:
            tel_scrap_csv.append(tel_scrap[i].text)



print(len(names_for_csv))
print(len(address_scrap_csv))
print(len(tel_scrap_csv))

dict = {'name': names_for_csv, 'Address': address_scrap_csv, 'Contact Number': tel_scrap_csv} 
df = pd.DataFrame(dict)

df.to_csv('ScrappedData.csv')















