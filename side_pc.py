import sys
import asyncio
from bleak import BleakScanner, BleakClient
import argparse
from typing import List,Any
from contextlib import suppress
from pythonosc import dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from struct import *

#oscメッセージを送る先のサーバーとポート
ip = "127.0.0.1"
port = 9000
oscclient = SimpleUDPClient(ip, port)

#このサーバーのipとポート
parser = argparse.ArgumentParser()
parser.add_argument("--ip",
default="127.0.0.1", help="The ip to listen on")
parser.add_argument("--port",
type=int, default=9067, help="The port to listen on")
args = parser.parse_args()

# MindstormsのハブとのBLE通信設定
PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"
HUB_NAME = "Pybricks Hub"

# UnityとのOSCデータのやり取り設定
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
    elif address == "/motorE":
        port = b"E"
    elif address == "/motorF":
        port = b"F"
    else:
        pass
    
    try:
        message = pack('!c3sf',port,bytes(command, encoding='utf-8'),value)
    except Exception as e:
        print(e)
        pass
    else:
        accept = True
        port, cmd, spd = unpack('!c3sf',message)
        #print(port,cmd,spd)

def controll_Hub():
    #まだ使わないのであとで書く
    pass

def disconnect():
    global accept
    global message
    message = pack('!c3sf',b"A",b"bye","00")
    accept = True
    print(unpack('!c3sf',message))


dispatcher = dispatcher.Dispatcher()
dispatcher.map("/pythonosc", printdata) #確認用
dispatcher.map("/motor*", move_mortor) #/motor(任意のポートA~F)アドレス宛のOSCメッセージを受け取ったらモーター動かす
dispatcher.map("/exit", disconnect)
    

async def communicate_hub():
    global message
    main_task = asyncio.current_task()
    
    def handle_disconnect(_):
        print("Hub was disconnected.")
        if not main_task.done():
            sys.exit()
            

    
    async def handle_rx(_, data: bytearray):
        if data[0] == 0x01:
            payload = data[1:]

            if b'The program was stopped' in payload:
                sys.exit()
            if len(payload) == 16: #カラーセンサ
                try:
                    add, value = unpack("!10p6p",payload)
                    value = value.strip(b"\x00").decode('utf-8')
                except (ValueError,Exception) as e:
                        print(e)
                else:pass
            else: #モーターの角度
                try:
                    add, value = unpack("!10pf",payload)
                except (ValueError,Exception) as e:
                        print(e)
                else:pass
            add = "/" + add.strip(b"\x00").decode('utf-8')
            oscclient.send_message(add,value)
                

    print("searching...")
    device = await BleakScanner.find_device_by_name(HUB_NAME,timeout= 15)

    if device is None:
        print(f"could not find hub with name: {HUB_NAME}")
        return
    
    async with BleakClient(device, handle_disconnect) as client:

        async def send(data):
            global accept
            try:
                if accept:
                    await client.write_gatt_char(
                        PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                        b"\x06" + data,  # 多分ACK(0x06 肯定応答)なるもの
                        response=True
                    )
                    accept = False
            except Exception as e:
                print(e)
                pass

        print("Start the program on the hub now with the button.")
        await client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)
        while True:
            try:
                await send(message)
                await asyncio.sleep(0.02)

            except Exception as e:
                print(e)
                await asyncio.sleep(1)
                pass

async def main():
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()
    
    await communicate_hub()

    transport.close()



asyncio.run(main())