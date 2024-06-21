from datetime import datetime
import json
import threading

from django.http import JsonResponse
from django.shortcuts import render

from app.models import mastering_data, measure_data, parameter_settings




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


def master(request):
    if request.method == 'POST':
        try:
            
            # Retrieve the selected values from the request body
            data = json.loads(request.body.decode('utf-8'))
            print("data",data)

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
            part_model_values = measure_data.objects.values_list('part_model', flat=True).distinct()
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
