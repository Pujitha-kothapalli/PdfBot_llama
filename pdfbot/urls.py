# pdfbot/urls.py

from django.contrib import admin
from django.urls import path, include
from pdfapp.views import pdf_qa_view

urlpatterns = [
    path('admin/', admin.site.urls),
   path('', include('pdfapp.urls')), 
]
