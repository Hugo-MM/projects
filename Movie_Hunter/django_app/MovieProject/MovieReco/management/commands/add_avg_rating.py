# -*- coding: utf-8 -*-

import csv
from django.core.management.base import BaseCommand

from MovieReco.models import  Movie

class Command(BaseCommand):
    help = "Loads movie avg rating from CSV file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        file_path = options["file_path"]
        with open(file_path, "r") as csv_file:
            data = csv.reader(csv_file, delimiter=',')
            for row in data:
                movie = Movie.objects.get(pk=row[1])
                try:
                    movie.model_id = int(row[3].replace('.0',''))
                    movie.avg_rating = round(float(row[4]),2)
                except ValueError:
                    movie.model_id = None
                    movie.avg_rating = None
                movie.save()

        print('ok')
