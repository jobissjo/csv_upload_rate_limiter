from django.urls import path
from . import views

urlpatterns = [
    path('token/', views.GetTokenView.as_view(), name='get_token'),
    path('file-upload/', views.FileUploadView.as_view(), name='upload_csv'),
]