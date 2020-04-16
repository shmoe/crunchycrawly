import crunchyroll_utils as cr
import sqlite3
import cursor
import util

import sys
import time
import math
import inspect

ROOT_FOLDER = "Anime"
BLACKLIST = ("Ongoing by Air Day", "Watch List", "Completed", "Reference")

def parseBookmarks(bookmarks_path):
	"""takes a Firefox places.sqlite file and returns an appropriate tree structure for
	hasNewContent(...)

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

	def get_subfolders(cursor, folder_ids, blacklist):
		sql = "SELECT id from moz_bookmarks WHERE type=2 AND parent IN({SEQ1}) AND title NOT IN({SEQ2})".format( SEQ1=','.join(['?']*len(folder_ids)), SEQ2=','.join(['?']*len(folder_blacklist)) )
		cursor.execute(sql, folder_ids + blacklist)
		rows = c.fetchall()
		if len(rows) == 0:
			return folder_ids
		else:
			return folder_ids + get_subfolders(cursor, tuple([row[0] for row in rows]), blacklist)

	global ROOT_FOLDER, BLACKLIST
	root_folder = (ROOT_FOLDER,)
	folder_blacklist = BLACKLIST

	conn = sqlite3.connect(bookmarks_path)
	c = conn.cursor()

	c.execute("SELECT id FROM moz_bookmarks WHERE type = 2 and title = ?", root_folder)
	root_ids = c.fetchall()
	if len(root_ids) > 1:
		frame_info = inspect.getframeinfo(inspect.currentframe())
		raise RuntimeError(util.get_ffl_str(frame_info) + " root folder name {} not unique".format(root_folder[0]))

	root_id = root_ids[0]
	if root_id == None:
		frame_info = inspect.getframeinfo(inspect.currentframe())
		raise RuntimeError(util.get_ffl_str(frame_info) + " bookmark folder {} not found".format(root_folder[0]))

	subfolders = get_subfolders(c, root_id, folder_blacklist)

	#TODO select only Crunchyroll series urls
	c.execute("""SELECT moz_bookmarks.title, moz_places.url FROM moz_bookmarks
				 JOIN moz_places ON moz_bookmarks.fk = moz_places.id
				 WHERE moz_places.url LIKE '%crunchyroll.com/%'
				 AND moz_bookmarks.type=1 AND moz_bookmarks.parent IN({SEQ})""".format(SEQ=",".join(['?']*(len(subfolders)+1))), root_id + subfolders)

	bookmarks = {}

	rows = c.fetchall()

	if len(rows) == 0:
		frame_info = inspect.getframeinfo(inspect.currentframe())
		raise RuntimeError(util.get_ffl_str(frame_info) + "no bookmarks found in {}".format(root_folder[0]))

	for pair in map(map_bookmark, rows):
		bookmarks.update(pair)

	conn.close()
	return bookmarks

def hasNewContent(show, bookmarks, verbose=False):
	"""takes the bookmarks dict key for a show and returns if the show has new content
	that has not been recorded as seen in the dict

Arguments:
show --- the key to the bookmarks dict for a particular show
bookmarks --- a properly formatted dictionary of bookmarks
"""
	current_episode = bookmarks[show]["episode"]
	current_season = bookmarks[show]["season"]

	latest_season = cr.getLatestSeason(bookmarks[show]["title_stub"])
	latest_episode = cr.getLatestEpisode(bookmarks[show]["title_stub"])

	retval = 0
	#check if there is a new season
	if current_season != None and latest_season != None and int(latest_season) >= int(current_season):
		retval = 2
	#check if there is a new episode
	elif current_episode != None and latest_episode != None and int(latest_episode) >= int(current_episode):
		retval = 1

	if verbose:
		if retval != 0:
			print(show + " has a new " + ("season" if retval == 2 else "episode"))
		elif retval == 0:
			print(show + " has no new content")
	return retval

def progressBar(completed_tasks_ref, total_tasks):
	"""displays a progress bar based on number of tasks completed and returns 0 when
	completed_tasks_ref == total_tasks

Arguments:
completed_tasks_ref --- reference to the variable that holds the total number
	of completed tasks. only read to prevent threading conflicts
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
		time.sleep(0.01)
		sys.stdout.write("\b" * (bar_width + 2))
		sys.stdout.flush()

	sys.stdout.write("[" + "="*bar_width + "]" + "\n\n")
	sys.stdout.flush()

	cursor.show()
	return 3

