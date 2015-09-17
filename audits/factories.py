# factory_boy's factories for the app audit.
import random
import string

import factory
import factory.fuzzy

from audits.models import FormFieldRecipe


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

    ## Many to Many fields ##

    @factory.post_generation
    def required_doctypes(self, create, extracted, **kwargs):
        if not create:
            return  # Simple build, do nothing.
        if extracted:
            # A list of related_doctypes were passed in, use them
            for doctype in extracted:
                self.required_doctypes.add(doctype)

    @factory.post_generation
    def extra_fields(self, create, extracted, **kwargs):
        if not create:
            return  # Simple build, do nothing.
        if extracted:
            # A list of FormFieldRecipe instances were passed in, use them
            for form_field_recipe in extracted:
                self.extra_fields.add(form_field_recipe)



class DoctypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'audits.Doctype'

    name = factory.Sequence(lambda n: 'Doctype #%s' % (n,))

class FormFieldRecipeFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'audits.FormFieldRecipe'

    key = factory.Sequence(lambda n: 'field_{}'.format(n))
    tag = factory.Sequence(lambda n: 'tag_{}'.format(n))
    form_field_class = factory.fuzzy.FuzzyChoice(map(
        lambda x: x[0],
        FormFieldRecipe.FIELD_CHOICES
    ))
    input_label = factory.Faker('word')
    tooltip_text = factory.Faker('paragraph', nb_sentences=1)
