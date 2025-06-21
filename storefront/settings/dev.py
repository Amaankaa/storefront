from .common import *

DEBUG = True


SECRET_KEY = 'django-insecure-_fwyeg5p$y2y8izai=@we94b4i-pvu&^5esv(v=vk629c8w9^^'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront2',
        'HOST': '192.168.102.38',
        'USER': 'root',
        'PASSWORD': 'root123',
    }
}