import time
from subprocess import call

for i in xrange(1,11):
 call(["fswebcam", "-r", "640x480", "--no-banner", "./%d.jpg" % i])
 time.sleep(1)
