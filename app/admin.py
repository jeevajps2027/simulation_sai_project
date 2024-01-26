
from django.contrib import admin
from.models import viewvalues,parameterValue
from.models import readings,find,TableOneData,TableTwoData,TableThreeData,TableFourData,TableFiveData
# Register your models here.

admin.site.register(find)
admin.site.register(readings)
admin.site.register(TableOneData)
admin.site.register(TableTwoData)
admin.site.register(TableThreeData)
admin.site.register(TableFourData)
admin.site.register(TableFiveData)
admin.site.register(viewvalues)
admin.site.register(parameterValue)

