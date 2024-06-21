from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app.models import comport_settings
import serial.tools.list_ports
import threading
import serial


serial_data = ""
serial_data_lock = threading.Lock()

serial_thread = None

def read_serial_data(ser):
    global serial_data
    while True:
        try:
            receive = ser.read().decode('ASCII')
            if receive == '\n':  # Assuming newline indicates end of a message
                with serial_data_lock:
                    print("Current Serial Data:", serial_data, flush=True)  # Display only the current serial data
                serial_data = ""  # Reset serial_data for the next message
            else:
                with serial_data_lock:
                    serial_data += receive
        except Exception as e:
            # Handle exceptions or log errors here
            pass

@csrf_exempt
def comport(request):
    global serial_thread

    if request.method == 'POST':
        selected_com_port = request.POST.get('com_port')
        selected_baud_rate = request.POST.get('baud_rate')
        bytesize = 8
        timeout = None
        stopbits = 1
        parity = 'N'

        try:
            first_comport_settings_id = comport_settings.objects.first().id
            comport_settings_obj, created = comport_settings.objects.get_or_create(
                id=first_comport_settings_id,
                defaults={
                    'com_port':selected_com_port,
                    'baud_rate': selected_baud_rate,
                    'bytesize': bytesize,
                    'stopbits': stopbits,
                    'parity': parity
                }
            )

            # If the object already exists, update its fields with new values
            if not created:
                comport_settings_obj.com_port = selected_com_port
                comport_settings_obj.baud_rate = selected_baud_rate
                comport_settings_obj.bytesize = bytesize
                comport_settings_obj.stopbits = stopbits
                comport_settings_obj.parity = parity
                comport_settings_obj.save()

            ser = serial.Serial(port=selected_com_port, baudrate=int(selected_baud_rate), bytesize=bytesize, timeout=timeout, stopbits=stopbits, parity=parity)
            print(f"COmport serial data is: {ser}")

            command = "MMMMMMMMMM"
            ser.write(command.encode('ASCII'))

            # Check if the serial thread is not running, then start it
            if serial_thread is None or not serial_thread.is_alive():
                serial_thread = threading.Thread(target=read_serial_data, args=(ser,))
                serial_thread.daemon = True
                serial_thread.start()

        except Exception as e:
            return JsonResponse({'error': str(e)})
        
        

    com_ports = [port.device for port in serial.tools.list_ports.comports()]
    baud_rates = ["4800", "9600", "14400", "19200", "38400", "57600", "115200", "128000"]

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        with serial_data_lock:
            if 'last_position' not in request.session:
                request.session['last_position'] = 0

            current_position = request.session['last_position']
            formatted_data = "".join(serial_data[current_position:])
            request.session['last_position'] = len(serial_data)

            print("Current Serial Data:", formatted_data, flush=True)
        
        return JsonResponse({'serial_data': formatted_data})

    return render(request, 'app/comport.html', {'com_ports': com_ports, 'baud_rates': baud_rates})




"""
1.serial.tools.list_ports
  Serial Library: This refers to the serial library in Python,
  communication with devices like Arduino, sensors, or other hardware

  tools:it is the sub-package 
  contains utility functions and classes that aid in working with serial devices.

  list_ports:interact with available serial ports on the system.

2.Threading
  Threads enable concurrent execution, allowing multiple tasks to run simultaneously and improve performance

3.CSRF (Cross-Site Request Forgery)
  csrf_exempt in Django disables CSRF protection for a specific view, allowing requests to bypass CSRF token validation.
"""