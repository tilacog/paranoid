# factory_boy's factories for the app audit.
import random
import string

import factory
from .models import Package, Audit

def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for x in range(length))


class PackageFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'audits.Package'

    name = factory.LazyAttribute(lambda t: random_string())
    description = factory.Faker('text', locale='pt_BR')


class AuditFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'audits.Audit'

    name = factory.Sequence(lambda n: 'Audit #%s' % (n,))
    description = factory.Faker('text', locale='pt_BR')
    execution_script = factory.Sequence(lambda n: 'Script #%s' % (n,))
    package = factory.SubFactory(PackageFactory)

    # post generation...
    # required_doctypes ...
    # required_kvs ...
