"""
WSGI config for MoviesPro project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

path = 'C:\Users\HP\Desktop\ProjectMovieTicket\MoviesPro'
if path not in sys.path:
    sys.path.append(path)



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MoviesPro.settings')

# 🔐 environment variables (IMPORTANT)
os.environ['SECRET_KEY'] = 'django-insecure-&kisw)b4@d^!9#a$n10(g_jbwpcijbu2&*w-axuurr60qo@-c^'
os.environ['DEBUG'] = 'False'

# Razorpay keys
os.environ['RAZORPAY_KEY_ID'] = 'rzp_test_S64c1UBhvLAM9y'
os.environ['RAZORPAY_KEY_SECRET'] = 'sj8D9pCTfl9VUf2A77f3GT3K'

application = get_wsgi_application()



