#!/usr/bin/env python
import os
import sys
from django.contrib.sites.models import Site

Site.objects.create(domain='https://nowtify-dev.herokuapp.com', name='https://nowtify-dev.herokuapp.com')

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Nowtify.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
