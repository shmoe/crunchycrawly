import crunchyroll_utils as cr
import sqlite3
import os.path
import sys
import asyncio

def parseBookmarks(bookmarks_path):
	"""takes a Firefox places.sqlite file and returns an appropriate tree structure for hasNewContent(...)

	Argument:
	bookmarks_path --- the path to the appropriate places.sqlite file
	"""
	def map_bookmark(bookmark):
		title = None
		season = None
		episode = None

		tokens = bookmark[0].split(" ", 1)
		tokens[0] = tokens[0].replace("*", "").replace("`", "").replace("(","").replace(")","").replace("[","").replace("]","")

		title = tokens[1]
		if tokens[0][0] == "s":
			season = tokens[0][1:]
		else:
			episode = tokens[0]

		return {title : {"title_stub": bookmark[1].split(".com/")[1], "season": season, "episode": episode}}


	root_folder = ("Anime",)
	folder_blacklist = ("Ongoing by Air Day", "Watch List", "Completed", "Reference")

	conn = sqlite3.connect(bookmarks_path)
	c = conn.cursor()

	c.execute("SELECT id FROM moz_bookmarks WHERE type = 2 and title = ?", root_folder)
	params = c.fetchone() + folder_blacklist

	c.execute("SELECT id FROM moz_bookmarks WHERE type=2 AND parent = ? AND title NOT IN({SEQ})".format(SEQ=','.join(['?']*len(folder_blacklist))), params)
	subfolders = tuple( map(lambda row : row[0], c.fetchall()) )

	c.execute("""SELECT moz_bookmarks.title, moz_places.url FROM moz_bookmarks
				 JOIN moz_places ON moz_bookmarks.fk = moz_places.id
				 WHERE moz_bookmarks.type=1 and moz_bookmarks.parent IN({SEQ})""".format(SEQ=",".join(['?']*len(subfolders))), subfolders)

	bookmarks = {}
	for pair in map(map_bookmark, c.fetchall()):
		bookmarks.update(pair)

	conn.close()
	return bookmarks

async def hasNewContent(show, bookmarks):
	"""takes the bookmarks dict key for a show and returns if the show has new content that has not been recorded as seen in the dict

	Arguments:
	show --- the key to the bookmarks dict for a particular show
	bookmarks --- a properly formatted dictionary of bookmarks
	"""
	current_episode = bookmarks[show]["episode"]
	current_season = bookmarks[show]["season"]

	latest_season = cr.getLatestSeason(bookmarks[show]["title_stub"])
	latest_episode = cr.getLatestEpisode(bookmarks[show]["title_stub"])


	#check if there is a new season
	if current_season != None and latest_season != None and int(latest_season) >= int(current_season):
		print(show  + ": new season")
		return 2

	#check if there is a new episode
	if current_episode != None and latest_episode != None and int(latest_episode) >= int(current_episode):
		print(show + ": new episode")
		return 1

	print(show)
	return 0

async def wrap_tasks(bookmarks):
	tasks = []
	for show in bookmarks:
		tasks.append(hasNewContent(show, bookmarks))
	return await asyncio.gather(*tasks)

#TODO implement for non-Windows 
if os.name == "nt":
	profile_path = os.path.expandvars("%APPDATA%\\Mozilla\\Firefox\\Profiles\\")
	if len(sys.argv) > 1:
		profile_path += sys.argv[1] + "\\"
	else:
		profile_path += "rblyzgbi.default-release\\"
else:
	profile_path = "testenv/"


try:
	bookmarks = parseBookmarks(profile_path + "places.sqlite")
except Exception as e:
	sys.exit(e)

new_season = []
new_episode = []

results = asyncio.run(wrap_tasks(bookmarks))

for result in results:
	if result == 2:
		new_season.append(title)
	elif result == 1:
		new_episode.append(title)

print("New Season:", flush=True)
for title in new_season:
	print("   ", title, flush=True)

print("New Episode:", flush=True)
for title in  new_episode:
	print("   ", title, flush=True)
