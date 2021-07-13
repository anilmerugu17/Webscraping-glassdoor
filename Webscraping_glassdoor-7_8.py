#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Author - Anil Kumar Merugu
#Emaid id - anilmerugu17@gmail.com
#Should you have any queries, please drop an email


# In[1]:


from webdriver_manager.chrome import ChromeDriverManager
import json
from parse_utils import *
from lxml import etree
from urllib.parse import urljoin
import logging
import logging.config
import requests
import pandas as pd
import re
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time


# In[2]:


BASE_URL = 'http://www.glassdoor.com'
LOGIN_URL = urljoin(BASE_URL, 'profile/login_input.htm')
DELAY = 5


# In[3]:


def enter_company_name(element, company):
    i=0
    while i < 100:
        element.send_keys(Keys.BACK_SPACE)
        i = i+1
    element.send_keys(company)
    element.submit()
    
   


# In[4]:


def gd_login(driver, login_url, email, pwd):

    driver.get(login_url)
    email_field = driver.find_element_by_xpath(
        "//*[@type='submit']//preceding::input[2]"
    )
    email_field.send_keys(email)
    pwd_field = driver.find_element_by_xpath(
        "//*[@type='submit']//preceding::input[1]"
    )
    pwd_field.send_keys(pwd)
    pwd_field.submit()
    #time.sleep(3)


# In[5]:


# Launch driver
chrome_options = webdriver.chrome.options.Options()

# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.maximize_window()

email = 'example@gmail.com'  #Replace username and password with your Glassdoor username and password
pwd = 'examplepassword'

# Log into account
gd_login(driver, LOGIN_URL, email, pwd)

#Read excel file
excel_df = pd.read_excel('Fortune 500 2020 firms.xlsx')

companies = excel_df['Company Name'].tolist()

i=1

df = pd.DataFrame(columns=['Company Name', 'Website', 'Size', 'Type', 'Revenue', 'Headquarters',
                           'Founded', 'Industry', 'CEO name', 'Summary', 'Mission', 'Overall', 'Cultures & Values','Diversity & Inclusion',
                           'Work/Life Balance', 'Senior Management', 'Compensation and Benefits',
                           'Career Opportunities', 'Recommend to a friend', 'CEO Approval', 'Interview experience (positive %)',
                           'Interview experience (neutral %)',  'Interview experience (negative %)', 'Getting interview (Applied online)',
                           'Getting interview(refferal)', 'Getting interview(In-person)', 'Interview Difficulty', 'Benefits'
                            ])

