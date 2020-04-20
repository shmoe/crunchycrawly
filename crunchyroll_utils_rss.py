from xml.dom import Node
from inspect import currentframe

import crunchyroll_lib_rss as cr
from util import RTError

def getLatestSeason(show):
	"""\
get the name of the latest season number for a specific series on crunchyroll

Argument:
series_url_fragment --- the name of the series formatted as it is in its url
	(eg. "my-hero-academia" for My Hero Academia)
"""
	xml = cr.getShowPage(show)
	season = 0

	latest_video_node = cr.getLatestEpisodeNode(xml)
	season_nodes = latest_video_node.getElementsByTagName(cr.EPISODE_DICT["season_tagName"])
	if len(season_nodes) == 0:
		return 1

	season = latest_video_node.getElementsByTagName(cr.EPISODE_DICT["season_tagName"])[0].firstChild.data

	return int(season)

def getLatestEpisode(show):
	"""\
get the number of the latest episode number for a specific series on crunchyroll

Argument:
series_url_fragment --- the name of the series formatted as it is in its url
	(eg. "my-hero-academia" for My Hero Academia)
"""
	latest_video = None

	xml = cr.getShowPage(show)
	video_node = cr.getLatestEpisodeNode(xml)

	nodes = video_node.getElementsByTagName(cr.EPISODE_DICT["episode_tagName"])
	if len(nodes) == 0:
		raise RTError("no {} tags found".format(cr.EPISODE_DICT["episode_tagName"]), currentframe())
	if not nodes[0].hasChildNodes():
		raise RTError("{} has no children".format(cr.EPISODE_DICT["episode_tagName"]), currentframe())

	latest_video = nodes[0].firstChild.data
	return int(latest_video)
