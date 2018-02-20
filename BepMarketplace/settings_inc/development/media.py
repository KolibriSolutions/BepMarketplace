# path for media upload. Media download is not available on this path.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/download/'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
# copy static files from custom apps to the same static root as other files
STATIC_ROOT = os.path.join(BASE_DIR, '../templates/static/')

# path for media download. This uses auth via the sendfile backend in the downloads app.
SENDFILE_BACKEND = 'sendfile.backends.development'
SENDFILE_ROOT = MEDIA_ROOT
SENDFILE_URL = '/protected/'
