from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse,Http404
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .forms import LoginForm
import subprocess

# Create your views here.


def login_view(request):
    form = LoginForm(request.POST or None)
    print("form created", request.POST,form.is_valid())
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('get_profile'))
    return render(request, 'myApp/registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/')


@login_required(login_url='/login/',
                redirect_field_name='/profile/')
def empty_view(request):
    return HttpResponseRedirect('/login/')


@login_required(login_url='/login/',redirect_field_name='/profile/')
def get_profile(request):
    if request.method == 'GET':
        print('Profile GET:')
        return render(request, 'myApp/profile.html', {
                                           'username': request.user.username,
                                           'email': request.user.email
                                           })
    if request.method == 'POST':
        print('Profile POST:')
        delete_result = subprocess.run(['ansible-playbook', 'hello_world.yml'])
        print('End ansible')

        return render(request, 'myApp/profile.html', {
            'username': request.user.username,
            'email': request.user.email
        })

    else:
        return HttpResponseNotFound('Sorry Page Not Found')

