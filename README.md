# crunchycrawly
Python command line utility that crawls through Firefox bookmarks and Crunchyroll and returns a list of bookmarked series that have new episodes or seasons

Takes the name of a Firefox profile's folder as an argument.

## Assumptions made about bookmarks
1. Bookmark titles should be preceded by a string that denotes what episode or season you will watch next e.g. ` *[345] Bleach` or `` `(s3) That Time I was Reincarnated as a Slime``
      - *crunchycrawly* does not care whether you use backticks or asterisks, nor square brackets or parenthesis, as long as they are there.
      - Personally I use backticks to denote shows on "hiatus", astericks to denote currently running shows, parenthesis to denote the enclosed episode or season is the latest, and square brackets to denote the enclosed is *not* the latest season or episode.
2. The toplevel folder in your bookmarks that is searched, currently, one called "Anime". Please avoid any collisions with this name, as Firefox folders don't currently support labels or keywords
      - This folder and its subfolders that are not in the **blacklist** (currently not recursive) are searched for bookmarks.
3. The subfolder blacklist, by default, contains "Ongoing by Air Day", "Watch List", "Completed" and "Reference".
      - support for a config file and command line options to define your own root folder and blacklist coming soon
