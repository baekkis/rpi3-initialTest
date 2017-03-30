import sys
import re
import urllib, urllib2
import time
from soco.snapshot import Snapshot
from soco.plugins import SoCoPlugin

from google.cloud import translate

__all__ = ['Talk']



class TalkerPlugin(SoCoPlugin):
    """
        The main use of this plugin is to make your Sonos system speak text.  It works by sending a request to the
        Google Text To Speech service, downloading an MP3 from the service, then playing the MP3 on the desired Sonos
        players.  It will pause and resume playback properly if you are listening to music at the time the message is
        sent.

        SETUP REQUIREMENTS:  You must add the path to the Google Text To Speech MP3 to your Sonos music library in order
        to obtain the URI for that file.  Once this is done, you can find the URI "get_music_library_information()"
        method in the soco package.
    """
    def __init__(self,soco,mp3Path,sonosURI,zoneNames=None,maxAttempts=5):
        """
        :param soco: soco instance per soco plugin instructions
        :param mp3Path: The path you wish for the TTS message to be saved.
        :param sonosURI: URI of mp3 file. This should point to the same file that exists at mp3Path
        :param zoneNames: List of Sonos player names you wish for your message to play on. i.e. ['Kitchen','Office'].
                          If nothing is passed, the message will play on all Sonos players.
        :param maxAttempts: Number of attempts to run soco.discover(). I found that regardless of the timeout passed to
                            soco.discover(), it may still fail, but multiple attempts usually works.
        :return: TalkerPlugin object

        """

 #       zoneNames = ['192.168.1.110']
        self.sonosURI = sonosURI
        self.mp3Path = mp3Path

        self.zones = None
        while not self.zones:
            self.zones = soco.discover(timeout=3)

        assert self.zones is not None, 'Connection to Sonos system failed.'

        zoneList = []
        nameList = []
        for zone in self.zones:
            zoneList.append(zone)
            nameList.append(zone.ip_address)
            print ("{0} - {1}".format(zone.ip_address, zone.player_name.encode('latin-1')))

        if zoneNames:
            assert type(zone.ames) == list and all([zone in nameList for zone in zoneNames]), \
            'Speaker object must be instantiated with a list of existing zone names on your network'
            speakingSoCos = [zone for zone in zoneList if zone.ip_address in zoneNames]
        else:
            speakingSoCos = zoneList

        speakingSoCos.pop(0)

        super(TalkerPlugin, self).__init__(soco)

    def talk(self,talkString='Dette er en test. Tester  1 2 3',volume=1):
        """
        :param talkString: String you wish your Sonos system to speak
        :param volume: Volume you wish for your Sonos system to speak at.  The volume will be set back to the previous
                       value after the message has been spoken
        :return: None
        """

        self._snap()

        tts = GoogleTTS()

        text_lines = tts.convertTextAsLinesOfText(talkString)

        tts.downloadAudioFile(text_lines,'en',open(self.mp3Path,'wb'))

        coordinators = [zone for zone in self.zones if zone.is_coordinator and not zone.is_playing_tv]
        for zone_c in coordinators:
            trans_state = zone_c.get_current_transport_info()
            if trans_state['current_transport_state'] == 'PLAYING':
                zone_c.pause()

        for zone in self.zones:
            if zone.is_playing_tv:
                zone.volume = 0
            else:
                zone.volume = 0

        waitTime = 0
        for zone_c in coordinators:
            zone_c.play_uri(self.sonosURI,title=u'Python Talking Script')
            print ("{}".format(zone_c.get_current_track_info()['duration']))
            if(waitTime == 0):
                waitTime = int(zone_c.get_current_track_info()['duration'][-2:])
        
        time.sleep(waitTime)
        self._restore()


    def _snap(self):
            for zone in self.zones:
                    zone.snap = Snapshot(zone)
                    zone.snap.snapshot()

    def _restore(self):
        for zone in self.zones:
            if zone.is_playing_tv:
                pass
            else:
                print('restoring {}'.format(zone.player_name.encode('latin-1')))
                zone.snap.restore(fade=True)


class GoogleTTS(object):
    """
        Taken from script at https://github.com/JulienD/Google-Text-To-Speech. No license info in repo.
    """
    def __init__(self):
        pass

    def convertTextAsLinesOfText(self,text):
        """ This convert a word, a short text, a long text into several parts to
            smaller than 100 characters.
        """

        # Sanitizes the text.
        text = text.replace('\n','')
        text_list = re.split('(\,|\.|\;|\:)', text)

        # Splits a text into chunks of texts.
        text_lines = []
        for idx, val in enumerate(text_list):

            if (idx % 2 == 0):
                text_lines.append(val)
            else :
                # Combines the string + the punctuation.
                joined_text = ''.join((text_lines.pop(),val))

                # Checks if the chunk need to be splitted again.
                if len(joined_text) < 100:
                    text_lines.append(joined_text)
                else:
                    subparts = re.split('( )', joined_text)
                    temp_string = ""
                    temp_array = []
                    for part in subparts:
                        temp_string = temp_string + part
                        if len(temp_string) > 80:
                            temp_array.append(temp_string)
                            temp_string = ""
                    #append final part
                    temp_array.append(temp_string)
                    text_lines.extend(temp_array)

        return text_lines

    def downloadAudioFile(self,text_lines, language, audio_file):
        """
            Donwloads a MP3 from Google Translatea mp3 based on a text and a
            language code.
        """
        print (text_lines)
        client = translate.Client()
        client = translate.Client('AIzaSyALXksbtDoz0srfWrs80XdfyAxpkHw_scs')
#        print ("Client prepared {}".format(client))
        translated = client.translate(['Gjorde det vondt?'], target_language='de')
        print ("{}".format(translated))


        for idx, line in enumerate(text_lines):
            sys.stdout.write('.')
            sys.stdout.flush()
            if len(line) > 0:
                try:
                    response = urllib2.urlopen(req)
                    audio_file.write(response.read())
                    time.sleep(.5)
                except urllib2.HTTPError as e:
                    print ('{}'.format(e))


#        print ('Saved MP3 to {}'.format(audio_file.name))
#        audio_file.close()


    def unicode_urlencode(self,params):
        """
            Encodes params to be injected in an url.
        """
        if isinstance(params, dict):
            params = params.items()
        return urllib.urlencode([(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params])


def testStuff():
    import soco
    talker = TalkerPlugin(soco,'/home/pi/Public/Files/Sounds/tmp/talkOutput.mp3',
                          'x-file-cifs://raspberrypi/PiShare/Sounds/tmp/test.mp3')

    talker.talk(volume='1')

if __name__ == '__main__':
    testStuff()
