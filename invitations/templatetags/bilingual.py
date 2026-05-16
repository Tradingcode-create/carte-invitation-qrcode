from django import template
from django.utils import translation


register = template.Library()


@register.simple_tag(takes_context=True)
def tr(context, fr_text, en_text):
    request = context.get("request")
    language = ""
    if request is not None:
        language = getattr(request, "LANGUAGE_CODE", "")
    language = (language or translation.get_language() or "fr")[:2]
    return en_text if language == "en" else fr_text
