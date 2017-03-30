#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import httplib, urllib

import soco
import time
speakers = soco.discover()
speaker = soco.SoCo("192.168.1.160")

waitTime = 0
for zone_c in speakers:
	print('Play doorbell', zone_c.player_name.encode('latin-1'))
	zone_c.get_metadata(zone_c.get_current_track_info()['duration'])
	#zone_c.play_uri('x-file-cifs://raspberrypi/PiShare/Sounds/doorbell.mp3')
	if waitTime == 0:
 		waitTime = int(zone_c.get_current_track_info()['duration'][-2:])

print("Time to wait {0}..".format(waitTime))
time.sleep(waitTime)
print("Finished")

#for zone in soco.discover():
#	print ("Spiller {0}({1})".format(zone.player_name.encode('iso-8859-1'), zone.ip_address))


#print ("{0}".format(speaker.player_name.encode('iso-8859-1')))

#speaker.volume = 0
#speaker.play_uri('x-file-cifs://raspberrypi/PiShare/Sounds/doorbell.mp3')
