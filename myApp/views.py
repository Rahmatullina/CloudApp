from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse,Http404
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .forms import LoginForm
import subprocess
import random,string,re,time,os
from django.contrib import messages
from subprocess import PIPE

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
        print('/Profile/ GET:')
        messages.info(request, "Hello it is your profile" )
        return render(request, 'myApp/profile.html', {
                                           'username': request.user.username,
                                           'email': request.user.email,
                                           'is_created_VM': False
                                           })
    if request.method == 'POST':
        print('/Profile/ POST:')
        compelted = create_VM_and_run(request.user.username)
        if compelted:
            with open(f'./{request.user.username}/output.txt') as file:
                messages.info(request, 'Sinonims :' + ' '.join(list(file.readlines())))
                os.remove(f'./{request.user.username}/output.txt')
        else: messages.info(request, 'Some Error occured during running task')
        return render(request, 'myApp/profile.html', {
            'username': request.user.username,
            'email': request.user.email,
            'is_created_VM': True,
            'is_completed': 'is completed. :)' if compelted else 'is not completed, Sorry'
        })

    else:
        return HttpResponseNotFound('Sorry Page Not Found')


def random_id(length=6):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def deletevm(vm_id):
    print(f'Deleting VM with id: \033[1m{vm_id}\033[0m')
    delete_result = subprocess.run(['ansible-playbook', './playbooks/deleteVM.yml', '--extra-vars', 'vmID=' + vm_id], stdout=PIPE, stderr=PIPE)
    print(f'VM deletion exited with return code: {delete_result.returncode} ({"un" if delete_result.returncode != 0 else ""}successful)')
    if delete_result.returncode != 0:
        print('=> STDOUT:')
        print(delete_result.stdout.decode('utf-8'))
        print('=> STDERR:')
        print(delete_result.stderr.decode('utf-8'))
        return


def create_VM_and_run(username):
    vm_id = random_id()
    create_time = time.time()
    result = subprocess.run(['ansible-playbook', './playbooks/createVM.yml','--extra-vars', 'vmID=' + vm_id], stdout=PIPE, stderr=PIPE)
    print(
        f'VM creation exited with return code: {result.returncode} ({"un" if result.returncode != 0 else ""}successful)')
    if result.returncode != 0:
        print('=> STDOUT:')
        print(result.stdout.decode('utf-8'))
        print('=> STDERR:')
        print(result.stderr.decode('utf-8'))
        return False
    vm_ip = re.findall(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        result.stdout.decode('utf-8'))[0]
    print(f'Created VM with IP: {vm_ip} ({int(time.time() - create_time)}s)')

    with open(f'./playbooks/template.configuration') as template_config:
        template = template_config.read().replace('IP_ADDRESS', vm_ip)
        with open(f'hosts_{vm_id}.ini', 'w') as hosts:
            hosts.write(template)

    print(f'Setting up the VM...')
    setup_time = time.time()
    setup_result = subprocess.run(['ansible-playbook', '-i', f'hosts_{vm_id}.ini', './playbooks/runTask.yml','--extra-vars','username='+ username], stdout=PIPE, stderr=PIPE)
    print(f'VM setup exited with return code: {setup_result.returncode} '
          f'({"un" if setup_result.returncode != 0 else ""}successful, {int(time.time() - setup_time)}s)')

    if setup_result.returncode != 0:
        print('=> STDOUT:')
        print(setup_result.stdout.decode('utf-8'))
        print('=> STDERR:')
        print(setup_result.stderr.decode('utf-8'))
        os.remove(f'hosts_{vm_id}.ini')
        deletevm(vm_id)
        return False
    os.remove(f'hosts_{vm_id}.ini')
    deletevm(vm_id)
    return True

