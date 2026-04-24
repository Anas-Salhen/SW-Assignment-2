from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import get_user_model
from .services import AuthManager

User = get_user_model()


class RegisterView(View):
    def post(self, request):
        data = json.loads(request.body)

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        manager = AuthManager()
        try:
            user = manager.register(username, email, password)
        except ValueError as e:
            return JsonResponse({'error': 'Missing fields'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Couldn\'t register user'}, status=500)


        return JsonResponse({
            'message': 'User created successfully',
            'user_id': user.id
        }, status=201)



class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        manager = AuthManager()
        try:
            manager.login(request, username, password)
        except ValueError as e:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': 'Login failed'}, status=500)

        return JsonResponse({
            'message': 'Login successful'
        })