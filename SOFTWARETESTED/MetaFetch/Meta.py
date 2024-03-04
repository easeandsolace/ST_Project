# This script is designed to automate the task of updating the metadata (title and description) of pages on a website. It does so by reading URLs and their corresponding new titles and descriptions from an Excel file, then using Selenium WebDriver to navigate to each URL, update the metadata, and save the changes. The script utilizes multiprocessing to handle chunks of the data concurrently, potentially speeding up the process when dealing with a large number of pages.
#  !!!!! MANUAL AUTH !!!!!!
import pandas as pd
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from multiprocessing import Process
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def check_the_result(intial_data, adding_result):
    if intial_data == adding_result:
        return True
    else:
        return False

def split_dataframe():
    chunk_size = 2000
    df = pd.read_excel("meta.xlsx")
    list_of_smaller_dfs = list()
    num_chunks = len(df) // chunk_size + 1
    for i in range(num_chunks):
        list_of_smaller_dfs.append(df[i * chunk_size:(i + 1) * chunk_size])
    return list_of_smaller_dfs


list_of_urls_and_crosslink = []


def processing(chunx):
    opts = Options()
    opts.add_argument('--user-data-dir=C:\\Users\\steam\\AppData\\Local\\Google\\Chrome\\User Data')
    opts.add_argument(r"user-data-dir=C:\Users\steam\AppData\Local\Google\Chrome\User Data\Profile 1")
    # opts.headless = True
    # opts.add_argument('--disable-gpu')
    opts.add_argument("window-size=1440,900")
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    # Авторизация
    browser.get("https://softwaretested.com/cp/")
    time.sleep(10)


    for index, row in chunx.iterrows():
        try:

            browser.get(row[0])
            browser.implicitly_wait(15)
            print(row[0])
            # browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            title = browser.find_element(By.XPATH, "//div[@id=\"yoast-google-preview-title-metabox\"]")
            browser.execute_script("arguments[0].scrollIntoView();", title)
            time.sleep(1)
            title.click()
            time.sleep(1)
            ActionChains(browser).key_down(Keys.CONTROL, title).send_keys('a').key_up(Keys.CONTROL,
                                                                                             title).perform()
            time.sleep(1)
            title.send_keys(Keys.BACKSPACE)
            time.sleep(1)

            title.send_keys(row[1])

            time.sleep(1)
            print("title posted")

            # TITLE POSTING CHECK
            added_title = browser.find_element(By.XPATH, "//*[@id=\"yoast-google-preview-title-metabox\"]/div/div/div/span/span").text
            print(check_the_result(row[1], added_title))
            # TITLE POSTING CHECK
            #
            # #DESC PART
            description = browser.find_element(By.XPATH, "//div[@id=\"yoast-google-preview-description-metabox\"]")
            browser.execute_script("arguments[0].scrollIntoView();", description)
            time.sleep(1)
            description.click()
            time.sleep(1)
            ActionChains(browser).key_down(Keys.CONTROL, description).send_keys('a').key_up(Keys.CONTROL,
                                                                                            description).perform()
            time.sleep(1)
            description.send_keys(Keys.BACKSPACE)

            time.sleep(1)
            description.send_keys(row[2])
            print("desc posted")

            #DESCRIPTION POSTING CHECK
            added_description = browser.find_element(By.XPATH, "//*[@id=\"yoast-google-preview-description-metabox\"]/div/div/div/span/span").text
            print(check_the_result(row[2], added_description))
            # DESCRIPTION POSTING CHECK

            time.sleep(1)
            preview = browser.find_element(By.XPATH, "//*[@id=\"preview-action\"]")
            save = browser.find_element(By.XPATH, "//*[@id=\"publish\"]")
            browser.execute_script("arguments[0].scrollIntoView();", preview)
            time.sleep(1)
            save.click()
            print("saved")
            browser.implicitly_wait(15)
            time.sleep(3)
        except Exception as e:
            continue


if __name__ == "__main__":
    process_list = []
    for dataframe in split_dataframe():
        p = Process(target=processing, args=(dataframe,))
        p.start()
        process_list.append(p)
    for process in process_list:
        process.join()
