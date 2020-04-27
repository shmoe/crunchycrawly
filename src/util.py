from inspect import getframeinfo

def get_ffl_str(frame_info):
	"""\
takes the info for a certain frame and returns a string of format
	"[filename/functionname/linenumber]"

frame_info --- named tuple returned by inspect.getframeinfo(...)
"""
	return "[{filename}/{function}/{lineno}]".format(filename=frame_info[0], function=frame_info[2], lineno=frame_info[1])

class RTError(RuntimeError):
	def __init__(self, str, frame):
		super().__init__(get_ffl_str(getframeinfo(frame)) + " " + str)