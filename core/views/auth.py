from django.contrib import messages
from django.contrib.auth import (
    authenticate, login, logout
)
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View

from core.decorators import (
    login_required, user_passes_test
)
from core.models import User


@method_decorator(
    user_passes_test(
        lambda u: u.is_anonymous(),
        login_url=reverse('index'),  # This should probably be redirect_url.
        next='',
    ),
    name='dispatch'
)
class LoginView(View):
    """
    View for logging users in.

    This view should only accept POST requests from anonymous users. GET
    requests and logged in users will be redirected to `/`. After logging in,
    users will be redirected to `/`.

    View URL: `/auth/login`
    """
    def get(self, request):
        return redirect(reverse('index'))

    def post(self, request):
        try:
            username = request.POST['username']
            password = request.POST['password']
        except KeyError:
            messages.error(
                request,
                'Invalid data submitted for authentication.'
            )
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Login success! Yey!
                login(request, user)
            else:
                messages.error(
                    request,
                    'Wrong username/password combination.'
                )

        return redirect(reverse('index'))


@method_decorator(
    login_required(
        login_url=reverse('index'),
        next=''
    ),
    name='dispatch',
)
class LogoutView(View):
    """
    View for logging users out.

    This view should only accept POST requests from logged in users. GET
    requests and anonymous users will be immediately redirected to `/`. After
    logging out, users will be redirected to `/`.

    Logout views must not accept GET requests because:
       1) It can be abused and have the user unknowingly get logged out of
          their session, which can be done by setting an image tag's src to the
          logout URL of a website, for example [1].
       2) Browsers pre-fetch websites that they think you will visit next. This
          pre-fetching may cause you to logout from the website you're
          currently visiting [2].

       References:
        [1] https://stackoverflow.com/a/3522013/1116098
        [2] https://stackoverflow.com/a/14587231/1116098

    View URL: `/auth/logout`
    """
    def get(self, request):
        return redirect(reverse('index'))

    def post(self, request):
        logout(request)

        messages.success(request, 'Logged out successfully.')

        return redirect(reverse('index'))
