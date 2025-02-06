import asyncio
from bleak import BleakClient, BleakScanner
import bleak
import time
import cv2

async def connect_to_esp():
    devices = await BleakScanner.discover()
    def gather_device():
        
        for device in devices:
            print(device)  # Look for your ESP32 in the list
    def save(filename,data):
        print(data)
        file=open(filename+".csv","w") #open csv
        file.write(str(data)) #save data in bulk
        file.close()
    t1=time.time()

    cap = cv2.VideoCapture(0)
    # Define codec
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    
    print("Press 'r' to start recording, 's' to stop, and 'q' to quit.")
    while 1:
        devices = await BleakScanner.discover()
        try:
            data_csv=""
            filename=""
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
                out = None
                recording = False
                while 1: #once successfully connected loop forever (till erros happen)
                    ret, frame = cap.read() #read camera
                    if not ret: #if camera breaks 
                         break
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('r') and not recording: #if r key pressed begin recording
                         await client.write_gatt_char(char_uuid_write, b"RECORD")
                         filename = f"recording_{time.strftime('%Y%m%d_%H%M%S')}"
                         print(f"Recording started: {filename}")
                         out = cv2.VideoWriter(filename+".avi", fourcc, 20.0, (frame.shape[1], frame.shape[0])) #save data
                         recording = True
                    if key == ord('s') and recording: #if s pressed stop recording
                         print("Recording stopped.")
                         await client.write_gatt_char(char_uuid_write, b"GIVE ME") #send request for data
                         data=""
                         while data=="": #wait for data to come
                             data = str(await client.read_gatt_char(char_uuid_read).decode('utf-8'))
                             print("Received from ESP:", data)
                         recording = False
                         out.release()
                         out = None
                         save(filename,data_csv)
                    if recording and out is not None:
                         out.write(frame)

                    if key == ord('q'):  # Press 'q' to exit
                         break
                    #time.sleep(0.1)
        except bleak.exc.BleakDeviceNotFoundError:
            gather_device()
            if recording:
                out = cv2.VideoWriter(filename+".avi", fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                save(filename,data_csv)
        except OSError:
            gather_device()
            if recording:
                out = cv2.VideoWriter(filename+".avi", fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                save(filename,data_csv)
        except asyncio.exceptions.TimeoutError:
            gather_device()
            if recording:
                out = cv2.VideoWriter(filename+".avi", fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                save(filename,data_csv)
        except KeyboardInterrupt:
            if recording:
                out = cv2.VideoWriter(filename+".avi", fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                save(filename,data_csv)
            break
        except Exception as e:
            if recording:
                out = cv2.VideoWriter(filename+".avi", fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                save(filename,data_csv)
            print(e)
            gather_device()


asyncio.run(connect_to_esp())
