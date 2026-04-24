from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login


User = get_user_model()


class AuthManager ():
    def register(username, email, password):
        if not username or not password:
            raise ValueError("Missing fields")
        
        return User.objects.create_user(username, email, password)
            
    def login(self, request, username, password):
        if not username or not password:
            raise ValueError("Missing fields")
            
        user = self.validateCredentials(request, username, password)
        login(request, user)
        
    def validateCredentials(request, username, password):
        user = authenticate(request, username=username, password=password)
        if user is None:
            raise ValueError("Invalid credentials")
        return user