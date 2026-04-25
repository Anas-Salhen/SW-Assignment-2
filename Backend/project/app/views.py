from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import get_user_model
from .services import AuthManager
from .services import TransactionManager
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

class AddIncomeView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
            
        data = json.loads(request.body)
        manager = TransactionManager()
        
        try:
            income, updated_balance = manager.add_income(
                user=request.user,
                amount=data.get('amount'),
                source=data.get('source'),
                description=data.get('description')
            )
            return JsonResponse({
                'message': 'Income added successfully',
                'income_id': income.id,
                'updatedBalance': str(updated_balance)
            }, status=201)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)  
        
class AddExpenseView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
            
        data = json.loads(request.body)
        manager = TransactionManager()
        
        try:
            expense, updated_balance = manager.add_expense(
                user=request.user,
                amount=data.get('amount'),
                category_name=data.get('category'), 
                method=data.get('paymentMethod'),
                description=data.get('description')
            )
            
            return JsonResponse({
                'message': 'Expense added successfully',
                'expense_id': expense.id,
                'updatedBalance': str(updated_balance)
            }, status=201)
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred'}, status=500)