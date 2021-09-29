
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib import auth, messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect

from MovieReco.models import Genre, Country, Language, Director, Writer, Actor, Movie, UserMovieRate, MovieSynopsisDistance, MovieContentSimilarity
from MovieReco.forms import MovieLikeForm, SignupForm, LoginForm

import random

from sklearn.metrics.pairwise import linear_kernel
from scipy.sparse import csr_matrix
import numpy as np
import pickle

def Welcome(request):
    if request.user.is_anonymous:
        return render(request, 'MovieReco/Welcome.html')

    try:
        user_movie_rates = UserMovieRate.objects.filter(user=request.user)
    except:
        user_movie_rates = None

    return render(request, 'MovieReco/Welcome.html', {'user': request.user, 'user_movie_rates': user_movie_rates})

def About(request):

    return render(request, 'MovieReco/About.html')


def MovieView(request, movie_id):
    """
        This view displays a movie along with all its attributes.
    """
    movie = get_object_or_404(Movie, pk=movie_id)

    return render(request, 'MovieReco/MovieView.html', {'movie': movie})

@login_required(login_url='MovieReco:login')
def MovieLikeView(request, movie_id):
    """
        This view enables a user to rate a movie (from 0 to 5).
    """
    movie = get_object_or_404(Movie, pk=movie_id)
    try:
        previous_rate = UserMovieRate.objects.get(user=request.user, movie=movie)
    except ObjectDoesNotExist:
        previous_rate = None

    if request.method == 'POST':
        form = MovieLikeForm(request.POST)
        if form.is_valid():
            rate = int(form.cleaned_data['rate'])
            if previous_rate:
                previous_rate.rate = rate
                previous_rate.save()
            else:
                UserMovieRate.objects.create(user=request.user, movie=movie, rate=rate)
            return HttpResponseRedirect('/MovieReco')

    else:
        form = MovieLikeForm(initial={'movie_id': movie_id})

    return render(request, 'MovieReco/MovieLikeView.html', {'form': form, 'movie':movie,
        'movie_id': movie.id, 'previous_rate': previous_rate})

@login_required(login_url='MovieReco:login')
def GetReco(request):
    """
        Three algorithms are used to compute recommendations :
            1. Collaborative filtering (based on truncated SVD)
            2. Item-based (distance between movies)
            3. Item-based on synopsis (distance between tf-idf of movies synopsis)
    """
    ### Algorithm 1 : collaborative filtering.
    try:
        user_movie_rates = UserMovieRate.objects.filter(user=request.user)
    except:
        user_movie_rates = None

    # Two models can be used :
    #   - 'svd.sav' truncated SVD on centered rates, need for an additional data processing (see below)
    #   - 'svd_data_not_centered.sav' truncated SVD

    #model = pickle.load(open('svd.sav','rb'))
    model = pickle.load(open('svd_data_not_centered.sav','rb'))
    user_movie_rates = UserMovieRate.objects.filter(user=request.user)
    user_ids = []
    rates = []
    movie_ids = []
    for rating in user_movie_rates:
        if rating.movie.model_id is not None:
            rates.append(rating.rate)
            movie_ids.append(rating.movie.model_id)
            user_ids.append(0) # our user will be on the first line

    # The expected size of input matrix is 2782 x 3931.
    # so we add a fake user to make sure the dimensions of input matrix are ok.
    user_ids.append(2782-1)
    rates.append(0)
    movie_ids.append(3931-1)

    # We now convert data into a sparse matrix and compute the predictions.
    user_csr = csr_matrix((rates, (user_ids, movie_ids)))

    # If usinf 'svd_data_not_centered.sav' model, just run
    user_predicted_rates = np.matmul(model.transform(user_csr), model.components_)[0,:]
    
    # If using 'svd.sav', it is necessary to add the average rate of each movie because
    # train data has been centered.
    # avg_ratings = Movie.objects.filter(model_id__in=[i for i in range(3931)])
    # for movie in avg_ratings:
    #    user_predicted_rates[movie.model_id] += float(movie.avg_rating)
    
    # We now sort the movies according to the predicted rates
    all_best_idx = np.argsort(user_predicted_rates)[::-1][:100]

    del movie_ids[-1] # to remove the fake last movie
    reco_idx = list(set(all_best_idx) - set(movie_ids))[:10]
    movie_reco = Movie.objects.filter(model_id__in=reco_idx)

    ### Algorithm 2 : Item-based (distance between movies)
    movie_already_rated = [rating.movie.id for rating in user_movie_rates]
    user_vect = np.zeros((0,26))    # this vector is meant to represent the user's tastes among the movies representation space

    similar_movie_ids = [] # we will store there the ids of movies similar to the ones the user liked.
    similar_movies_vect = 'no data yet'
    user_vect = 'no data yet'
    # Building of the user vector, we keep here only the only the user liked.
    for rating in user_movie_rates:
        if rating.rate >= 4:
            movie = rating.movie
            movie_genre = [genre.id for genre in movie.genre.all()]
            movie_genre_vect = [1 if i in movie_genre else 0 for i in range(26)] # because 26 genre (pk from 0 to 25)
            movie_vect = movie_genre_vect

            if user_vect == 'no data yet':
                user_vect = movie_vect
            else:
                user_vect = [x + y for x, y in zip(user_vect, movie_vect)] # addition of new information into of the user vector

            # Selection of closest movies
            similar_movies = MovieContentSimilarity.objects.filter(pairing_movies=movie).order_by('-similarity_score')
            for pair in similar_movies:
                pairing_movies = pair.pairing_movies.all()
                if len(pairing_movies) > 1: # otherwise, it is actually the same movie in the pair.
                    movie_1 = pairing_movies[0]
                    movie_2 = pairing_movies[1]
                    if movie_1.id == movie.id:
                        similar_movie = movie_2
                    else:
                        similar_movie = movie_1

                movie_genre = [genre.id for genre in similar_movie.genre.all()]
                movie_genre_vect = [1 if i in movie_genre else 0 for i in range(26)] # because 26 genre (pk from 0 to 25)

                similar_movie_ids.append(similar_movie.id)
                movie_vect = movie_genre_vect

                if similar_movies_vect == 'no data yet':
                    similar_movies_vect = movie_vect
                else:
                    similar_movies_vect = similar_movies_vect + movie_vect

    # merge the arrays with the user_vect at first row. and compute the distances matrix
    data = np.array(user_vect + similar_movies_vect).reshape(len(similar_movie_ids)+1,26)
    distances = linear_kernel(data)

    user_reco = distances[0][1:] # start at 1 because the first one is the user itself
    user_reco = np.argsort(user_reco)[::-1]  # it contains the position of closest movies.

    movie_reco_ids = [similar_movie_ids[i] for i in user_reco] 
    reco_idx = list(set(movie_reco_ids) - set(movie_already_rated))[:10]
    movie_reco_content = Movie.objects.filter(id__in=reco_idx)

    ### Algorithm 3 : Item-based on synopsis (distance between tf-idf of movies synopsis)
    # The recommendations are actually computed for each movie the users liked.
    # and are implemented with the 'SameSynopsys' view below.

    return render(request, 'MovieReco/GetReco.html', {'user': request.user,
        'user_movie_rates': user_movie_rates,
        'movie_reco': movie_reco,  'movie_reco_content': movie_reco_content})

