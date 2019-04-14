from django.core.management.base import BaseCommand, CommandError
from streaming.models import *
from datetime import *
from streaming.util import *


class Command(BaseCommand):
    def handle(self, *args, **options):
            for user in SiteUser.objects.all():
                rental_charge(user)
