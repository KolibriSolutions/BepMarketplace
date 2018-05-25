
# MIDDLEWARE.remove("htmlmin.middleware.HtmlMinifyMiddleware")

# to allow websockets in CSP over plain http
CSP_CONNECT_SRC = ("'self'", "ws://localhost:*")  # websockets and ajax. Make sure wss:// is set and not ws://.

