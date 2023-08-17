from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import (HttpResponse, HttpResponseRedirect, HttpResponseServerError,JsonResponse)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,Group
from .forms import UserLoginForm
from django.contrib.auth import (authenticate, get_user_model, login, logout)
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from Slate_CMT.forms import *
import logging

LOGGER = logging.getLogger(__name__)

@login_required
def home(request):
    return render(request,'home.html')

def logins(request):
    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if request.POST and form.is_valid()!=True:
        messages.error(request, 'Please check the username and Password')
    if form.is_valid():
        print(request.user)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        if request.user.is_authenticated :
            if next:
                return redirect(next)
        return redirect('home')
    elif request.user.is_authenticated:
        if next:
            return redirect(next)
        return redirect('home' )
    return render(request,'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')

def csrf_failure(request, reason=""):
    LOGGER.error('csrf_failure')
    return redirect('/')

@login_required
def login_via_admin(request,id):
    if request.user.is_superuser:
        user=User.objects.get(id=id)
        login(request, user)
        return redirect('/')
    else:
        return redirect('/')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/changepassword.html', {'form': form})

# @login_required
# def change_theme(request,val):
#     usr = user_ext.objects.get(user_id=request.user.id) if user_ext.objects.filter(user_id=request.user.id).exists() else user_ext()
#     usr.user = request.user
#     usr.theme = val
#     usr.save()
#     return JsonResponse({'success':'success','theme':val})
    
