from django.shortcuts import redirect
from django.urls import reverse


class RoleBasedRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.path == reverse('login'):  # Redirect after login
                if request.user.is_superuser:
                    return redirect('admin_dashboard')
                else:
                    return redirect('/')
        return self.get_response(request)
