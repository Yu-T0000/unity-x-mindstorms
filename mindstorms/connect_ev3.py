#!/usr/bin/env python3
from time import sleep
import paho.mqtt.client as mqtt
from ev3dev2.motor import *
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor
from ev3dev2.sensor import *
import struct

port = ""
cmd = ""
spd = 0
get_data = False


class activate_motor:

    angle = 0
    message = b" "

    def __init__(self,port,client):
        self.port = port
        self.mortor = ""
        self.angle = 0
        self.client = client
        if port == "A":
            self.motor = Motor(OUTPUT_A)
        elif port == "B":
            self.motor = Motor(OUTPUT_B)
        elif port == "C":
            self.motor = Motor(OUTPUT_C)
        elif port == "D":
            self.motor = Motor(OUTPUT_D)
        else:
            print("none")
        self.motor.run_to_abs_pos(position_sp=0, speed_sp=50, stop_action='brake')
    
    def running(self, cmd, spd):
        #runよりdcの方がいいかも 要検討
        if cmd == b"fwd":
            self.motor.run_forever(speed_sp=spd)
        elif cmd == b"rev":
            self.motor.run_forever(speed_sp= -1 * spd)
        elif cmd == b"hld":
            self.motor.stop(stop_action='hold')
        elif cmd == b"stp":
            self.motor.stop(stop_action='brake')
    
    def mesure_360(self,address: bytes): #0~360の値を送る
        angle = self.motor.position - (self.motor.position // 360) * 360 #360超える
        message = struct.pack('!10pf', address, angle)
        self.client.publish('ev3/data', message)
        sleep(0.01)

    def mesure_180(self,address: bytes): #-179~180の値を送る
        angle = ((self.motor.position - (self.motor.position // 360) * 360) + 180) % 360 -180
        message = struct.pack('!10pf', address, angle)
        self.client.publish('ev3/data', message)
        sleep(0.01)

class activate_Csensor:
    #カラーセンサ
    message = ""
    msg = ""

    def __init__(self,port,client):
        self.port = port
        self.C_sensor = None
        self.client = client
        if port == "S1":
            self.C_sensor = ColorSensor(INPUT_1)
        elif port == "S2":
            self.C_sensor = ColorSensor(INPUT_2)
        elif port == "S3":
            self.C_sensor = ColorSensor(INPUT_3)
        elif port == "S4":
            self.C_sensor = ColorSensor(INPUT_4)
        else:
            print("none")
    
    def send_color(self,address: bytes):
        _Color = self.C_sensor.color
        if _Color == 0:
            self.msg = b"NONE"
        elif _Color == 1:
            self.msg = b"BLACK"
        elif _Color == 2:
            self.msg = b"BLUE"
        elif _Color == 3:
            self.msg = b"GREEN"
        elif _Color == 4:
            self.msg = b"YELLOW"
        elif _Color == 5:
            self.msg = b"RED"
        elif _Color == 6:
            self.msg = b"WHITE"
        elif _Color == 7:
            self.msg = b"BROWN"
        message = struct.pack("!10p6p", address, self.msg)
        self.client.publish('ev3/data', message)
        sleep(0.01)

class activate_USsensor:
    #距離センサ
    #だいぶ重いので非推奨
    message = ""
    msg = ""

    def __init__(self,port,client):
        self.port = port
        self.US_sensor = None
        self.client = client
        if port == "S1":
            self.US_sensor = UltrasonicSensor(INPUT_1)
        elif port == "S2":
            self.US_sensor = UltrasonicSensor(INPUT_2)
        elif port == "S3":
            self.US_sensor = UltrasonicSensor(INPUT_3)
        elif port == "S4":
            self.US_sensor = UltrasonicSensor(INPUT_4)
        else:
            print("none")
    
    def send_distance(self,address: bytes):
        _dist = round(self.US_sensor.distance_centimeters)
        message = struct.pack('!10pf', address, _dist)
        self.client.publish('ev3/data', message)
        sleep(0.001)


class MQTTev3(mqtt.Client):
    def __init__(self):
        super().__init__()
        self.protocol = mqtt.MQTTv311

    def run(self, hostname, topic):
        self.connect(hostname, port=1883, keepalive=60)
        self.subscribe(topic, 0)
        self.loop_start()



def on_message(client, userdata, msg):
    global port
    global cmd
    global spd
    global get_data
    try:
        port, cmd, spd = struct.unpack('!s3sf',msg.payload)
        get_data = True
        print(msg.topic + ' ' + port + ' ' + cmd  + ' ' + spd)
    except:
        pass



if __name__ == '__main__':

    print('run conev3.py :)')

    client = MQTTev3()
    client.on_message = on_message
    client.run('127.0.0.1','unity/con')

    motorA = activate_motor("A",client)
    #motorB = activate_motor("B",client)
    #ensor = activate_Csensor("S1",client)

    while True:
        while not(get_data):
            motorA.mesure_180(b"/move")
            #motorB.mesure_180(b"/add2")
            #sensor.send_color(b"/add3")

        get_data = False
        if port == b"A":
            motorA.running(cmd, spd)
        elif port == b"B":
            #motorB.running(cmd, spd)
        elif port == b"X":
            #motorA.running(cmd, spd)
            #motorB.running(cmd, spd)

    client.disconnect()