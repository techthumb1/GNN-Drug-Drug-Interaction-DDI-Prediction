# backend/config/gunicorn_config.py
bind = "0.0.0.0:5050"
workers = 2
timeout = 120
