USE_LISTEN_PORT=${LISTEN_PORT:-80}
echo "server {
    listen ${USE_LISTEN_PORT};
    root ${STATIC_ROOT};
    location / {
        try_files \$uri \$uri/index.html @app;
    }
    location @app {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/uwsgi.sock;
    }
}" > /etc/nginx/conf.d/nginx.conf

python start.py
