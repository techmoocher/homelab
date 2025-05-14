from machine import ADC, Pin
from time import sleep, time
import dht
import urequests
import network


SSID = input("SSID: ")
PASSWORD = input("Password: ")
API_KEY_WRITE = "some_api_write"
API_KEY_READ = "some_api_read"
CHANNEL_ID = "some_id"

dht_sensor = dht.DHT11(Pin(32))
light_sensor = ADC(Pin(33))
light_sensor.atten(ADC.ATTN_11DB)
#led1 = Pin(34, Pin.OUT)
print()

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    start_time = time();
    while not wlan.isconnected():
        print("Connecting to WiFi......")
        sleep(1)
    end_time = time();
    elapsed_time = end_time - start_time
    print("Successfully connected to WiFi!")
    print(f"Total time costed: {elapsed_time:.2f} seconds")
    print()
    print("IP Address: ", end="")
    print(wlan.ifconfig())
    
def send_data(temp, humidity, light):
    request = "https://api.thingspeak.com/update?api_key={}&field1={}&field2={}&field3={}"
    request= request.format(API_KEY_WRITE, temp, humidity, light)
    
    response = urequests.get(request)
    response.close()
    print("Sent data: Temperature={}, Humidity={}, Light={}".format(temp, humidity, light))
    
    
connect_wifi()
while True:
    dht_sensor.measure()
    temp = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    light_value = light_sensor.read()
    
    #led1.on()
    send_data(temp, humidity, light_value)
    #led1.off()
    
    sleep(10)
