import crunchyroll_utils as cr
import sqlite3

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

	return bookmarks

test_bookmarks = { "My Hero Academia": {"title_stub":"my-hero-academia", "episode" : "88", "season" : "4"}, "Black Clover": {"title_stub":"black-clover", "episode": "129", "season": None}} # test code


def hasNewContent(show, bookmarks):
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
		return 2

	#check if there is a new episode
	if current_episode != None and latest_episode != None and int(latest_episode) >= int(current_episode):
		return 1

	return 0

#TODO take location of places.sqlite from stdin then pass to parseBookmarks
bookmarks = parseBookmarks("places.sqlite")

new_season = []
new_episode = []

for title in bookmarks:
	result = hasNewContent(title, bookmarks)
	if result == 2:
		new_season.append(title)
	elif result == 1:
		new_episode.append(title)

print("New Season:")
for title in new_season:
	print("   ", title)

print("New Episode:")
for title in  new_episode:
	print("   ", title)

#parseBookmarks("C:\\Users\\griff\\AppData\\Mozilla\\Firefox\\Profiles\\rblyzgbi.default-release\\places.sqlite")