'''
The code here is to access each URL from the list of URLs previously retrieved
And scrape the necessary data to form a basic Pandas DataFrame
More formatting is done on another file
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

import sleb_urls

def clean_gfs(lst):
    """
    remove numbered bullet points with space
    """
    new = []
    for i in range(len(lst)):
        gf = lst[i].split()
        if gf == []:
            continue
        elif gf[0] == str(i + 1) or gf[0] == str(i + 1) + '.':
            a = " ".join(gf[1:])
            new.append(a)
        else:
            new.append(lst[i])
    return new

def clean_gfs2(lst):
    """
    remove numbered bullet points without space
    """
    new = []
    for i in range(len(lst)):
            gf = lst[i]
            if gf[:2] == str(i+1) + '.':
                    new.append(gf[2:])
            else:
                    new.append(gf)
    return new

def remove_period(string):
    if string[-1] == '.':
        return string[:-1]
    else:
        return string

def refresh_name(drivr):
    '''
    refresh page if name is not loaded after 3 seconds
    '''
    name = drivr.find_element(By.CLASS_NAME, 'name').text
    start = time.time()
    elapsed = start - time.time()
    while name == '' and elapsed >= -5:
        name = drivr.find_element(By.CLASS_NAME, 'name').text
        elapsed = start - time.time()
        if name != '':
            return name
    drivr.refresh()
    print("refreshing page")
    return refresh_name(drivr)
    
all_bdgs = {'Project Name': [], 'BCA ID': [], 'Project Description:': [], 'Prominent Green Features:': [], 'Award:': [], 'Certification Year:': [], 'GFA:': [], 'Address:': [], 'Postal Code:': [], 'District:': [], 'Developer': [], 'ESD/ESCO/Green Consultant': [], 'Architect': [], 'Structural Engineer': [], 'M & E Engineer': [], 'Landscape Consultant': [], 'Quality Surveyor': [], 'Main Contractor': [], 'Facility Management': []}

PATH = "C:\Program Files (x86)\msedgedriver.exe" # Path to webdriver. Webdriver is different for different browsers. I use Microsoft Edge in my case

service = Service(executable_path=PATH) # Webdriver is needed for selenium to work and can be downloaded from the browsers' respective websites
driver = webdriver.Edge(service=service)
driver.maximize_window()
driver.implicitly_wait(10)

counter = 0
for url in sleb_urls.urls:
    counter += 1
    if counter %20 == 0:
        print(f"{counter} URLs processed out of {len(sleb_urls.urls)}")
    driver.get(url) # Access the website

    # BCA ID
    bca_id = driver.current_url[driver.current_url.index('=') + 1:]

    all_bdgs["BCA ID"].append(bca_id)

    # Building name
    name = driver.find_element(By.CLASS_NAME, 'name').text
    while name == '':
         name = refresh_name(driver)
    print(name)
    all_bdgs["Project Name"].append(name)

    # Building description
    desc = driver.find_elements(By.CLASS_NAME, 'info')[0]
    desc_title = desc.find_element(By.TAG_NAME, 'h6').text
    while desc_title == '':
        desc_title = desc.find_element(By.TAG_NAME, 'h6').text
    desc_text = desc.find_element(By.TAG_NAME, 'p').text
    try:
        all_bdgs[desc_title].append(desc_text)
    except:
        print("description not loaded")
        print(desc_title)
        print(desc_text)

    # Green features
    gf = driver.find_elements(By.CLASS_NAME, 'info')[1]
    gf_title = gf.find_element(By.TAG_NAME, 'h6').text
    while gf_title == '':
        gf = driver.find_elements(By.CLASS_NAME, 'info')[1]
        gf_title = gf.find_element(By.TAG_NAME, 'h6').text
    gf_text = gf.find_element(By.TAG_NAME, 'p').text
    gf_text = gf_text.replace("•", "")
    gf_text = gf_text.split("\n")
    gf_text = clean_gfs(gf_text)
    gf_text = clean_gfs2(gf_text)
    gf_text = list(map(remove_period, gf_text))
    all_bdgs[gf_title].append(gf_text)

    # building info and certification info
    info = driver.find_elements(By.CLASS_NAME, 'info.horizontal')
    info_headers = list(map(lambda x: x.find_element(By.TAG_NAME, 'h6'), info))
    info_headers = list(map(lambda x: x.text, info_headers))
    info_vals = list(map(lambda x: x.find_element(By.TAG_NAME, 'p'), info))
    info_vals = list(map(lambda x: x.text, info_vals))
    start = time.time()
    elapsed = start - time.time()
    while info_vals[0] == '-' and elapsed >= -10: # 10 second timeout
        info_vals = list(map(lambda x: x.find_element(By.TAG_NAME, 'p'), info))
        info_vals = list(map(lambda x: x.text, info_vals))
        elapsed = start - time.time()
        if info_vals[0] != '-':
            break
    for i in range(len(info_headers)):
        all_bdgs[info_headers[i]].append(info_vals[i])

    # stakeholder info
    staff_info = driver.find_element(By.CLASS_NAME, 'staff')
    staff_info = staff_info.find_elements(By.TAG_NAME, 'li')
    staff_info_headers = list(map(lambda x: x.find_element(By.TAG_NAME, 'h6'), staff_info))
    staff_info_headers = list(map(lambda x: x.text, staff_info_headers))
    staff_info_vals = list(map(lambda x: x.find_element(By.TAG_NAME, 'p'), staff_info))
    staff_info_vals = list(map(lambda x: x.text, staff_info_vals))
    for s in list(all_bdgs.keys())[10:]:
        if s in staff_info_headers:
            all_bdgs[s].append(staff_info_vals[staff_info_headers.index(s)])
        else:
            all_bdgs[s].append("")

print(all_bdgs)
GM_bdgs = pd.DataFrame(all_bdgs)
GM_bdgs.to_csv("GM_buildings_raw.csv", index=False)
os.startfile("GM_buildings_raw.csv")
