import asyncio
from bleak import BleakClient, BleakScanner
import bleak
import time

async def connect_to_esp():
    devices = await BleakScanner.discover()
    def gather_device():
        for device in devices:
            print(device)  # Look for your ESP32 in the list
    while 1:
        try:
            esp_address = "30:C6:F7:22:D0:12"  # Replace with your ESP32's MAC address
            async with BleakClient(esp_address) as client:
                print(f"Connected to {esp_address}")

                services = await client.get_services()
                for service in services:
                    print(service)

                # Example: Read/write characteristic UUID
                char_uuid_write = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Replace with actual UUID
                await client.write_gatt_char(char_uuid_write, b"Hello ESP32!")
                char_uuid_read = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Replace with actual UUID
                data = await client.read_gatt_char(char_uuid_read)
                print("Received from ESP:", data)
                for i in range(100):
                    await client.write_gatt_char(char_uuid_write, b"Hello ESP32!")
                    data = await client.read_gatt_char(char_uuid_read)
                    print("Received from ESP:", data)
                    time.sleep(0.1)
        except bleak.exc.BleakDeviceNotFoundError:
            gather_device()
        except OSError:
            gather_device()
        except asyncio.exceptions.TimeoutError:
            gather_device()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            gather_device()


asyncio.run(connect_to_esp())
