
def to_xapi(evt):

	print '{time}: {event_type} by {username}'.format(**evt)
	print evt

	# set up common elements in statement
	statement = {
		'actor': {
			'account': {
				'homePage': evt['host'],
				'name': evt['username']
			},
			'name': evt['username']
		},
		'timestamp': evt['time'],
		'context': {
			'platform': 'open.edx.org'
		}
	}

	# event indicates a problem has been attempted
	if evt['event_type'] == 'problem_check' and evt['event_source'] == 'server':

		statement.update({
			'verb': {
				'id': 'http://adlnet.gov/expapi/verbs/attempted',
				'display': {
					'en-US': 'attempted'
				}
			},
			'object': {
				'type': 'Activity',
				'id': evt['context']['problem_id']
			}
		})
		return statement

	else:
		return None
