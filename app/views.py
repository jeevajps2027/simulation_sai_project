import traceback
from pyexpat.errors import messages
import re
from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate,login
import serial.tools.list_ports
import threading
import serial
import keyboard
import time
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.views import View


""" Probe Classbased View """
class ProbeView(View):
    template_name = 'app/probe/probe1.html'

    def get(self, request, channel_name=None, *args, **kwargs):

        try:
            with serial_data_lock:
                data_to_display = serial_data

            # Split the serial data into 11 channels (A-K) using regular expressions
            parts = re.split(r'([A-K])', data_to_display)
            parts = [part for part in parts if part.strip()]  # Remove empty strings

            # Create a dictionary to store data for each channel
            channel_data = {}

            for channel_id, part in zip(parts[0::2], parts[1::2]):
                part = part.replace('+','')
                channel_data[channel_id] = part

            context = {'serial_data': channel_data}

            return render(request, self.template_name, context)
        except Exception as err:
            print(f"Failed message is : {err}")
            print(f"Failed reason is : {traceback.format_exc()}")

        
    

def home(request):
    if request.method == 'POST':
        username = request.POST['user']
        password = request.POST['password']

        if username == 'admin' and password == 'admin':
            # Redirect to the index page if credentials are correct
            return redirect('index')  # 'index' is the name of the URL pattern for your index page
        else:
            # If the username and password don't match, display an error message
            messages.error(request, 'Invalid username or password')

    return render(request, "app/home.html")


import serial
import threading
from django.http import JsonResponse
from django.shortcuts import render

# Use a lock to ensure thread safety when accessing serial_data
serial_data = ""
serial_data_lock = threading.Lock()

serial_thread = None

def read_serial_data(ser):
    global serial_data
    while True:
        try:
            receive = ser.read().decode('ASCII')
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

        try:
            ser = serial.Serial(port=selected_com_port, baudrate=int(selected_baud_rate), bytesize=8, timeout=None, stopbits=1, parity='N')

            # Check if the serial thread is not running, then start it
            if serial_thread is None or not serial_thread.is_alive():
                serial_thread = threading.Thread(target=read_serial_data, args=(ser,))
                serial_thread.daemon = True
                serial_thread.start()

        except Exception as e:
            return JsonResponse({'error': str(e)})

    com_ports = [port.device for port in serial.tools.list_ports.comports()]
    baud_rates = ["4800", "9600", "14400", "19200", "38400", "57600", "115200", "128000"]

    with serial_data_lock:
        data_to_display = serial_data

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'serial_data': data_to_display})

    return render(request, 'app/comport.html', {'com_ports': com_ports, 'baud_rates': baud_rates, 'serial_data': data_to_display})


 

def index(request):
    return render(request,'app/index.html')




def probe1(request):
    print(f"REQIUEST DATA IS: {request}")
    try:
        with serial_data_lock:
            data_to_display = serial_data

        # Split the serial data into 11 channels (A-K) using regular expressions
        parts = re.split(r'([A-K])', data_to_display)
        parts = [part for part in parts if part.strip()]  # Remove empty strings

        # Create a dictionary to store data for each channel
        channel_data = {}
        for channel_id, part in zip(parts[0::2], parts[1::2]):
            part = part.replace('+','')
            channel_data[channel_id] = part
    
        return render(request, 'app/probe/probe1.html', {'serial_data': channel_data})
    except Exception as err:
        print(f"Failed message is : {err}")
        print(f"Failed reason is : {traceback.format_exc()}")


def probe2(request):
    with serial_data_lock:
        data_to_display = serial_data

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # Split the serial data into 11 channels (A-K) using regular expressions
        parts = re.split(r'([A-K])', data_to_display)
        parts = [part for part in parts if part.strip()]  # Remove empty strings

        # Create a dictionary to store data for each channel
        channel_data = {}
        for channel_id, part in zip(parts[0::2], parts[1::2]):
            part = part.replace('+','')
            channel_data[channel_id] = part

        # Return the channel data as JSON response
        return JsonResponse({'serial_data': channel_data})

    return render(request, 'app/probe/probe2.html', {'serial_data': data_to_display})





def probe3(request):
    return render(request,'app/probe/probe3.html')
def probe4(request):
    return render(request,'app/probe/probe4.html')
def probe5(request):
    return render(request,'app/probe/probe5.html')
def probe6(request):
    return render(request,'app/probe/probe6.html')