need_to_refresh = 0
for company in companies:
    #input the company name in Company input box and click on search icon
    print("\n%s )next itr company %s" %(i, company))
    
    ceo = ""
    company_name =""
    website = ""
    size = ""
    company_type = ""
    pstve_intrvw_exp=""
    ngtv_intrvw_exp="" 
    neutral_intrvw_exp =""
    applied_online=""
    employee_referal=""
    in_person=""
    difficulty=""
    benefits =""
    mission =""
    other =""
    cultures = ""
    diversity = ""
    overall_rating = ""
    work_life_bal = ""
    senior_mgmt = ""
    compnsatin_benefits =""
    career_oppurtunities = ""
    recommend_to_frnd = ""
    ceo_approval = ""
    positive_business_outlook = ""
    benefits = ""
    summary = ""
    element = ""
    ceo_ratings = ""
    try:
        company_input = WebDriverWait(driver, DELAY).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@id='KeywordSearch']"))
        )
        driver.find_element_by_xpath("/html[1]/body[1]/header[1]/nav[1]/div[1]/div[1]/div[1]/div[4]/div[2]/form[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]").clear()
        company_input.clear()
    except TimeoutException:
        company_input = WebDriverWait(driver, DELAY).until(
                    EC.visibility_of_element_located((By.XPATH, "//input[@id='sc.keyword']"))
                )
        company_input.clear()
    finally:
        if company_input:
            enter_company_name(company_input, company)
        else:
            driver.quit()

    #Wait a bit for the search results to load
    time.sleep(5)

    #From given list of companies from Search, click on first company
    try:
        element = driver.find_element_by_xpath("/html[1]/body[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/a[1]")
        print("found search results for the company %s" %(company))
    except (NoSuchElementException, TimeoutException) as e :
        logger.error(f'Not able to find comapny %s in search results' %(company))
        values_to_add = {'Company Name': company}
    
        row_to_add = pd.Series(values_to_add, name=i)

        df = df.append(row_to_add)
        
        i = i+1
        
        need_to_refresh = need_to_refresh + 1
        
        if(need_to_refresh == 2):
            driver.refresh()
            
        time.sleep(3)
        continue
        
    driver.execute_script("arguments[0].scrollIntoView();", element)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "/html[1]/body[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/a[1]"))).click()
    
    # Scraping the necessary fields
    
    try:
        company_name = driver.find_element_by_xpath('//*[@id="DivisionsDropdownComponent"]').text  
    except NoSuchElementException:
        pass 

    try:
        website = driver.find_element_by_xpath('//*[@id="EIOverviewContainer"]/div/div[1]/ul/li[1]/a').text  
    except NoSuchElementException:
        pass
    
    try:
        size = driver.find_element_by_xpath('//*[@id="EIOverviewContainer"]/div/div[1]/ul/li[3]/div').text 
    except NoSuchElementException:
        pass
    
    try:
        company_type = driver.find_element_by_xpath('//*[@id="EIOverviewContainer"]/div/div[1]/ul/li[5]/div').text
    except NoSuchElementException:
        pass
    
    try:
        revenue = driver.find_element_by_xpath('//*[@id="EIOverviewContainer"]/div/div[1]/ul/li[7]/div').text
    except NoSuchElementException:
        pass 
    
    try:
        hq = driver.find_element_by_xpath('//*[@id="EIOverviewContainer"]/div/div[1]/ul/li[2]/div').text
    except NoSuchElementException:
        pass
     
    try:
        founded = driver.find_element_by_xpath('//*[@id="EIOverviewContainer"]/div/div[1]/ul/li[4]/div').text
    except NoSuchElementException:
        pass
    
    try:
        industry = driver.find_element_by_xpath('//*[@id="EIOverviewContainer"]/div/div[1]/ul/li[6]/div').text
    except NoSuchElementException:
        pass   
       
    try:
        mission_ele = driver.find_element_by_xpath('//*[@id="EIOverviewContainer"]/div/div[1]/div[1]/span/button')
        
        if(mission_ele.is_displayed):
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="EIOverviewContainer"]/div/div[1]/div[1]/span/button'))).click()
        mission = driver.find_element_by_xpath('//*[@id="EIOverviewContainer"]/div/div[1]/div[1]/span').text
    except (NoSuchElementException, TimeoutException) as e:
        pass    
    
    #Interview mode 
    try:
        applied_online = driver.find_element_by_xpath("//div[@class='d-flex pb-sm c0 css-3uwbvr ee3ubnb1']//span[@class='ml-auto']").text
    except NoSuchElementException:
        pass 
    
    try:
        employee_referal = driver.find_element_by_xpath("//div[@class='d-flex pb-sm c2 css-3uwbvr ee3ubnb1']//span[@class='ml-auto']").text
    except NoSuchElementException:
        pass    
     
    try:
        in_person = driver.find_element_by_xpath("//div[@class='d-flex pb-sm c1 css-3uwbvr ee3ubnb1']//span[@class='ml-auto']").text
    except NoSuchElementException:
        pass     
    
    try:
        ceo_div = driver.find_element_by_xpath("//div[@class='d-lg-table-cell ceoName pt-sm pt-lg-0 px-lg-sm css-dwl48b css-1cnqmgc']").text
        ceo_ratings = driver.find_element_by_xpath("//div[@class='d-lg-table-cell ceoName pt-sm pt-lg-0 px-lg-sm css-dwl48b css-1cnqmgc']//div[@class='numCeoRatings css-mi55ob']").text
        ceo = ceo_div.replace(ceo_ratings,'')
    except NoSuchElementException as e:
        pass    
    except Exception:
        pass
    
    try:
        difficulty = driver.find_element_by_xpath("//div[@class='d-flex']//div[@class='align-self-center']//div[@class='css-155sv15 e1webdg50']").text
    except NoSuchElementException:
        pass 
    
    try:
        pstve_intrvw_exp = driver.find_element_by_xpath("//div[@class='d-flex pb-sm c0 css-3uwbvr ee3ubnb1']//span[@class='ml-auto']").text
    except NoSuchElementException:
        pass     
     
    try:    
        ngtv_intrvw_exp = driver.find_element_by_xpath("//div[@class='d-flex pb-sm c1 css-3uwbvr ee3ubnb1']//span[@class='ml-auto']").text
    except NoSuchElementException:
        pass
        
    try:    
        neutral_intrvw_exp = driver.find_element_by_xpath("//div[@class='d-flex pb-sm c2 css-3uwbvr ee3ubnb1']//span[@class='ml-auto']").text
    except NoSuchElementException:
        pass
    
    try:
    #Click on the svg down arrow(v) to open the pop up
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='css-aztz7y eky1qiu1']//span[@class='SVGInline']//*[local-name()='svg']"))).click()
    except (NoSuchElementException, TimeoutException) as e:
        pass

    #Wait for few seconds for the pop up to open
    time.sleep(3)

    #Scrape all the fields present in the pop up
    try: 
        overall_rating = driver.find_element_by_xpath("//div[@class='row d-flex align-items-center m-0']//div[@class='col-2 p-0 ratingTrends__RatingTrendsStyle__ratingNum ratingTrends__RatingTrendsStyle__ratingText']//span[@class='ratingTrends__RatingTrendsStyle__overallRatingNum']").text
    except NoSuchElementException:
        pass
     
    try:
        cultures = driver.find_element_by_xpath("(//div[@class='row m-0']//div[@class='col-2 p-0 ratingTrends__RatingTrendsStyle__ratingNum ratingTrends__RatingTrendsStyle__ratingText '])[1]").text
    except NoSuchElementException:
        pass
    
    try:
        diversity = driver.find_element_by_xpath("(//div[@class='row m-0']//div[@class='col-2 p-0 ratingTrends__RatingTrendsStyle__ratingNum ratingTrends__RatingTrendsStyle__ratingText '])[2]").text
    except NoSuchElementException:
        pass
    
    try:
        work_life_bal = driver.find_element_by_xpath("(//div[@class='row m-0']//div[@class='col-2 p-0 ratingTrends__RatingTrendsStyle__ratingNum ratingTrends__RatingTrendsStyle__ratingText'])[1]").text
    except NoSuchElementException:
        pass
        
    try:   
        senior_mgmt = driver.find_element_by_xpath("(//div[@class='row m-0']//div[@class='col-2 p-0 ratingTrends__RatingTrendsStyle__ratingNum ratingTrends__RatingTrendsStyle__ratingText'])[2]").text
    except NoSuchElementException:
        pass
    
    try:
        compnsatin_benefits = driver.find_element_by_xpath("(//div[@class='row m-0']//div[@class='col-2 p-0 ratingTrends__RatingTrendsStyle__ratingNum ratingTrends__RatingTrendsStyle__ratingText'])[3]").text
    except NoSuchElementException:
        pass
    
    try:
        career_oppurtunities = driver.find_element_by_xpath("(//div[@class='row m-0']//div[@class='col-2 p-0 ratingTrends__RatingTrendsStyle__ratingNum ratingTrends__RatingTrendsStyle__ratingText'])[4]").text
    except NoSuchElementException:
        pass
    
    
    try:
        donut_class = driver.find_elements_by_class_name("donut__DonutStyle__donutchart_text")
        recommend_to_frnd = donut_class[0].text
        ceo_approval = donut_class[1].text
        positive_business_outlook =  donut_class[2].text
       
    except (NoSuchElementException, IndexError) as e:
        print("IndexError/NoSuchElementException caught while trying to scrape either recommend to friend, ceo approval or positive business outlook")
        logger.info(f'IndexError/NoSuchElementException caught while trying to scrape either recommend to friend, ceo approval or positive business outlook')
        pass
    except Exception as e:
        print("Exception caught while trying to scrape either recommend to friend, ceo approval or positive business outlook")
        logger.info(f'Exception caught while trying to scrape either recommend to friend, ceo approval or positive business outlook')
        pass
     
    try:    
        #click on 'x' to close the popup window
        time.sleep(3)
        driver.find_element_by_xpath("//span[@alt='Close']//*[local-name()='svg']//*[name()='path' and contains(@d,'M13.34 12l')]").click()

    except (NoSuchElementException, TimeoutException) as e:
        pass
    
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="EIProductHeaders"]/div/a[5]'))).click()
    except (NoSuchElementException, TimeoutException) as e:
        pass
    
    try:
        benefits = driver.find_element_by_xpath('//*[@id="NodeReplace"]/div/div[1]/div[2]/div/div[1]/strong').text
    except NoSuchElementException:
        pass
    
    try:
        summary = driver.find_element_by_xpath('//div[@class="col px-xsm"]').text
    except NoSuchElementException:
        pass
    
    print("company name %s" %(company_name))
    print("ceo ratings %s" %(ceo_ratings))
    print("difficulty = %s" %(difficulty))
    print("ceo = %s" %(ceo))
    print("pstve_intrvw_exp = %s" %(pstve_intrvw_exp))
    print("ngtv_intrvw_exp = %s" %(ngtv_intrvw_exp))
    print("neutral_intrvw_exp = %s" %(neutral_intrvw_exp))
    print("type = %s" %(company_type))
    print("Revenue = %s" %(hq))
    print("Founded = %s" %(founded))
    print("Industry = %s" %(industry))
    print("Mission = %s" %(mission))
    print("applied online %s" %(applied_online))
    print("employee_referal %s" %(employee_referal))
    print("in_person %s" %(in_person))
    print("Overall rating = %s" %(overall_rating))
    print("Cultures&values = %s" %(cultures))
    print("diversity = %s" %(diversity))                                           
    print("work_life_bal %s" %(work_life_bal))
    print("senior_mgmt %s" %(senior_mgmt))
    print("compnsatin_benefits %s" %(compnsatin_benefits))
    print("career_oppurtunities %s" %(career_oppurtunities))
    print("recommend to frnd %s" %(recommend_to_frnd))
    print("ceo approval %s" %(ceo_approval))
    print("Positive business outlook %s" %(positive_business_outlook))  
    print("Benefits %s" %(benefits))
    print("Summary %s" %(summary))
    
    writer = pd.ExcelWriter('scraped_companies.xlsx', engine='openpyxl') 
    wb = writer.book
    
    
    values_to_add = {'Company Name': company , 'Website': website, 'Size': size, 'Type':company_type, 'Revenue': revenue,
                     'Headquarters': hq, 'Founded': founded, 'Industry': industry, 'CEO name': ceo, 'Summary': summary, 'Mission': mission,
                     'Overall': overall_rating, 'Cultures & Values' : cultures, 'Diversity & Inclusion': diversity,
                     'Work/Life Balance': work_life_bal, 'Senior Management': senior_mgmt, 'Compensation and Benefits': compnsatin_benefits,
                     'Career Opportunities': career_oppurtunities, 'Recommend to a friend': recommend_to_frnd, 'CEO Approval': ceo_approval,
                     'Interview experience (positive %)': pstve_intrvw_exp, 'Interview experience (neutral %)': neutral_intrvw_exp,
                     'Interview experience (negative %)': ngtv_intrvw_exp, 'Getting interview (Applied online)': applied_online,
                     'Getting interview(refferal)': employee_referal, 'Getting interview(In-person)': in_person, 
                     'Interview Difficulty': difficulty, 'Benefits': benefits}
    
    row_to_add = pd.Series(values_to_add, name=i)

    df = df.append(row_to_add)
    
    i = i+1
    if(i==3):
        break

#driver.close()
df.to_excel(writer, index=True)
wb.save('Fortune 500 output.xlsx')


# In[ ]:





# In[ ]:




