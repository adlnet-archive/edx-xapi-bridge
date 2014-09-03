import json, re, xml.etree.ElementTree as ET

pending_grades = {}

def to_xapi(evt):

	# set up common elements in statement
	statement = {
		'actor': {
			'account': {
				'homePage': 'http://'+evt['host'],
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
				'objectType': 'Activity',
				'id': evt['event']['problem_id'],
				'definition': {
					'name': {'en-US': evt['context']['module']['display_name']}
				}
			},
			'result': {
				'score': {
					'raw': evt['event']['grade'],
					'min': 0,
					'max': evt['event']['max_grade'],
					'scaled': float(evt['event']['grade'])/evt['event']['max_grade']
				},
				'success': evt['event']['success'] == 'correct'
			}
		})
		statement['context']['contextActivities'] = {'parent': [{'id':'i4x://'+evt['context']['course_id']}]}

		return statement

	else:
		return None
