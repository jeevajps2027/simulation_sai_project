from django.shortcuts import redirect, render


def home(request):
    from app.models import UserLogin
    error_message = ''

    if request.method == 'POST':
        username = request.POST.get('user')
        password = request.POST.get('password')

        # Get or create UserLogin instance with id=1
        user_login, created = UserLogin.objects.get_or_create(id=1, defaults={'username': username, 'password': password})

        # Update username and password if already exists
        if not created:
            user_login.username = username
            user_login.password = password
            user_login.save()

        # Check username and password for redirection
        if username in ['admin', 'o', 'saadmin'] and password == username:
            return redirect('index')
        else:
            error_message = 'Invalid username or password'

    return render(request, "app/home.html", {'error_message': error_message})
