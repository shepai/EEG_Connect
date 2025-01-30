import asyncio
from bleak import BleakClient, BleakScanner
import bleak
import time
import cv2
import numpy as np

async def connect_to_esp():
     devices = await BleakScanner.discover()

     for device in devices:
          print(device)  # Look for your ESP32 in the list

     esp_address = "30:C6:F7:22:D0:12"  # Replace with your ESP32's MAC address
     connected=False
     while not connected:
          try:
               client = BleakClient(esp_address)
               await client.connect()
               print(f"Connected to {esp_address}")
               connected=True
          except bleak.exc.BleakDeviceNotFoundError:
               pass

     services = await client.get_services()
     for service in services:
          print(service)
     # Example: Read/write characteristic UUID
     char_uuid_write = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Replace with actual UUID
     await client.write_gatt_char(char_uuid_write, b"Hello ESP32!")
     char_uuid_read = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Replace with actual UUID
     data = await client.read_gatt_char(char_uuid_read)
     print("Received from ESP:", data)
     # Initialize camera
     cap = cv2.VideoCapture(0)

     # Define codec
     fourcc = cv2.VideoWriter_fourcc(*'XVID')
     out = None
     recording = False
     data=[]
     print("Press 'r' to start recording, 's' to stop, and 'q' to quit.")

     while True:
          ret, frame = cap.read()
          if not ret:
               break
          
          cv2.imshow('Video Feed', frame)

          key = cv2.waitKey(1) & 0xFF

          if key == ord('r') and not recording:
               filename = f"recording_{time.strftime('%Y%m%d_%H%M%S')}"
               print(f"Recording started: {filename}")
               out = cv2.VideoWriter(filename+".avi", fourcc, 20.0, (frame.shape[1], frame.shape[0]))
               recording = True
               data_read = await client.read_gatt_char(char_uuid_read)
               print("Received from ESP:", data_read)
               data.append([time.time(),data_read])
          if key == ord('s') and recording:
               print("Recording stopped.")
               recording = False
               np.save(filename,np.array(data))
               out.release()
               out = None
               data=[]
          if recording and out is not None:
               out.write(frame)

          if key == ord('q'):  # Press 'q' to exit
               break

     # Cleanup
     cap.release()
     if out is not None:
          out.release()
     cv2.destroyAllWindows()



asyncio.run(connect_to_esp())
