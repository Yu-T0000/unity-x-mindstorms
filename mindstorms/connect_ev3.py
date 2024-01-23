#!/usr/bin/env python3
from time import sleep
import paho.mqtt.client as mqtt
from ev3dev2.motor import *
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
        print(address,angle)
        message = struct.pack('!10pf', address, angle)
        self.client.publish('ev3/data', message)
        sleep(0.1)

    def mesure_180(self,address: bytes): #-179~180の値を送る
        angle = ((self.motor.position - (self.motor.position // 360) * 360) + 180) % 360 -180
        print(address,angle)
        message = struct.pack('!10pf', address, angle)
        self.client.publish('ev3/data', message)
        sleep(0.1)


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

    client = MQTTev3()
    client.on_message = on_message
    client.run('127.0.0.1','unity/con')

    motorA = activate_motor("A",client)
    motorB = activate_motor("B",client)

    print('run conev3.py :)')

    while not (cmd == b'bye'):
        while not(get_data):
            motorA.mesure_360(b"/add1")
            motorB.mesure_180(b"/add2")
        get_data = False
        if port == b"A":
            motorA.running(cmd, spd)
        elif port == b"B":
            motorB.running(cmd, spd)

    client.disconnect()