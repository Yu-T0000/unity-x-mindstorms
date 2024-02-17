# firmware provided via https://beta.pybricks.com/
from pybricks.hubs import InventorHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port,Color, Stop, Button
from pybricks.tools import wait

# Standard MicroPython modules
import ustruct
from usys import stdin, stdout
from uselect import poll

class activate_motor:

    angle = 0
    message = ""

    def __init__(self,port):
        self.port = port
        self.mortor = ""
        self.angle = 0
        if port == "A":
            self.motor = Motor(Port.A)
        elif port == "B":
            self.motor = Motor(Port.B)
        elif port == "C":
            self.motor = Motor(Port.C)
        elif port == "D":
            self.motor = Motor(Port.D)
        elif port == "E":
            self.motor = Motor(Port.E)
        elif port == "F":
            self.motor = Motor(Port.F)
        else:
            print("none")
        self.motor.run_target(90,0,then = Stop.COAST)
    
    def running(self, cmd, spd):
        #runよりdcの方がいいかも 要検討
        if cmd == b"fwd":
            self.motor.run(spd)
        elif cmd == b"rev":
            self.motor.run(-1*spd)
        elif cmd == b"hld":
            self.motor.hold()
        elif cmd == b"stp":
            self.motor.stop()
    
    def mesure_360(self,address: bytes): #0~360の値を送る
        angle = self.motor.angle() % 360
        message = ustruct.pack('!10sf', address, angle)
        stdout.buffer.write(message)
        wait(15)

    def mesure_180(self,address: bytes): #-179~180の値を送る
        angle = (self.motor.angle() + 180) % 360 - 180
        message = ustruct.pack('!10sf', address, angle)
        stdout.buffer.write(message)
        wait(15)

    def button_check(self,address: bytes):
        angle = (self.motor.angle() + 180) % 360 - 180
        message = ustruct.pack('!10s6s', address, b"push")
        if angle > -17:
            self.is_push = True
        if angle < -18:
            if self.is_push:
                stdout.buffer.write(message)
                self.is_push = False
            self.motor.run_target(500, 2, Stop.COAST, False)
    
    def button_control(self, cmd):
        if cmd == b"hld":
            self.motor.run_target(500, 1, Stop.HOLD, False)
        elif cmd == b"psh":
            self.motor.run_target(500, -15, Stop.COAST, False)

class activate_Csensor:
    #カラーセンサ
    message = ""
    msg = ""

    def __init__(self,port):
        self.port = port
        self.C_sensor = ""
        if port == "A":
            self.C_sensor = ColorSensor(Port.A)
        elif port == "B":
            self.C_sensor = ColorSensor(Port.B)
        elif port == "C":
            self.C_sensor = ColorSensor(Port.C)
        elif port == "D":
            self.C_sensor = ColorSensor(Port.D)
        elif port == "E":
            self.C_sensor = ColorSensor(Port.E)
        elif port == "F":
            self.C_sensor = ColorSensor(Port.F)
        else:
            print("none")
    
    def send_color(self,address: bytes):
        _Color = self.C_sensor.color()
        if _Color == Color.RED:
            self.msg = b"RED"
        elif _Color == Color.YELLOW:
            self.msg = b"YELLOW"
        elif _Color == Color.GREEN:
            self.msg = b"GREEN"
        elif _Color == Color.BLUE:
            self.msg = b"BLUE"
        elif _Color == Color.WHITE:
            self.msg = b"WHITE"
        elif _Color == Color.NONE:
            self.msg = b"NONE"
        message = ustruct.pack("!10s6s", address, self.msg)
        stdout.buffer.write(message)
        wait(15)

#使うモーター、センサーの指定

hub = InventorHub()
motorA = activate_motor("A")
motorB = activate_motor("B")
sensor = activate_Csensor("C")

#ここまで


# Optional: Register stdin for polling. This allows
# you to wait for incoming data without blocking.
keyboard = poll()
keyboard.register(stdin)

while True:

    
    while not keyboard.poll(0):
        #ここで送りたいデータを宣言
        motorA.mesure_360(b"/add")
        motorB.mesure_360(b"/add2")
        sensor.send_color(b"/add3")
        #ここまで
        

    # Read bytes.
    try:
        msg = stdin.buffer.read(8)
        port, cmd, spd = ustruct.unpack('!s3sf',msg)
    except Exception as e:
        stdout.buffer.write(msg)
        #stdout.buffer.write(bytearray(e, encode = 'utf-8'))
        stdout.buffer.write(b'The program was stopped')

    # どのモーターにどんな動きをさせるか宣言
    if port == b"A":
        motorA.running(cmd, spd)
    elif port == b"B":
        motorB.running(cmd, spd)
    # ここまで

    if cmd == b"bye":
        break



