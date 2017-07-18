import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import sys
import pandas as pd
from collections import namedtuple

list_places = ["alice springs"]
# full path to the webdriver to use; use webdriver.PhantomJS() for invisible browsing
#driver = webdriver.Chrome('/Users/ik/Codes/hotel-emails-tripadvisor/webdriver/chromedriver')
driver = webdriver.PhantomJS('/Users/ik/Codes/hotel-emails-tripadvisor/webdriver/phantomjs')
# default waiting time
WAIT_TIME = 30
# base URL
BASE_REVIEW_URL = "http://tripadvisor.com.au/"
# page to go to first
start_page  = "https://www.tripadvisor.com.au/Hotels"

Hotel = namedtuple('Hotel', ["tradv_id", "name", "address", "website", "email"])

# create a hotel url list for the hotels on this page
hotel_ids = []

def _how_many_pages_on_pagination_bar():
	"""
	locate the pagination bar at the bottom of the current page and find how many pages are there
	"""
	all_possible_bar_divs = driver.find_elements_by_xpath("//div[contains(@class,'unified') and contains(@class, 'standard_pagination')]")
	max_page = None

	if all_possible_bar_divs:
		for located_div in all_possible_bar_divs:
			try:
				max_page = int(located_div.get_attribute("data-numpages"))
				break  # no need to keep looking
			except:
				continue
		if max_page:
			return max_page
		else:
			print("[ERROR]: can't find max page on the pagination bar at the bottom...")
			sys.exit(0)
	else:
		print("[ERROR]: can't locate the pagination bar at the bottom...")
		sys.exit(0)

def _get_address():
	"""
	find and get a hotel address on the current page
	"""

	hotel_address = []

	try:
		span_address = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "street-address")))
		hotel_address.append(span_address.text.lower().strip())
	except:
		pass
		#print("[WARNING]: cannot find street address for {}..".format(hname_lst[i]))
	try:
		span_locality = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "locality")))
		hotel_address.append(span_locality.text.lower().strip())
	except:
		pass
		#print("[WARNING]: cannot find localty for {}..".format(hname_lst[i]))
	#print(hotel_address[-1])

	try:
		span_country = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "country-name")))
		hotel_address.append(span_country.text.lower().strip())
	except:
		pass
		#print("[WARNING]: cannot find country for {}..".format(hname_lst[i]))

	return " ".join(hotel_address) if hotel_address else None

def _get_website():
	"""
	in case there's a link to a hotel's website, collect it
	"""
		# see if there's a link to the hotel's website; if there is, click
	try:
		WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "website"))).click()
		# the website is supposed to start loading in a new window
		driver.switch_to_window(driver.window_handles[-1])
		website = driver.current_url.split("//")[1].split("/")[0].lower().strip()
		driver.close()
		driver.switch_to_window(driver.window_handles[-1])
		return website
	except:
		return None

def _get_email():

	# check if there's an option to email the hotel
	try:
		email_hotel_option = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "email")))
	except:
		print("[WARNING]: can't find the email hotel option...")
		driver.close()
		driver.switch_to_window(driver.window_handles[0])
		return None

	try:
		email_hotel_option.click()
		time.sleep(3)
	except:
		print("[ERROR]: cannot click on the email option...")
		sys.exit(0)

	try:
		alert = driver.switch_to.alert
	except:
		print("[ERROR]: cannot switch to alert!")
		sys.exit(0)

	# if got here, the switch to alert went well
	inps = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.ID, 'receiver')))
	if not inps:
		print("[ERROR]: cannot find any suitable inputs!")
		return None
	else:
		for inp in inps:
			try:
				hotel_email = inp.get_attribute("value").lower().strip()
				driver.close()
				driver.switch_to.window(driver.window_handles[-1])
				return hotel_email
			except:
				print("[ERROR]: cannot pick the value of email input!")
				sys.exit(0)

