import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from openpyxl import Workbook
from app.models import MeasurementData, TableFiveData,parameter_settings,TableOneData,TableThreeData,TableTwoData,TableFourData,consolidate_with_srno


def report(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form_id = data.get('id')
            if form_id == 'consolidate_with_srno':
                partModel = data.get('partModel')
                parameterName = data.get('parameterName')
                operator = data.get('operator')
                formattedFromDate = data.get('fromDate')
                formattedToDate = data.get('toDate')
                machine = data.get('machine')
                vendorCode = data.get('vendorCode')
                jobNo = data.get('jobNo')
                shift = data.get('shift')
                currentDateTime = data.get('currentDateTime')

                print("partModel",partModel)
                print("parameterName",parameterName)
                print("operator",operator)
                print("formattedFromDate",formattedFromDate)
                print("formattedToDate",formattedToDate)
                print("machine",machine)
                print("vendorCode",vendorCode)
                print("jobNo",jobNo)
                print("shift",shift)
                print("currentDateTime",currentDateTime)

                # Get or create consolidate_with_srno instance with id=1
                instance, created = consolidate_with_srno.objects.get_or_create(id=1)

                # Update the instance with the new data
                instance.part_model = partModel
                instance.parameter_name = parameterName
                instance.operator = operator
                instance.formatted_from_date = formattedFromDate
                instance.formatted_to_date = formattedToDate
                instance.machine = machine
                instance.vendor_code = vendorCode
                instance.job_no = jobNo
                instance.shift = shift
                instance.current_date_time = currentDateTime

                # Save the instance
                instance.save()
            
                

            part_model = data.get('partModel')
            print(part_model)

            # Filter parameter_settings where model_id matches part_model and get distinct parameter_name
            parameter_data = parameter_settings.objects.filter(model_id=part_model).values_list('parameter_name', flat=True).distinct()
            print('Filtered parameter_name:', parameter_data)

            punch_data = MeasurementData.objects.filter(part_model=part_model).values_list('comp_sr_no', flat=True).distinct()
            print('your component_serial_number from that views:',punch_data)
                        
             # Prepare the response data
            response_data = {
                'status': 'success',
                'message': f"Received model: {part_model}",
                'parameter_names': list(parameter_data),
                'component_serial_numbers': list(punch_data)
            }
            return JsonResponse(response_data)
        except json.JSONDecodeError:
            response = {'status': 'error', 'message': 'Invalid JSON'}
            return JsonResponse(response, status=400)
         
    elif request.method == 'GET':
        try:
            model_data = TableOneData.objects.values_list('part_model', flat=True).distinct()
            print('your part_model from that views:',model_data)
            
            machine_data = TableThreeData.objects.values_list('machine_name', flat=True).distinct()
            print('your part_model from that views:',machine_data)
            
            shift_data = TableTwoData.objects.values_list('batch_no', flat=True).distinct()
            print('your part_model from that views:',shift_data)
            
            operator_data = TableFourData.objects.values_list('operator_name', flat=True).distinct()
            print('your part_model from that views:',operator_data)
            
           
            vendor_data = TableFiveData.objects.values_list('vendor_code', flat=True).distinct()
            print('your vendor from that views:',vendor_data)
            
            # Create a context dictionary to pass the data to the template
            context = {
                'model_data' : model_data,
                'machine_data' : machine_data,
                'shift_data' : shift_data,
                'operator_data' : operator_data,
                'vendor_data' : vendor_data,

            }
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format in the request body'}, status=400)    
    # Render the template with the context
    return render(request, 'app/report.html', context)
