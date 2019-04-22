from django.core.management.base import BaseCommand, CommandError
from streaming.models import *
from streaming.util import *
import json
import re


class Command(BaseCommand):
    def handle(self, *args, **options):
        data_extractor = re.compile(r"Episode\s(\d+)\s([^\n]*)")
        with open('playlists.json') as input_file:
            data = json.load(input_file)
            for show, episodes in data.items():
                print("For show: ", show)
                for title, playlist in episodes.items():
                    matches = data_extractor.search(title)
                    if matches:
                        tv = TVEpisode.objects.get(title=matches.group(2), episode_number=matches.group(1))
                        tv.file_location = playlist
                        tv.save()
