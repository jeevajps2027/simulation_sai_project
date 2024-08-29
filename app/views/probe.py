from django.shortcuts import redirect, render




def probe(request):
    from app.models import find
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
        

    return render(request, 'app/probe.html', {'probe_coefficients': probe_coefficients ,'low_count':low_count })

"""
1.import re
  Regular Expressions -  powerful tools used for pattern matching and string manipulation

2.serial
  Serial Library: This refers to the serial library in Python,
  communication with devices like Arduino, sensors, or other hardware

3.Threading
  Threads enable concurrent execution, allowing multiple tasks to run simultaneously and improve performance


"""