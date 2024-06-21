
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from app.models import MasterIntervalSettings, ShiftSettings

@csrf_exempt
def utility(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            form_id = data.get('id')
            
            if form_id == 'master_interval':
                timewise = data.get('timewise')
                componentwise = data.get('componentwise')
                hour = data.get('hour')
                minute = data.get('minute')
                component_no = data.get('component_no')

                print("Master Interval Settings:")
                print("id_value:", form_id)
                print("timewise:", timewise)
                print("componentwise:", componentwise)
                print("hour:", hour)
                print("minute:", minute)
                print("component_no:", component_no)
                # Convert hour, minute, and component_no to integers if they exist
                hour = int(hour) if hour else None
                minute = int(minute) if minute else None
                component_no = int(component_no) if component_no else None

               # Retrieve existing instance or create a new one
                interval_settings, created = MasterIntervalSettings.objects.get_or_create(id=1)
                
                # Update attributes
                interval_settings.timewise = timewise
                interval_settings.componentwise = componentwise
                interval_settings.hour = hour
                interval_settings.minute = minute
                interval_settings.component_no = component_no
                
                # Save changes to the database
                interval_settings.save()

                print("Master Interval Settings saved:", interval_settings)

                # Process the interval settings data here

            elif form_id == 'shift_settings':
                shift = data.get('shift')
                shift_time = data.get('shift_time')

                print("Shift Settings:")
                print("id_value:", form_id)
                print("shift:", shift)
                print("shift_time:", shift_time)

                # Check if a ShiftSettings object with the same shift already exists
                existing_shift = ShiftSettings.objects.filter(shift=shift).first()

                if existing_shift:
                    # Update the shift_time of the existing ShiftSettings object
                    existing_shift.shift_time = shift_time
                    existing_shift.save()
                else:
                    # Create a new ShiftSettings object
                    shift_settings_obj = ShiftSettings.objects.create(shift=shift, shift_time=shift_time)
                    shift_settings_obj.save()
            elif form_id == 'customer_details':
                customer_name = data.get('customer_name')
                contact_person = data.get('contact_person')
                email = data.get('email')
                phone_no = data.get('phone_no')
                dept = data.get('dept')
                address = data.get('address')
                logo_file = data.get('logo')
                
                print("Logo File Name:", logo_file)
               
                print("customer_details:",customer_name,contact_person,email,phone_no,dept,address)


            return JsonResponse({'status': 'success'})
        
        elif request.method == 'GET':
            try:
                master_interval_settings = MasterIntervalSettings.objects.all()
                shift_settings = ShiftSettings.objects.all()
                print("Master Interval Settings:", master_interval_settings)
                print("Shift Settings:", shift_settings)
                # Pass the retrieved data to the template for rendering
                return render(request, 'app/utility.html', {'master_interval_settings': master_interval_settings,'shift_settings':shift_settings})

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

            
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return render(request, 'app/utility.html')
