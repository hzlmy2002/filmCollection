# filmCollection

### Use with Docker Development Environments

You can open this sample in the Dev Environments feature of Docker Desktop version 4.12 or later.

[Open in Docker Dev Environments <img src="../open_in_new.svg" alt="Open in Docker Dev Environments" align="top"/>](https://open.docker.com/dashboard/dev-envs?url=https://github.com/docker/awesome-compose/tree/master/nginx-flask-mysql)


## Deploy with docker compose

```
$ docker compose up --build -d
Creating network "nginx-flask-mysql_default" with the default driver
Pulling db (mysql:8.0.19)...
5.7: Pulling from library/mysql
...
...
WARNING: Image for service proxy was built because it did not already exist. To rebuild this image you must use `docker-compose build` or `docker-compose up --build`.
Creating nginx-flask-mysql_db_1 ... done
Creating nginx-flask-mysql_backend_1 ... done
Creating nginx-flask-mysql_proxy_1   ... done
```

## Expected result

Listing containers should show three containers running and the port mapping as below:
```
$ docker compose ps
IMAGE                          COMMAND                  CREATED         STATUS                   PORTS                    NAMES
filmcollection-proxy           "nginx -g 'daemon of…"   2 minutes ago   Up 2 minutes             0.0.0.0:80->80/tcp       filmcollection-proxy-1
filmcollection-backend         "flask run"              2 minutes ago   Up 2 minutes             0.0.0.0:8000->8000/tcp   filmcollection-backend-1
phpmyadmin/phpmyadmin:latest   "/docker-entrypoint.…"   2 minutes ago   Up 2 minutes             0.0.0.0:800->80/tcp      Phpmyadmin
mariadb:10-focal               "docker-entrypoint.s…"   2 minutes ago   Up 2 minutes (healthy)   3306/tcp, 33060/tcp      filmcollection-db-1
```

After the application starts, navigate to `http://localhost:80` in your web browser or run:
```
$ curl localhost:80
<div>Blog post #1</div><div>Blog post #2</div><div>Blog post #3</div><div>Blog post #4</div>
```

View PHPmyAdmin
```
user: root 
password: film

http://localhost:8090

```

Stop and remove the containers
```
$ docker compose down
```