@login_required(login_url='MovieReco:login')
def SameSynopsys(request, movie_id):
    """
        This view selects the 10 closest movies from the target movie according to 'MovieSynopsisDistance'.
        Note that the closest movie is the target movie itself which is why we remove it from the selection.
    """
    movie = get_object_or_404(Movie, pk=movie_id)
    reco_movies = []
    selection = MovieSynopsisDistance.objects.filter(pairing_movies=movie).order_by('-distance_score')[1: 1+10]
    for reco in selection:
        pairing_movies = reco.pairing_movies.all()
        reco_1 = pairing_movies[0]
        reco_2 = pairing_movies[1]
        if reco_1.id == movie.id:
            reco_movies.append(reco_2)
        else:
            reco_movies.append(reco_1)

    return render(request, 'MovieReco/SameSynopsys.html', {'movie':movie, 'reco_movies': reco_movies })


@login_required(login_url='MovieReco:login')
def SameCredits(request, movie_id):
    """
       This view selects the 10 closest movies from the target movie according to 'MovieSynopsisDistance'.
        Note that the closest movie is the target movie itself which is why we remove it from the selection.
    """
    movie = get_object_or_404(Movie, pk=movie_id)
    reco_movies = []

    selection= MovieContentSimilarity.objects.filter(pairing_movies=movie).order_by('-similarity_score')[1: 1+10]
    for reco in selection:
        pairing_movies = reco.pairing_movies.all()
        reco_1 = pairing_movies[0]
        reco_2 = pairing_movies[1]
        if reco_1.id == movie.id:
            reco_movies.append(reco_2)
        else:
            reco_movies.append(reco_1)

    return render(request, 'MovieReco/SameCredits.html', {'movie':movie, 'reco_movies': reco_movies })

def RandomMovieList(request):
    """
        This view displays a random movie list to help the user in the rating process.
        In order to filter a little bit the number of movies, a filter is implementer on 'imdb_rate'
    """
    movies = Movie.objects.filter(imdb_rate__gte=7).order_by('?')

    paginator = Paginator(movies, 10)
    page = request.GET.get('page')
    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        movies = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        movies = paginator.page(paginator.num_pages)
    
    context = {'movies': movies}
    
    return render(request, 'MovieReco/RandomMovieList.html', context)

def SearchMovie(request):
    """"
        Simple search engine to find movies based on their title.
    """

    query = request.GET.get('lookformovies')
    if query:
        movies = Movie.objects.filter(title__icontains=query)
        search_title = "Movies found in relation to the key words : %s"%query
    else:
        movies = None
        search_title = None

    context = {
        'movies': movies,
        'search_title': search_title
    }
    return render(request, 'MovieReco/SearchView.html', context)


def CustomLogin(request):
    """
        Login view, customed compared to Django default view.
    """

    if request.user.is_authenticated:
        return redirect('MovieReco:Welcome')

    if request.method == 'POST':
        loginForm = LoginForm(request.POST)
        user = auth.authenticate(username=loginForm['username'].value(),
                                 password=loginForm['password'].value())

        if user is not None:
            # correct username and password login the user
            auth.login(request, user)
            return redirect('MovieReco:Welcome')#(request.POST.get("next", 'MovieReco/MovieReco'))
        else:
            messages.error(request, 'Login failed, try again !')
    return render(request, "MovieReco/CustomLogin.html", {"next": "/"})

@sensitive_post_parameters('password1', 'password2')
def CreateUser(request):
    """
        This view displays the form used to create a new user.
    """
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            NewUser = form.save()
            auth.login(request, NewUser)
            return redirect('MovieReco:Welcome')
    else:
        form = SignupForm()
    return render(request, 'MovieReco/SignUp.html', {'form': form})
