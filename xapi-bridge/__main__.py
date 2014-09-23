import sys, os, json, requests, threading
from urlparse import urljoin
from pyinotify import WatchManager, Notifier, EventsCodes, ProcessEvent
import converter, settings

class QueueManager:
	'''
	Manages the batching and publishing of statements in a thread-safe way.
	'''

	def __init__(self):
		self.cache = []
		self.cache_lock = threading.Lock()
		self.publish_timer = None

	def __del__(self):
		self.destroy()
		
	def destroy(self):

		if self.publish_timer != None:
			self.publish_timer.cancel()

	def push(self, stmt):
		'''Add a statement to the outgoing queue'''

		# push statement to queue
		with self.cache_lock:
			self.cache.append(stmt)

		# set timeout to publish statements
		if len(self.cache) == 1 and settings.PUBLISH_MAX_WAIT_TIME > 0:
			self.publish_timer = threading.Timer(settings.PUBLISH_MAX_WAIT_TIME, self.publish)
			self.publish_timer.start()

		# publish immediately if statement threshold is reached
		if settings.PUBLISH_MAX_PAYLOAD <= len(self.cache):
			self.publish()

	def publish(self):
		'''Publish the queued statements to the LRS and clear the queue'''

		# make sure no new statements are added while publishing
		with self.cache_lock:

			# push statements to the lrs
			url = urljoin(settings.LRS_ENDPOINT, 'statements')
			r = requests.post(url, data=json.dumps(self.cache),
				auth=(settings.LRS_USERNAME, settings.LRS_PASSWORD),
				headers={'X-Experience-API-Version':'1.0.1', 'Content-Type':'application/json'})

			print r.text

			# clear cache and cancel any pending publish timeouts
			self.cache = []
			if self.publish_timer != None:
				self.publish_timer.cancel()


class TailHandler(ProcessEvent):
	'''
	Parse incoming log events, convert to xapi, and add to publish queue
	'''

	MASK = EventsCodes.OP_FLAGS['IN_MODIFY']

	def __init__(self, filename):

		# prepare file input stream
		self.ifp = open(filename, 'r', 1)
		self.ifp.seek(0,2)

		self.publish_queue = QueueManager()
		self.raceBuffer = ''

	def __enter__(self):
		return self
	def __exit__(self, type, value, tb):
		self.publish_queue.destroy()
		
	def process_IN_MODIFY(self,event):
		'''Handles any changes to the log file'''

		# read all new contents from the end of the file
		buff = self.raceBuffer + self.ifp.read()

		# if there's no newline at end of file, we probably read it before edx finished writing
		# add read contents to a buffer and return
		if len(buff) != 0 and buff[-1] != '\n':
			self.raceBuffer = buff
			
		else:
			self.raceBuffer = ''
			evts = [i for i in buff.split('\n') if len(i) != 0]
			for e in evts:
				try:
					evtObj = json.loads(e)
				except ValueError as err:
					print 'Could not parse JSON for', e
					continue

				xapi = converter.to_xapi(evtObj)
				if xapi != None:
					for i in xapi:
						self.publish_queue.push(i)
						print '{} - {} {} {}'.format(i['timestamp'], i['actor']['name'], i['verb']['display']['en-US'], i['object']['definition']['name']['en-US'])
				


def watch(watch_file):
	'''
	Watch the given file for changes
	'''
	
	wm = WatchManager()

	with TailHandler(watch_file) as th:

		notifier = Notifier(wm, th)
		wdd = wm.add_watch(watch_file, TailHandler.MASK)

		notifier.loop()

		# flush queue before exiting
		th.publish_queue.publish()


	print 'Exiting'


if __name__ == '__main__':

	log_path = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else '/edx/var/log/tracking.log'
	print 'Watching file', log_path
	watch(log_path)
