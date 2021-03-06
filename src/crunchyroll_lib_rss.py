from urllib.request import urlopen, Request
from xml.dom.minidom import parse as xmlParse
from datetime import datetime
from inspect import currentframe

from pytz import timezone
from util import RTError

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"
EPISODE_DICT = {"date_tagName": "pubDate", "episode_tagName":"crunchyroll:episodeNumber", "season_tagName" : "crunchyroll:season"}

last_show = None
last_check = None
def getShowPage(show):
	"""\
get the xml file for the given show's RSS feed and returns a xml.dom Document

Argument:
series_url_fragment --- the name of the series formatted as it is in its url
	(eg. "my-hero-academia" for My Hero Academia) 
"""
	global last_show
	if last_show != None and last_show[0] == show:
		return last_show[1]

	with urlopen(Request("http://crunchyroll.com/" + show + ".rss", headers={"User-Agent":USER_AGENT}), timeout=15) as response:
		xml = xmlParse(response)

	last_show = (show, xml)
	return xml

def toTimeStamp(dt_str):
	"""\
takes a string of format "WEEKDAY, MON DD YYYY HH:MM:SS TMZ" and returns it as a
	POSIX timestamp

Argument:
dt_str --- a date-time string of the above format
"""
	MONTHS = { "Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12 } 

	year = 0
	mon = 0
	day = 0
	time = ""
	tmz = ""

	tmp = dt_str.split(" ")[1:]

	day = int(tmp[0])
	mon = MONTHS[tmp[1]]
	year = int(tmp[2])
	time = list(map(lambda i : int(i), tmp[3].split(":")))
	tmz = tmp[4]

	return datetime(year, mon, day, time[0], time[1], time[2], tzinfo=timezone(tmz)).timestamp()

def getLatestEpisodeNode(xml):
	"""\
takes the xml.dom object of an RSS feed and returns the node that
	contains the number of the latest episode

Argument:
xml --- a show's RSS feed parsed as an xml.dom Document
"""
	global last_check
	if last_check != None and last_check[0] is xml:
		return last_check[1]

	episode_list = []

	for node in xml.getElementsByTagName(EPISODE_DICT["date_tagName"]):
		episode_list.append( (node.parentNode, toTimeStamp(node.firstChild.data)) )
	if len(episode_list) == 0:
		raise RTError("no nodes with tag {} found".format(EPISODE_DICT["date_tagName"]), currentframe())

	episode_list.sort(key = lambda tup : tup[1])

	last_check = (xml, episode_list[-1][0])
	return episode_list[-1][0]
