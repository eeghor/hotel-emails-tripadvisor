import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select  # to deal with dropdown menues
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import re
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from collections import defaultdict, namedtuple
from datetime import datetime, date # need to convert timezone

WAIT_TIME = 40
BASE_REVIEW_URL = "http://tripadvisor.com.au/"
#driver = webdriver.PhantomJS()
driver = webdriver.Chrome('/Users/ik/Codes/hotel-emails-tripadvisor/webdriver/chromedriver')

RNK_PAGE_CNT = 1

wtapl = []

start_page  = "https://www.tripadvisor.com.au/Best-Hotels-Sydney.html"
driver.get(start_page)

Hotel = namedtuple("Hotel", "name address website email")

hotel_name_lst = []
hotel_url_lst = []

pagination_bar = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "pageNumbers")))

try:
	pagination_bar.find_element_by_xpath("span[@data-page-number='1']").click()
	print("clicked")
except:
	print("1 not clickable, so we are on page 1 already")
	# find hotel list placement
	# div_hotels_cell = driver.find_element_by_xpath("//div[@class='hotels_list_placement']")
	for a in driver.find_elements_by_xpath(".//a[@class='property_title']"):
		print(a.text)
		hotel_url_lst.append(a.get_attribute("href"))
		hotel_name_lst.append(a.text)
		time.sleep(1)

for i, url in enumerate(hotel_url_lst):
	
	if hotel_name_lst[i] == "Ovolo 1888 Darling Harbour":
		print("hotel: ", hotel_name_lst[i])
	
		driver.get(url)
		hotel_main_window = driver.current_window_handle
	
		hotel_address = []
	
		try:
			span_address = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "street-address")))
			hotel_address.append(span_address.text)
		except:
			print("cannot find street address..")
		try:
			span_locality = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "locality")))
			hotel_address.append(span_locality.text)
		except:
			print("cannot find localty..")
		try:
			span_country = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "country-name")))
			hotel_address.append(span_country.text)
		except:
			print("cannot find country..")
	
		print("address: ", " ".join(hotel_address))
	
		# see if there's a list to the hotel's website
		try:
			WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "website"))).click()
			for h in driver.window_handles:
				if h != hotel_main_window:
					driver.switch_to_window(h)
					hotel_website = driver.current_url.split("//")[1].split("/")[0]
					driver.close()
					driver.switch_to_window(hotel_main_window)
	
		except:
			hotel_website = None
	
		print("web site: ", hotel_website)
	
		# now check if there's an option to email the hotel
		try:
			WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "email"))).click()
			print("clicked send email")
			for h in driver.window_handles:
				if h != hotel_main_window:
					driver.switch_to_window(h)
					# look for a imput that has id receiver
					inp = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.ID, "receiver")))
					hotel_email = inp.text
					print("found input!")
					driver.close()
					driver.switch_to_window(hotel_main_window)
		except:
			hotel_email = None
	
		print("email: ", hotel_email)
	
		# for handle in driver.window_handles:
		# 	if handle != original_window_handla:
	# 		driver.switch_to_window(handle)
	# 		print("now at ", driver.current_url)
	
	# driver.switch_to_window(original_window_handla)
	
	# try:
	# 	click_span_email = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "email")))
	# 	print("email=", click_span_email.text)
	# 	click_span_email.click()
	
	# 	for handle in driver.window_handles:
	# 		if handle != original_window_handla:
	# 			driver.switch_to_window(handle)
	# 			div_email = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.NAME, "receiver")))
	# 			print("email addr=", div_email.text)
	# except:
	# 	pass




# for n, a in enumerate(driver.find_elements_by_xpath("//a[@class='property_title']")):
# 	try:
# 		gota = a.get_attribute("href")
# 		hotel_url_lst.append(gota)
# 		hotel_name_lst.append(a.text)
# 	except:
# 		continue
# 	if n == 2:
# 		break

# print(hotel_name_lst)
# print(hotel_url_lst)

# print("going to hotel pages...", hotel_url_lst[-1])
# driver.get(hotel_url_lst[-1])


# # start visiting hotel pages
# for hotel, url in zip(hotel_name_lst, hotel_url_lst):
# 	print("trying url=", url)
# 	driver.get(url)
# 	time.sleep(5)
# 	# 	# find tha email hotel thing
# 	try:
# 		email_hotel = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "E-mail")))
# 		# main_window_handle = driver.current_window_handle
# 		print("email hotel=", email_hotel)
# 		# # main_window_handle = driver.current_window_handle
# 		# email_hotel.click()
# 		# for handle in driver.window_handles:
# 		# 	if handle != main_window_handle:
# 		# 		driver.switch_to.window(handle)
# 		# 		try:
# 		# 			hotel_email = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.ID, "receiver"))).text
# 		# 			print(hotel_email)
# 		# 		except:
# 		# 			print("this hotel has not email")
# 	except:
# 		driver.close()
# 		continue
# 	# driver.close()



# 	# find all rows
# 	rows = ranking_table.find_elements_by_xpath(".//tbody/tr")
	
# 	for row in rows:

# 		# find all cells, i.e. <td>s
# 		clls = row.find_elements_by_xpath(".//td[contains(@class, 'mobile') and contains(@class, 'center')]")

# 		wtapl.append(WTA_Player(crank=clls[0].text.strip(), 
# 			country=clls[1].find_element_by_xpath(".//span[contains(@class, 'hide')]").text.strip().capitalize(),
# 			name=row.find_element_by_xpath(".//td/a[@class='pink']").text.split(",")[1].strip().capitalize(),
# 			surname=row.find_element_by_xpath(".//td/a[@class='pink']").text.split(",")[0].strip().capitalize(),
# 			# on the page, DOBs are listed as, for example, 12 FEB 1992, i.e. %d %b %Y
# 			dob=datetime.strptime(row.find_element_by_xpath(".//td[contains(@class,'hide')]").text.strip(), "%d %b %Y").strftime("%d-%b-%Y")))
	
# 	print("ranks collected so far: {}".format(len(wtapl)))
# 	# go to the next ranking page via the menu
# 	Select(WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".rankings-rank-change")))).select_by_value(str(RNK_PAGE_CNT))

driver.quit()

# end_time = time.time()

# print("done. collected {} ranks.".format(len(wtapl)))
# print("elapsed time: {} min".format(round((end_time - start_time)/60, 1)))

# df = pd.DataFrame(wtapl)

# csv_fl = "wta_ranking_" + date.today().strftime("%d%b%Y") +".csv"

# df.to_csv(csv_fl, index=False, sep="\t")

# print("saved everything in the file called {} in your local directory".format(csv_fl))

