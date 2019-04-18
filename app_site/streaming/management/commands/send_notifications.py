from django.core.management.base import BaseCommand, CommandError
from streaming.models import *
from datetime import *
from streaming.util import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in SiteUser.objects.all():
            if user.preferences.email_opt_in is True:
                send_inbox_message(user)
            #if user.billing.next_payment_date <= datetime.now().date():
                #package_charge(user)