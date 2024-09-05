from collections import defaultdict
from datetime import datetime
import json
import threading
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
import pytz
from django.utils import timezone  
from django.db.models import Q

from app.models import MasterIntervalSettings, MeasurementData, ResetCount, TableOneData, Master_settings, measure_data, parameter_settings


def process_row(row):
    try:
        date_str = row.get('date')
        print("date_str", date_str)
        
        # Convert date string to datetime object
        date_obj = datetime.strptime(date_str, '%d/%m/%Y %I:%M:%S %p')
        print("date_obj", date_obj)
        
        # Make the datetime object timezone-aware
        timezone = pytz.timezone('Asia/Kolkata')  # Replace with your timezone
        date_obj_aware = timezone.localize(date_obj)
        print("date_obj_aware", date_obj_aware)
        
        # Remove timezone information before storing
        date_obj_naive = date_obj_aware.replace(tzinfo=None)
        print("date_obj_naive", date_obj_naive)
        
        MeasurementData.objects.create(
            parameter_name=row.get('parameterName'),
            readings=row.get('readings'),
            nominal=row.get('nominal'),
            lsl=row.get('lsl'),
            usl=row.get('usl'),
            status_cell=row.get('statusCell'),
            date=date_obj_naive,
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
            form_id = data.get('id')
            print("form_id:",form_id)
            
            if form_id == 'punch_value':
                punch_value = data.get('punch_value')
                part_model = data.get('part_model_value')
                print(punch_value , part_model)

                # Check if punch_value exists in the comp_sr_no field of MeasurementData
                if MeasurementData.objects.filter(part_model=part_model, comp_sr_no=punch_value).exists():
                    print(f"Punch number '{punch_value}' is already present.")
                    return JsonResponse({'status': 'error', 'message': f"Punch number '{punch_value}' is already present."})

                   
             

            table_data = data.get('tableData', {}).get('formDataArray', [])

            errors = [process_row(row) for row in table_data]
            if any(errors):
                return JsonResponse({'status': 'error', 'message': errors[0]}, status=500)
            
            if form_id == 'reset_count':
                part_model = data.get('partModel')
                date = data.get('date')

                # Check if a ResetCount instance with the same part_model exists
                reset_count, created = ResetCount.objects.update_or_create(
                    part_model=part_model,
                    defaults={
                        'date': date
                    }
                )

            part_model = data.get('partModel')
            customer_name_values = TableOneData.objects.filter(part_model=part_model).values_list('customer_name', flat=True).first()

           
            parameter_settings_qs = parameter_settings.objects.filter(model_id=part_model, hide_checkbox=False).order_by('id')
            last_stored_parameter = {item['parameter_name']: item for item in Master_settings.objects.filter(selected_value=part_model, parameter_name__in=parameter_settings_qs.values_list('parameter_name', flat=True)).values()}


            response_data = {
                'status': 'success',
                'message': 'Do next Measurement cycle',
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
            }

            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
    elif request.method == 'DELETE':
        data = json.loads(request.body)
        punch_value = data.get('punch_value')
        part_model = data.get('part_model_value')

        try:
            MeasurementData.objects.filter(part_model=part_model, comp_sr_no=punch_value).delete()
            return JsonResponse({'status': 'success', 'message': 'Punch value deleted successfully.'})
        except MeasurementData.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Punch value does not exist.'})

        
        
   

    elif request.method == 'GET':
         # Initialize the hide variable with a default value
        hide = None
        try:
            part_model = measure_data.objects.values_list('part_model', flat=True).distinct().get()
            print("part_model:", part_model)
        except measure_data.DoesNotExist:
            part_model = None
            print("No part model found.")
        except measure_data.MultipleObjectsReturned:
            print("Multiple part models found.")

        parameter_settings_qs = parameter_settings.objects.filter(model_id=part_model, hide_checkbox=False).order_by('id')
        last_stored_parameters = Master_settings.objects.filter(selected_value=part_model, parameter_name__in=parameter_settings_qs.values_list('parameter_name', flat=True))
        # Create a dictionary with parameter_name as keys and items as values
        last_stored_parameter = {item['parameter_name']: item for item in last_stored_parameters.values()}
        print("last_stored_parameter",last_stored_parameter)
        # Extract datetime objects from the values of last_stored_parameter
        last_dates = [item['date_time'].strftime("%m-%d-%Y %I:%M:%S %p") for item in last_stored_parameter.values()]
        # Get distinct formatted dates
        last_stored_dates =', '.join(list(set(last_dates)))

        print("Distinct formatted dates:", last_stored_dates)
                        

        step_no_values_queryset = parameter_settings.objects.filter(model_id=part_model).values_list('step_no', flat=True).order_by('id')
        step_no_values = list(step_no_values_queryset)
        print('your step_no values are:',step_no_values)


        if part_model:
            hide = TableOneData.objects.filter(part_model = part_model).values_list('hide', flat=True).distinct()
             # Retrieve the distinct 'part_no' and 'char_lmt' values
            part_no_char_lmt = TableOneData.objects.filter(part_model=part_model).values_list('part_no', 'char_lmt').distinct()

            if hide.exists():  # Check if queryset has any results
                hide = hide[0]  # Access the first value
                print('hide:', hide)
             # Loop through the 'part_no' and 'char_lmt' values
            for part_no, char_lmt in part_no_char_lmt:
                print('part_no:', part_no)
                print('char_lmt:', char_lmt)


        # Retrieve the datetime_value from the specified part_model in ResetCount
        reset_count_value = ResetCount.objects.filter(part_model=part_model).first()
        if reset_count_value:
            date_format_input = '%d/%m/%Y %I:%M:%S %p'
            datetime_naive = datetime.strptime(reset_count_value.date, date_format_input)
            date_obj_naive = timezone.make_aware(datetime_naive, timezone.get_default_timezone())
            datetime_value = date_obj_naive.replace(tzinfo=None)
            print("datetime_value:", datetime_value)
        else:
            datetime_value = None
            print("No datetime value found for the specified part model")
        
        if datetime_value:
            # Filter MeasurementData objects from the datetime_value onwards
            filtered_measurement_data = MeasurementData.objects.filter(part_model=part_model, date__gt=datetime_value)
        else:
            # Get all MeasurementData objects for the specified part_model
            filtered_measurement_data = MeasurementData.objects.filter(part_model=part_model)
        
        # Retrieve and print distinct component serial numbers with non-empty values
        comp_sr_no_list = filtered_measurement_data.exclude(comp_sr_no__isnull=True).exclude(comp_sr_no__exact='').values_list('comp_sr_no', flat=True).distinct()
        print('Distinct component_serial_number (non-empty):', comp_sr_no_list)
        
        # Retrieve all values which contain null or empty component serial numbers
        invalid_values_list = filtered_measurement_data.filter(Q(comp_sr_no__isnull=True) | Q(comp_sr_no__exact=''))
        
        # Initialize variables to track distinct dates, part_status, and associated IDs
        distinct_dates = set()
        date_status_id_map = defaultdict(lambda: {'part_statuses': set(), 'data': []})
        status_counts = defaultdict(int)
        
        # Iterate through the queryset to collect distinct dates, part_status, and associated IDs
        for obj in invalid_values_list:
            date_str = obj.date.strftime('%Y-%m-%d %H:%M:%S')  # Format date as string
            part_status = obj.part_status  # Get part_status
            if date_str not in distinct_dates:
                distinct_dates.add(date_str)
            if part_status not in date_status_id_map[date_str]['part_statuses']:
                date_status_id_map[date_str]['part_statuses'].add(part_status)
                date_status_id_map[date_str]['data'].append({'id': obj.id, 'part_status': part_status})
                status_counts[part_status] += 1
        
        # Initialize a dictionary to store part statuses for each component serial number
        part_status_dict = defaultdict(set)
        
        # Populate the dictionary with distinct part statuses for each component serial number
        for comp_sr_no in comp_sr_no_list:
            part_statuses = filtered_measurement_data.filter(comp_sr_no=comp_sr_no).values_list('part_status', flat=True).distinct()
            part_status_dict[comp_sr_no].update(part_statuses)
        
        # Initialize a dictionary to count each part status
        part_status_count = defaultdict(int)
        
        # Count part statuses and populate part_status_count
        for comp_sr_no, part_statuses in part_status_dict.items():
            for status in part_statuses:
                part_status_count[status] += 1
        
        # Print the component serial numbers along with their distinct part statuses
        for comp_sr_no, part_statuses in part_status_dict.items():
            print(f'Component Serial Number: {comp_sr_no}, Part Statuses: {list(part_statuses)}')
        
        # Print the counts for each part status from part_status_count
        print("\nPart Status Counts (with component serial numbers):")
        for status, count in part_status_count.items():
            print(f"{status}: {count}")
        
        # Combine counts from status_counts and part_status_count for overall counts
        overall_status_counts = defaultdict(int)
        for status, count in status_counts.items():
            overall_status_counts[status] += count
        for status, count in part_status_count.items():
            overall_status_counts[status] += count
        
        # Print overall status counts
        print("\nOverall Status Counts (including without component serial numbers):")
        if 'ACCEPT' not in overall_status_counts:
            overall_status_counts['ACCEPT'] = 0
        if 'REJECT' not in overall_status_counts:
            overall_status_counts['REJECT'] = 0
        if 'REWORK' not in overall_status_counts:
            overall_status_counts['REWORK'] = 0
        
        print(f"ACCEPT: {overall_status_counts['ACCEPT']}")
        print(f"REJECT: {overall_status_counts['REJECT']}")
        print(f"REWORK: {overall_status_counts['REWORK']}")
        
#///////////////////////////////////////////////////////////////////////////////////////////////////////

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
            'last_stored_dates':last_stored_dates,
            'machine_values' : machine_values,
            'operator_values' :operator_values,
            'shift_values' : shift_values,
            'hide':hide,
            'part_no':part_no,
            'char_lmt':char_lmt,
            'overall_accept_count': overall_status_counts['ACCEPT'],
            'overall_reject_count': overall_status_counts['REJECT'],
            'overall_rework_count': overall_status_counts['REWORK'],
        }
       
        return render(request, 'app/measurement.html', context)
    else:
        # Handle other request methods if needed
        return HttpResponseNotAllowed(['GET'])


"""
1.defaultdict : is a subclass of Python's built-in dictionary (dict). 
  It overrides one method (__missing__) to provide a default value for a nonexistent key.

  in our case it used for counting elements,grouping data
"""