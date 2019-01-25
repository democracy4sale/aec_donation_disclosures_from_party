#!/usr/bin/env python
#Scraper for donations declared by parties with canonical donor names from the AEC


import csv
import mechanize 
import lxml.html
import scraperwiki
import requests
import traceback

 
annDonorsurl = "http://periodicdisclosures.aec.gov.au/AnalysisParty.aspx"
 

periods = [
#{"year":"2011-2012","id":"49"},
#{"year":"2012-2013","id":"51"},
#{"year":"2013-2014","id":"55"},
#{"year":"2014-2015","id":"56"},
#{"year":"2015-2016","id":"60"},
{"year":"2016-2017","id":"64"}
]

# periods = [{"year":"2014-2015","id":"56"}]

partyGroups = [{"entityID":4,"group":"alp"},
{"entityID":52,"group":"alp"},
{"entityID":55,"group":"alp"},
{"entityID":50,"group":"alp"},
{"entityID":64,"group":"alp"},
{"entityID":54,"group":"alp"},
{"entityID":27,"group":"alp"},
{"entityID":51,"group":"alp"},
{"entityID":53,"group":"alp"},
{"entityID":132,"group":"alp"},
{"entityID":32,"group":"greens"},
{"entityID":72,"group":"greens"},
{"entityID":138,"group":"greens"},
{"entityID":1100,"group":"greens"},
{"entityID":98,"group":"greens"},
{"entityID":31,"group":"greens"},
{"entityID":97,"group":"greens"},
{"entityID":205,"group":"greens"},
{"entityID":137,"group":"greens"},
{"entityID":4028,"group":"greens"},
{"entityID":158,"group":"greens"},
{"entityID":153,"group":"greens"},
{"entityID":207,"group":"greens"},
{"entityID":186,"group":"greens"},
{"entityID":27964,"group":"greens"},
{"entityID":6,"group":"liberal"},
{"entityID":40,"group":"liberal"},
{"entityID":46,"group":"liberal"},
{"entityID":35,"group":"liberal"},
{"entityID":44,"group":"liberal"},
{"entityID":36,"group":"liberal"},
{"entityID":43,"group":"liberal"},
{"entityID":41,"group":"liberal"},
{"entityID":211,"group":"liberal"},
{"entityID":19,"group":"nationals"},
{"entityID":37,"group":"nationals"},
{"entityID":39,"group":"nationals"},
{"entityID":38,"group":"nationals"},
{"entityID":49,"group":"nationals"},
{"entityID":42,"group":"nationals"},
{"entityID":24,"group":"liberal"}
]


#Check if scraper has been run before, see where it got up to

if scraperwiki.sqlite.get_var('upto'):
	upto = scraperwiki.sqlite.get_var('upto')
	# print "Scraper upto:",upto,"period:",periods[upto]['year']
else:
	print "Scraper first run"
	upto = 0    

#to run entirely again, just set upto to 0 
upto = 0  

#unique number for every entry
count = 0

#Scrape for time periods taking into account previous runs using 'upto'

for x in xrange(upto, len(periods)):
	br = mechanize.Browser()
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
	response = br.open(annDonorsurl)
	print "Loading data for "+periods[x]['year']
	# for form in br.forms():
	# 	print form

	#print br.forms()    

	#print "All forms:", [ form.name  for form in br.forms() ]
 
	br.select_form(nr=0)

	# print br.form
	# print periods[x]['id']

	
	br['ctl00$dropDownListPeriod']=[periods[x]['id']]
	response = br.submit("ctl00$buttonGo")

	response = br.open(annDonorsurl)
	br.select_form(nr=0)
	#print br.form.controls[10] 
	items = br.form.controls[10].get_items()

	for item in items:
		print item.name
		print "Entity:", item.attrs['label']
		#item.name
		response = br.open(annDonorsurl)
		br.select_form(nr=0)
		br['ctl00$ContentPlaceHolderBody$dropDownListParties']=[item.name]
		response = br.submit("ctl00$ContentPlaceHolderBody$analysisControl$buttonAnalyse")

		#check if donations listed

		html = response.read()
		root = lxml.html.fromstring(html)
		tds = root.cssselect("#ContentPlaceHolderBody_gridViewAnalysis tr td")
		
		if tds[0].text == "There have been no receipts reported":
			print tds[0].text
			continue

		br.select_form(nr=0)
		br['ctl00$ContentPlaceHolderBody$pagingControl$cboPageSize']=["500"]
		response = br.submit("ctl00$ContentPlaceHolderBody$pagingControl$buttonGo")
		html = response.read()
		
		#print html

		root = lxml.html.fromstring(html)
		trs = root.cssselect("#ContentPlaceHolderBody_gridViewAnalysis tr")
		pages = root.cssselect(".pagingLink table td")
		noPages = len(pages)
		page = 1

		uptotrs = 1

		for i in xrange(uptotrs,len(trs)):

			#ignore the trs at the end of the page

			if 'class' not in trs[i].attrib:
				continue
				
			if trs[i].attrib['class'] == 'pagingLink':
				continue

			tds = trs[i].cssselect("td")

			donType = lxml.html.tostring(tds[0]).split('<a href="')[1].split('.aspx?')[0]
			#print donType
			submissionID = lxml.html.tostring(tds[0]).split('SubmissionId=')[1].split('&amp;ClientId=')[0]
			#print submissionID
			clientID = lxml.html.tostring(tds[0]).split('ClientId=')[1].split('">')[0]
			#print clientID
			donName = lxml.html.tostring(tds[0]).split('">')[2].split('</a')[0]
			#print donName
			address = tds[1].text
			#print address
			state = tds[2].text
			#print state
			postcode = tds[3].text
			#print postcode
			receiptType = tds[4].text
			#print receiptType
			value = tds[5].text.replace("$", "").replace(",","")
			#print value
			donUrl = lxml.html.tostring(tds[0]).split('<a href="')[1].split('">')[0]
			#print donUrl 


			fixedUrl = 'http://periodicdisclosures.aec.gov.au/' + donUrl.replace("amp;","")
			html = requests.get(fixedUrl).content
			dom = lxml.html.fromstring(html)
			h2s = dom.cssselect(".rightColfadWideHold h2")
			if donType == "Donor" or donType == "AssociatedEntity":
				cleanName = h2s[0].text.strip()
				#print cleanName.strip()
			if donType == "Party":
				cleanName = h2s[1].text.strip()
				#print cleanName.strip()

			data = {}
			data['donType'] = donType
			data['submissionID'] = submissionID
			data['clientID'] = clientID
			data['donName'] = donName
			data['address'] = address
			data['state'] = state
			data['postcode'] = postcode
			data['receiptType'] = receiptType
			data['value'] = value
			data['donUrl'] = donUrl
			data['rowCount'] = i
			data['page'] = page
			data['entityID'] = item.name
			data['period'] = periods[x]['year']
			data['entityName'] = item.attrs['label']
			data['cleanName'] = cleanName

