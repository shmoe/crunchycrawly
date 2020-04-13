import crunchyroll_utils as cr
import sqlite3
import cursor

import sys
import time
import math

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
	root_id = c.fetchone()
	params = tuple(root_id) + folder_blacklist

	c.execute("SELECT id FROM moz_bookmarks WHERE type=2 AND parent = ? AND title NOT IN({SEQ})".format(SEQ=','.join(['?']*len(folder_blacklist))), params)
	subfolders = tuple( map(lambda row : row[0], c.fetchall()) )

	#TODO select ids of all nested subfolders of `subfolders` and add to `subfolders`

	c.execute("""SELECT moz_bookmarks.title, moz_places.url FROM moz_bookmarks
				 JOIN moz_places ON moz_bookmarks.fk = moz_places.id
				 WHERE moz_bookmarks.type=1 and moz_bookmarks.parent IN({SEQ})""".format(SEQ=",".join(['?']*(len(subfolders)+1))), root_id + subfolders)

	bookmarks = {}
	for pair in map(map_bookmark, c.fetchall()):
		bookmarks.update(pair)

	conn.close()
	return bookmarks

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

def progressBar(completed_tasks_ref, total_tasks):
	"""displays a progress bar based on number of tasks completed and returns 0 when completed_tasks_ref == total_tasks

	Arguments:
	completed_tasks_ref --- reference to the variable that holds the total number of completed tasks. only read to
		prevent threading conflicts
	total_tasks --- total number of tasks
	"""
	cursor.hide()
	bar_width = 30
	while completed_tasks_ref["tasks"] < total_tasks:
		completed_tasks = completed_tasks_ref["tasks"]
		num_ticks = int(math.ceil(bar_width * (completed_tasks / total_tasks)))
		num_blank = bar_width - num_ticks
		sys.stdout.write("[" + "="*num_ticks + " "*num_blank + "]")
		sys.stdout.flush()
		time.sleep(0.1)
		sys.stdout.write("\b" * (bar_width + 2))
		sys.stdout.flush()

	sys.stdout.write("[" + "="*bar_width + "]" + "\n\n")
	sys.stdout.flush()

	cursor.show()
	return 3

if __name__ == "__main__":
	import concurrent.futures
	import os.path
	import glob
	#will break on implementing commandline options
	if len(sys.argv) > 1:
		profile = sys.argv[1]
	else:
		profile = "*.default-release"

	#TODO implement for non-Windows
	if os.name == "nt":
		profile_path = os.path.expandvars("%APPDATA%\\Mozilla\\Firefox\\Profiles\\" + profile + "\\")
	elif os.name == "posix":
		profile_path = os.path.expandvars("~/.mozilla/firefox/" + profile + "/") #test for macOS
		if os.getenv("DEBUG", default=False):
			profile_path = "testenv/" #debug

	try:
		bookmarks = parseBookmarks(glob.glob(profile_path)[0] + "places.sqlite")
	except Exception as e:
		sys.exit(e)

	new_season = []
	new_episode = []

	with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
		#look up how the below statement works
		futures = {executor.submit(hasNewContent, show, bookmarks): show for show in bookmarks}
		completed_futures_obj = {"tasks":0}
		total_futures = len(futures)
		executor.submit(progressBar, completed_futures_obj, total_futures)
		for future in concurrent.futures.as_completed(futures):
			result = future.result()
			if result != 3:
				completed_futures_obj["tasks"] += 1

			if result == 3:
				print(str(completed_futures_obj["tasks"]) + "/" + str(total_futures))
			elif result == 2:
				new_season.append(futures[future])
			elif result == 1:
				new_episode.append(futures[future])

	print("New Season:", flush=True)
	for title in new_season:
		print("   ", title, flush=True)

	print("New Episode:", flush=True)
	for title in  new_episode:
		print("   ", title, flush=True)
