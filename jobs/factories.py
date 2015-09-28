# factory_boy's factories for the app audit.
import random
import string

from django.conf import settings

import factory
import factory.fuzzy
from accounts.factories import UserFactory
from audits.factories import AuditFactory, DocumentFactory


class JobFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'jobs.Job'

    audit = factory.SubFactory(AuditFactory)
    user = factory.SubFactory(UserFactory)


    @factory.post_generation
    def num_documents(self, create, extracted, **kwargs):
        """Creates a number of related documents for this job."""
        if not create:
            return # Simple build, do nothing.
        if extracted:
            assert isinstance(extracted, int)
            for i in range(extracted):
                document = DocumentFactory()
                self.documents.add(document)
