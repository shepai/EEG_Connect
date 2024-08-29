# Bluetooth client
# Code by:
#    Dexter R Shepherd
#
#
# Combined bluetooth capabilities into a singular class for micropython (ESP or Pico W)
from micropython import const
import asyncio
import aioble
import bluetooth
import struct
from machine import Pin
from random import randint

class ble_device:
    def __init__(self):
        self._BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
        self._BLE_SENSOR_CHAR_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')
        self._BLE_LED_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')
        # How frequently to send advertising beacons.
        self._ADV_INTERVAL_MS = 250_000

        # Register GATT server, the service and characteristics
        self.ble_service = aioble.Service(self._BLE_SERVICE_UUID)
        self.sensor_characteristic = aioble.Characteristic(self.ble_service, self._BLE_SENSOR_CHAR_UUID, read=True, notify=True)
        self.led_characteristic = aioble.Characteristic(self.ble_service, self._BLE_LED_UUID, read=True, write=True, notify=True, capture=True)

        # Register service(s)
        aioble.register_services(self.ble_service)
    async def peripheral_task(self):
        while True:
            try:
                async with await aioble.advertise(
                    self._ADV_INTERVAL_MS,
                    name="EEG_dude",
                    services=[self._BLE_SERVICE_UUID],
                    ) as connection:
                        print("Connection from", connection.device)
                        await connection.disconnected()             
            except asyncio.CancelledError:
                # Catch the CancelledError
                print("Peripheral task cancelled")
            except Exception as e:
                print("Error in peripheral_task:", e)
            finally:
                # Ensure the loop continues to the next iteration
                await asyncio.sleep_ms(100)
    async def sensor_task(self):
        while True:
            self.sensor_characteristic.write(str(0).encode('utf-8'), send_update=True)
            #print('New random value written: ', value)
            await asyncio.sleep_ms(1000)
    
bd=ble_device()
async def main():
    t1 = asyncio.create_task(bd.sensor_task())
    t2 = asyncio.create_task(bd.peripheral_task())
    await asyncio.gather(t1, t2)

asyncio.run(main())