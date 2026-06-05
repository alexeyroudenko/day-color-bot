# import asyncio
# from bleak import BleakScanner
# async def main():
#     devices = await BleakScanner.discover(10.0, return_adv=True)
#     for d in devices:
#         print(d)
# asyncio.run(main())


import asyncio
from bledom.device import BleLedDevice
from bleak import BleakScanner, BleakClient
import time
import json

ELK = "ELK-BLEDOB"
MELK = "MELK-OA00005"
URL = "http://192.168.31.18:5000/state_info/"


def get_colors():
    import requests
    json_data = requests.get(URL).json()
    print(json_data)
    return json_data

def hex_to_rgb(hex):
  rgb = []
  for i in (0, 2, 4):
    decimal = int(hex[i:i+2], 16)
    rgb.append(decimal)
    return tuple(rgb)
        
def get_color(h):
    hh = h.lstrip('#')
    print(hh)
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    print('RGB =', rgb)
    return rgb
 
def get_state():
    colors = get_colors()
    color1 = get_color(colors[0].lstrip('#'))
    color2 = get_color(colors[1].lstrip('#'))
    return [color1, color2]

async def main():
    print("start look leds")
    c = 0
    color1 = (255,0,0)
    color2 = (255,0,0)
    
    # colors = get_state()
    # color1 = colors[0]
    # color2 = colors[1]
    
    device1 = None
    
    for device in await BleakScanner.discover(timeout = 15):
        print(device.name)
        
        if device.name == ELK:
            client = BleakClient(device)
            await client.connect()
            svcs = client.services
            print("Services:")
            for service in svcs:
                print(service)

            device = await BleLedDevice.new(client)
            
            # COUNT = 100
            # while True:
            #     if c % 100 == COUNT-1:
            #         colors = get_state()
            #         color1 = colors[0]
            #         color2 = colors[1]
            #         print(f"colors {color1} {color2}")
            #     time.sleep(.01)
            #     color = (c*5) % 255
            #     print(f"send {c} {color1}, {color2}")
            #     await device.set_color(color1[0],color1[1],int(color1[2]/25))
            #     c = c+1

        # await device.power_off()


# colors = get_state()
# color1 = colors[0]
# color2 = colors[1]
# print(f"colors {color1} {color2}")

asyncio.run(main())

