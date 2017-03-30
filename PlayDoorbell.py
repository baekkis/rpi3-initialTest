#https://github.com/SoCo/SoCo/issues/414
import time
import soco
from soco.snapshot import Snapshot

class SonosInterface(object):
    def __init__(self):
        self.zones = None
        while not self.zones:
            self.zones = soco.discover(timeout=3)
        
#        print (self.zones)

    def doorbell(self):
        for zone in self.zones:
            zone.snap = Snapshot(zone)
            zone.snap.snapshot()
#            print('found zone')
#            print(zone.snap.volume, zone.is_coordinator, zone.is_playing_tv,  zone.player_name.encode('latin-1'))

        coordinators = [zone for zone in self.zones if zone.is_coordinator and not zone.is_playing_tv]

#        print (coordinators)

        for zone_c in coordinators:
            trans_state = zone_c.get_current_transport_info()
            #print(zone_c.player_name.encode('latin-1'), trans_state)
            if trans_state['current_transport_state'] == 'PLAYING':
                zone_c.pause()

        for zone in self.zones:
            if zone.is_playing_tv:
                zone.volume = 0
            else:
                zone.volume = 1

        waitTime = 0
        for zone_c in coordinators:
#            print('Play doorbell', zone_c.player_name.encode('latin-1'))
            zone_c.play_uri('x-file-cifs://raspberrypi/PiShare/Sounds/doorbell.mp3')
            if(waitTime == 0):
                waitTime = int(zone_c.get_current_track_info()['duration'][-2:])


        time.sleep(waitTime)
        for zone in self.zones:
            if zone.is_playing_tv:
                pass
            else:
                print('restoring {}'.format(zone.player_name.encode('latin-1')))
                zone.snap.restore(fade=True)

if __name__ == "__main__":
    sc = SonosInterface()
    sc.doorbell()
    print("two.py is being run directly")
else:
    print("two.py is being imported into another module")
