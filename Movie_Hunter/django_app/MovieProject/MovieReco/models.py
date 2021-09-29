# -*- coding: utf-8 -*-

from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.models import User


class Genre(models.Model):
	name = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return "{name}".format(name=self.name)

class Country(models.Model):
	name = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return "{name}".format(name=self.name)

class Language(models.Model):
	name = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return "{name}".format(name=self.name)

class Director(models.Model):
	first_name = models.CharField(max_length=50, null=True)
	last_name = models.CharField(max_length=50)

	def __str__(self):
		return "%s %s" % (self.first_name, self.last_name)

class Writer(models.Model):
	first_name = models.CharField(max_length=50, null=True)
	last_name = models.CharField(max_length=50)

	def __str__(self):
		return "%s %s" % (self.first_name, self.last_name)

class Actor(models.Model):
	first_name = models.CharField(max_length=50, null=True)
	last_name = models.CharField(max_length=50)

	def __str__(self):
		return "%s %s" % (self.first_name, self.last_name)

class Movie(models.Model):
    title = models.CharField(max_length=50)
    imdbid = models.CharField(max_length=20, unique=True)
    imdb_rate = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    year = models.IntegerField(null=True)
    duration = models.IntegerField(default=None, null=True)
    synopsys = models.CharField(max_length=1000, default = "")

    model_id = models.IntegerField(null=True) #idx in the SVD modelization
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True)

    genre = models.ManyToManyField(Genre, blank=True)
    country = models.ManyToManyField(Country, blank=True)
    language = models.ManyToManyField(Language, blank=True)
    director = models.ManyToManyField(Director, blank=True)
    writer = models.ManyToManyField(Writer, blank=True)
    actor = models.ManyToManyField(Actor, blank=True)

    def __str__(self):
    	return "{title}".format(title=self.title)

class UserMovieRate(models.Model):
	movie = models.ForeignKey(Movie, unique=False, default=1, on_delete=models.CASCADE)
	rate = models.IntegerField()
	user = models.ForeignKey(User, unique=False, default=1, on_delete=models.CASCADE)
	
	def __str__(self):
		return "{user} : {movie}".format(user=self.user, movie=self.movie)

class MovieSynopsisDistance(models.Model):
	pairing_movies = models.ManyToManyField(Movie, blank=True)
	distance_score = models.DecimalField(max_digits=8, decimal_places=7, null=True)

class MovieContentSimilarity(models.Model):
	pairing_movies = models.ManyToManyField(Movie, blank=True)
	similarity_score = models.IntegerField(null=True)

	def __str__(self):
		return str(self.similarity_score)


