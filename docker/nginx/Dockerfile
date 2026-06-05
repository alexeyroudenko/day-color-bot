FROM nginx:1.25

RUN rm /etc/nginx/conf.d/default.conf
RUN rm /usr/share/nginx/html/index.html
COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf
