import tkinter as tk
from tkinter import ttk
from tkinter import Text
import serial
import serial.tools.list_ports
import threading

def read_serial_data():
    selected_baud_rate = baud_rate_combobox.get()
    selected_com_port = com_port_combobox.get() # Get the selected baud rate
    try:
        ser = serial.Serial(port=selected_com_port, baudrate=int(selected_baud_rate), bytesize=8, timeout=None, stopbits=1, parity='N')
        while True:
            receive = ser.read(1).decode('ASCII')
            text_widget.insert("end", receive)
            text_widget.see("end")
    except Exception as e:
        print(f"Error: {e}")

def start_serial_thread():
    global serial_thread
    serial_thread = threading.Thread(target=read_serial_data)
    serial_thread.daemon = True  # This ensures that the thread terminates when the main window is closed
    serial_thread.start()

# Create the main application window
app = tk.Tk()
app.title("COMPORT SETTINGS")
app.geometry("800x600")
app.configure(background="grey")

# Title
title_label = ttk.Label(app, text="COMPORT SETTINGS", font=("Helvetica", 20, "bold"), foreground="white")
title_label.pack(pady=30)

# Frame
frame = ttk.Frame(app, borderwidth=2, relief="solid", padding=50)
frame.place(x=380, width=480)

# COM Port
com_ports = [port.device for port in serial.tools.list_ports.comports()]
com_port_label = ttk.Label(frame, text="COMPORT-NO", font=("Helvetica", 12, "bold"))
com_port_label.grid(row=0, column=0, sticky="w")
com_port_combobox = ttk.Combobox(frame, values=com_ports, width=20)
com_port_combobox.grid(row=0, column=1)

# Baud Rate
baud_rates = ["4800", "9600", "14400", "19200", "38400", "57600", "115200", "128000"]
baud_rate_label = ttk.Label(frame, text="BAUD RATE", font=("Helvetica", 12, "bold"))
baud_rate_label.grid(row=1, column=0, sticky="w")
baud_rate_combobox = ttk.Combobox(frame, values=baud_rates, width=20)
baud_rate_combobox.grid(row=1, column=1)

# Parity
parity_options = ["None", "Even", "Odd", "Mark", "Space"]
parity_label = ttk.Label(frame, text="PARITY", font=("Helvetica", 12, "bold"))
parity_label.grid(row=2, column=0, sticky="w")
parity_combobox = ttk.Combobox(frame, values=parity_options, width=20)
parity_combobox.grid(row=2, column=1)
parity_combobox.set("None")

# Stop Bits
stop_bits_options = ["1", "1.5", "2"]
stop_bits_label = ttk.Label(frame, text="STOPBIT", font=("Helvetica", 12, "bold"))
stop_bits_label.grid(row=3, column=0, sticky="w")
stop_bits_combobox = ttk.Combobox(frame, values=stop_bits_options, width=20)
stop_bits_combobox.grid(row=3, column=1)
stop_bits_combobox.set("1")

# Data Bits
data_bits_options = ["4", "5", "6", "7", "8"]
data_bits_label = ttk.Label(frame, text="DATABIT", font=("Helvetica", 12, "bold"))
data_bits_label.grid(row=4, column=0, sticky="w")
data_bits_combobox = ttk.Combobox(frame, values=data_bits_options, width=20)
data_bits_combobox.grid(row=4, column=1)
data_bits_combobox.set("8")

# Serial Data Text
text_widget = Text(frame, height=10, width=50, state="normal")
text_widget.grid(row=5, column=0, columnspan=2, pady=20)
text_widget.config(state="disabled")

# OK Button
ok_button = ttk.Button(frame, text="OK", command=start_serial_thread, style="TButton", width=20)
ok_button.grid(row=6, column=1, pady=10)

# Cancel Button
cancel_button = ttk.Button(frame, text="CANCEL", style="TButton", width=20)
cancel_button.grid(row=6, column=0, pady=10)

app.mainloop()
