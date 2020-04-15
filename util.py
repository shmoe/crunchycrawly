def get_ffl_str(frame_info):
	"""takes the info for a certain frame and returns a string of format
	"[filename/functionname/linenumber]"

frame_info --- named tuple returned by inspect.getframeinfo(...)
"""
	return "[{filename}/{function}/{lineno}]".format(filename=frame_info[0], function=frame_info[2], lineno=frame_info[1])

