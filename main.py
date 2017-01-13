#upython standard libraries
import sys, utime, ujson, gc, micropython, network, machine, ntptime

#local imports
import network_setup
from time_manager import TimeManager
from data_stream import DataStreamClient

#DEBUG = False
DEBUG = True

WEEKDAYS = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

#read the SECRET configuration file, NOTE this contains PRIVATE keys and 
#should never be posted online
config = ujson.load(open("SECRET_CONFIG.json",'r'))

#connect to the network
sta_if, ap_if = network_setup.do_connect(**config["network_settings"])

#configure the persistent data stream client
dbs = config['database_server_settings']
dsc = DataStreamClient(host=dbs['host'],
                       port=dbs['port'],
                       public_key=dbs['public_key'],
                       private_key=dbs['private_key'])

TM = TimeManager()
print(TM.get_datetime())

#GPIO setup
led_pin  = machine.Pin(2, machine.Pin.OUT)
lamp_pin = machine.Pin(15, machine.Pin.OUT)

def pulse_led(duration_ms = 1000):
    led_pin.low() #is active low on Feather HUZZAH
    utime.sleep_ms(500)
    led_pin.high()
    
pulse_led(1000)


d = {} #stores sample data
while True:
    start_ms = utime.ticks_ms()
    previous_connection_state = True
    try:
        #check to see if we are still connected
        if sta_if.isconnected():
            print("Network is connected.")
            pulse_led(500)
        else: #have no network connection
            print("Network is down!")
            if previous_connection_state == True: #we were just connected last iteration
                pass
            pulse_led(500)
            utime.sleep_ms(500)
            pulse_led(500)
        
        dt = TM.get_datetime() #(year, month, weekday, hour, min, second, millisecond)
        if DEBUG:
            print("raw dt =",dt)
        year, month, day, weekday, hour, minute, second, millisecond = dt
        local_hour = (hour + config['main_loop_settings']['tz_hour_shift']) % 24
        d['local_hour']    = local_hour
        d['rtc_timestamp'] = "{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}".format(
              year=year, month=month, day=day, hour=hour, minute=minute, second=second)
        print("The day of the week is {day_name} and the local hour is {local_hour:d}.".format(day_name=WEEKDAYS[weekday], local_hour = local_hour))
        #decide to turn light on or off
        when_start = config['main_loop_settings']['lamp_start_hour']
        when_stop  = config['main_loop_settings']['lamp_stop_hour']
        if DEBUG:
            print("ON interval hours: (%r, %r), current hour: %d" % (when_start, when_stop, hour))
        if hour >= when_start and hour < when_stop:
            print("Lamp is ON")
            lamp_pin.high()
            d['lamp_state'] = "ON"
        else:
            print("Lamp is OFF")
            lamp_pin.low()
            d['lamp_state'] = "OFF"
        print("DATA:", d)
        #push data to the data stream
        reply = dsc.push_data(d.items())
        if DEBUG:
            print(reply)
    except Exception as exc:
        #write error to log file
        #errorlog = open("errorlog.txt",'w')
        #sys.print_exception(exc, errorlog)
        #errorlog.close()
        if DEBUG:
            sys.print_exception(exc) #print to stdout
            #re raise the exception to halt the program
            raise exc
    finally:
        #do cleanup at end of loop
        #force garbage collection
        gc.collect()
        #print some debugging info
        if DEBUG:
            print("Memory Free: %d" % gc.mem_free())
            print(micropython.mem_info())
        #delay until next interval
        loop_ms = utime.ticks_ms() - start_ms
        leftover_ms = config['main_loop_settings']['sample_interval']*1000 - loop_ms
        if leftover_ms > 0:
                utime.sleep_ms(leftover_ms)

        
