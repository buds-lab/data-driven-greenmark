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

'''
Start at institutional school
manually include orchardgateyway@emerald and page 15 of commercial
manually include Block N2.1 - Nanyang Technological University and page 18 of insitutional(school)
'''

# setting index for each building type
types = {
'Office': 0,
'Office Interior': 1,
'Others': 2,
'Commercial': 3,
'Data Centre': 4,
'District': 5,
'Hotel': 6,
'Industrial': 7,
'Institutional': 8,
'Institutional (Healthcare)': 9,
'Institutional (School)': 10,
'Infrastructure': 11,
'Park': 12,
'Public Housing': 13,
'Rapid Transit System': 14,
'Residential': 15,
'Retail': 16,
'Retail (Tenant)': 17,
'Restaurant': 18,
'Supermarkets': 19,
'Mixed Development': 20,
'Healthier Workplaces': 21,
'Laboratories': 22,
}

urls = []

try:
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
    # remove the bottom left smiley face icon as it interferes with the sidebar
    driver.execute_script("""
        var l = document.getElementsByClassName("hydrated")[1];
        l.parentNode.removeChild(l);
    """)
    
    sidebar = driver.find_element(By.ID, 'TypesOfBuildingsHeader')
    sidebar.click()
    sidebar = driver.find_element(By.ID, 'TypesOfBuildingsCollapse')
    checkboxes = sidebar.find_elements(By.CLASS_NAME, 'check')

    for i in range(len(checkboxes)):
        for k,v in types.items():
            if v == i:
                bdg_type = k
                print(bdg_type)
        checkbox = checkboxes[i]
        if i > 0:
            prev_checkbox = checkboxes[i-1]
            prev_checkbox.click()
        checkbox.click()
        if i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
            continue

        time.sleep(10)
        dic = {"link": [], "building_use": []}

        no_of_pages = driver.find_element(By.CLASS_NAME, 'total')
        no_of_pages = int(''.join(x for x in no_of_pages.text if x.isdigit()))
        print(f"Total number of pages: {no_of_pages}")

        links = []                
        for page in range(1, no_of_pages+1):
            print(f"PAGE: {page}")
            print("-----")
            time.sleep(0.5)
            if page == 15 and bdg_type == "Commercial": # skip page 15 of commercial buildings; to manually add
                next_page = driver.find_element(By.LINK_TEXT, str(page + 1))
                next_page.click()
                continue
            if page == 18 and bdg_type == "Institutional (School)": # skip page 18 of insitutional(school) buildings; to manually add
                next_page = driver.find_element(By.LINK_TEXT, str(page + 1))
                next_page.click()
                continue
            
            if links == driver.find_elements(By.CLASS_NAME, 'view-more') or (page != no_of_pages and len(links) < 10):
                time.sleep(10)

            links = driver.find_elements(By.CLASS_NAME, 'view-more') # retrieve the click elements of all buildings in that page

            for link in links:
                link.click()
                time.sleep(3)
                name_links = driver.find_elements(By.CLASS_NAME, 'name')
                print(list(map(lambda x: x.text, name_links)))
                for name in name_links:
                    if name.text != '':
                        name_link = name
                try:
                    name_link.click()
                except:
                    print(name_link.text)
                    print("not clicking on name, trying again")
                    time.sleep(3)
                    name_link.click()
                    continue # skip the orchard building on page 178 which always results in an error
                tabs = driver.window_handles
                driver.switch_to.window(tabs[1]) # switch tabs to the tab with the id
                url = str(driver.current_url)
                if url not in urls:
                    urls.append(url)
                    dic["link"].append(url)
                    dic["building_use"].append(bdg_type)
                driver.close() # close this tab
                driver.switch_to.window(tabs[0]) # go back to the previous tab
                back = driver.find_element(By.CLASS_NAME, 'switch-btn.list.detail')
                back.click()

            if page < no_of_pages:
                next_page = driver.find_element(By.LINK_TEXT, str(page + 1))
                next_page.click()
                
        df = pd.DataFrame(dic)
        df.to_csv(f"{bdg_type}.csv", index=False)
            
    time.sleep(3)
    driver.quit()
except:
    time.sleep(3)
    driver.quit()
    raise
