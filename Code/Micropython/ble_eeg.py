#code for connecting the eeg via bluetoth for ddata collection
#not live version
import bluetooth
import ble_simple_peripheral as BLESimplePeripheral
from machine import Pin, ADC
import time


# eeg data
adc = ADC(Pin(13))
adc.atten(ADC.ATTN_11DB)
big_boi_string=""
ble = bluetooth.BLE()
p = BLESimplePeripheral.BLESimplePeripheral(ble)
RECORD=False

l=[]
def split_string(s,n=15):
    return [s[i:i+n] for i in range(0,len(s),n)]
def on_rx(v):
    global p
    global l
    global RECORD
    global start_time
    global big_boi_string
    print(v)
    if v==b"RECORD":
        RECORD=True
        start_time=time.ticks_ms()
    elif v==b"GIVE ME":
        l=split_string(big_boi_string,100)
        print("LINES",len(big_boi_string.split("\n")))
        big_boi_string=""
        RECORD=False
        p.send(str(len(l)))
    elif b"GIVE_MANY" in v:
        v=v.decode("utf-8")
        v=v.replace("GIVE_MANY","")
        v=int(v)
        p.send(str(v)+"--"+l[v])
    print("RECORDING:",str(RECORD))
p.on_write(on_rx)

start_time=time.ticks_ms()
while True:
    if p.is_connected():
        # Short burst of queued notifications.
        if RECORD:
            data = adc.read()
            big_boi_string+=str(time.ticks_ms()-start_time)+","+str(data)+"\n"
        
        time.sleep_ms(40)

