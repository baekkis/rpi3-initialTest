import RPi.GPIO as GPIO
import time
import random as rand

GPIO.setmode(GPIO.BOARD)

GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12, 50)

p.start(1)

wait = rand.randrange(500) / 100
i = 1
d = 1
try:
  while True:
#    if i == 12:
#      i = 0
#      time.sleep(.1) # sleep 1 seconds
#    else:
#      time.sleep(.1)
#    if d == 0:
#      time.sleep(wait)
#    else:
    time.sleep(wait)
    p.ChangeDutyCycle(i)  # turn towards 90 degree

    if d == 0:
      i = i-1
    else:
      i = i+1

    if i == 12 or i == 1:
      wait = rand.randrange(100) / 100
      if d == 0:
         d = 1
      else:
        d = 0

except KeyboardInterrupt:
  p.stop()
  GPIO.cleanup()
