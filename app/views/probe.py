
import re
import threading
from django.http import JsonResponse
from django.shortcuts import redirect, render
import serial
from app.models import comport_settings, find


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



def probe(request):
    if request.method == 'POST':
        probe_id = request.POST.get('probeId')
        a_values = [float(value) for value in request.POST.getlist('a[]')]
        a1_values = [float(value) for value in request.POST.getlist('a1[]')]
        b_values = [float(value) for value in request.POST.getlist('b[]')]
        b1_values = [float(value) for value in request.POST.getlist('b1[]')]
        e_values = [float(value) for value in request.POST.getlist('e[]')]

        print('THESE ARE THE DATA YOU WANT TO DISPLAY:', probe_id, a_values, a1_values, b_values, b1_values, e_values)

        probe, created = find.objects.get_or_create(probe_id=probe_id)

        probe.low_ref = a_values[0] if a_values else None
        probe.low_count = a1_values[0] if a1_values else None
        probe.high_ref = b_values[0] if b_values else None
        probe.high_count = b1_values[0] if b1_values else None
        probe.coefficent = e_values[0] if e_values else None

        probe.save()
        
        return redirect('master_page', probe_id=probe_id)

    elif request.method == 'GET':
        comport_settings_obj = comport_settings.objects.first()  # Assuming you want the first object
        selected_com_port = comport_settings_obj.com_port
        selected_baud_rate = comport_settings_obj.baud_rate
        bytesize = comport_settings_obj.bytesize
        stopbits = comport_settings_obj.stopbits
        parity = comport_settings_obj.parity

        # Get the list of available com ports
        com_ports = [port.device for port in serial.tools.list_ports.comports()]

       # Check if the selected com port is in the list of available com ports
        if selected_com_port not in com_ports:
            error_message = f"Selected COM port '{selected_com_port}' is not available"
            context = {'error_occurred': True, 'error_message': error_message}
            
            return render(request, 'app/probe.html', context)
        
        context = {
            'com_port': selected_com_port,
            'baud_rate': selected_baud_rate,
            'bytesize': bytesize,
            'stopbits': stopbits,
            'parity': parity,
        }
        
        with serial_data_lock:
            data_to_display = serial_data

        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            # Split the serial data into 11 channels (A-K) using regular expressions
            parts = re.split(r'([A-K])', data_to_display)
            parts = [part for part in parts if part.strip()]  # Remove empty strings

            # Create a dictionary to store data for each channel
            channel_data = {}
            for channel_id, part in zip(parts[0::2], parts[1::2]):
                part = part.replace('+', '')
                channel_data[channel_id] = part

            # Return the channel data as JSON response
            return JsonResponse({'serial_data': channel_data})
        
        # Retrieve the distinct probe IDs
        probe_ids = find.objects.values_list('probe_id', flat=True).distinct()
        
        # Create a dictionary to store coefficient values for each probe ID
        probe_coefficients = {}
        low_count = {}
        
        for probe_id in probe_ids:
            # Retrieve the latest coefficient value for the current probe ID
            latest_calibration = find.objects.filter(probe_id=probe_id).latest('id')
            
            # Extract the coefficient value
            coefficient_value = latest_calibration.coefficent
            low_value = latest_calibration.low_count
            
            
            # Store the coefficient value in the dictionary with the probe ID as the key
            probe_coefficients[probe_id] = coefficient_value
            low_count[probe_id] = low_count

            print(f'Probe ID: {probe_id}, Coefficient: {coefficient_value}')
            print(f'Probe ID: {probe_id}, Low values: {low_value}')
        

    return render(request, 'app/probe.html', {'serial_data': data_to_display ,'probe_coefficients': probe_coefficients ,'low_count':low_count })

"""
1.import re
  Regular Expressions -  powerful tools used for pattern matching and string manipulation

2.serial
  Serial Library: This refers to the serial library in Python,
  communication with devices like Arduino, sensors, or other hardware

3.Threading
  Threads enable concurrent execution, allowing multiple tasks to run simultaneously and improve performance


"""