if __name__ == "__main__":
	def main(argv):
		"""usage: python crunchycrawly.py [option] [profile path]
Options and arguments:
-h,	--help			display this dialog
-v,	--verbose		disable progress bar and output detailed play-by-play
	--rss			use Crunchyroll's RSS feed to check for new content
	--html			use the serie's html page to check for new content,
					this is the default and most well supported
-b,	--blacklist=FOLDERS	takes a list of bookmark folders to exclude from the
					search
-r,	--root-folder=FOLDER	takes the name of the top bookmark folder to search
					for series. this folder must have a unique
					name to avoid collisions
-c,	--config=FILE		takes the path to a config file
"""
		import concurrent.futures
		import platform
		import os
		import glob
		import getopt

		VERBOSE = False
		RSS = False

		try:
			opts, args = getopt.getopt(argv, "hvb:r:c:", ["help", "verbose", "rss", "html", "blacklist=","root-folder=", "config="])
		except getopt.GetoptError as e:
			sys.exit(e)

		for opt, arg in opts:
			global ROOT_FOLDER, BLACKLIST
			if opt in ["-h", "--help"]:
				print(main.__doc__)
				sys.exit(0)
			if opt in ["-v", "--verbose"]:
				VERBOSE = True
			if opt == "--rss":
				RSS = True
			if opt == "--html":
				RSS = False
			if opt in ["-b", "--blacklist"]:
				BLACKLIST = tuple(arg.split(" "))
			if opt in ["-r", "--root-folder"]:
				ROOT_FOLDER = arg
			if opt in ["-c", "--config-file"]:
				with open(arg, 'r') as config_file:
					for line in config_file:
						pair = [el.strip() for el in line.split("=")]
						if pair[0] == "ROOT_FOLDER":
							ROOT_FOLDER = pair[1]
						elif pair[0] == "BLACKLIST":
							BLACKLIST = tuple([el.strip() for el in pair[1].split(",")])

		if RSS:
			import crunchyroll_utils_rss
			global cr
			cr = crunchyroll_utils_rss

		try:
			if len(args) == 0:
				profile = "*.default-release"
			elif len(args) == 1:
				profile = args[1]
			else:
				frame_info = inspect.getframeinfo(inspect.currentframe())
				raise RuntimeError(util.get_ffl_str(frame_info) + " expected 0-1 arguments, got {}".format(len(args)))

			if platform.system() == "Windows":
				profile_path = os.path.expandvars("%APPDATA%\\Mozilla\\Firefox\\Profiles\\" + profile + "\\")
			elif platform.system() == "Linux":
				profile_path = os.path.expandvars("~/.mozilla/firefox/" + profile + "/")
				if os.getenv("DEBUG", default=False):
					profile_path = "testenv/" #debug
			elif platform.system() == "Darwin":
				profile_path = os.path.expandvars("~/Library/Application Support/Mozilla/Firefox/Profiles/" + profile + "/")
			else:
				frame_info = inspect.getframeinfo(inspect.currentframe())
				raise RuntimeError(util.get_ffl_str(frame_info) + "platform OS not supported")

			bookmarks = parseBookmarks(glob.glob(profile_path)[0] + "places.sqlite")
		except Exception as e:
			sys.exit(e)

		#DEBUG
		print("{")
		for key, val in bookmarks.items():
			print("\t{k}	{v}".format(k=key,v=val))
		print("}")
		return 0

		new_season = []
		new_episode = []

		with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
			futures = {executor.submit(hasNewContent, show, bookmarks, VERBOSE): show for show in bookmarks}
			completed_futures_obj = {"tasks":0}
			total_futures = len(futures)

			if not VERBOSE:
				executor.submit(progressBar, completed_futures_obj, total_futures)

			for future in concurrent.futures.as_completed(futures):
				result = future.result()
				completed_futures_obj["tasks"] += 1

				if result == 2:
					new_season.append(futures[future])
				elif result == 1:
					new_episode.append(futures[future])

		if VERBOSE:
			print("\n")

		print("New Season:", flush=True)
		for title in new_season:
			print("   ", title, flush=True)

		print("New Episode:", flush=True)
		for title in  new_episode:
			print("   ", title, flush=True)


	main(sys.argv[1:])
