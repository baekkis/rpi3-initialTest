
import soco.plugins.talk as talk
import soco
 
mp3Path = '/home/pi/Public/Files/Sounds/tmp/talkOutput.mp3'
uri = 'x-file-cifs://raspberrypi/PiShare/Sounds/talkOutput.mp3'

talker = talk.TalkerPlugin(soco,mp3Path,uri)
talker.talk('Warning. Warning. This is not a drill',volume=1)

