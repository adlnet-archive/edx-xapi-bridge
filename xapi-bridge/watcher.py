import os
from pyinotify import WatchManager, Notifier, EventsCodes, ProcessEvent

class TailHandler(ProcessEvent):

	MASK = EventsCodes.OP_FLAGS['IN_MODIFY']

	def __init__(self, filename):

		# set up superclass
		super(TailHandler, self).__init__()

		# prepare file input stream
		self.ifp = open(filename, 'r', 0)
		self.ifp.seek(0,2)

	def process_IN_MODIFY(self,event):
		print self.ifp.read()


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
