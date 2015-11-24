import markdown
from django import template
from django.utils.safestring import SafeString


register = template.Library()

@register.filter(name='markdown')
def markdownify(text):
    return SafeString(markdown.markdown(text))
