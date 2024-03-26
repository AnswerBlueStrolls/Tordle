import requests
from bs4 import BeautifulSoup
import argparse
import time
import os
import csv
import sys
from unidecode import unidecode
import logging

# seconds to wait between page requests
delay = 5
header = 'Chrome/52 (Macintosh; Intel Mac OS X 10_10_5); Jingyi Li/UC Berkeley/email@address.com'
def get_tag_info(category, meta):
	'''
	given a category and a 'work meta group, returns a list of tags (eg, 'rating' -> 'explicit')
	'''
	try:
		tag_list = meta.find("dd", class_=str(category) + ' tags').find_all(class_="tag")
	except AttributeError as e:
		return []
	return [unidecode(result.text) for result in tag_list] 
	
def get_stats(meta):
	'''
	returns a list of  
	language, published, status, date status, words, chapters, comments, kudos, bookmarks, hits
	'''
	categories = ['language', 'published', 'status', 'words', 'chapters', 'comments', 'kudos', 'bookmarks', 'hits'] 

	stats = list(map(lambda category: meta.find("dd", class_=category), categories))

	if not stats[2]:
		stats[2] = stats[1] #no explicit completed field -- one shot
	try:		
		stats = [unidecode(stat.text) for stat in stats]
	except AttributeError as e: #for some reason, AO3 sometimes miss stat tags (like hits)
		new_stats = []
		for stat in stats:
			if stat: new_stats.append(unidecode(stat.text))
			else: new_stats.append('null')
		stats = new_stats

	stats[0] = stats[0].rstrip().lstrip() #language has weird whitespace characters
	#add a custom completed/updated field
	status  = meta.find("dt", class_="status")
	if not status: status = 'Completed' 
	else: status = status.text.strip(':')
	stats.insert(2, status)

	return stats      

def get_tags(meta):
	'''
	returns a list of lists, of
	rating, category, fandom, pairing, characters, additional_tags
	'''
	tags = ['rating', 'category', 'fandom', 'relationship', 'character', 'freeform']
	return list(map(lambda tag: get_tag_info(tag, meta), tags))

# get kudos
def get_kudos(meta):
	if (meta):
		users = []
		## hunt for kudos' contents
		kudos = meta.contents

		# extract user names
		for kudo in kudos:
			if kudo.name == 'a':
				if 'more users' not in kudo.contents[0] and '(collapse)' not in kudo.contents[0]:
					users.append(kudo.contents[0])
		
		return users
	return []

# get author(s)
def get_authors(meta):
	tags = meta.contents
	authors = []

	for tag in tags:
		if tag.name == 'a':
			authors.append(tag.contents[0])

	return authors

# get bookmarks by page
def get_bookmarks(url, header_info):
	bookmarks = []
	headers = {'user-agent' : header_info}

	req = requests.get(url, headers=headers)
	src = req.text

	time.sleep(delay)
	soup = BeautifulSoup(src, 'html.parser')

	sys.stdout.write('scraping bookmarks ')
	sys.stdout.flush()

	# find all pages
	if (soup.find('ol', class_='pagination actions')):
		pages = soup.find('ol', class_='pagination actions').findChildren("li" , recursive=False)
		max_pages = int(pages[-2].contents[0].contents[0])
		count = 1

		sys.stdout.write('(' + str(max_pages) + ' pages)')
		sys.stdout.flush()

		while count <= max_pages:
			# extract each bookmark per user
			tags = soup.findAll('h5', class_='byline heading')
			bookmarks += get_users(tags)

			# next page
			count+=1
			req = requests.get(url+'?page='+str(count), headers=headers)
			src = req.text
			soup = BeautifulSoup(src, 'html.parser')
			sys.stdout.write('.')
			sys.stdout.flush()
			time.sleep(delay)
	else:
		tags = soup.findAll('h5', class_='byline heading')
		bookmarks += get_users(tags)

	print('')
	return bookmarks

# get users form bookmarks	
def get_users (meta):
	users = []
	for tag in meta:
			user = tag.findChildren("a" , recursive=False)[0].contents[0]
			users.append(user)

	return users
	
def access_denied(soup):
	if (soup.find(class_="flash error")):
		return True
	if (not soup.find(class_="work meta group")):
		return True
	return False

def get_fic_from_ao3(fic_id, output, lang="English"):
	'''
	fic_id is the AO3 ID of a fic, found every URL /works/[id].
	writer is a csv writer object
	the output of this program is a row in the CSV file containing all metadata
	and the fic content itself (excludes content if metadata_only=True).
	header_info should be the header info to encourage ethical scraping.
	'''
	print('Loading ', fic_id)
	url = 'http://archiveofourown.org/works/'+str(fic_id)+'?view_adult=true' + '&amp;view_full_work=true'
	writer = csv.writer(output)
	headers = {'user-agent' : header}
	status = 429
	while 429 == status:
		req = requests.get(url, headers=headers)
		status = req.status_code
		if 429 == status:
			error_row = [fic_id] + ["Status: 429"]
			logging.error(error_row)
			print("Request answered with Status-Code 429")
			print("Trying again in 1 minute...")
			time.sleep(60)

	if 400 <= status:
		print("Error scraping ", fic_id, "Status ", str(status))
		error_row = [fic_id] + [status]
		logging.error(error_row)
		return 0

	src = req.text
	soup = BeautifulSoup(src, 'html.parser')
	if (access_denied(soup)):
		print('Access Denied')
		error_row = [fic_id] + ['Access Denied']
		logging.error(error_row)
	else:
		meta = soup.find("dl", class_="work meta group")
		author = get_authors(soup.find("h3", class_="byline heading"))
		tags = get_tags(meta)
		stats = get_stats(meta)
		title = unidecode(soup.find("h2", class_="title heading").string).strip()
		visible_kudos = get_kudos(soup.find('p', class_='kudos'))
		hidden_kudos = get_kudos(soup.find('span', class_='kudos_expanded hidden'))
		all_kudos = visible_kudos + hidden_kudos

		if lang != stats[0]:
			print('Fic is not in ' + lang + ', skipping...')
			return 0
		else:
			all_bookmarks = []
			#get the fic itself
			content = soup.find("div", id= "chapters")
			chapters = content.select('p')
			chaptertext = '\n\n'.join([chapter.text for chapter in chapters])
			
			row = [fic_id] + [title] + [author] + list(map(lambda x: ', '.join(x), tags)) + stats + [all_kudos] + [all_bookmarks] + [chaptertext]
			try:
				writer.writerow(row)
				print('Done.')
				return len(row)
			except:
				print('Unexpected error: ', sys.exc_info()[0])
				error_row = [fic_id] +  [sys.exc_info()[0]]
				logging.error(error_row)
	return 0
