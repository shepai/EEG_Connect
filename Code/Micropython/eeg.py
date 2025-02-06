#collect eeg data
from machine import Pin, ADC
import time
adc = ADC(Pin(13))
adc.atten(ADC.ATTN_11DB)
start = Pin(32, Pin.IN,Pin.PULL_DOWN)  # Button connected to pin 
end = Pin(33, Pin.IN,Pin.PULL_DOWN)  # Button connected to pin 
close = Pin(10, Pin.IN,Pin.PULL_DOWN)  # Button connected to pin 
file_num=0
break_clause=False
collect=False
f=None
start_time=0

if __name__ == '__main__':
    while not break_clause:
        if start.value()==1 and not collect: #start selected
            print("Collecting...")
            f=open('data'+str(file_num)+'.csv','w')
            start_time = time.ticks_ms()
            collect=True
        if end.value()==1 and collect: #end selected
            print("Saving...")
            f.close()
            collect=False
            file_num+=1
        if close.value()==1: break_clause=True
        if collect: #read sensor and save
            end_time = time.ticks_ms()
            sensor = adc.read()
            print(sensor)
            f.write(str((end_time-start_time)/1000)+","+str(sensor)+"\n")
        time.sleep(0.05)
        
