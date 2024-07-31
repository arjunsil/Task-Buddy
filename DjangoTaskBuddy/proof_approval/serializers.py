from rest_framework import serializers
from .models import Task

# Serializer for the Task model
class TaskSerializer(serializers.ModelSerializer):
    # Read-only fields that will be automatically set and shouldn't be updated by the user
    day_of_week = serializers.ReadOnlyField()  # This field is derived from the date field
    approval_status = serializers.ReadOnlyField()  # This field is updated only after task completion
    embedding = serializers.ReadOnlyField()  # This field is set when the task is created
    

    class Meta:
        model = Task  # Specify the model to be serialized
        fields = [
            'id', 'user', 'date', 'time', 'day_of_week', 'category',
            'task_description', 'time_taken', 'proof_dict', 'approval_status', 
            'expected_proof_num', 'valid_proof_num', 'invalid_proof_num', 'embedding'
        ]  # List all fields except 'embedding'
        read_only_fields = ('day_of_week', 'approval_status','valid_proof_num', 'invalid_proof_num')  # Make these fields read-only
