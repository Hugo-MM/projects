from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'MovieReco'

urlpatterns = [
    url(r'^$', views.Welcome, name='Welcome'),
    url(r'^about/$', views.About, name='About'),

    url(r'^movie/(?P<movie_id>[0-9]+)/$',
        views.MovieView, name='MovieView'),
    url(r'^movie/(?P<movie_id>[0-9]+)/like/$', views.MovieLikeView, name='MovieLikeView'),
    url(r'^randommovielist/$', views.RandomMovieList, name='RandomMovieList'),
    url(r'^get_reco/$', views.GetReco, name='GetReco'),
    url(r'^get_reco/same_synopsys/(?P<movie_id>[0-9]+)/$', views.SameSynopsys, name='SameSynopsys'),
    url(r'^get_reco/same_credits/(?P<movie_id>[0-9]+)/$', views.SameCredits, name='SameCredits'),
    url(r'^search/$', views.SearchMovie, name='SearchMovie'),
    
    url(r'^sign_up/$', views.CreateUser, name='CreateUser'),
    url(r'^login/$', views.CustomLogin, name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='MovieReco:Welcome'),
        name='logout')
]