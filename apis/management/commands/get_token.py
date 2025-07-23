from django.core.management.base import BaseCommand
from apis.models import User

from apis.utils import get_tokens_for_user

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, default='testuser@gmail.com', nargs='?', help='email')
        parser.add_argument("password", type=str, default='testuser@123', nargs='?', help='password')
        parser.add_argument('--superuser', action='store_true', help='Create superuser')
        parser.add_argument('--skip_validation', action='store_true', help='Skip validation')
    
    def handle(self, *args, **kwargs):
        password = kwargs['password']
        email = kwargs['email']
        superuser = kwargs['superuser']
        skip_validation = kwargs['skip_validation']

        user_queryset = User.objects.filter(email__iexact=email)
        if user_queryset.exists():
            user = user_queryset.first()
            if skip_validation:
                user.is_superuser = superuser
                user.set_password(password)
                user.save()
            else:
                self.stdout.write(self.style.HTTP_INFO(f'User with email {email} already exists'))
                self.stdout.write(self.style.HTTP_INFO('Fpr Skipping validation, use --skip_validation flag'))
                return
            
        else:
                
            user = User.objects.create_user(password=password, email=email, is_superuser=superuser)

        
        tokens = get_tokens_for_user(user)
        self.stdout.write(self.style.HTTP_INFO(f'email: {email}, password: {password}'))
        self.stdout.write(self.style.HTTP_INFO(f'Access token:\n {tokens["access"]}\n'))
        self.stdout.write(self.style.HTTP_INFO(f'Refresh token:\n {tokens["refresh"]}'))

        
        