from mqtt_controller import magnet_control, servo_control, cleanup
import time
'''
print ("TEST: Mıknatıslar Açılıyor")
magnet_control(True, True)
time.sleep(10)

print ("TEST: mıknatıs1 açık mıknatıs2 kapalı")
magnet_control(True, False)
time.sleep (10)

print ("TEST: mıknatıs1 kapalı  Mıknatıs2 açık ")
magnet_control(False, True)
time.sleep (10)

print ("TEST: Mıknatıs1 kapalı mıknatıs2 kapalı")
magnet_control(False, False)
'''
try:
	print ("servo saat yönü sarıyor")
	servo_control(open_servo = True)
	time.sleep(1)

	print ("servo saat yönü tersi sarıyor")
	servo_control(open_servo = False)
	time.sleep(1)

finally:
	cleanup()
