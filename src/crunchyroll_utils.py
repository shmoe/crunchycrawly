from xml.dom import Node
from inspect import currentframe

import crunchyroll_lib as cr
from util import RTError

def getLatestSeason(show):
	"""\
get the name of the latest season number for a specific series on crunchyroll

Argument:
series_url_fragment --- the name of the series formatted as it is in its url
	(eg. "my-hero-academia" for My Hero Academia)
"""
	html = cr.getShowPage(show)
	season = 0

	title_attr = cr.SEASON_DICT["title_attr"]
	for node in html.getElementsByTagName(cr.SEASON_DICT["tagName"]):
		if node.hasAttribute("class") and cr.SEASON_DICT["class"] in node.getAttribute("class"):
			for child in node.childNodes:
				#TODO find other way to exclude dubbed seasons
				if child.nodeType == Node.ELEMENT_NODE and child.hasAttribute(title_attr) and not "Dubbed" in child.getAttribute(title_attr):
					season += 1
					break

	return season

def getLatestEpisode(show):
	"""\
get the number of the latest episode number for a specific series on crunchyroll

Argument:
series_url_fragment --- the name of the series formatted as it is in its url
	(eg. "my-hero-academia" for My Hero Academia)
"""
	latest_video = None

	html = cr.getShowPage(show)
	latest_season = cr.getLatestSeasonNode(html)

	if not latest_season.hasChildNodes():
		raise RTError("node has no children", currentframe())
	for child in latest_season.childNodes:
		if child.nodeType == Node.ELEMENT_NODE and child.hasAttribute("class") and "portrait-grid" in child.getAttribute("class"):
			latest_season = child
			break

	if not latest_season.hasChildNodes():
		raise RTError("node has no children", currentframe())
	for child in latest_season.childNodes:
		id_stub = cr.VIDEO_DICT["id_stub"]
		if child.nodeType == Node.ELEMENT_NODE and child.hasAttribute("id") and child.getAttribute("id")[0 : len(id_stub)] == id_stub:
			latest_video = child
			break

	title_node = latest_video.getElementsByTagName(cr.VIDEO_DICT["title_tagName"])
	if len(title_node) == 0:
		raise RTError("no {} tag found".format(cr.VIDEO_DICT["title_tagName"]), currentframe())

	span = latest_video.getElementsByTagName(cr.VIDEO_DICT["title_tagName"])[0].toxml()

	title_stub = cr.VIDEO_DICT["title_stub"]
	latest_video_number = ""
	for char in span[span.find(title_stub) + len(title_stub) :].split()[0]:
		if not char.isdigit():
			break
		latest_video_number += char

	return latest_video_number
