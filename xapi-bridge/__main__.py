import sys, os, json
from pyinotify import WatchManager, Notifier, EventsCodes, ProcessEvent
import converter, settings

class QueueManager:

	def __init__(self):
		self._cache = []

	def push(self, stmt):

		self._cache.append(stmt)

		# publish if statement threshold is reached
		if settings.PUBLISH_MAX_PAYLOAD <= len(self._cache):
			self.publish()

	def publish(self):
		pass


class TailHandler(ProcessEvent):

	MASK = EventsCodes.OP_FLAGS['IN_MODIFY']

	def __init__(self, filename):

		# set up superclass
		super(TailHandler, self).__init__()

		# prepare file input stream
		self.ifp = open(filename, 'r', 0)
		self.ifp.seek(0,2)

		self.publish_queue = QueueManager()


	def process_IN_MODIFY(self,event):

		buff = self.ifp.read()
		evts = [i for i in buff.split('\n') if len(i) != 0]
		for e in evts:
			try:
				evtObj = json.loads(e)
			except ValueError as err:
				print 'Could not parse JSON for', e

			xapi = converter.to_xapi(evtObj)
			if xapi != None:
				self.publish_queue.push(xapi)
				


def watch(watch_file):
	'''
	Watch the given file for changes
	'''
	
	wm = WatchManager()

	notifier = Notifier(wm, TailHandler(watch_file))
	wdd = wm.add_watch(watch_file, TailHandler.MASK)

	while True:
		try:
			notifier.process_events()
			if notifier.check_events():
				notifier.read_events()
		except KeyboardInterrupt:
			notifier.stop()
			break


if __name__ == '__main__':

	log_path = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else '/edx/var/log/tracking.log'
	watch(log_path)
