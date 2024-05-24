
from django.contrib import admin
from.models import MasterData,comport_settings,mastering_data,parameter_settings,MeasurementData
from.models import find,TableOneData,TableTwoData,TableThreeData,TableFourData,TableFiveData
# Register your models here.

admin.site.register(find)
admin.site.register(TableOneData)
admin.site.register(TableTwoData)
admin.site.register(TableThreeData)
admin.site.register(TableFourData)
admin.site.register(TableFiveData)
admin.site.register(MasterData)
admin.site.register(comport_settings)
admin.site.register(mastering_data)
admin.site.register(parameter_settings)
admin.site.register(MeasurementData)