
from django.contrib import admin
from.models import comport_settings,mastering_data,parameter_settings,MeasurementData,MasterIntervalSettings
from.models import find,TableOneData,TableTwoData,TableThreeData,TableFourData,TableFiveData,ShiftSettings,measure_data,UserLogin
from.models import consolidate_with_srno,consolidate_without_srno,parameterwise_report,jobwise_report
# Register your models here.

admin.site.register(find)
admin.site.register(TableOneData)
admin.site.register(TableTwoData)
admin.site.register(TableThreeData)
admin.site.register(TableFourData)
admin.site.register(TableFiveData)
admin.site.register(comport_settings)
admin.site.register(mastering_data)
admin.site.register(parameter_settings)
admin.site.register(MeasurementData)
admin.site.register(MasterIntervalSettings)
admin.site.register(ShiftSettings)
admin.site.register(measure_data)
admin.site.register(UserLogin)
admin.site.register(consolidate_with_srno)
admin.site.register(consolidate_without_srno)
admin.site.register(parameterwise_report)
admin.site.register(jobwise_report)