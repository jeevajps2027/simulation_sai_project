import serial

# Define the serial port and baud rate
serial_port = '/dev/ttyUSB0'  # Replace with your actual serial port
baud_rate = 19200  # Match this with the baud rate of your serial device

try:
    # Open the serial port
    ser = serial.Serial(serial_port, baud_rate)

    # Read and print data from the serial port
    while True:
        data = ser.readline().decode('utf-8')
        print(data, end='')

except serial.SerialException as e:
    print(f"An error occurred: {e}")
finally:
    # Close the serial port when done
    ser.close()
