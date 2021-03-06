import RPi.GPIO as GPIO

class ledManager:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(16,GPIO.OUT)
        GPIO.setup(20,GPIO.OUT)
        GPIO.setup(21,GPIO.OUT)

    def off(self):
        GPIO.output(16, GPIO.LOW)
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.LOW)

    def green(self):
        self.off()
        GPIO.output(20, GPIO.HIGH)

    def blue(self):
        self.off()
        GPIO.output(16, GPIO.HIGH)

    def red(self):
        self.off()
        GPIO.output(21, GPIO.HIGH)

    def blueGreen(self):
        self.off()
        GPIO.output(20, GPIO.HIGH)
        GPIO.output(16, GPIO.HIGH)

    def violet(self):
        self.off()
        GPIO.output(16, GPIO.HIGH)
        GPIO.output(21, GPIO.HIGH)

    def yellow(self):
        self.off()
        GPIO.output(21, GPIO.HIGH)
        GPIO.output(20, GPIO.HIGH)

    def white(self):
        self.off()
        GPIO.output(16, GPIO.HIGH)
        GPIO.output(20, GPIO.HIGH)
        GPIO.output(21, GPIO.HIGH)
