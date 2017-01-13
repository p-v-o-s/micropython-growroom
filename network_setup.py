#upython standard libraries
import utime, ujson, network

#DEBUG = False
DEBUG = True


def do_connect(sta_if_active = False, #default to inactive station interface
               ap_if_active  = None,
               connections   = [],
               ap_essid      = "micropython-AP",
               **kwargs,
               ):
    #check on the network status and wait until connected 
    if DEBUG:
        print("Configuring network settings:")

    has_connection = False

    #first configure the station interface
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(sta_if_active)
    if DEBUG:
        print("\tSTA_IF active = %s" % sta_if_active)
    if sta_if_active:
        for cn in connections:
            if DEBUG:
                print("\tAttempting to connect to essid = '%s'" % cn[0])
            sta_if.connect(cn[0],cn[1])
            #check that we have actually connected
            # NOTE this is import after calling machine.reset()
            for i in range(10):
                if sta_if.isconnected():
                    if DEBUG:
                        print("\tWLAN is connected!")
                        print("\tnetwork_config:", sta_if.ifconfig())
                    has_connection = True
                    break
                utime.sleep_ms(1000)
                if DEBUG:
                    print("\twaiting for WLAN to connect")
            else:
                print("\tWarning: Failed to connect to external network!")

    #next configure access point interface
    ap_if = network.WLAN(network.AP_IF)
    #default to active access point if we don't already have a connection
    if ap_if_active is None and has_connection:
        ap_if_active = False
    if ap_if_active is None and not has_connection:
        ap_if_active = True
    if DEBUG:
        print("\tAP_IF active = %s" % ap_if_active)
    if ap_if_active:
        if not ap_essid is None:
            if DEBUG:
                print("\tsetting AP essid = '%s'" % ap_essid)
            ap_if.active(False) #must shut down to configure
            ap_if.config(essid=ap_essid)
            ap_if.active(ap_if_active)
            
    return (sta_if,ap_if)
        
if __name__ == "__main__":
    do_connect()
