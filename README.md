# Xvun -test

Coverage of the project with tests - 99%.

### Launch of the project

#### 1) Clone repositories
```
git clone https://github.com/Lanterman/xvun_test.git
```
#### 2) Create and run docker-compose
```
docker-compose up -d --build
```
##### 2.1) To create a superuser, run the following instruction:
```
docker exec -it <backend_container_ID> python manage.py createsuperuser
```

#### 3) Follow the link in the browser:
 - ##### to launch the swagger openapi:
    ```
    http://127.0.0.1:8000/swagger/
    ```
 - ##### to launch the drf openapi:
    ```
    http://127.0.0.1:8000/api/v1/
    ```
