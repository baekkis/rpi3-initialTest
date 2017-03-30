import sys
import re
import urllib, urllib2
import time
from soco.snapshot import Snapshot
from soco.plugins import SoCoPlugin
from google.cloud import translate
from pushbullet import Pushbullet
from gtts import gTTS
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('app.ini')

pb = Pushbullet(parser.get('soco', 'push'))

__all__ = ['Talk']
print(pb.devices)
print(pb.channels)
#mc = pb.channels[0]
#mc.push_note("Fellesmelding", "''Hjemme'' modus aktivert ".encode('latin-1'))

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

#        zoneNames = ['192.168.1.204']
        zoneNames = ['192.168.1.110']
#set([SoCo("192.168.1.158"), SoCo("192.168.1.110"), SoCo("192.168.1.204")])
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
#            print ("{0} - {1}".format(zone.ip_address, zone.player_name.encode('latin-1')))
        """
        if zoneNames:
            assert type(zoneNames) == list and all([zone in nameList for zone in zoneNames]), \
            'Speaker object must be instantiated with a list of existing zone names on your network'
            speakingSoCos = [zone for zone in zoneList if zone.ip_address in zoneNames]
        else:
            speakingSoCos = zoneList

        speakingSoCos.pop(0)
        """
        self.zones = [zone for zone in zoneList if zone.ip_address in zoneNames]
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

#        tts.downloadAudioFile(text_lines,'en',open(self.mp3Path,'wb'))
        tts.downloadAudioFile(text_lines,'no', self.mp3Path)
#        file = open(self.mp3Path, 'wb')
#        print(file)

        coordinators = [zone for zone in self.zones if zone.is_coordinator and not zone.is_playing_tv]
        for zone_c in coordinators:
            trans_state = zone_c.get_current_transport_info()
            if trans_state['current_transport_state'] == 'PLAYING':
                zone_c.pause()

        for zone in self.zones:
            if zone.is_playing_tv:
                zone.volume = 0
            else:
                zone.volume = 10

        waitTime = 0
        for zone_c in coordinators:
            zone_c.play_uri(self.sonosURI,title=u'Python Talking Script')
            print ("Playing on {0}: {1}".format(zone_c.player_name.encode('latin-1'), zone_c.get_current_track_info()))
            if(waitTime == 0):
                waitTime = int(zone_c.get_current_track_info()['duration'][-2:]) + 1
        
        print  ("Waiting {}".format(waitTime))
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
#                print('restoring {}'.format(zone.player_name.encode('latin-1')))
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
        """
        request_headers = {
            "Accept-Language": "nb-NO,nb;q=0.8,no;q=0.6,nn;q=0.4,en-US;q=0.2,en;q=0.2,da;q=0.2,sv;q=0.2",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Host": "translate.google.com",
            "Cookie": "CONSENT=YES+NO.no+20150921-01-1; SID=-AP7ucOBsPeIAz-5asMi5d9JukWhLUdmEYPT1rKjBrVkwQ83bLYYUOiuzvVZToABuYujzw.; HSID=Ax-F5ZOxX-RSlwcCQ; APISID=XMrsYAJItDE4ZPvm/ATnvUmu7i5QiLaRvE; NID=94=GKZQ7J6TOO80ohBwBqugTgI7Bqv345zenOOoTGMEgQ9dNogkUf_LvaDbzzpkTnKLDaXAJsAZ9csRQXNbd9C0qTVWlIkC4KidKQhQX89fkcfwwb8JK-rHKYgzq8hrKr-XvtvfHCrGR-IEBKlrDrtyGjyGx9odmkM7LPfeAgL6j_vJYqF4O9-4LtyWM_kRRXnTavc2fSg5jUk8Ab0MEGt_BkJLli3hjTNK3YLikTkL89BqZ5mvD3YCXIZlhCqQ7fkyBIzeUOvatwsiIpFf1eZvaiVyunyZsCSuOqx2M4-3sDQ-iT1fBH9eAfl5_GT2SHzs41Os5tOFCh3Z5AiDjIZdZrTwp2M09FgejFg28WQEla0gGNjrkA; _ga=GA1.3.125360758.1404686689",
            "Connection": "keep-alive",
            "X-Client-Data": "CK+1yQEIkbbJAQiktskBCMG2yQEI8JjKAQj7nMoBCKmdygE="
        }
        """

#        for idx, line in enumerate(text_lines):
#            push = pb.push_note("Speaking", line)
#            print ("Text to speech for : {}".format(line))
#            query_params = {"key": "AIzaSyALXksbtDoz0srfWrs80XdfyAxpkHw_scs","tl": language, "source": "Nb-no", "q": line, "client": "tw-ob", "textlen": len(line), "idx": 0, "total": "1", "ie": "UTF-8"}
#            query_params = {"tl": language, "source": "Nb-no", "client": "tw-ob", "textlen": len(line), "idx": 0, "total": "1", "ie": "UTF-8", "q": line}
#            url = "https://translate.google.com/translate_tts?"+ self.unicode_urlencode(query_params)
#            request_headers.update({"Referer": url})

#            req = urllib2.Request(url, {}, request_headers)
#            print (url)
#            tts = gTTS(text=line, lang=language)
#            sys.stdout.write('.')
#            sys.stdout.flush()
#            if len(line) > 0:
#                try:
#                    response = urllib2.urlopen(req)
#                    audio_file.write(response.read())
#                    print ("Reponse: {}".format(response))
#                    time.sleep(.5)
#                except urllib2.HTTPError as e:
#                    print ('Error: {}'.format(e))


#        lines = ', '.join(str(x) for x in text_lines)
        lines = ''.join(map(str,text_lines))
        tts = gTTS(text=lines, lang=language)
#        tts.save('/home/pi/Public/Files/Sounds/tmp/talkOutput.mp3')
        print (lines)
        print (audio_file)
        tts.save(audio_file)

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
                          'x-file-cifs://raspberrypi/PiShare/Sounds/tmp/talkOutput.mp3')

    talker.talk('Hei huset!', volume='25')

if __name__ == '__main__':
    testStuff()
