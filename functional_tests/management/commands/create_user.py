from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--password', required=True)

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        User = get_user_model()
        user = User.objects.create_user(email=email, password=password)

        msg = "Created user:{}".format(user)
        self.stdout.write(msg)
