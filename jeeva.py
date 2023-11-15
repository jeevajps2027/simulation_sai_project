import tkinter as tk
from tkinter import ttk
from tkinter import Label, Text, Frame
import threading
import serial
import keyboard
import serial.tools.list_ports
from tkinter.font import Font

#com for everything    
form = tk.Tk()
form.geometry("710x550")

#title for page
form.title("sai accurate")

#size of the page
form.resizable(height="false",width="false")
#font changes
myfont=Font(family="italics",size=15,weight="bold")

#background color of page
form.config(bg="lightgrey",height=20,width=100)

#its like a h1 tags
lblTitle=Label(form,text="COMPORT SETTINGS",font=myfont)
lblTitle.grid(pady=20)

#frame creation
frame1=Frame(form,highlightbackground="black",highlightthickness=2)
frame1.grid(padx=150)

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

#comport
lblCom=Label(frame1,text="COMPORT-NO",font=myfont,pady=10)
lblCom.grid(row=1,column=0)

com_port_combobox = ttk.Combobox(frame1, width=30, state="readonly")
com_port_combobox.grid(row=1, column=1)

# Populate the COM Port Combobox with available COM ports using pyserial
com_ports = [port.device for port in serial.tools.list_ports.comports()]
com_port_combobox['values'] = com_ports

if com_ports:
    com_port_combobox.current(0) 
#Parity creation
lblParity=Label(frame1,text="PARITY",font=myfont,pady=10)
lblParity.grid(row=3,column=0)

cb=ttk.Combobox(frame1,width=30,state="readonly")
cb['values']=("Odd","Even","None","Mark","Space")
cb.current(2)
cb.grid(row=3,column=1)

#Stop creation
lblStop=Label(frame1,text="STOPBIT",font=myfont,pady=10)
lblStop.grid(row=4,column=0)

cb=ttk.Combobox(frame1,width=30,state="readonly")
cb['values']=("1","1.5","2")
cb.current(0)
cb.grid(row=4,column=1)

#Data creation
lblData=Label(frame1,text="DATABIT",font=myfont,pady=10)
lblData.grid(row=5,column=0)

cb=ttk.Combobox(frame1,width=30,state="readonly")
cb['values']=("4","5","6","7","8")
cb.current(4)
cb.grid(row=5,column=1)

# Create a Label for Baud Rate
lblBaud = Label(frame1, text="BAUD RATE", font=myfont, pady=10)
lblBaud.grid(row=2, column=0)

# Create a Combobox for baud rates
baud_rate_combobox = ttk.Combobox(frame1, width=30, state="readonly")
baud_rate_combobox['values'] = ("4800", "9600", "14400", "19200", "38400", "57600", "115200", "128000")
baud_rate_combobox.current(1)
baud_rate_combobox.grid(row=2, column=1)

# Create a Text widget for displaying serial data
text_widget = Text(frame1, width=50, height=10)
text_widget.grid(row=6, column=0, columnspan=2)

# Create a button to start the serial thread
start_button = tk.Button(frame1, text="OK",bg="green",fg="white",width=10, command=start_serial_thread)
start_button.grid(row=7,column=1,pady=10)
cancel_button = tk.Button(frame1, text="CANCEL",bg="red",fg="white",width=10)
cancel_button.grid(row=7,column=0,pady=10)

form.mainloop()
