# factory_boy's factories for the app audit.
import random
import string

from django.conf import settings

import factory
import factory.fuzzy
from accounts.factories import UserFactory
from audits.models import Audit, Doctype


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

    name = factory.fuzzy.FuzzyText()
    description = factory.Faker('text', locale='pt_BR')
    runner = factory.fuzzy.FuzzyChoice(
        # Must pick the first element as Django choices come in pairs
        [i[0] for i in Audit.runner_choices]
    )
    package = factory.SubFactory(PackageFactory)

    ## Many to Many fields ##
    @factory.post_generation
    def num_doctypes(self, create, extracted, **kwargs):
        """Creates a number of related doctypes for this audit."""
        if not create:
            return # Simple build, do nothing.
        if extracted:
            assert isinstance(extracted, int)
            for i in range(extracted):
                doctype = DoctypeFactory()
                self.required_doctypes.add(doctype)


class DoctypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'audits.Doctype'

    name = factory.fuzzy.FuzzyText()
    validator  = factory.fuzzy.FuzzyChoice(
        # Must pick the first element as Django choices come in pairs
        [i[0] for i in Doctype.validator_choices]
    )


class DocumentFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'audits.Document'

    doctype = factory.SubFactory(DoctypeFactory)
    file = factory.django.FileField(
        filename='test_file_' + random_string() + '.test',
        data=random_string()
    )
    user = factory.SubFactory(UserFactory)
