from django.conf import settings
from django.urls import path,include
from django.conf.urls.static import static
from app import views





urlpatterns = [
    path('',views.home,name="home"),
    path('comport/',views.comport, name='comport'),
    path('index/',views.index,name="index"),
    path('probe1/',views.probe1,name="probe1"),
    path('probe2/',views.probe2,name="probe2"),
    path('probe3/',views.probe3,name="probe3"),
    path('probe4/',views.probe4,name="probe4"),
    path('probe5/',views.probe5,name="probe5"),
    path('probe6/',views.probe6,name="probe6"),
    path('probe12/',views.probe12,name="probe12"),
    path('trace/',views.trace,name="trace"),
    path('parameter/',views.parameter,name="parameter"),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)