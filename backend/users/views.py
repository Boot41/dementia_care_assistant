import os
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from .models import UserMemory

GROQ_API_KEY = os.getenv('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')

@api_view(['POST'])
def add_or_update_memory(request):
    user = request.user
    key = request.data.get('key')
    value = request.data.get('value')

    # Add or update memory in the database
    memory, created = UserMemory.objects.update_or_create(
        user=user, 
        key=key, 
        defaults={'value': value}
    )
    if created:
        return JsonResponse({'message': f'Memory added: {key} is {value}'}, status=201)
    else:
        return JsonResponse({'message': f'Memory updated: {key} is now {value}'}, status=200)

@api_view(['GET'])
def retrieve_memory(request, key):
    user = request.user
    try:
        memory = UserMemory.objects.get(user=user, key=key)
        return JsonResponse({'value': memory.value})
    except UserMemory.DoesNotExist:
        return JsonResponse({'error': "Memory not found."}, status=404)

@api_view(['DELETE'])
def delete_memory(request, key):
    user = request.user
    try:
        memory = UserMemory.objects.get(user=user, key=key)
        memory.delete()
        return JsonResponse({'message': "Memory deleted."})
    except UserMemory.DoesNotExist:
        return JsonResponse({'error': "Memory not found."}, status=404)

def call_groq_api(prompt):
    url = "https://api.groq.com/v1/chat/completions"  # Example endpoint
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.5,
        "top_p": 1,
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json().get("choices")[0].get("message").get("content")
