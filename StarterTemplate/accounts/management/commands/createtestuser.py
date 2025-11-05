from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Create a test user with MongoEngine'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='testuser1', help='Username for the test user')
        parser.add_argument('--email', type=str, default='test1@example.com', help='Email for the test user')
        parser.add_argument('--password', type=str, default='testpass123', help='Password for the test user')
        parser.add_argument('--superuser', action='store_true', help='Make the user a superuser')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        is_superuser = options['superuser']

        # Check if user already exists
        if User.objects(username=username).first():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists!'))
            return

        # Create the user
        user = User(
            username=username,
            email=email,
            first_name='Test1',
            last_name='User1',
            is_staff=is_superuser,
            is_superuser=is_superuser
        )
        user.set_password(password)
        user.save()

        user_type = 'superuser' if is_superuser else 'user'
        self.stdout.write(self.style.SUCCESS(f'Successfully created {user_type} "{username}"'))
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Password: {password}')
