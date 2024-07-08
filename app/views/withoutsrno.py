from collections import defaultdict
from datetime import datetime
import io
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
import pandas as pd
from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import CSS, HTML
from app.models import MeasurementData, consolidate_without_srno, parameter_settings

def withoutsrno(request):
    if request.method == 'GET':
        consolidate_without_values = consolidate_without_srno.objects.all()
        part_model = consolidate_without_srno.objects.values_list('part_model', flat=True).distinct().get()

        fromDateStr = consolidate_without_srno.objects.values_list('formatted_from_date', flat=True).get()
        toDateStr = consolidate_without_srno.objects.values_list('formatted_to_date', flat=True).get()

        parameter_name = consolidate_without_srno.objects.values_list('parameter_name', flat=True).get()
        operator = consolidate_without_srno.objects.values_list('operator', flat=True).get()
        machine = consolidate_without_srno.objects.values_list('machine', flat=True).get()
        shift = consolidate_without_srno.objects.values_list('shift', flat=True).get()

        date_format_input = '%d-%m-%Y %I:%M:%S %p'
        from_datetime_naive = datetime.strptime(fromDateStr, date_format_input)
        to_datetime_naive = datetime.strptime(toDateStr, date_format_input)

        from_datetime = timezone.make_aware(from_datetime_naive, timezone.get_default_timezone())
        to_datetime = timezone.make_aware(to_datetime_naive, timezone.get_default_timezone())

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

        filtered_data = MeasurementData.objects.filter(**filter_kwargs).values()
        distinct_comp_sr_nos = filtered_data.filter(Q(comp_sr_no__isnull=True) | Q(comp_sr_no__exact=''))
        if not distinct_comp_sr_nos:
            context = {
                'no_results': True
            }
            return render(request, 'app/reports/consolidateWithoutSrNo.html', context)

        grouped_by_date = defaultdict(list)
        for entry in distinct_comp_sr_nos:
            grouped_by_date[entry['date']].append(entry)

        distinct_dates = grouped_by_date.keys()
        total_count = len(distinct_dates)

        data_dict = {
            'Date': [],
            'Operator': [],
            'Shift': []
        }
        parameter_data = parameter_settings.objects.filter(model_id=part_model).values('parameter_name', 'usl', 'lsl')

        for param in parameter_data:
            param_name = param['parameter_name']
            usl = param['usl']
            lsl = param['lsl']
            key = f"{param_name} <br>{usl} <br>{lsl}"
            data_dict[key] = []

        data_dict['Status'] = []

        accept_count = 0
        rework_count = 0
        reject_count = 0

        for date, records in grouped_by_date.items():
            formatted_date = date.strftime('%d-%m-%Y %I:%M:%S %p')
            operator = records[0]['operator']
            shift = records[0]['shift']
            part_status = records[0]['part_status']

            data_dict['Date'].append(formatted_date)
            data_dict['Operator'].append(operator)
            data_dict['Shift'].append(shift)

            temp_dict = {key: '' for key in data_dict.keys() if key not in ['Date', 'Operator', 'Shift', 'Status']}

            for record in records:
                param_name = record['parameter_name']
                usl = parameter_settings.objects.get(parameter_name=param_name, model_id=part_model).usl
                lsl = parameter_settings.objects.get(parameter_name=param_name, model_id=part_model).lsl
                key = f"{param_name} <br>{usl} <br>{lsl}"

                if record['status_cell'] == 'ACCEPT':
                    readings_html = f'<span style="background-color: #00ff00; padding: 2px;">{record["readings"]}</span>'
                elif record['status_cell'] == 'REWORK':
                    readings_html = f'<span style="background-color: yellow; padding: 2px;">{record["readings"]}</span>'
                elif record['status_cell'] == 'REJECT':
                    readings_html = f'<span style="background-color: red; padding: 2px;">{record["readings"]}</span>'

                temp_dict[key] = readings_html

            for key in temp_dict:
                data_dict[key].append(temp_dict[key])

            if part_status == 'ACCEPT':
                status_html = f'<span style="background-color: #00ff00; padding: 2px;">{part_status}</span>'
                accept_count += 1
            elif part_status == 'REWORK':
                status_html = f'<span style="background-color: yellow; padding: 2px;">{part_status}</span>'
                rework_count += 1
            elif part_status == 'REJECT':
                status_html = f'<span style="background-color: red; padding: 2px;">{part_status}</span>'
                reject_count += 1

            data_dict['Status'].append(status_html)

       
        df = pd.DataFrame(data_dict)
        df.index = df.index + 1  # Shift index by 1 to start from 1

        table_html = df.to_html(index=True, escape=False, classes='table table-striped')

        context = {
            'table_html': table_html,
            'consolidate_without_values': consolidate_without_values,
            'accept_count': accept_count,
            'rework_count': rework_count,
            'reject_count': reject_count,
            'total_count': total_count,
        }  
        request.session['data_dict'] = data_dict  
        return render(request, 'app/reports/consolidateWithoutSrNo.html', context)

    elif request.method == 'POST':
        export_type = request.POST.get('export_type')
        data_dict = request.session.get('data_dict')  # Retrieve data_dict from session
        if data_dict is None:
            return HttpResponse("No data available for export", status=400)

        df = pd.DataFrame(data_dict)
        df.index = df.index + 1

       

        if export_type == 'pdf':
            template = get_template('app/reports/consolidateWithoutSrNo.html')
            context = {
                'table_html': df.to_html(index=True, escape=False, classes='table table-striped table_data'),
                'consolidate_without_values': consolidate_without_srno.objects.all(),
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
            ''')


            # Inside your if block where export_type == 'pdf'
            pdf_filename = f"consolidateWithoutSrNo_{datetime.now().strftime('%Y/%m/%d_%H/%M/%S')}.pdf"


            pdf = HTML(string=html_string).write_pdf(stylesheets=[css])
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
            return response

        else:
            return HttpResponse("Invalid export type", status=400)

    return HttpResponse("Unsupported request method", status=405)
