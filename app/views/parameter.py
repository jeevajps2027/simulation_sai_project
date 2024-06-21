import json
from django.http import  JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from app.models import TableOneData, parameter_settings


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

   

    return render(request, 'app/parameter.html')


"""
1.get_object_or_404 : is a shortcut function in Django used to retrieve an object from the database

2.CSRF (Cross-Site Request Forgery)
  csrf_exempt in Django disables CSRF protection for a specific view, allowing requests to bypass CSRF token validation.

"""