from __future__ import print_function
import time
from RF24 import *

from utils.packet_manager_simple import PacketManager
from utils.radio import configure_radios
from utils.config import get_args, process_config
from utils.ledManager import ledManager

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
radio_tx, radio_rx = configure_radios(channel_TX, channel_RX,1)
radio_rx.startListening()
radio_tx.stopListening()

# Create packets
packet_manager = PacketManager(config.document_path)
packets = packet_manager.create_window()

#Define loop variables
led.violet()
i=0

# We'll have tot_packets/WINDOW_SIZE windows sent, in each window we'll send WINDOW_SIZE packets
tot_packets = len(packets)
window_counter = 0
WINDOW_SIZE = 32 # TODO: Put in config file
ACK_SIZE = 32

# TODO: to avoid this code mess (below), make classes transmitter and receiver, these ones will have methods like: stop_and_wait(already implemented), sliding_window (this one)

for window_counter in range(tot_packets/WINDOW_SIZE): # TODO: add some padding in case tot_packets/WINDOW_SIZE is not integer    
    # rx_acks => remaining packets to send
    rx_acks = [ i for i in range(WINDOW_SIZE)] # esto de crear la lista asi y aqui no me gusta, habra que cambiarlo, por un contador?
    timeout = False
    # Start timeout
    started_waiting_at = millis()
    # No nos podriamos petar el timeout @AdrianRodriguez?
    while( (len(rx_acks) > 0) or (not timeout) ): # si ha saltado el timeout o el numbero de acks recibidos es menor que la window size tendra que enviar 
        for packet_index in rx_acks:
            radio_tx.write(packets[window_counter * WINDOW_SIZE + packet_index])
        # Once it has sent all the packets in the window it cheks the ACK and checks the timeout
        while (not radio_rx.available()) and (not timeout):
            if (millis() - started_waiting_at) > int(config.timeout_time):
                timeout = True
        if(timeout): 
            timeout = False
        else:
            # There is sth in the receiver
            ack = radio_rx.read(ACK_SIZE)
            if(ack[0]==0 and ack[1]==0):
                # All packets are OK
                break
            else:
                for ack_idx in range(ACK_SIZE):
                    del rx_acks[ack_idx]
        
led.off()