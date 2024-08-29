from django.conf import settings
from django.urls import path,include
from django.conf.urls.static import static
from .views import home,index,comport,probe,trace,parameter,master,measurebox,measurement
from .views import utility,report,spc,srno,withoutsrno,paraReport,jobReport

urlpatterns = [
    path('',home,name="home"),
    path('index/',index,name="index"),
    path('comport/',comport,name="comport"),
    path('probe/',probe,name="probe"),
    path('trace/',trace,name="trace"),
    path('parameter/',parameter,name="parameter"),
    path('master/',master,name="master"),
    path('measurebox/',measurebox,name="measurebox"),
    path('measurement/',measurement,name="measurement"),
    path('utility/',utility,name="utility"),
    path('report/',report,name="report"),
    path('spc/',spc,name="spc"),
    path('srno/',srno,name="srno"),
    path('withoutsrno/',withoutsrno,name="withoutsrno"),
    path('paraReport/',paraReport,name="paraReport"),
    path('jobReport/',jobReport,name="jobReport"),

    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)