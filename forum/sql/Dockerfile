FROM mysql

ENV MYSQL_ROOT_PASSWORD root

ENV MYSQL_DATABASE project

COPY setup.sql /docker-entrypoint-initdb.d/

RUN echo "[mysqld]\ncharacter-set-server=utf8mb4\ncollation-server=utf8mb4_unicode_ci" > /etc/mysql/conf.d/charset.cnf

EXPOSE 3306
