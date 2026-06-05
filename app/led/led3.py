import asyncio
from bleak import BleakScanner, BleakClient
import time 
async def main():
    while True:
        myDevice = ''
        devices = await BleakScanner.discover(1.0, return_adv=True)
        for d in devices:
            print(d, devices[d][1].local_name)
            # if(devices[d][1].local_name == 'iPhone'):
            #     print("Found it")
            #     myDevice = d
            
        time.sleep(1)

        # address = myDevice
        # async with BleakClient(address) as client:
        #     svcs = client.services
        #     print("Services:")
        #     for service in svcs:
        #         print(service)


asyncio.run(main())