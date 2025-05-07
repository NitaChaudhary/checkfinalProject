# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'yash108.rejoice@gmail.com'
# EMAIL_HOST_PASSWORD = 'ogyizehsfblgswzp'
# EMAIL_PORT = 587

from decouple import config

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'yashpp5545@gmail.com'
# EMAIL_HOST_PASSWORD = 'jyixqsmsdrbgyvsv'
# EMAIL_PORT = 587

EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True)  # Use True as default
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')  # Default to Gmail's SMTP
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='yash108.rejoice@gmail.com')  # Your email
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='ogyizehsfblgswzp')  # Your password
EMAIL_PORT = config('EMAIL_PORT', default=587)  # Default SMTP port