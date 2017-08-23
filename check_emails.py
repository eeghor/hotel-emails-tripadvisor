"""
basic email validity check
"""

import requests
import sys

email_file = sys.argv[1]
save_file  = "verified_emails.txt"
SAVE_EVERY = 100

emails = [line.strip() for line in open(email_file, "r").readlines() if line.strip()]

print("total email addresses to check: {}".format(len(emails)))

# possible prefixes
pref1 = "http:// https://".split()
pref2 = ["www.", ""]

# temporary lists
email_lst = []
email_status = []

cgood = 0
cbad = 0

for i, email_part in enumerate(emails[5200:]):
	
	email_lst.append(email_part)
	cand_urls = [pr1 + pr2 + email_part for pr1 in pref1 for pr2 in pref2]
	ff = False
	for url in cand_urls:
		try:
			r = requests.get(url, timeout=10)
			# if request returned something
			if r.status_code in [200, 301]:   # 200 = OK, 301 = redirection
				email_status.append("ok")
				ff = True
				cgood += 1
				print(email_part + " is ok (status code {})".format(r.status_code))
				break
			# any other codes the same as bad address
		except:
			# cannot get anything  - just try next candidate
			continue
	
	if not ff:
		email_status.append("bad")
		cbad += 1 
		print(email_part + " is bad")

	if (((i+1)%SAVE_EVERY == 0) and (i>0)) or (i == len(emails) - 1):
		with open(save_file, "a+") as f:
			for z in zip(email_lst, email_status):
				f.write("{}:{}\n".format(*z))

		email_lst = []
		email_status = []

		print("processed {}/{} emails: good {} ({:.1f}%) bad {} ({:.1f}%)".format(i+1, len(emails), 
											cgood, 100*cgood/len(emails), 
											cbad, 100*cbad/len(emails)))