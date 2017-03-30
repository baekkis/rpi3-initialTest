import soco
 
#Replace with your speaker IP address
sonos = soco.SoCo("192.168.1.160")

sound = sonos.music_library.get_tracks(search_term='test')
print (sound[0].item_id)
#print(soco.music_library.get_tracks()) 
#print(soco.music_library.get_tracks(search_term='test')[0].uri) 
