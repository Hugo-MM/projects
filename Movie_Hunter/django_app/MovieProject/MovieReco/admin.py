from django.contrib import admin

from MovieReco.models import Genre, Country, Language, Director, Writer, Actor, Movie, UserMovieRate, MovieSynopsisDistance, MovieContentSimilarity

admin.site.register(Genre)

admin.site.register(Country)

admin.site.register(Language)

admin.site.register(Director)

admin.site.register(Writer)

admin.site.register(Actor)

admin.site.register(Movie)

admin.site.register(UserMovieRate)

admin.site.register(MovieSynopsisDistance)

admin.site.register(MovieContentSimilarity)