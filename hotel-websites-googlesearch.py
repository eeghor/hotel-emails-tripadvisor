from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import sys
from unidecode import unidecode
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains

DATA_DIR = "C:/Users/igork/Data/"

# read the hotel file
hotels = pd.read_csv(DATA_DIR + "hotels/australian_hotels.csv", sep="\t", dtype=str)
hotels_nowebsite = hotels.loc[hotels.website.isnull()]
print("hotels without web sites: {}".format(len(hotels_nowebsite)))

# page where they have the full list of name types by letter, gender or usage
BASE_URL = "https://www.google.com.au"

# full path to the webdriver to use; use webdriver.PhantomJS() for invisible browsing
driver = webdriver.Chrome('webdriver/chromedriver')

ws_list = []

for i, row in enumerate(hotels_nowebsite.itertuples()):
	
	if (i+1)%10 == 0:
		print("processed {}/{} hotels".format(i+1, len(hotels_nowebsite)))
	
	try:
		search_str = " ".join([row.name, row.address])
	except:
		ws_list.append(None)
		continue

	driver.get(BASE_URL)
	
	# find the search box, enter hotel name and address and click search
	sb = driver.find_element_by_id("lst-ib")
	sb.clear()
	sb.send_keys(search_str)
	driver.find_element_by_xpath("//input[@type='submit']").click()
	time.sleep(2)
	
	# try to find the infobox
	try:
		infobox = driver.find_element_by_id("rhs_block") # this is div
	except:
		print("cannot see any infobox..")
		print("moving on to next hotel...")
		ws_list.append(None)
		continue
	
	try:
		infobox.find_element_by_class_name("ab_button").click()
	except:
		ws_list.append(None)
		continue
	
	time.sleep(2)
	website = driver.current_url
	ws_list.append(website)
	driver.execute_script("window.history.go(-1)")
	time.sleep(1)

# done. now just add collected websites to data frame
hotels.loc[hotels.website.isnull(), "website"] = ws_list
hotels.to_csv("hotesl_updared.csv", sep="\t", index=False)