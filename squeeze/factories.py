import factory


class SqueezejobFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'squeeze.SqueezeJob'

    real_user_email = factory.Faker('email')
    real_user_name = factory.Faker('name')
    job = factory.SubFactory('jobs.factories.JobFactory', num_documents=1)
