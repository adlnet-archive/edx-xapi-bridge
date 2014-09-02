import sys, os
from watcher import watch

# get file path from arg
print sys.argv
if len(sys.argv) == 2:
	watchfile = os.path.abspath(sys.argv[-1])
else:
	watchfile = '/edx/var/log/tracking.log'

watch(watchfile)

