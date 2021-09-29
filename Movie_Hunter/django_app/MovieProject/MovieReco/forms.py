# -*- coding: utf-8 -*-
from django.utils import timezone

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm as dPasswordChangeForm, SetPasswordForm

from MovieReco.models import Movie


class MovieLikeForm(forms.Form):
    movie_id = forms.CharField(widget=forms.HiddenInput())
    rate = forms.TypedChoiceField(
        label='How much do you like this movie ?',
        widget=forms.RadioSelect(),
        choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')))

class LoginForm(forms.Form):
    username = forms.CharField(
        label='login',
        max_length=30)
    password = forms.CharField(
        label='password',
        widget=forms.PasswordInput)

class SignupForm(UserCreationForm):

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username in User.objects.all().values_list('username', flat=True):
            raise forms.ValidationError("Someone already goes by this name on this website, you have to find another one !")
        return username.lower()

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')