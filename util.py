def get_ffl_str(frame_info):
	return "[{filename}/{function}/{lineno}]".format(filename=frame_info[0], function=frame_info[2], lineno=frame_info[1])

