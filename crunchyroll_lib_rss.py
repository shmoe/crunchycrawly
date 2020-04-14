from urllib.request import urlopen, Request
from xml.dom.minidom import parse as xmlParse
from datetime import datetime
import inspect

import pytz
import util

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"
EPISODE_DICT = {"date_tagName": "pubDate", "episode_tagName":"crunchyroll:episodeNumber", "season_tagName" : "crunchyroll:season"}

last_show = None
last_check = None
def getShowPage(show):
  global last_show
  if last_show != None and last_show[0] == show:
    return last_show[1]

  with urlopen(Request("http://crunchyroll.com/" + show + ".rss", headers={"User-Agent":USER_AGENT}), timeout=15) as response:
    xml = xmlParse(response)

  last_show = (show, xml)
  return xml

def toTimeStamp(dt_str):
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

	return datetime(year, mon, day, time[0], time[1], time[2], tzinfo=pytz.timezone(tmz)).timestamp()

def getLatestEpisodeNode(xml):
	global last_check
	if last_check != None and last_check[0] is xml:
		return last_check[1]

	episode_list = []

	for node in xml.getElementsByTagName(EPISODE_DICT["date_tagName"]):
		episode_list.append( (node.parentNode, toTimeStamp(node.firstChild.data)) )
	if len(episode_list) == 0:
		frame_info = inspect.getframeinfo(inspect.currentframe())
		raise RuntimeError(util.get_ffl_str(frame_info) + " no nodes with tag {} found".format(EPISODE_DICT["date_tagName"]))

	episode_list.sort(key = lambda tup : tup[1])

	last_check = (xml, episode_list[-1][0])
	return episode_list[-1][0]
