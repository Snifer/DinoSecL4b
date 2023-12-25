FROM php:apache

RUN docker-php-ext-install mysqli
COPY ./web /var/www/html

