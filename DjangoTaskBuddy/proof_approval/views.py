from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Task
from .serializers import TaskSerializer
import openai  # Import OpenAI for embedding generation
from django.conf import settings
import os

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

    openai.api_key = settings.OPENAI_API_KEY

    response = openai.Embedding.create(
        input=task_text,
        model="text-embedding-ada-002"
    )
    
    embedding = response['data'][0]['embedding']
    
    return embedding

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_proof_picture(request, pk):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=404)
    
    if 'time_taken' in request.data:
        task.time_taken = request.data['time_taken']

    proof_image = request.FILES.get('proof_image_upload')

    if proof_image:
        # Save proof image to the user's directory
        filename = os.path.join('media', task.user_directory_path(task, proof_image.name))
        with open(filename, 'wb+') as destination:
           for chunk in task.proof_image.chunks():
                destination.write(chunk)

        # Validate proof image
        is_valid = validate_proof(task, filename)
        task.proof_images[filename] = is_valid
        
        if is_valid:
            task.valid_proof_num += 1
            # ADD VALID MESSAGE
        else:
            task.invalid_proof_num += 1

        task.approval_status = (task.valid_proof_num) == (task.expected_proof_num)

        # Update the embedding
        embedding = generate_embedding(task)
        task.embedding = embedding
        task.save()  # Save the task with the updated embedding

        return Response(TaskSerializer(task).data)
    else:
        return Response({"error": "No proof image uploaded"}, status=400)
    
def validate_proof(task, proof_image_path):
    openai.api_key = settings.OPENAI_API_KEY

    # Create a prompt for the OpenAI model using the task description
    prompt = f"Task: {task.task_description}\nProof: {proof_image_path}\nDoes this proof partially or completely satisfy the task?"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )

    validation_result = response.choices[0].text.strip().lower()
    if validation_result == 'yes':
        return True
    else:
        return False

