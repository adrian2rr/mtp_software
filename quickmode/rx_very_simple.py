from __future__ import print_function
import time
# from RF24 import *
import zlib
from utils import configure_radios
from utils import get_args, process_config
from utils.packet_manager_simple import PacketManagerAck
from utils import ledManager

"""
TODO: Create packet manager that reassembles the packets instead of reassembling the packets in the last if
"""
compression = True

try:
    args = get_args()
    config = process_config(args.config)

except:
    print("missing or invalid arguments")
    exit(0)

millis = lambda: int(round(time.time() * 1000))

print('Quick Mode script! ')

print('RX Role:Pong Back, awaiting transmission')

# Set led Manager
led = ledManager()
led.red()

# Set comunication parameters
channel_RX = 60
channel_TX = 70

# Initialize radio
radio_tx, radio_rx = configure_radios(channel_TX, channel_RX, 0)
radio_rx.startListening()
radio_tx.stopListening()

# Create local variables
frames = []
last_packet = False
num_packets = 0
num_file = 0

# Create Ack packet
packet_manager_ack = PacketManagerAck()
packet_ack = packet_manager_ack.create()

led.blue()

WINDOW_SIZE = 31
data_size = 31
loop = True
window_old = -1
ack_old = False
last_packet = False
rx_id_old = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

while loop:
    if(radio_rx.available()):
        # Set window variables
        rx_id = [0]      # The receiver will check this after receiving a window. Example: [0, 1, 2, 4, 6] --> I have to ask for retx of pkt 3 and 5
        window_bytes = [0] * WINDOW_SIZE * data_size
        end_of_window = False
        last_window = 32
        ack_sent = False

        while(not end_of_window):
            while(radio_rx.available()):

                # First check of the payload
                length = radio_rx.getDynamicPayloadSize()
                receive_payload = radio_rx.read(length)
                # now process rx_payload
                header = receive_payload[0]
                window = 0x40 & header
                frame_id = int(0x3f & header)
                rx_id[0] = window // 64

                print("Received packet id: " + str(frame_id) + " window: " + str(window) + " window old: " + str(window_old))
                # print(receive_payload[1:])
                if(window != window_old):

                    if(header > 127):
                        # This means that eot = 1, the header field will be something like = 1XXX XXXX so it will be > 127
                        last_packet = True
                        last_window = int(frame_id)
                        print("EOT!")
                        if(frame_id not in rx_id[1:]):
                            rx_id.append(frame_id)
                            ack_sent = False
                        last_packet_size = len(receive_payload)
                        window_bytes[frame_id * data_size:frame_id * data_size + last_packet_size - 1] = receive_payload[1:]
                    else:
                        if(frame_id not in rx_id[1:]):
                            rx_id.append(frame_id)
                            ack_sent = False

                        window_bytes[frame_id * data_size:frame_id * data_size + len(receive_payload) - 1] = receive_payload[1:]
                    if((len(rx_id) == WINDOW_SIZE + 1) or (len(rx_id) == last_window + 2)):
                        end_of_window = True

                        rx_id_old = rx_id

                else:
                    ack_old = True


            # send correct ids (rx_id)

            rx_id_1 = [rx_id[0]]
            rx_id_2 = rx_id[1:]
            rx_id_2.sort()
            rx_id_1.extend(rx_id_2)
            rx_id = rx_id_1

            if((len(rx_id) > 1 and rx_id[-1] == (WINDOW_SIZE - 1) and not ack_sent) or (len(rx_id) > 1 and rx_id[-1] == last_window and not ack_sent) and not ack_old):

                radio_tx.write(bytes(rx_id))
                print("Sent ACK: " + str(rx_id))
                ack_sent = True


            if (ack_old):
                if(last_packet):
                    rx_id_old = rx_id_old[:last_window + 2]

                radio_tx.write(bytes(rx_id_old))
                print("Sent ACK old: " + str(rx_id_old))
                ack_old = False


        # Once all the window is received correctly, store the packets
        if(len(rx_id) == WINDOW_SIZE + 1):
            frames.extend(bytes(window_bytes))

            print("End of window " + str(window) + ", packet saved")
            window_old = window

        if(len(rx_id) == last_window + 2):
            frames.extend(bytes(window_bytes[:(last_window) * data_size + last_packet_size - 1]))

            print("End of window " + str(window) + ", packet saved")
            window_old = window
        # If it is the last packet save the txt


        if last_packet and len(rx_id) == last_window + 2:
            # led.green()
            print('Reception complete.')
            # If we are here it means we received all the frames so we have to uncompress

            if compression:
                uncompressed_frames = zlib.decompress(bytes(frames))

                f = open('file' + str(num_file) + '.txt', 'wb')
                f.write(bytes(uncompressed_frames))
                f.close()
                print('File saved with name: ' + 'file' + str(num_file) + '.txt')
            else:
                f = open('file' + str(num_file) + '.txt', 'wb')
                f.write(bytes(frames))
                f.close()
                print('File saved with name: ' + 'file' + str(num_file) + '.txt')
            frames = []
            last_packet = False
            num_packets = 0
            num_file += 1
            input('Press Enter to finish')
            led.off()
            loop = 0
