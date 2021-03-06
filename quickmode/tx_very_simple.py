from __future__ import print_function
import time
from RF24 import *

from utils.packet_manager_simple import PacketManager
from utils import configure_radios
from utils import get_args, process_config
from utils import ledManager

try:
    args = get_args()
    config = process_config(args.config)

except:
    print("missing or invalid arguments")
    exit(0)

millis = lambda: int(round(time.time() * 1000))

print('Quick Mode script! ')

print('TX Role: Ping Out, starting transmission')

# Set led Manager
led = ledManager()
led.red()

# Define comunication parameters
channel_TX = 60
channel_RX = 70
payload_size = config.payload_size

# Start radios
radio_tx, radio_rx = configure_radios(channel_TX, channel_RX, 1)
radio_rx.startListening()
radio_tx.stopListening()

# Create packets
packet_manager = PacketManager(config.document_path)
packets = packet_manager.create_window()

# Define loop variables
led.violet()
i = 0

# We'll have tot_packets/WINDOW_SIZE windows sent, in each window we'll send WINDOW_SIZE packets
tot_packets = len(packets)
window_counter = 0
WINDOW_SIZE = 31 # TODO: Put in config file
window = 31
if(tot_packets%WINDOW_SIZE==0):
    rang = tot_packets//WINDOW_SIZE
else:
    rang = tot_packets//WINDOW_SIZE+1

# Don't touch this
# TODO: to avoid this code mess (below), make classes transmitter and receiver, these ones will have methods like: stop_and_wait(already implemented), sliding_window (this one)
for window_counter in range(rang):
    print(window)
    if (tot_packets/WINDOW_SIZE-window_counter<1):
        window = (tot_packets-(window_counter)*WINDOW_SIZE)
        print("Window")
        print(window)

    print("-----------------------------------------------------")
    print("Sending window " + str(window_counter))
    # rx_acks => remaining packets to send
    rx_acks = 0 
    rx_acks_bools = [0] * window # 0 if the receiver has not received the packet, 1 if the receiver has sent ACK
    timeout = False
    # si ha saltado el timeout o el numbero de acks recibidos es menor que la window size tendra que enviar 
    while( (rx_acks < window) or (timeout) ): 
        timeout = False
        for packet_index in range(len(rx_acks_bools)):
            if(rx_acks_bools[packet_index] == 0):
                radio_tx.write(packets[window_counter * WINDOW_SIZE + packet_index])
                print("tx packet " + str(window_counter*WINDOW_SIZE+packet_index))
        # Once it has sent all the packets in the window it checks the ACK and checks the timeout
        started_waiting_at = millis()
        while (not radio_rx.available()) and (not timeout):
            if (millis() - started_waiting_at) > int(config.timeout_time):
                timeout = True
                started_waiting_at = millis()
                
        if(timeout):
            print("Ha saltado el timeout")
        else:
            # There is sth in the receiver
            print("I listen to ACK")
            ack = radio_rx.read(radio_rx.getDynamicPayloadSize())
            # Some packets are wrong, they will send the ones that are good
            print("Received ACK = ")
            print((ack))
            for ack_idx in ack[1:window+1]:
                if(rx_acks_bools[ack_idx] == 0 and ack[0] == window_counter%2):
                    # It was wrong and not is OK
                    print("Packet " + str(ack_idx) + " correct")
                    rx_acks += 1
                    rx_acks_bools[ack_idx] = 1
            print("ACKS array")
            print(rx_acks_bools)
            wrong_packets = window - rx_acks
            print("Wrong packets " + str(wrong_packets))
    

led.off()
