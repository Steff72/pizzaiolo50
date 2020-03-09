from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User


def register(request):
    if request.method == 'POST':
        # get form entries
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # check pw match
        if password != password2:
            messages.error(request, 'Passwords dont match!')
            return redirect('register')

        # check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken!')
            return redirect('register')

        # check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('register')

        # all ok
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )
        user.save()
        messages.success(request, 'Registered successfully!')
        return redirect('login')

    else:
        # GET request
        return render(request, 'accounts/register.html')


def login(request):
    if request.method == 'POST':
        # get form entries
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            # success
            auth.login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('index')

        else:
            messages.error(request, 'Invalid credentials!')
            return redirect('login')

    else:
        return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.success(request, 'Logged out!')
    return redirect('index')
