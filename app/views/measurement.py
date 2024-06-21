from collections import defaultdict
from datetime import datetime
import json
import threading

from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render

from app.models import MasterIntervalSettings, MeasurementData, TableOneData, mastering_data, measure_data, parameter_settings

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

def process_row(row):
    try:
        date_str = row.get('date')
        # Convert date string to datetime object
        date_obj = datetime.strptime(date_str, '%d/%m/%Y %I:%M:%S %p')
        MeasurementData.objects.create(
            parameter_name=row.get('parameterName'),
            readings=row.get('readings'),
            nominal=row.get('nominal'),
            lsl=row.get('lsl'),
            usl=row.get('usl'),
            status_cell=row.get('statusCell'),
            date=date_obj,
            operator=row.get('operator'),
            shift=row.get('shift'),
            machine=row.get('machine'),
            part_model=row.get('partModel'),
            part_status=row.get('partStatus'),
            customer_name=row.get('customerName'),
            comp_sr_no=row.get('compSrNo')
        )
        return None
    except Exception as e:
        return str(e)

def measurement(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("data:",data)

            table_data = data.get('tableData', {}).get('formDataArray', [])

            errors = [process_row(row) for row in table_data]
            if any(errors):
                return JsonResponse({'status': 'error', 'message': errors[0]}, status=500)

            part_model = data.get('partModel')
            customer_name_values = TableOneData.objects.filter(part_model=part_model).values_list('customer_name', flat=True).first()

            comp_sr_no_list_distinct = MeasurementData.objects.filter(part_model=part_model).values_list('comp_sr_no', flat=True).distinct()
            part_status_dict = defaultdict(set)
            for comp_sr_no in comp_sr_no_list_distinct:
                part_statuses = MeasurementData.objects.filter(comp_sr_no=comp_sr_no).values_list('part_status', flat=True).distinct()
                part_status_dict[comp_sr_no].update(part_statuses)

            part_status_count = defaultdict(int)
            for part_statuses in part_status_dict.values():
                for status in part_statuses:
                    part_status_count[status] += 1

            parameter_settings_qs = parameter_settings.objects.filter(model_id=part_model, hide_checkbox=False)
            last_stored_parameter = {item['parameter_name']: item for item in mastering_data.objects.filter(selected_value=part_model, parameter_name__in=parameter_settings_qs.values_list('parameter_name', flat=True)).values()}


            response_data = {
                'status': 'success',
                'message': 'Data successfully processed.',
                'parameterNameValues': list(parameter_settings_qs.values_list('parameter_name', flat=True)),
                'lslValues': list(parameter_settings_qs.values_list('lsl', flat=True)),
                'uslValues': list(parameter_settings_qs.values_list('usl', flat=True)),
                'ltlValues': list(parameter_settings_qs.values_list('ltl', flat=True)),
                'utlValues': list(parameter_settings_qs.values_list('utl', flat=True)),
                'nominalValues': list(parameter_settings_qs.values_list('nominal', flat=True)),
                'measurementModeValues': list(parameter_settings_qs.values_list('measurement_mode', flat=True)),
                'o1_values': [item['o1'] for item in last_stored_parameter.values()],
                'd_values': [item['d'] for item in last_stored_parameter.values()],
                'e_values': [item['e'] for item in last_stored_parameter.values()],
                'probe_values': [item['probe_no'] for item in last_stored_parameter.values()],
                'step_no_values': list(parameter_settings_qs.values_list('step_no', flat=True)),
                'customer_name_values': customer_name_values,
                'part_status_counts': dict(part_status_count),
            }

            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


    elif request.method == 'GET':
        try:
            part_model = measure_data.objects.values_list('part_model', flat=True).distinct().get()
            print("part_model:", part_model)
        except measure_data.DoesNotExist:
            part_model = None
            print("No part model found.")
        except measure_data.MultipleObjectsReturned:
            print("Multiple part models found.")


        step_no_values_queryset = parameter_settings.objects.filter(model_id=part_model).values_list('step_no', flat=True)
        step_no_values = list(step_no_values_queryset)
        print('your step_no values are:',step_no_values)


        if part_model:
            hide = TableOneData.objects.filter(part_model = part_model).values_list('hide', flat=True).distinct()
            if hide.exists():  # Check if queryset has any results
                hide = hide[0]  # Access the first value
                print('hide:', hide)

        # Your initial queryset for part_model_values
        part_model_values = measure_data.objects.values_list('part_model', flat=True).distinct()
        print('part_model_values:', part_model_values)

        machine_values = measure_data.objects.values_list('machine', flat=True).distinct()
        print('machine_values:', machine_values)

        operator_values = measure_data.objects.values_list('operator', flat=True).distinct()
        print('operator_values:', operator_values)

        shift_values = measure_data.objects.values_list('shift', flat=True).distinct()
        print('shift_values:', shift_values)


        master_interval_settings = MasterIntervalSettings.objects.all()
        print("master_interval_settings:",master_interval_settings)

        for setting in master_interval_settings:
            print("ID:", setting.id)
            print("Timewise:", setting.timewise)
            print("Componentwise:", setting.componentwise)
            print("Hour:", setting.hour)
            print("Minute:", setting.minute)
            print("Component No:", setting.component_no)
        # Convert the queryset to a list of dictionaries
        interval_settings_list = list(master_interval_settings.values())

        # Serialize the list to JSON
        interval_settings_json = json.dumps(interval_settings_list)
        # Do something with the retrieved values, such as passing them to the template
        context = {
            'part_model': part_model,
            'part_model_values': part_model_values,
            'step_no_values' : step_no_values,
            'interval_settings_json':interval_settings_json,
            'machine_values' : machine_values,
            'operator_values' :operator_values,
            'shift_values' : shift_values,
            'hide':hide,
        }
        global serial_data
        with serial_data_lock:
            context['serial_data']=serial_data
        return render(request, 'app/measurement.html', context)
    else:
        # Handle other request methods if needed
        return HttpResponseNotAllowed(['GET'])


"""
1.defaultdict : is a subclass of Python's built-in dictionary (dict). 
  It overrides one method (__missing__) to provide a default value for a nonexistent key.

  in our case it used for counting elements,grouping data
"""