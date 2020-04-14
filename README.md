# crunchycrawly
Python command line utility that crawls through Firefox bookmarks and Crunchyroll and returns a list of bookmarked series that have new episodes or seasons

```
usage: python crunchycrawly.py [option] [profile path]
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
```

## Assumptions made about bookmarks
1. Bookmark titles should be preceded by a string that denotes what episode or season you will watch next e.g. ` *[345] Bleach` or `` `(s3) That Time I was Reincarnated as a Slime``
      - *crunchycrawly* does not care whether you use backticks or asterisks, nor square brackets or parenthesis, as long as they are there.
      - Personally I use backticks to denote shows on "hiatus", astericks to denote currently running shows, parenthesis to denote the enclosed episode or season is the latest, and square brackets to denote the enclosed is *not* the latest season or episode.
2. The toplevel folder in your bookmarks that is searched, currently, one called "Anime". Please avoid any collisions with this name, as Firefox folders don't currently support labels or keywords
      - This folder and its subfolders that are not in the **blacklist** (currently not recursive) are searched for bookmarks.
3. The subfolder blacklist, by default, contains "Ongoing by Air Day", "Watch List", "Completed" and "Reference".
      - support for a config file and command line options to define your own root folder and blacklist coming soon

## Example of a bookmark tree
Struck-through directories are ignored as they are in the default blacklist
- **Anime**
   + ~**Ongoing by Air Date**~
   + ~**Watch List**~
   + **Romance**
      + `(s3) Oregairu
   + **Action**
      + *[345] Bleach
      + *(130) Black Clover
      + *(s2) That Time I was Reincarnated as a Slime
   + **Comedy**
      + `(22) Tonari No Seki-kun
      + `(13) Tanaka-kun Is Always Listless
   + ~**Reference**~
   
## Example of a config file
crunchycrawly.config
```
ROOT_FOLDER=ANIME
BLACKLIST=Ongoing By Air Day, Watch List, Completed, Reference
```
