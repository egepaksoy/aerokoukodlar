import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

BROKER_ADRESS = "192.168.31.108"
BROKER_PORT = 1883
TOPIC = "kontrol"

client = mqtt.Client()
client.connect(BROKER_ADRESS, BROKER_PORT, 60)

SERVO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def send_command (command):
	client.publish(TOPIC, command)
	print(f"[MQTT] Komut gönderildi: {command}") 

def magnet_control (magnet1: bool, magnet2: bool):
	if magnet1:
		send_command("em1_on")
	else:
		send_command("em1_off")

	if magnet2:
		send_command("em2_on")
	else:
		send_command("em2_off")

def set_servo_angle(angle):
	duty = int(angle / 18 + 2)
	GPIO.output(SERVO_PIN, True)
	pwm.ChangeDutyCycle(duty)
	time.sleep(0.5)
	GPIO.output(SERVO_PIN, False)
	pwm.ChangeDutyCycle(0)

def servo_control(open_servo: bool):
	if open_servo:
		print ("Servo açılıyor")
		set_servo_angle(90)
	else:
		print ("Servo kapanıyor")
		set_servo_angle(180)

def cleanup():
	pwm.stop()
	GPIO.cleanup()

