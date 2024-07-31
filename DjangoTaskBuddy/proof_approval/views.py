import base64
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Task
from .serializers import TaskSerializer
from openai import OpenAI
from django.conf import settings
from datetime import timedelta  # Import timedelta
import boto3
import os
from PIL import Image


# Set the OpenAI API key once
client = OpenAI()

#Set up AWS S3 bucket
s3_client = boto3.client(
    's3',
    aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
    region_name = settings.AWS_S3_REGION_NAME
)

rek_client = boto3.client(
    'rekognition',
    region_name = settings.AWS_S3_REGION_NAME
)

@api_view(['POST'])
def create_task(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        task = serializer.save()  

        embedding = generate_embedding(task)
        task.embedding = embedding
        task.save()  

        return Response(TaskSerializer(task).data)  # Return the serialized task data
    else:
        return Response(serializer.errors, status=400)

def generate_embedding(task):
    # Combine task fields to create a text representation
    task_text = f"{task.user.id} {task.task_description} {task.category} {task.date} {task.time} {task.day_of_week} {task.time_taken} {task.approval_status}"

    response = client.embeddings.create(input=task_text,
    model="text-embedding-3-small")

    embedding = response.data[0].embedding

    return embedding

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_proof_picture(request, pk):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=404)

    if 'time_taken' in request.data:
        # Convert time_taken to a timedelta object
        time_taken_str = request.data['time_taken']
        hours, minutes, seconds = map(int, time_taken_str.split(':'))
        task.time_taken = timedelta(hours=hours, minutes=minutes, seconds=seconds)

    proof_image = request.FILES.get('proof_image_upload')

    if proof_image:

        path = f'tasks/{task.id}/{proof_image.name}'

        s3_client.upload_fileobj(
            proof_image,
            settings.AWS_STORAGE_BUCKET_NAME,
            path,
            ExtraArgs={'ContentType': proof_image.content_type}
        )


        response = rek_client.detect_text(
            Image = {
                'S3Object' : {
                    'Bucket' : settings.AWS_STORAGE_BUCKET_NAME,
                    'Name' : path
                }
            }
        )

        detected_text = []
        for text_detail in response['TextDetections']:
            if text_detail['Confidence'] >= 92:
                detected_text.append(text_detail['DetectedText'])

        response = rek_client.detect_labels(
            Image = {
                'S3Object' : {
                    'Bucket' : settings.AWS_STORAGE_BUCKET_NAME,
                    'Name' : path
                }
            }
        )
        detected_labels = []
        for label in response['Labels']:
            if label['Confidence'] >= 92:
                detected_labels.append(label['Name'])

        # Validate proof image
        is_valid = validate_proof(task, detected_text, detected_labels)

        if is_valid:
            task.valid_proof_num += 1

            # ADD VALID MESSAGE
        else:
            task.invalid_proof_num += 1

        task.proof_dict[proof_image.name] = is_valid
        task.approval_status = (task.valid_proof_num) == (task.expected_proof_num)

        # Update the embedding
        embedding = generate_embedding(task)
        task.embedding = embedding
        task.save()  # Save the task with the updated embedding

        return Response(TaskSerializer(task).data)
    else:
        return Response({"error": "No proof image uploaded"}, status=400)

def validate_proof(task, proof_text, proof_label):
    prompt = f"Task: Show confirmation of {task.task_description}\nText in Image: {proof_text}\nLabels found in Image: {proof_label}\nDoes this proof partially or completely satisfy the task? Answer only yes or no"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a task validator."},
            {"role": "user", "content": prompt}
        ]
    )

    validation_result = response.choices[0].message.content.strip().lower()  

    # Log the full response for debugging
    print("LLM Response:", response)


    if validation_result == 'yes':
        return True
    else:
        return False

