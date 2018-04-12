FROM tiangolo/uwsgi-nginx-flask:python3.6
ENV STATIC_ROOT /app/static
COPY ./app /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
