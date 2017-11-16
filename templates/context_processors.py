from django.conf import settings

# def contactemail(request):
#     return {
#         'CONTACT_EMAIL' : settings.CONTACT_EMAIL
#     }
#
# def domain(request):
#     return {
#         'DOMAIN' : settings.DOMAIN
#     }

def debugsetting(request):
    return {
        'DEBUG' : settings.DEBUG
    }