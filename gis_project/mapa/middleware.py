from django.contrib.auth.models import Group

class GuestUserMiddleware:
    """
    Automatycznie przypisuje grupę 'guest' dla niezalogowanych użytkowników
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        if not request.user.is_authenticated:
            request.user_group = 'guest'
        else:
            
            if request.user.is_superuser or request.user.groups.filter(name='admin').exists():
                request.user_group = 'admin'
            elif request.user.groups.filter(name='pro').exists():
                request.user_group = 'pro'
            else:
                request.user_group = 'guest'
        
        response = self.get_response(request)
        return response