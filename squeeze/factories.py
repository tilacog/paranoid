import factory
from squeeze.forms import get_beta_user
import dateutil.parser


class SqueezejobFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'squeeze.SqueezeJob'

    real_user_email = factory.Faker('email')
    real_user_name = factory.Faker('name')
    job = factory.SubFactory(
        'jobs.factories.JobFactory',
        num_documents=1,
        user=get_beta_user(),
    )

    @factory.post_generation
    def expired(self, create, extracted, **kwargs):
        """Sets the created_at attribute to a long time ago
        """
        if not create:
            return # Simple build, do nothing.
        if extracted:
            assert isinstance(extracted, bool)
            self.created_at = dateutil.parser.parse('1900-01-01 00:00:01+00:00')
