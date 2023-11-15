import serial
import keyboard

# Configure the serial port (adjust the parameters as needed)
ser = serial.Serial(
    port='COM1',       # Replace with the name of your COM port
    baudrate=19200,     # Set your baud rate
    bytesize=8,
    timeout=None,
    stopbits=1,
    parity='N'
)

received_data = []  # Initialize an empty list to store received bytes

while True:
    ser.write("A".encode('ASCII'))
    receive = ser.read()
    if receive:
        received_data.append(receive)  # Append the received byte to the list
        print(receive.decode('ASCII'), end='')

    if keyboard.is_pressed('q'):
        break

# Convert the list of received bytes to a list of integers (optional)
received_data_as_int = [int(byte[0]) for byte in received_data]

print(received_data)  # List of received bytes
print(received_data_as_int)  # List of received bytes as integers