# 			print data
			
			for groupID in partyGroups:
					if item.name == groupID['entityID']:
						data['partyGroup'] = groupID['group']


			scraperwiki.sqlite.save(unique_keys=["rowCount","page","period","entityID"], data=data)

		#get other pages if present
		
		if noPages > 1:
			print "multiple pages, doing more now"
			for page in xrange(1,noPages):
				print page
				br.select_form(nr=0)
				br.set_all_readonly(False)
				br.find_control("ctl00$buttonGo").disabled = True
				br.find_control("ctl00$ContentPlaceHolderBody$analysisControl$buttonAnalyse").disabled = True
				br.find_control("ctl00$ContentPlaceHolderBody$analysisControl$buttonAnalyse").disabled = True
				br.find_control("ctl00$ContentPlaceHolderBody$analysisControl$buttonExport").disabled = True
				br["__EVENTTARGET"] = 'ctl00$ContentPlaceHolderBody$gridViewAnalysis'
				br["__EVENTARGUMENT"] = 'Page$2'
				response = br.submit()
				html = response.read()
				#print html

				root = lxml.html.fromstring(html)
				trs = root.cssselect("#ContentPlaceHolderBody_gridViewAnalysis tr")
				uptotrs = 1  

				for i in xrange(uptotrs,len(trs)):

					if 'class' not in trs[i].attrib:
						continue
						
					if trs[i].attrib['class'] == 'pagingLink':
						continue

					tds = trs[i].cssselect("td")   
					donType = lxml.html.tostring(tds[0]).split('<a href="')[1].split('.aspx?')[0]
					#print donType
					submissionID = lxml.html.tostring(tds[0]).split('SubmissionId=')[1].split('&amp;ClientId=')[0]
					#print submissionID
					clientID = lxml.html.tostring(tds[0]).split('ClientId=')[1].split('">')[0]
					#print clientID
					donName = lxml.html.tostring(tds[0]).split('">')[2].split('</a')[0]
					#print donName
					address = tds[1].text
					#print address
					state = tds[2].text
					#print state
					postcode = tds[3].text
					#print postcode
					receiptType = tds[4].text
					#print receiptType
					value = tds[5].text.replace("$", "").replace(",","")
					#print value
					donUrl = lxml.html.tostring(tds[0]).split('<a href="')[1].split('">')[0]
					#print donUrl 


					fixedUrl = 'http://periodicdisclosures.aec.gov.au/' + donUrl.replace("amp;","")
					html = requests.get(fixedUrl).content
					dom = lxml.html.fromstring(html)
					h2s = dom.cssselect(".rightColfadWideHold h2")
					if donType == "Donor" or donType == "AssociatedEntity":
						cleanName = h2s[0].text.strip()
						#print cleanName.strip()
					if donType == "Party":
						cleanName = h2s[1].text.strip()
						#print cleanName.strip()


					count += 1
					data = {}
					data['donType'] = donType
					data['submissionID'] = submissionID
					data['clientID'] = clientID
					data['donName'] = donName
					data['address'] = address
					data['state'] = state
					data['postcode'] = postcode
					data['receiptType'] = receiptType
					data['value'] = value
					data['donUrl'] = donUrl
					data['rowCount'] = i
					data['page'] = page+1
					data['entityID'] = item.name
					data['period'] = periods[x]['year']
					data['entityName'] = item.attrs['label']
					data['cleanName'] = cleanName

# 					print data

					for groupID in partyGroups:
						if item.name == groupID['entityID']:
							data['partyGroup'] = groupID['group']
					
					scraperwiki.sqlite.save(unique_keys=["rowCount","page","period","entityID"], data=data)
              

	scraperwiki.sqlite.save_var('upto', x)   
