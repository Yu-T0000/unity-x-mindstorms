import sys
import socket
import asyncio
from bleak import BleakScanner, BleakClient
import argparse
from typing import List,Any
from pythonosc import dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from struct import *

#oscメッセージを送る先のサーバーとポート
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

# MindstormsのハブとのBLE通信設定
PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"
HUB_NAME = "Pybricks Hub"

# UnityとのOSCデータのやり取り設定
accept = False
message = ""
add = None

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
    elif address == "/motorAll":
        port = b"X"
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
        print(port,cmd,spd)


def disconnect():
    sys.exit()


dispatcher = dispatcher.Dispatcher()
dispatcher.map("/*", printdata) #確認用
dispatcher.map("/motor*", move_mortor) #/motor(任意のポートA~F)アドレス宛のOSCメッセージを受け取ったらモーター動かす
dispatcher.map("/exit", disconnect)
    

async def communicate_hub():
    global message
    main_task = asyncio.current_task()
    
    def handle_disconnect(_):
        print("Hub was disconnected.")
        if not main_task.done():
            sys.exit()
            main_task.cancel()
    
    ready_event = asyncio.Event()
    
    async def handle_rx(_, data: bytearray):
        global add
        if data[0] == 0x01:
            payload = data[1:]

            if b'The program was stopped' in payload:
                sys.exit()
            elif payload == b"rdy":
                ready_event.set()

            else:
                try:
                    #角度
                    add, value = unpack("!10pf",payload)
                except:
                    try:
                        #カラーセンサ
                        add, value = unpack("!10p6s",payload)
                        value = value.strip(b"\x00").decode('utf-8')
                        
                    except (ValueError,Exception) as e:
                        #print(e)
                        pass
                    else:pass
                if add is not None: 
                    try:
                        add = "/" + add.strip(b"\x00").decode('utf-8')
                        oscclient.send_message(add,value)
                        print(add,value)
                    except:pass
                else:pass
                
                

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
                        b"\x06" + data,  # prepend "write stdin" command (0x06)
                        response=True
                    )
                    accept = False
            except Exception as e:
                print(e)
                pass

        print("Start the program on the hub now with the button.")
        await client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)
        print(":)")
        while True:
            try:
                await send(message)
                print(message)
                await asyncio.sleep(0.02)

            except Exception as e:
                print(e)
                await asyncio.sleep(1)
                pass

async def main():
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving
    
    await communicate_hub()

    transport.close()


# Run the main async program.
if __name__ == '__main__':
    asyncio.run(main())