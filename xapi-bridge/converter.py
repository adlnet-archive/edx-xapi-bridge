
def to_xapi(evt):

	print '{time}: {event_type} by {username}'.format(**evt)

	# event indicates a problem has been attempted
	if evt['event_type'] == 'problem_check' and evt['event_source'] == 'server':
		pass
	else:
		return None
