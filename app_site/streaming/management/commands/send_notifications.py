from django.core.management.base import BaseCommand, CommandError
from streaming.models import *
from datetime import *
from streaming.util import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Sending notifications to users if their subscriptions end in 5 days...")
        for user in SiteUser.objects.all():
            
            d1 = datetime.strptime(str(user.billing.next_payment_date), "%Y-%m-%d")
            d2 = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d")
            
            #if (abs((d2 - d1).days)) == 5: #send the user a notification if their subscription ends in 5 days
            if user.username == "lala":
                send_inbox_message(user)
                if user.preferences.inbox_opt_in is True:
                    send_inbox_message(user)
                if user.preferences.email_opt_in is True:
                    send_email(user)
        print("Finished sending notifications")