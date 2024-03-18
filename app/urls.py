from django.conf import settings
from django.urls import path,include
from django.conf.urls.static import static
from app import views





urlpatterns = [
    path('',views.home,name="home"),
    path('comport/',views.comport, name='comport'),
    path('index/',views.index,name="index"),
    path('probe/',views.probe,name="probe"),
    path('trace/',views.trace,name="trace"),
    path('parameter/', views.parameter, name='parameter'),
    path('master/',views.master,name="master"), 
    path('measurement/',views.measurement,name="measurement"),
    path('measurebox/',views.measurebox,name="measurebox"), 

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)