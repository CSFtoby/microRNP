# Microservicio template para desarrollo de microservicios con python y FastAPI

## Requisitos

- Docker
- Python 3.10
- FastAPI 0.104.0
- oracledb 1.4.1
- python-dotenv 1.0.0
- pydantic 2.4.2
- pydantic-settings 2.0.3
- requests 2.31.0

## Clonar el repositorio

```bash
git clone https://github.com/Cooperativa-Sagrada-Familia/microservicio-template-python-fastapi.git [Proyecto/Equipo]-[Tipo de Servicio]-[Funcionalidad Principal]-[Versión (opcional)]

```

## Cambiar remote origin

Esto es importante para mantener el orden y no hacer push al repositorio base
```bash
git remote set-url origin URL_REPOSITORIO
```


## Crear .env con las variables de entorno

```bash
cp .env.example .env
```

## Construir el contenedor

```bash
docker compose build
```

## Ejecutar el contenedor

```bash
docker compose up
```

## Detener el contenedor

```bash
docker compose down
```

## Estructura del proyecto

- docker-compose.yml: Define los servicios, redes y volúmenes del microservicio
- Dockerfile: Define la configuración del contenedor
- .env.example: Contiene las variables de entorno del microservicio con valores de ejemplo
- .env: Contiene las variables de entorno del microservicio, conexiones a bases de datos, etc.
- requirements.txt: Contiene las dependencias del microservicio
- logs: Contiene los logs del microservicio
- .gitignore: Contiene las rutas que no se deben subir a github
- README.md: Contiene la documentación del microservicio

- app: Contiene el código del microservicio
- app/main.py: Contiene el punto de entrada del microservicio
- app/routes: En microservicios de tipo API, contiene las rutas del microservicio
- app/models: Contiene los modelos de datos del microservicio
- app/services: En microservicios de tipo API que se vuelvan lo suficientemente complejos, en mejor dividir el código en servicios, esto quiere decir que en el archivo main.py se importen los servicios y se utilicen en las rutas
- app/utils: no esta implementado en este template, pero se puede utilizar para funciones generales que no sean de negocio
- app/config: contiene la configuración del microservicio, levantamiento de logs, variables de entorno, etc.


# Links de interés

- [FastAPI](https://fastapi.tiangolo.com/)
- [Oracle](https://www.oracle.com/database/technologies/appdev/oracle-db-express-editions.html)
- [Python](https://www.python.org/)
- [Docker](https://www.docker.com/)

## auto API docs

local: <http://localhost:8000/docs>

## auto redoc

local: <http://localhost:8000/redoc>
