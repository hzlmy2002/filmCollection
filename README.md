# filmCollection


## Deploy with docker compose

```
$ docker compose up --build -d

```
## Expected result

Listing containers should show three containers running and the port mapping as below:
```
$ docker compose ps
IMAGE                     COMMAND                  CREATED         STATUS                    PORTS                               NAMES
filmcollection-backend    "python3 app.py"         8 minutes ago   Up 36 seconds             0.0.0.0:5000->5000/tcp              filmcollection-backend-1
filmcollection-db         "docker-entrypoint.s…"   8 minutes ago   Up 39 seconds (healthy)   0.0.0.0:3306->3306/tcp, 33060/tcp   filmcollection-db-1
phpmyadmin                "/docker-entrypoint.…"   8 minutes ago   Up 39 seconds             0.0.0.0:8090->80/tcp                filmcollection-phpmyadmin-1
filmcollection-frontend   "python3 app.py"         8 minutes ago   Up 39 seconds             0.0.0.0:8000->8000/tcp              filmcollection-frontend-1

```

View PHPmyAdmin
```
user: root 
password: film

http://localhost:8090

```

View Frontend
```
http://localhost:8000

```

View Swagger (API docs) at backend
```
http://localhost:5000/api/docs

```

Stop and remove the containers
```
$ docker compose down
```
