from django.urls import path
from .views import pdf_qa_view

urlpatterns = [
    path('', pdf_qa_view, name='pdf_qa'),
]
