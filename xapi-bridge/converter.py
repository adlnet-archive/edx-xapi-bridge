import json, re, xml.etree.ElementTree as ET


def merge(d1,d2):

	if isinstance(d1,dict) and isinstance(d2,dict):

		final = {}
		for k,v in d1.items()+d2.items():
			if k not in final:
				final[k] = v
			else:
				final[k] = merge(final[k], v)

		return final
	
	elif d2 != None:
		return d2
	
	else:
		return d1

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

		attempt = merge(statement, {
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
			},
			'context': {
				'contextActivities': {
					'parent': [{'id': 'i4x://'+evt['context']['course_id']}]
				}
			}
		})

		pf = merge(statement, {
			'verb': {
				'id': 'http://adlnet.gov/expapi/verbs/passed' if evt['event']['success'] == 'correct' else 'http://adlnet.gov/expapi/verbs/failed',
				'display': {
					'en-US': 'passed' if evt['event']['success'] == 'correct' else 'failed'
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
			},
			'context': {
				'contextActivities': {
					'parent': [{'id': 'i4x://'+evt['context']['course_id']}]
				}
			}
		})

		return attempt, pf


	# event indicates a video was loaded
	elif evt['event_type'] == 'load_video':

		event = json.loads(evt['event']);

		stmt = merge(statement, {
			'verb': {
				'id': 'http://adlnet.gov/expapi/verbs/launched',
				'display': {
					'en-US': 'Launched'
				}
			},
			'object': {
				'objectType': 'Activity',
				'id': 'i4x://' + evt['context']['course_id'] + event['id'],
				'definition': {
					'name': {'en-US': "Loaded Video" }
				}
			},
			'context': {
				'contextActivities': {
					'parent': [{'id': 'i4x://'+evt['context']['course_id']}]
				}
			}
		})

		return (stmt, )

	# event indicates a video was played
	elif evt['event_type'] == 'play_video':

		event = json.loads(evt['event']);

		stmt = merge(statement, {
			'verb': {
				'id': 'http://adlnet.gov/expapi/verbs/progressed',
				'display': {
					'en-US': 'Progressed'
				}
			},
			'object': {
				'objectType': 'Activity',
				'id': 'i4x://' + evt['context']['course_id'] + event['id'],
				'definition': {
					'name': {'en-US': "Played Video" }
				}
			},
			'result': {
				'extensions': {
					'ext:currentTime': event['currentTime']
				}
			},
			'context': {
				'contextActivities': {
					'parent': [{'id': 'i4x://'+evt['context']['course_id']}]
				}
			}
		})

		return (stmt, )

	# event indicates a video was paused
	elif evt['event_type'] == 'pause_video':

		event = json.loads(evt['event']);

		stmt = merge(statement, {
			'verb': {
				'id': 'http://adlnet.gov/expapi/verbs/suspended',
				'display': {
					'en-US': 'Suspended'
				}
			},
			'object': {
				'objectType': 'Activity',
				'id': 'i4x://' + evt['context']['course_id'] + event['id'],
				'definition': {
					'name': {'en-US': "Paused Video" }
				}
			},
			'result': {
				'extensions': {
					'ext:currentTime': event['currentTime']
				}
			},
			'context': {
				'contextActivities': {
					'parent': [{'id': 'i4x://'+evt['context']['course_id']}]
				}
			}
		})

		return (stmt, )

	# event indicates a video was stopped
	elif evt['event_type'] == 'stop_video':

		event = json.loads(evt['event']);

		stmt = merge(statement, {
			'verb': {
				'id': 'http://adlnet.gov/expapi/verbs/completed',
				'display': {
					'en-US': 'Completed'
				}
			},
			'object': {
				'objectType': 'Activity',
				'id': 'i4x://' + evt['context']['course_id'] + event['id'],
				'definition': {
					'name': {'en-US': "Completed Video" }
				}
			},
			'result': {
				'extensions': {
					'ext:currentTime': event['currentTime']
				}
			},
			'context': {
				'contextActivities': {
					'parent': [{'id': 'i4x://'+evt['context']['course_id']}]
				}
			}
		})

		return (stmt, )

	# event indicates a video was seeked
	elif evt['event_type'] == 'seek_video':

		event = json.loads(evt['event']);

		stmt = merge(statement, {
			'verb': {
				'id': 'http://adlnet.gov/expapi/verbs/interacted',
				'display': {
					'en-US': 'Interacted'
				}
			},
			'object': {
				'objectType': 'Activity',
				'id': 'i4x://' + evt['context']['course_id'] + event['id'],
				'definition': {
					'name': {'en-US': "Video seek" }
				}
			},
			'result': {
				'extensions': {
					'ext:old_time': event['old_time'],
					'ext:new_time': event['new_time'],
					'ext:type': event['type']
				}
			},
			'context': {
				'contextActivities': {
					'parent': [{'id': 'i4x://'+evt['context']['course_id']}]
				}
			}
		})

		return (stmt, )

	# event indicates a video speed was changed
	elif evt['event_type'] == 'speed_change_video':

		event = json.loads(evt['event']);

		stmt = merge(statement, {
			'verb': {
				'id': 'http://adlnet.gov/expapi/verbs/interacted',
				'display': {
					'en-US': 'Interacted'
				}
			},
			'object': {
				'objectType': 'Activity',
				'id': 'i4x://' + evt['context']['course_id'] + event['id'],
				'definition': {
					'name': {'en-US': "Video speed change" }
				}
			},
			'result': {
				'extensions': {
					'ext:currentTime': event['current_time'],
					'ext:old_speed': event['old_speed'],
					'ext:new_speed': event['new_speed'],
				}
			},
			'context': {
				'contextActivities': {
					'parent': [{'id': 'i4x://'+evt['context']['course_id']}]
				}
			}
		})

		return (stmt, )

	# event indicates a video transcript was hidden
	elif evt['event_type'] == 'hide_transcript':

		event = json.loads(evt['event']);

		stmt = merge(statement, {
			'verb': {
				'id': 'http://adlnet.gov/expapi/verbs/interacted',
				'display': {
					'en-US': 'Interacted'
				}
			},
			'object': {
				'objectType': 'Activity',
				'id': 'i4x://' + evt['context']['course_id'] + event['id'],
				'definition': {
					'name': {'en-US': "Video transcript hidden" }
				}
			},
			'result': {
				'extensions': {
					'ext:currentTime': event['currentTime']
				}
			},
			'context': {
				'contextActivities': {
					'parent': [{'id': 'i4x://'+evt['context']['course_id']}]
				}
			}
		})

		return (stmt, )

	# event indicates a video transcript was shown
	elif evt['event_type'] == 'show_transcript':

		event = json.loads(evt['event']);

		stmt = merge(statement, {
			'verb': {
				'id': 'http://adlnet.gov/expapi/verbs/interacted',
				'display': {
					'en-US': 'Interacted'
				}
			},
			'object': {
				'objectType': 'Activity',
				'id': 'i4x://' + evt['context']['course_id'] + event['id'],
				'definition': {
					'name': {'en-US': "Video transcript shown" }
				}
			},
			'result': {
				'extensions': {
					'ext:currentTime': event['currentTime']
				}
			},
			'context': {
				'contextActivities': {
					'parent': [{'id': 'i4x://'+evt['context']['course_id']}]
				}
			}
		})

		return (stmt, )
		
	# event indicates a complete button in the PRT has been clicked
	elif evt['event_type'] == 'prt_complete':

		stmt = merge(evt['event'], statement)
		return stmt,

	else:
		return ()
