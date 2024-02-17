import sys
import socket
import asyncio
import argparse
from typing import List,Any
from pythonosc import dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from struct import *
import paho.mqtt.client as mqtt

#oscメッセージを送る先のサーバーとポート(unity)
ip = socket.gethostbyname(socket.gethostname())
port = 9000
oscclient = SimpleUDPClient(ip, port)

#このサーバーのipとポート
parser = argparse.ArgumentParser()
parser.add_argument("--ip",
default=ip, help="The ip to listen on")
parser.add_argument("--port",
type=int, default=9067, help="The port to listen on")
args = parser.parse_args()


#UnityとのOSCデータのやり取り設定
accept = False
message = ""

def printdata(address: str, *osc_arguments: List[str]):
    print(address + "  " + str(osc_arguments[0]))


def move_mortor(address: str, *osc_arguments: List[Any]):
    if not len(osc_arguments) == 2 or type(osc_arguments[0]) is not str:
        print("引数は(コマンド),(速度)!")
        return
    global accept
    global message

    command, value = osc_arguments
    print(address + "  " + command + " " + str(value))
    if address == "/motorA":
        port = b"A"
    elif address == "/motorB":
        port = b"B"
    elif address == "/motorC":
        port = b"C"
    elif address == "/motorD":
        port = b"D"
    elif address == "/motorAll":
        port = b"X"
    else:
        pass
    
    try:
        message = pack('!s3sf',port,bytes(command, encoding='utf-8'),value)
    except Exception as e:
        print(e)
        pass
    else:
        accept = True
        port, cmd, spd = unpack('!s3sf',message)
        print(port,cmd,spd)


def disconnect():
    global accept
    global message
    message = pack('3s3sf',b"A",b"bye","00")
    accept = True


dispatcher = dispatcher.Dispatcher()
dispatcher.map("/pythonosc", printdata) #確認用
dispatcher.map("/motor*", move_mortor) #/motor(任意のポートA~F)アドレス宛のOSCメッセージを受け取ったらモーター動かす
dispatcher.map("/exit", disconnect)



async def communicate_hub():
    global accept
    def on_connect(client, userdata, flags, respons_code):
        print('status {0}'.format(respons_code))
        client.subscribe('ev3/data')
    
    def on_disconnect(client, userdata, flags, respons_code):
        print("end")
        sys.exit()

    def on_message(client, userdata, msg):
        #ev3からのデータを送る部分
        if msg.payload == b'bye':
            sys.exit()
        else:
            try:
                #角度
                add, value = unpack("!10pf",msg.payload)
            except:
                try:
                    #カラーセンサ
                    add, value = unpack("!10p6p",msg.payload)
                    value = value.decode('utf-8')
                except (ValueError,Exception) as e:
                        print(e)
                else:pass
            try:
                add = add.strip(b"\x00").decode('utf-8')
                print(add,value)
                oscclient.send_message(add,value)
            except:pass
    
    
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect_async("ev3dev.local", port=1883, keepalive=60)
    client.loop_start()
    while True:
        try:
            while True:
                await asyncio.sleep(0)
                if(accept):
                    client.publish('unity/con', message)
                    accept = False
                    await asyncio.sleep(0.01)
        except Exception as e:
            print(e)
            print("なんかエラー起きてるので再起動してください")
            client.disconnect()
            break

    
                

    
async def main():
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving
    print("connecting...")
    await communicate_hub()

    transport.close()

if __name__ == '__main__':
    asyncio.run(main())

