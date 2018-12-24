import urllib2
import xml.etree.ElementTree as ET
import time

#################################################

username = "YourUsernameHere"
retry_time = 30

#################################################
#################################################

def print_map(label, map):
	print(label)
	for key, value in map.items():
		print("\n\t"+key+": " + len(value))
		for game in value:
			print("\t\t" + game + "\t" + key)
	print("\n\n")

def resolve_redirects(url):
	try:
		return urllib2.urlopen(url)
	except urllib2.HTTPError, e:
		if e.code == 429:
			time.sleep(retry_time);
		return resolve_redirects(url)
	raise

def get_request(url):
	fp = resolve_redirects(url)
	mystr = fp.read()
	fp.close()	
	return mystr

def init_list(ref, index):
	if index not in ref:
		ref[index] = []
	return ref

#################################################
#################################################

mystr = get_request("https://www.boardgamegeek.com/xmlapi2/collection?own=1&excludesubtype=boardgameexpansion&username=" + username)
gamesXML = ET.fromstring(mystr).findall('item')

gameData = {}
categoryData = {}
mechanicData = {}
combinedData = {}

for elem in gamesXML:
	id = elem.attrib['objectid']
	gameData[id] = {}
	gameData[id]['name'] = elem.findall('name')[0].text
	gameData[id]['image'] = elem.findall('image')[0].text

	dom = ET.fromstring(get_request("https://www.boardgamegeek.com/xmlapi2/thing?id=" + id))
	gameXML = dom.findall('item')[0]

	gameData[id]['description'] = gameXML.findall('description')[0].text

	gameLinks = gameXML.findall('link')

	gameData[id]['mechanics'] = {}
	gameData[id]['categories'] = {}

	for gameLink in gameLinks:
		type = gameLink.attrib['type']
		specificCollection = None
		subtype = None
		if type == "boardgamemechanic":
			subtype = 'mechanics'
			specificCollection = mechanicData

		elif type == "boardgamecategory":
			subtype = 'categories'
			specificCollection = categoryData

		if subtype is not None:
			gameData[id][subtype][gameLink.attrib['id']] = gameLink.attrib['value']

			init_list(specificCollection, gameLink.attrib['value'])
			specificCollection[gameLink.attrib['value']].append(gameData[id]['name'])

			init_list(combinedData, gameLink.attrib['value'])
			combinedData[gameLink.attrib['value']].append(gameData[id]['name'])

print_map("Category", categoryData)
print_map("Mechanic", mechanicData)
print_map("Combined", combinedData)