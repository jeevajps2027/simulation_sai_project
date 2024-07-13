from datetime import datetime
import pandas as pd
from django.shortcuts import render
from django.utils import timezone
from app.models import MeasurementData, parameter_settings, consolidate_with_srno
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML, CSS
from io import BytesIO

def srno(request):
    if request.method == 'GET':
        consolidate_values = consolidate_with_srno.objects.all()
        part_model = consolidate_with_srno.objects.values_list('part_model', flat=True).distinct().get()
        print("part_model:", part_model)

        fromDateStr = consolidate_with_srno.objects.values_list('formatted_from_date', flat=True).get()
        toDateStr = consolidate_with_srno.objects.values_list('formatted_to_date', flat=True).get()
        print("fromDate:", fromDateStr, "toDate:", toDateStr)

        parameter_name = consolidate_with_srno.objects.values_list('parameter_name', flat=True).get()
        print("parameter_name:", parameter_name)
        operator = consolidate_with_srno.objects.values_list('operator', flat=True).get()
        print("operator:", operator)
        machine = consolidate_with_srno.objects.values_list('machine', flat=True).get()
        print("machine:", machine)
        shift = consolidate_with_srno.objects.values_list('shift', flat=True).get()
        print("shift:", shift)
        job_no = consolidate_with_srno.objects.values_list('job_no', flat=True).get()
        print("job_no:", job_no)

        date_format_input = '%d-%m-%Y %I:%M:%S %p'
        from_datetime_naive = datetime.strptime(fromDateStr, date_format_input)
        to_datetime_naive = datetime.strptime(toDateStr, date_format_input)

        from_datetime = timezone.make_aware(from_datetime_naive, timezone.get_default_timezone())
        to_datetime = timezone.make_aware(to_datetime_naive, timezone.get_default_timezone())

        print("from_datetime:", from_datetime, "to_datetime:", to_datetime)

        filter_kwargs = {
            'date__range': (from_datetime, to_datetime),
            'part_model': part_model,
        }

        if parameter_name != "ALL":
            filter_kwargs['parameter_name'] = parameter_name

        if operator != "ALL":
            filter_kwargs['operator'] = operator

        if machine != "ALL":
            filter_kwargs['machine'] = machine

        if shift != "ALL":
            filter_kwargs['shift'] = shift

        if job_no != "ALL":
            filter_kwargs['comp_sr_no'] = job_no

        filtered_data = MeasurementData.objects.filter(**filter_kwargs).values()

        distinct_comp_sr_nos = filtered_data.exclude(comp_sr_no__isnull=True).exclude(comp_sr_no__exact='').values_list('comp_sr_no', flat=True).distinct()
        print("distinct_comp_sr_nos:", distinct_comp_sr_nos)
        if not distinct_comp_sr_nos:
            context = {
                'no_results': True
            }
            return render(request, 'app/reports/consolidateSrNo.html', context)

        total_count = distinct_comp_sr_nos.count()
        print(f"Number of distinct comp_sr_no values: {total_count}")

        data_dict = {
            'Date': [],
            'Job Number': [],
            'Shift': [],
            'Operator': [],
            '1':[],
            '2':[],
            '3':[],
            '4':[],
            '5':[],
            '6':[],
            '7':[],
            '8':[],
            '9':[],
            '10':[],
            '11':[],
            '12':[],
            '13':[],
            '14':[],
            '15':[],
            '16':[],
            '17':[],
            '18':[],
            '19':[],
            '20':[],
            '21':[],
            '22':[],
            '23':[],
            '24':[],
            '25':[],
            '26':[],
            '27':[],
            '28':[],
            '29':[],
            '30':[],
            '31':[],
            '32':[],
            '33':[],
            '34':[],
            '35':[],
            '36':[],
            '37':[],
            '38':[],
            '39':[],
            '40':[],
            '41':[],


        }

        parameter_data = parameter_settings.objects.filter(model_id=part_model).values('parameter_name', 'usl', 'lsl')

        for param in parameter_data:
            param_name = param['parameter_name']
            usl = param['usl']
            lsl = param['lsl']
            key = f"{param_name} <br>{usl} <br>{lsl}"
            data_dict[key] = []

        data_dict['Status'] = []

        status_counts = {'ACCEPT': 0, 'REJECT': 0, 'REWORK': 0}

        for comp_sr_no in distinct_comp_sr_nos:
            print(f"Processing comp_sr_no: {comp_sr_no}")

            filter_params = filter_kwargs.copy()
            filter_params['comp_sr_no'] = comp_sr_no

            part_status = MeasurementData.objects.filter(**filter_params).values_list('part_status', flat=True).distinct().first()
            print(f"Part Status: {part_status}")

            comp_sr_no_data = MeasurementData.objects.filter(**filter_params).values(
                'parameter_name', 'readings', 'status_cell', 'operator', 'shift', 'machine', 'date'
            )

            combined_row = {
                'Date': '',
                'Job Number': comp_sr_no,
                'Shift': '',
                'Operator': '',
                'Status': ''
            }

            for data in comp_sr_no_data:
                parameter_name = data['parameter_name']
                usl = parameter_settings.objects.get(parameter_name=parameter_name, model_id=part_model).usl
                lsl = parameter_settings.objects.get(parameter_name=parameter_name, model_id=part_model).lsl
                key = f"{parameter_name} <br>{usl} <br>{lsl}"
                formatted_date = data['date'].strftime('%d-%m-%Y %I:%M:%S %p')
                if data['status_cell'] == 'ACCEPT':
                    readings_html = f'<span style="background-color: #00ff00; padding: 2px;">{data["readings"]}</span>'
                elif data['status_cell'] == 'REWORK':
                    readings_html = f'<span style="background-color: yellow; padding: 2px;">{data["readings"]}</span>'
                elif data['status_cell'] == 'REJECT':
                    readings_html = f'<span style="background-color: red; padding: 2px;">{data["readings"]}</span>'
                combined_row[key] = readings_html
                combined_row['Date'] = formatted_date
                combined_row['Operator'] = data['operator']
                combined_row['Shift'] = data['shift']

            if part_status == 'ACCEPT':
                status_html = f'<span style="background-color: #00ff00; padding: 2px;">{part_status}</span>'
                status_counts['ACCEPT'] += 1
            elif part_status == 'REWORK':
                status_html = f'<span style="background-color: yellow; padding: 2px;">{part_status}</span>'
                status_counts['REWORK'] += 1
            elif part_status == 'REJECT':
                status_html = f'<span style="background-color: red; padding: 2px;">{part_status}</span>'
                status_counts['REJECT'] += 1

            combined_row['Status'] = status_html

            for key in data_dict:
                data_dict[key].append(combined_row.get(key, ''))

        print(f"Status counts: ACCEPT={status_counts['ACCEPT']}, REJECT={status_counts['REJECT']}, REWORK={status_counts['REWORK']}")

        df = pd.DataFrame(data_dict)
        df.index = df.index + 1

        table_html = df.to_html(index=True, escape=False, classes='table table-striped')

        context = {
            'table_html': table_html,
            'consolidate_values': consolidate_values,
            'total_count': total_count,
            'accept_count': status_counts['ACCEPT'],
            'reject_count': status_counts['REJECT'],
            'rework_count': status_counts['REWORK'],
        }

        request.session['data_dict'] = data_dict  # Save data_dict to the session for POST request

        return render(request, 'app/reports/consolidateSrNo.html', context)

    elif request.method == 'POST':
        export_type = request.POST.get('export_type')
        data_dict = request.session.get('data_dict')  # Retrieve data_dict from session
        if data_dict is None:
            return HttpResponse("No data available for export", status=400)

        df = pd.DataFrame(data_dict)
        df.index = df.index + 1

       

        if export_type == 'pdf':
            template = get_template('app/reports/consolidateSrNo.html')
            context = {
                'table_html': df.to_html(index=True, escape=False, classes='table table-striped table_data'),
                'consolidate_values': consolidate_with_srno.objects.all(),
                'total_count': df.shape[0],  # Use DataFrame shape for total count
                'accept_count': df[df['Status'].str.contains('ACCEPT')].shape[0],
                'reject_count': df[df['Status'].str.contains('REJECT')].shape[0],
                'rework_count': df[df['Status'].str.contains('REWORK')].shape[0],

            }
            html_string = template.render(context)

            # CSS for scaling down the content to fit a single PDF page
            css = CSS(string='''
                @page {
                    size: A4 landscape; /* Landscape mode to fit more content horizontally */
                    margin: 0.5cm; /* Adjust margin as needed */
                }
                body {
                    margin: 0; /* Give body some margin to prevent overflow */
                    transform: scale(0.2); /* Scale down the entire content */
                    transform-origin: 0 0; /* Ensure the scaling starts from the top-left corner */
                }
                .table_data {
                    width: 5000px; /* Increase the table width */
                }
                table {
                    table-layout: fixed; /* Fix the table layout */
                    font-size: 20px; /* Increase font size */
                    border-collapse: collapse; /* Collapse table borders */
                }
                table, th, td {
                    border: 1px solid black; /* Add border to table */
                }
                th, td {
                    word-wrap: break-word; /* Break long words */
                }
                .no-pdf {
                    display: none;
                }
            ''')


            # Inside your if block where export_type == 'pdf'
            pdf_filename = f"consolidateSrNo_{datetime.now().strftime('%Y/%m/%d_%H/%M/%S')}.pdf"


            pdf = HTML(string=html_string).write_pdf(stylesheets=[css])
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
            return response

        else:
            return HttpResponse("Invalid export type", status=400)

    return HttpResponse("Unsupported request method", status=405)
