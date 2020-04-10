from urllib.request import urlopen
from xml.dom import Node
import html5lib

VIDEO_DICT = {"id_stub": "showview_videos_media_", "title_stub": "Episode ", "taName": "li", "title_tagName" : "a"}
VIDEOS_DICT = {"id": "showview_content_videos", "tagName": "div"}
SEASONS_DICT = {"class" : "list-of-seasons"}
SEASON_DICT = {"class" : "season", "tagName" : "li", "title_tagName" : "a", "title_attr": "title"}

last_show = None
def getShowPage(show):
  global last_show
  if last_show != None and last_show[0] == show:
    return last_show[1]

  with urlopen("http://crunchyroll.com/" + show, timeout=60) as response:
    html = html5lib.parse(response, transport_encoding=response.info().get_content_charset(), treebuilder="dom")

  last_show = (show, html)
  return html

def getElementById(element, id, tagName):
  for node in element.getElementsByTagName(tagName):
    if node.hasAttribute("id"):
      if node.getAttribute("id") == id:
        return node

def getLatestSeasonNode(html):
  videos_node = getElementById(html, VIDEOS_DICT["id"], VIDEOS_DICT["tagName"])

  seasons = None
  latest_season = None

  for child in videos_node.childNodes:
    if child.nodeType == Node.ELEMENT_NODE and child.hasAttribute("class") and SEASONS_DICT["class"] in child.getAttribute("class"):
      seasons = child
      break

  for child in seasons.childNodes:
    if child.nodeType == Node.ELEMENT_NODE and child.hasAttribute("class") and SEASON_DICT["class"] in child.getAttribute("class"):
      latest_season = child
      break

  return latest_season
