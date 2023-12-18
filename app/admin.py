from django.contrib import admin
from.models import probecalibration,partTable,batchTable,machineTable,operatorTable,vendorTable
# Register your models here.

admin.site.register(probecalibration)
admin.site.register(partTable)
admin.site.register(batchTable)
admin.site.register(machineTable)
admin.site.register(operatorTable)
admin.site.register(vendorTable)