from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Task(models.Model):
    class Category(models.TextChoices):
        SCHOOLWORK = "Schoolwork", "Schoolwork"
        PROFESSIONAL = "Professional", "Professional"
        JOB = "Job", "Job"
        ERRAND = "Errand", "Errand"

    # Many-to-one relationship with the User model. CASCADE deletes tasks if user is deleted.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Date of the task with default value set to now
    date = models.DateField(default=timezone.now)  # Stores date (year, month, day)
    
    # Time of the task with default value set to now
    time = models.TimeField(default=timezone.now)  # Stores time (hour, minute, second)
    
    # Day of the week for the task
    day_of_week = models.CharField(max_length=9, blank=True)
    
    # Category of the task, linked to the Category model
    # Category of the task using TextChoices enum
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.SCHOOLWORK
    )
        
    # Description of the task
    task_description = models.TextField()  # Stores a large text description of the task
    
    # Time taken to complete the task, optional field
    time_taken = models.DurationField(null=True, blank=True)  # Stores a duration (optional)
    
    # Expected number of proof images
    expected_proof_num  = models.IntegerField(default=1)

    # Number of validated proofs
    valid_proof_num  = models.IntegerField(default=0)

    # Proof picture for task completion, optional field
    proof_picture = models.ImageField(upload_to='proofs/', null=True, blank=True)  # Stores an image file (optional)
    
    # Approval status of the task, default is False
    approval_status = models.BooleanField(default=False)  # Boolean field, defaults to False
    
    # Embedding data for the task, stored as JSON
    embedding = models.JSONField(null=True, blank=True)  # Stores JSON data (optional)

    # save()
    def save(self, *args, **kwargs):
        # save day_of_week only once so it stays consistent with date field
        self.day_of_week = self.date.strftime('%A')
        super().save(*args, **kwargs)