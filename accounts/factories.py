import factory
from django.conf import settings



class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = settings.AUTH_USER_MODEL
        django_get_or_create = ('email',)


    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.Faker('password')

