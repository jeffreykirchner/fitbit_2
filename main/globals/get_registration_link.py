import urllib

from django.conf import settings
from django.utils.encoding import iri_to_uri, uri_to_iri, escape_uri_path, filepath_to_uri

from main.models import Parameters

from django.utils.text import slugify

def get_registration_link(player_key):
    p = Parameters.objects.first()

    s = urllib.parse.quote(f'{p.site_url}subject-fitbit-registration/{player_key}/user_id', safe="")

    return f"{settings.FITBIT_MS_REGISTRATION}/{s}"