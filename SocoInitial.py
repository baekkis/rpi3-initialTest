import soco
speakers = soco.discover()

#print (speakers)
# Display a list of speakers
for speaker in speakers:
	print ("Speaker {0} @ {1}".format(speaker.player_name.encode('latin-1'), speaker.ip_address.encode('latin-1')))
#    print ("{0} ({1})".format(speaker.player_name, speaker.ip_address))

# Play a speaker
play1 = speakers.pop()
print ("Playing from {0}".format(play1.player_name.encode('latin-1')))
play1.play()
