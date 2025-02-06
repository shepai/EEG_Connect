import asyncio
from bleak import BleakClient, BleakScanner
import bleak
import time
import cv2
import gc
gc.collect()

async def connect_to_esp():
    devices = await BleakScanner.discover()
    def gather_device():
        
        for device in devices:
            print(device)  # Look for your ESP32 in the list
    def save(filename,data):
        file=open(filename+".csv","w") #open csv
        file.write(str(data)) #save data in bulk
        file.close()
    t1=time.time()


    recording=False
    print("Press 'r' to start recording, 's' to stop, and 'q' to quit.")
    quitted=False
    while not quitted:
        devices = await BleakScanner.discover()
        try:
            data_csv=""
            filename=""
            esp_address = "A0:B7:65:63:C8:92"  # Replace with your ESP32's MAC address
            async with BleakClient(esp_address) as client:
                print(f"Connected to {esp_address}")

                services = await client.get_services()
                for service in services:
                    print(service)

                # Example: Read/write characteristic UUID
                char_uuid_write = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Replace with actual UUID
                await client.write_gatt_char(char_uuid_write, b"Hello ESP32!")
                char_uuid_read = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Replace with actual UUID
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = None
                recording = False
                cap = cv2.VideoCapture(0)
                while not quitted: #once successfully connected loop forever (till erros happen)
                    ret, frame = cap.read()
                    if not ret:
                        break
                    cv2.imshow('Video Feed', frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('r') and not recording: #if r key pressed begin recording
                         await client.write_gatt_char(char_uuid_write, b"RECORD")
                         filename = f"recording_{time.strftime('%Y%m%d_%H%M%S')}"
                         print(f"Recording started: {filename}")
                         out = cv2.VideoWriter(filename+".avi", fourcc, 20.0, (frame.shape[1], frame.shape[0])) #save data
                         recording = True
                    if key == ord('s') and recording: #if s pressed stop recording
                         print("Recording stopped.")
                         decoded=""
                         while decoded=="":
                             await client.write_gatt_char(char_uuid_write, b"GIVE ME") #send request for data
                             data = await client.read_gatt_char(char_uuid_read)
                             decoded=str(data.decode('utf-8'))
                         num=int(decoded)
                         print("EXPECTING",num,"data packets")
                         data_csv=""
                         l=0
                         added=[]
                         while l<num: #wait for data to come
                             await client.write_gatt_char(char_uuid_write, ("GIVE_MANY"+str(l)).encode("utf-8"))
                             data = await client.read_gatt_char(char_uuid_read)
                             decoded=str(data.decode('utf-8'))
                             decoded=decoded.split("--")
                             if len(decoded)>0 and int(decoded[0])==l and int(decoded[0]) not in added:
                                 data_csv+=decoded[1]
                                 added.append(l)
                                 l+=1
                             
                         print(l,"packets recieved")
                         recording = False
                         out.release()
                         out = None
                         save(filename,data_csv)
                    if recording and out is not None:
                         out.write(frame)

                    if key == ord('q'):  # Press 'q' to exit
                         quitted=True
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
