'''
The code here is to only retrieve the URLs of every building in the SLEB directory
The retrieving and formatting of data are done on 2 other files
'''

from selenium import webdriver
from selenium.webdriver import Edge
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os

import sleb_urls # this is the list of all the buildings' URLS

links = []

urls = sleb_urls.urls # this is the list of all the buildings' URLS

# There's one building which always results in an error for some reason, so instead of starting with a blank list of URLs, I manually inserted this URL first
# urls = ['https://www.sleb.sg/Building/GreenMarkBuildingsDirectory?id=799B4F1B-A16E-4F38-84A2-F579864E95E9']
# replace the urls with the updated list if there's an error when running the code

try:
    '''
    The code will keep running and restart once it has scraped through all 325 pages if there still isnt't 3250 URLs
    This is because for some reason, the website randomly rearranges the buildings, resulting in duplicates and missing buildings
    Errors may also occur due to connection issues etc., so it is best to have a fast internet connection to avoid having to restart many times
    '''
    while len(urls) < 3250: 

        PATH = "C:\Program Files (x86)\msedgedriver.exe" # Path to webdriver. Webdriver is different for different browsers. I use Microsoft Edge in my case

        service = Service(executable_path=PATH) # Webdriver is needed for selenium to work and can be downloaded from the browsers' respective websites
        driver = webdriver.Edge(service=service)
        driver.maximize_window()
        driver.get("https://www.sleb.sg/Building/GreenMarkBuildingsDirectory") # Access the website
        time.sleep(3) # wait for 3 seconds for webpage to load; can change depending on connection and loading speed

        # remove the top element (SLEB Bar) as it may overlap with the back button causing issues
        driver.execute_script("""
            var l = document.getElementsByClassName("sleb-header")[0];
            l.parentNode.removeChild(l);
        """)

    ##    no_of_pages = 3
        no_of_pages = driver.find_element(By.CLASS_NAME, 'total')
        no_of_pages = int(''.join(x for x in no_of_pages.text if x.isdigit()))
        print(f"Total number of pages: {no_of_pages}")

                
        for page in range(1, no_of_pages+1):
            print(f"PAGE: {page}")
            print("-----")
            time.sleep(0.5)
            if links == driver.find_elements(By.CLASS_NAME, 'view-more') or (page != 325 and len(links) < 10):
                time.sleep(7)
                links = driver.find_elements(By.CLASS_NAME, 'view-more') # retrieve the click elements of all buildings in that page
            else:
                links = driver.find_elements(By.CLASS_NAME, 'view-more') # retrieve the click elements of all buildings in that page

            for link in links:
                link.click()
                driver.implicitly_wait(20)
                name_link = driver.find_elements(By.CLASS_NAME, 'name')[10]
                try:
                    name_link.click()
                except:
                    continue # skip the orchard building on page 178 which always results in an error
                tabs = driver.window_handles
                driver.switch_to.window(tabs[1]) # switch tabs to the tab with the id
                url = str(driver.current_url)
                if url not in urls:
                    urls.append(url)
                driver.close() # close this tab
                driver.switch_to.window(tabs[0]) # go back to the previous tab
                back = driver.find_element(By.CLASS_NAME, 'switch-btn.list.detail')
                back.click()

            if page < no_of_pages:
                next_page = driver.find_element(By.LINK_TEXT, str(page + 1))
                next_page.click()

        print(urls) # this will be the resulting list of all URLs collected
        print(len(urls)) # there should be 3250 in total
        driver.quit()
except:
    driver.quit()
    raise
