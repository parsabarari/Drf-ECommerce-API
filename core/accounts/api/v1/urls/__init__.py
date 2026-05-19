from django.urls import include,path

app_name = 'api-v1'

urlpatterns = [
    path('',include('accounts.api.v1.urls.accounts')),
    path('profile/', include('accounts.api.v1.urls.profile'))
]
