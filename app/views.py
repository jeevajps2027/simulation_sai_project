import threading
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from pyexpat.errors import messages
import re
from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate,login
import serial.tools.list_ports
import threading
import serial
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from.models import MasterData,comport_settings,mastering_data,parameter_settings
from.models import find,TableOneData,TableTwoData,TableThreeData,TableFourData,TableFiveData
import json
from datetime import datetime
from django.views.decorators.cache import never_cache

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


import threading

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

        
 

 

def index(request):
    return render(request,'app/index.html')


from django.http import JsonResponse, HttpResponse
import json

@csrf_exempt
def trace(request, row_id=None):
    if request.method == 'POST':
        try:
            received_data = json.loads(request.body)
            print('received_data', received_data)

            if 'rowId' in received_data:
                row_id = received_data['rowId']
                print('row_id:', row_id)

                table_body_id = received_data.get('tableBodyId')
                print('your table_body_id is:',table_body_id)
                values = received_data.get('values')

                if table_body_id and values:
                    if table_body_id == 'tableBody-1':
                        try:
                            table_data = TableOneData.objects.get(pk=row_id)
                            table_data.part_name = values[0]
                            table_data.customer_name = values[1]
                            table_data.part_model = values[2]
                            table_data.part_no = values[3]
                            table_data.hide = values[4]
                            table_data.save()
                            return JsonResponse({'message': 'Data updated successfully'}, status=200)
                        except TableOneData.DoesNotExist:
                            pass
                    elif table_body_id == 'tableBody-2':
                        try:
                            table_data = TableTwoData.objects.get(pk=row_id)
                            table_data.batch_no = values[0]
                            table_data.save()
                            return JsonResponse({'message': 'Data updated successfully'}, status=200)
                        except TableTwoData.DoesNotExist:
                            pass
                    elif table_body_id == 'tableBody-3':
                        try:
                            table_data = TableThreeData.objects.get(pk=row_id)
                            table_data.machine_no = values[0]
                            table_data.machine_name = values[1]
                            table_data.save()
                            return JsonResponse({'message': 'Data updated successfully'}, status=200)
                        except TableThreeData.DoesNotExist:
                            pass
                    elif table_body_id == 'tableBody-4':
                        try:
                            table_data = TableFourData.objects.get(pk=row_id)
                            table_data.operator_no = values[0]
                            table_data.operator_name = values[1]
                            table_data.save()
                            return JsonResponse({'message': 'Data updated successfully'}, status=200)
                        except TableFourData.DoesNotExist:
                            pass
                    elif table_body_id == 'tableBody-5':
                        try:
                            table_data = TableFiveData.objects.get(pk=row_id)
                            table_data.vendor_code = values[0]
                            table_data.email = values[1]
                            table_data.save()
                            return JsonResponse({'message': 'Data updated successfully'}, status=200)
                        except TableFiveData.DoesNotExist:
                            pass

                return JsonResponse({'message': 'Record with provided rowId does not exist'}, status=404)

            # Code to handle creation of new records
            # This part of the code is based on your previous logic
            # It will create new records if the 'rowId' is not provided in the received data
            else:
                if received_data:
                    for item_id, rows in received_data.items():
                        for row in rows:
                            values = row['values']
                            if item_id == 'tableBody-1':
                                table_data = TableOneData.objects.create(
                                    part_name=values[0],
                                    customer_name=values[1],
                                    part_model=values[2],
                                    part_no=values[3],
                                    hide=values[4]
                                )
                            elif item_id == 'tableBody-2':
                                table_data = TableTwoData.objects.create(
                                    batch_no=values[0]
                                )
                            elif item_id == 'tableBody-3':
                                table_data = TableThreeData.objects.create(
                                    machine_no=values[0],
                                    machine_name=values[1]
                                )
                            elif item_id == 'tableBody-4':
                                table_data = TableFourData.objects.create(
                                    operator_no=values[0],
                                    operator_name=values[1]
                                )
                            elif item_id == 'tableBody-5':
                                table_data = TableFiveData.objects.create(
                                    vendor_code=values[0],
                                    email=values[1]
                                )
                            table_data.save()

                    return JsonResponse({'message': 'New record(s) created successfully'}, status=201)
                else:
                    return JsonResponse({'message': 'No data provided'}, status=400)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON format'}, status=400)

        

    elif request.method == 'GET':
        try:
            # Fetch stored data for tableBody-1 from your database or any storage mechanism
            # Replace this with your actual logic to fetch data for tableBody-1
            table_body_1_data = TableOneData.objects.all()
            table_body_2_data = TableTwoData.objects.all()
            table_body_3_data = TableThreeData.objects.all()
            table_body_4_data = TableFourData.objects.all()
            table_body_5_data = TableFiveData.objects.all()
            # Pass the retrieved data for tableBody-1 to the template for rendering
            return render(request, 'app/trace.html', {'table_body_1_data': table_body_1_data,'table_body_2_data':table_body_2_data,'table_body_3_data': table_body_3_data,'table_body_4_data': table_body_4_data,'table_body_5_data': table_body_5_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'DELETE':
        try:
            received_data = json.loads(request.body)

            for item_id, row_ids in received_data.items():
                print(f"Deleting rows with IDs {row_ids} from {item_id}")

                # Depending on the item_id, fetch the rows from the database
                if item_id == 'tableBody-1':
                    rows = TableOneData.objects.filter(id__in=row_ids)
                    # Print the column values of each row before deleting
                    for row in rows:
                        part_model_value = row.part_model
                        delete = parameter_settings.objects.filter(model_id=part_model_value).delete()

                elif item_id == 'tableBody-2':
                    rows = TableTwoData.objects.filter(id__in=row_ids)
                elif item_id == 'tableBody-3':
                    rows = TableThreeData.objects.filter(id__in=row_ids)
                elif item_id == 'tableBody-4':
                    rows = TableFourData.objects.filter(id__in=row_ids)
                elif item_id == 'tableBody-5':
                    rows = TableFiveData.objects.filter(id__in=row_ids)

                
                # Delete the rows
                rows.delete()

            return JsonResponse({'message': 'Data deleted successfully'}, status=200)

        except Exception as e:
            print(f"Error deleting rows: {e}")
            return JsonResponse({'error': 'Error deleting rows'}, status=500)
    
    else:
        return render(request, 'app/trace.html')






from django.shortcuts import render, get_object_or_404

@csrf_exempt
def parameter(request):
    if request.method == 'GET':
        try:
            table_body_1_data = TableOneData.objects.all()

            # Dynamically filter constvalue objects based on the model_id parameter
            model_id = request.GET.get('model_name')
            print('your selected model from the web page is:', model_id)

            # Get the selected parameter name from the request
            parameter_name = request.GET.get('parameter_name')
            print('Your selected parameter from the web page is:', parameter_name)

            # Check if an id is provided in the query parameters
            selected_id = request.GET.get('id')
            print('Selected ID:', selected_id)  # Add this line for debugging

            if selected_id:
                # Fetch the parameter details by ID
                parameter = get_object_or_404(parameter_settings, id=selected_id)

                # Convert parameter details to a dictionary
                parameter_details = {
                    'id': parameter.id,
                    'sr_no': parameter.sr_no, 
                    'parameter_name': parameter.parameter_name,
                    'single_radio': parameter.single_radio,
                    'double_radio': parameter.double_radio,
                    'analog_zero': parameter.analog_zero,
                    'reference_value': parameter.reference_value,
                    'high_mv': parameter.high_mv,
                    'low_mv': parameter.low_mv,
                    'probe_no': parameter.probe_no,
                    'measurement_mode': parameter.measurement_mode,
                    'nominal': parameter.nominal,
                    'usl': parameter.usl,
                    'lsl': parameter.lsl,
                    'mastering': parameter.mastering,
                    'step_no': parameter.step_no,
                    'hide_checkbox': parameter.hide_checkbox,
                    'utl':parameter.utl,
                    'ltl':parameter.ltl,
                    'digits':parameter.digits,
                    'job_dia':parameter.job_dia,
                }

                # Print the parameter details in the terminal
                print('Parameter Details:', parameter_details)

                # Return parameter details as JSON
                return JsonResponse({'parameter_details': parameter_details})

            elif model_id:
                # Filter constvalue objects based on the model_id
                paraname = parameter_settings.objects.filter(model_id=model_id).values('parameter_name','id')
                print('your filtered values are:', paraname)

                # Return filtered parameter names as JSON
                return JsonResponse({'paraname': list(paraname)})

            else:
                paraname = []  # If no model is selected, set paraname to an empty list

            return render(request, 'app/parameter.html', {
                'table_body_1_data': table_body_1_data,
                'paraname': paraname,
                'selected_model_id': model_id,
            })

        except Exception as e:
            print(f'Exception: {e}')
            return JsonResponse({'key': 'value'})
            
    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print(f'Your values received from the frontend: {data}')

            model_id = data.get('modelId')
            print('Model ID:', model_id)

            # Extract sr_no from the data
            sr_no = data.get('srNo')
            print('SR_NO:', sr_no)

            parameter_value = data.get('parameterValue')
            print('Parameter Name:', parameter_value)
            
            
            existing_instance = parameter_settings.objects.filter(model_id=model_id, sr_no=sr_no).first()

            if existing_instance:
                # Update the existing instance with the received values
                existing_instance.parameter_name = data.get('parameterValue')          
                existing_instance.single_radio = data.get('singleRadio')
                existing_instance.double_radio = data.get('doubleRadio')

                if existing_instance.single_radio:
                    existing_instance.analog_zero = data.get('analogZero')
                    existing_instance.reference_value = data.get('referenceValue')
                    existing_instance.high_mv = None
                    existing_instance.low_mv = None
                elif existing_instance.double_radio:
                    existing_instance.high_mv = data.get('highMV')
                    existing_instance.low_mv = data.get('lowMV')
                    existing_instance.analog_zero = None
                    existing_instance.reference_value = None

                # Update other values
                existing_instance.probe_no = data.get('probeNo')
                existing_instance.parameter_name = data.get('parameterValue')
                existing_instance.measurement_mode = data.get('measurementMode')
                existing_instance.nominal = data.get('nominal')
                existing_instance.usl = data.get('usl')
                existing_instance.lsl = data.get('lsl')
                existing_instance.mastering = data.get('mastering')
                existing_instance.step_no = data.get('stepNo')
                existing_instance.hide_checkbox = data.get('hideCheckbox')

                existing_instance.parameter_name = data.get('parameterValue')
                existing_instance.utl = data.get('utl')
                existing_instance.ltl = data.get('ltl')
                existing_instance.digits = data.get('digits')
                existing_instance.job_dia = data.get('job_dia')

                existing_instance.save()

                print("Your values in the server (updated):", existing_instance)


            else:    
                # Handle radio button values
                single_radio = data.get('singleRadio')
                double_radio = data.get('doubleRadio')
                if single_radio:
                    analog_zero = data.get('analogZero')
                    reference_value = data.get('referenceValue')
                    high_mv = None
                    low_mv = None
                elif double_radio:
                    high_mv = data.get('highMV')
                    low_mv = data.get('lowMV')
                    analog_zero = None
                    reference_value = None

                # Continue handling other values
                probe_no = data.get('probeNo')
                measurement_mode = data.get('measurementMode')
                nominal = data.get('nominal')
                usl = data.get('usl')
                lsl = data.get('lsl')
                mastering = data.get('mastering')
                step_no = data.get('stepNo')
                hide_checkbox = data.get('hideCheckbox')
                utl = data.get('utl')
                ltl = data.get('ltl')
                digits = data.get('digits')
                job_dia = data.get('job_dia')
                

                # Create an instance of your model with the received values
                const_value_instance = parameter_settings.objects.create(
                    model_id=model_id,
                    parameter_name=parameter_value,
                    sr_no=sr_no, 
                    single_radio=single_radio,
                    double_radio=double_radio,
                    analog_zero=analog_zero,
                    reference_value=reference_value,
                    high_mv=high_mv,
                    low_mv=low_mv,
                    probe_no=probe_no,
                    measurement_mode=measurement_mode,
                    nominal=nominal,
                    usl=usl,
                    lsl=lsl,
                    mastering=mastering,
                    step_no=step_no,
                    hide_checkbox=hide_checkbox,
                    utl=utl,
                    ltl=ltl,
                    digits=digits,
                    job_dia=job_dia
                )

                print("Your values in the server:", const_value_instance)
                # Save the instance to the database
                const_value_instance.save()

            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
            
    elif request.method == 'DELETE':
        try:
            # Check if an ID is provided in the query parameters
            selected_id = request.GET.get('id')
            print('Selected ID:', selected_id)

            if selected_id:
                # Fetch the parameter details by ID
                parameter = get_object_or_404(parameter_settings, id=selected_id)

                # Get the model_id and sr_no before deletion
                model_id = parameter.model_id
                sr_no = parameter.sr_no

                # Delete the parameter
                parameter.delete()

                print(f'Parameter with ID {selected_id} deleted successfully.')
                # Adjust sr_no values for the remaining parameters of the same model
                remaining_parameters = parameter_settings.objects.filter(model_id=model_id).order_by('sr_no')
                for index, remaining_param in enumerate(remaining_parameters, start=1):
                    if remaining_param.sr_no != index:
                        remaining_param.sr_no = index
                        remaining_param.save()

                return JsonResponse({'success': True, 'message': f'Parameter with ID {selected_id} deleted successfully.'})

            else:
                return JsonResponse({'success': False, 'message': 'ID not provided in the query parameters.'})

        except Exception as e:
            print(f'Exception: {e}')
            return JsonResponse({'success': False, 'message': str(e)})

    else:
        # Return 405 Method Not Allowed for other request methods
        return HttpResponseNotAllowed(['GET', 'POST', 'DELETE'])

    return render(request, 'app/parameter.html')



def master(request):
    if request.method == 'POST':
        try:
            
            # Retrieve the selected values from the request body
            data = json.loads(request.body.decode('utf-8'))

            # Process the data as needed
            probeNo = data.get('probeNo')
            a = data.get('a')
            b = data.get('b')
            e = data.get('e')
            d = data.get('d')
            o1 = data.get('o1')
            parameterName = data.get('parameterName')
            selectedValue = data.get('selectedValue')
            selectedMastering = data.get('selectedMastering')
            date_time_str = data.get('dateTime')

            

            if None not in [probeNo, a, b, e, d, o1, parameterName, selectedValue, selectedMastering, date_time_str]:

                if date_time_str:
                    # Parse the date and time string
                    dateTime = datetime.strptime(date_time_str, "%m/%d/%Y, %I:%M:%S %p")

                    # Create and save the instance
                    probe_data_instance = mastering_data(
                        probe_no=probeNo,
                        a=a,
                        b=b,
                        e=e,
                        d=d,
                        o1=o1,
                        parameter_name=parameterName,
                        selected_value=selectedValue,
                        selected_mastering=selectedMastering,
                        date_time=dateTime
                    )
                    probe_data_instance.save()
                else:
                    print("DateTime field is missing.")
    
            else:
                print("Some required fields are missing or set to None.")

            # Now, you can use the received data as required
            print('Probe No:', probeNo)
            print('a:', a)
            print('b:', b)
            print('Parameter Name:', parameterName)
            print('selectedValue :',selectedValue)
            print('selectedMastering :',selectedMastering)
            print('dateTime:',date_time_str)

            # Assuming you want to save the received data into your database
            selected_value = data.get('selectedValue')
            selected_mastering = data.get('selectedMastering')
            print('Selected values from the client side:', selected_value, selected_mastering)

            # Your filtering logic based on selected_value and selected_mastering
            filtered_data = parameter_settings.objects.filter(
                model_id=selected_value,
                hide_checkbox=False
            ).values()

            filter_my = mastering_data.objects.filter(
                selected_value=selected_value,
            ).values()

            # Extract necessary data from filtered_data
            parameter_names = [item['parameter_name'] for item in filtered_data]
            low_mv = [item['low_mv'] for item in filtered_data]
            high_mv = [item['high_mv'] for item in filtered_data]
            probe_no = [item['probe_no'] for item in filtered_data]
            nominal = [item['nominal'] for item in filtered_data]
            usl = [item['usl'] for item in filtered_data]
            print('usl values is:',usl)
            lsl = [item['lsl'] for item in filtered_data]
            print('lsl value is :',lsl)
            selected_mastering = [item['mastering'] for item in filtered_data]
            print('mastering value is :',selected_mastering)
            utl = [item['utl'] for item in filtered_data]
            print('utl values is:',utl)
            ltl = [item['ltl'] for item in filtered_data]
            print('ltl value is :',ltl)
            digits = [item['digits'] for item in filtered_data]
            print('digits value is :',digits)
            d = [item['d'] for item in filter_my]
            
            o1 = [item['o1'] for item in filter_my]

            e = [item['e'] for item in filter_my]
            
            
            # Initialize an empty dictionary to store last_stored_parameter
            last_stored_parameter = {}

            # Iterate over items in filter_my and populate last_stored_parameter
            for item in filter_my:
                last_stored_parameter[item['parameter_name']] = item

            # Initialize empty lists to store o1 and d values
            o1_values = []
            d_values = []
            e_values = []
            probe_values = []

            # Iterate over last_stored_parameter to extract o1 and d values
            for parameter_name, item in last_stored_parameter.items():
                o1_values.append(item['o1'])
                d_values.append(item['d'])
                e_values.append(item['e'])
                probe_values.append(item['probe_no'])
                print('Last stored parameter_name for', parameter_name, 'is:', item)

            # Print o1 and d values
            print('o1 values:', o1_values)
            print('d values:', d_values)
            print('e_values :',e_values)
            print('probe_values :',probe_values)



            


            
            response_data = {
                'message': 'Successfully received the selected values.',
                'selectedValue': selected_value,
                'parameter_names': parameter_names,
                'low_mv': low_mv,
                'high_mv': high_mv,
                'probe_no': probe_no,
                'mastering':selected_mastering,
                'nominal': nominal,
                'lsl' : lsl,
                'usl' :usl,
                'e' : e,
                'd' : d,
                'o1' : o1,
                'last_stored_parameter' : last_stored_parameter,
                'o1_values': o1_values,
                'd_values': d_values,
                'e_values' : e_values,
                'probe_values' : probe_values,
                'utl':utl,
                'ltl':ltl,
                'digits':digits,

            }

            return JsonResponse(response_data)
        
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format in the request body'}, status=400)

    elif request.method == 'GET':
        try:

            # Your initial queryset for part_model_values
            part_model_values = TableOneData.objects.values_list('part_model', flat=True).distinct()
            print('part_model_values:', part_model_values)

            context = {
                'part_model_values': part_model_values,
            }

        except Exception as e:
            print(f'Exception: {e}')
            return JsonResponse({'key': 'value'})
    
    global serial_data
    with serial_data_lock:
        context['serial_data']=serial_data

    return render(request, 'app/master.html', context)



def measurement(request):

    if request.method == 'POST':
        try:
            # Parse the JSON data sent in the request
            data = json.loads(request.body)
            
            # Extract the part model value from the data
            part_model = data.get('partModel')
            print('your data from frontend:',part_model)

            additional_input_value = data.get('additionalInputValue')
            parameter_name = data.get('preValue')
            print('new values for this :',additional_input_value,parameter_name)

            parameter_name_queryset = parameter_settings.objects.filter(model_id=part_model).values_list('parameter_name', flat=True)

            # Convert the queryset to a list to pass only the values
            parameter_name_values = list(parameter_name_queryset)
            print('parameter_name values are:',parameter_name_values)

            lsl_values_queryset = parameter_settings.objects.filter(model_id=part_model).values_list('lsl', flat=True)

            # Convert the queryset to a list to pass only the values
            lsl_values = list(lsl_values_queryset)
            print('lsl values are:',lsl_values)

            usl_values_queryset = parameter_settings.objects.filter(model_id=part_model).values_list('usl', flat=True)

            # Convert the queryset to a list to pass only the values
            usl_values = list(usl_values_queryset)
            print('usl values are:',usl_values)

            

            nominal_values_queryset = parameter_settings.objects.filter(model_id=part_model).values_list('nominal', flat=True)
            nominal_values = list(nominal_values_queryset)
            print('your nominal values are:',nominal_values)

            measurement_mode_values_queryset = parameter_settings.objects.filter(model_id=part_model).values_list('measurement_mode', flat=True)
            measurement_mode_values = list(measurement_mode_values_queryset)
            print('your measurement_mode values are:',measurement_mode_values)

            # Prepare the response data
            response_data = {
                'parameterNameValues': parameter_name_values,
                'lslValues': lsl_values,
                'uslValues': usl_values,
                'nominalValues': nominal_values,
                'measurementModeValues': measurement_mode_values,
                'additionalInputValue': additional_input_value,
                 
            }

            # Return a JSON response with the retrieved values
            return JsonResponse(response_data)
        except Exception as e:
            # Return a JSON response indicating error
            return JsonResponse({'error': str(e)}, status=500)

    
    elif request.method == 'GET':
        part_model = request.GET.get('partModel', None)
        operator = request.GET.get('operator', None)
        machine = request.GET.get('machine', None)
        shift = request.GET.get('shift', None)
        hiddenTextarea = request.GET.get('hiddenTextarea', None)

        para_values_queryset = parameter_settings.objects.filter(model_id=part_model).values_list('parameter_name', flat=True).distinct()

        # Convert the queryset to a list to pass only the values
        para_values = list(para_values_queryset)
        print('para values are:',para_values)

        lsl_values_queryset = parameter_settings.objects.filter(model_id=part_model).values_list('lsl', flat=True)

        # Convert the queryset to a list to pass only the values
        lsl_values = list(lsl_values_queryset)
        print('lsl values are:',lsl_values)

        usl_values_queryset = parameter_settings.objects.filter(model_id=part_model).values_list('usl', flat=True)

        # Convert the queryset to a list to pass only the values
        usl_values = list(usl_values_queryset)
        print('usl values are:',usl_values)

        

        nominal_values_queryset = parameter_settings.objects.filter(model_id=part_model).values_list('nominal', flat=True)
        nominal_values = list(nominal_values_queryset)
        print('your nominal values are:',nominal_values)

        
        if part_model:

            hide = TableOneData.objects.filter(part_model = part_model).values_list('hide', flat=True).distinct()
            if hide.exists():  # Check if queryset has any results
                hide = hide[0]  # Access the first value
                print('hide:', hide)

        # Your initial queryset for part_model_values
        part_model_values = TableOneData.objects.values_list('part_model', flat=True).distinct()
        print('part_model_values:', part_model_values)

        if part_model:
            customer_name_values = TableOneData.objects.filter(part_model=part_model).values_list('customer_name', flat=True).distinct()
            if customer_name_values.exists():  # Check if queryset has any results
                customer_name_values = customer_name_values[0]  # Access the first value


        # Do something with the retrieved values, such as passing them to the template
        context = {
            'part_model': part_model,
            'operator': operator,
            'machine': machine,
            'shift': shift,
            'hidden-textarea': hiddenTextarea,
            'part_model_values': part_model_values,
            'customer_name_values':customer_name_values,
            'hide' : hide,
            'para_values' : para_values,
            'nominal_values' : nominal_values,
            'lsl_values' : lsl_values,
            'usl_values' : usl_values,
        }
        return render(request, 'app/measurement.html', context)
    else:
        # Handle other request methods if needed
        return HttpResponseNotAllowed(['GET'])


def measurebox(request):
    if request.method == 'GET':
        try:
            # Your initial queryset for part_model_values
            part_model_values = TableOneData.objects.values_list('part_model', flat=True).distinct()
            print('part_model_values:', part_model_values)

            operator_values = TableFourData.objects.values_list('operator_name', flat=True).distinct()
            print('operator_values:', operator_values)

            batch_no_values = TableTwoData.objects.values_list('batch_no', flat=True).distinct()
            print('operator_values:', batch_no_values)

            machine_name_values = TableThreeData.objects.values_list('machine_name', flat=True).distinct()
            print('operator_values:', machine_name_values)

            customer_name_values = TableOneData.objects.values_list('customer_name', flat=True).distinct()
            print('customer_name_values:', customer_name_values)

            context = {
                'part_model_values': part_model_values,
                'operator_values': operator_values,
                'batch_no_values': batch_no_values,
                'machine_name_values': machine_name_values,
                'customer_name_values': customer_name_values,
                

            }

        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format in the request body'}, status=400)
    return render(request,'app/measurebox.html',context)






def report(request):
    return render(request,'app/report.html')



from django.shortcuts import render
from django.http import JsonResponse
import json

last_received_data = []

def jeeva(request):
    global last_received_data

    if request.method == 'POST':
        try:
            # Retrieve data from the POST request
            data = json.loads(request.body)

            # Extract relevant parameters from the received data
            preValue = data.get('preValue')
            additional_input = data.get('additionalInputValue')
            lsl = data.get('lsl')
            usl = data.get('usl')

            # Store the received data in the global variable
            last_received_data.append ({
                'preValue': preValue,
                'additional_input': additional_input,
                'lsl': lsl,
                'usl': usl
            })

            print('context values are:', last_received_data)

        except Exception as e:
            # Return a JSON response indicating error
            return JsonResponse({'error': str(e)}, status=500)

    # Check if the request is AJAX
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'last_received_data': last_received_data})

    # Render the HTML template for regular requests
    return render(request, 'app/jeeva.html', {'last_received_data': last_received_data})