for place in list_places:

	print("collecting {} hotels..".format(place))

	prop_list_per_place = []

	print("going to start page ", start_page)
	driver.get(start_page)  # the Hotels page
	time.sleep(6)
	text_field = WebDriverWait(driver,WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "typeahead_input")))
	text_field.clear()
	text_field.send_keys(place)
	# find the input and type in the place names
	# driver.find_element_by_class_name("typeahead_input").clear().send_keys(place)
	# find the find hotels button
	WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.CLASS_NAME, "submit_text"))).click()
	#driver.find_element_by_class_name("submit_text").click()
	time.sleep(5)
	# pagination bar at the bottom of the page
	try:
		pagination_bar = WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.CLASS_NAME, "pageNumbers")))
		driver.switch_to_window(driver.window_handles[0])

		max_page = _how_many_pages_on_pagination_bar()

		print("[pagination bar]: available pages to visit: {}".format(max_page))
	except:
		print("no pagination bar, there's only one page")
		max_page = 1

	# start visiting pages

	for page in range(1, max_page + 1):

		print("page {}".format(page))

		prop_names_on_page = []
		prop_urls_on_page = []

		# first simply find that button
		# pagination bar at the bottom of the page
		
		if max_page > 1:
			pagination_bar = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "pageNumbers")))
	
			try:
				page_button = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH,
					"//span[@data-page-number='" + str(page) + "']")))
			except:
				try:
					page_button = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH,
					"//a[@data-page-number='" + str(page) + "']")))
				except:
					print("[ERROR]: unable to find page {} button on the pagination bar!".format(page))
					sys.exit(0)
	
			#  if got to here, the button has been found; but it is clickable?
			time.sleep(3)
			try:
				page_button.click()
			except:
				# give a warning but assume that it's because we are already on the page we need
				print("[WARNING]: page button on the pagination bar is not clickable...")
	
			time.sleep(3)
	
			driver.switch_to_window(driver.window_handles[0])
			time.sleep(10)

		prop_ids_on_page = list(set([e.get_attribute("id") for e in driver.find_elements_by_xpath("//a[contains(@id, 'property_')]")]))
		print("new hotels on this page: {}/{}".format(len(set(prop_ids_on_page) - set(hotel_ids)), len(set(prop_ids_on_page))))

		for i in prop_ids_on_page:

			if i in hotel_ids:
				print("id {} already collected".format(i))
				continue
			else:
				hotel_ids.append(i)

			try:
				prop_names_on_page.append(WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.ID, i))).text.lower().strip())
			except:
				prop_names_on_page.append(WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.ID, i))).text.lower().strip())

			try:
				prop_urls_on_page.append(WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.ID, i))).get_attribute("href"))
			except:
				prop_urls_on_page.append(WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.ID, i))).get_attribute("href"))

		assert len(prop_urls_on_page) == len(prop_names_on_page), (
			"[ERROR]: number of urls {} doesn\'t match number of names {} on this page"
			.format(len(prop_urls_on_page), len(prop_names_on_page)))

		if prop_urls_on_page:
			for i, url in enumerate(prop_urls_on_page):

				this_hotel = Hotel(tradv_id = prop_ids_on_page[i],  name=prop_names_on_page[i], address=None, website=None, email=None)
				driver.execute_script("window.open('');")  # javascript because of some issues w Chrome - command + t may not work
				driver.switch_to.window(driver.window_handles[-1])
				driver.get(url)
				time.sleep(3)
				#  a d d r e s s
				this_hotel = this_hotel._replace(address=_get_address())
				# w e b s i t e
				this_hotel = this_hotel._replace(website=_get_website())
				# e m a i l
				this_hotel = this_hotel._replace(email=_get_email())
				print(this_hotel)
				prop_list_per_place.append(this_hotel)
		else:
			continue

	print("collected {} hotels in {}...".format(len(prop_list_per_place), place.lower()))
	with open("hotels_" + place.lower() + ".txt", "w") as f:
		for n in prop_list_per_place:
			f.write("{}\n".format(n))

driver.quit()