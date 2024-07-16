from django.urls import path
from .views import create_task, upload_proof_picture

urlpatterns = [
    # URL pattern for creating a new task
    path('tasks/', create_task, name='create_task'),
    
    # URL pattern for uploading proof pictures to a specific task
    path('tasks/<int:pk>/upload-proof-picture/', upload_proof_picture, name='upload_proof_picture'),
]
