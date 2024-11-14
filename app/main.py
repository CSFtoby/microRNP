from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import oracledb
from app.config.settings import Settings
from app.config.logger import get_logger
import time

# Configurar logger
logger = get_logger(__name__)

app = FastAPI(title="microservice RECO payment integration")
settings = Settings()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {duration:.2f}s"
    )

    return response


# Configuración de la conexión a Oracle
def get_db_connection():
    logger.info("=== Iniciando diagnóstico de conexión ===")
    try:
        # Crear el DSN
        logger.info("Configuración de conexión:")
        logger.info(f"Host: {settings.DB_HOST}")
        logger.info(f"Port: {settings.DB_PORT}")
        logger.info(f"Service Name: {settings.DB_SERVICE_NAME}")

        dsn = f"""(DESCRIPTION=
                    (ADDRESS=
                        (PROTOCOL=TCP)
                        (HOST={settings.DB_HOST})
                        (PORT={settings.DB_PORT})
                    )
                    (CONNECT_DATA=
                        (SERVICE_NAME={settings.DB_SERVICE_NAME})
                    )
                )"""

        logger.info(f"DSN generado: {dsn}")

        # Intentar conexión
        logger.info("Intentando conexión...")
        connection = oracledb.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD ,  # Ocultamos la contraseña en logs
            dsn=dsn,
            encoding="UTF-8",
            nencoding="UTF-8",
            threaded=True,
            events=True
        )

        logger.info("¡Conexión exitosa!")
        return connection
    except Exception as e:
        logger.error(f"Error de conexión: {str(e)}")
        logger.error(f"Tipo de error: {type(e)}")
        import traceback
        logger.error(f"Stacktrace: {traceback.format_exc()}")
        raise


@app.get("/health")
async def health_check():
    logger.info("Health check solicitado")
    return {"status": "healthy"}


@app.on_event("startup")
async def startup():
    logger.info("Iniciando aplicación")
    try:
        conn = get_db_connection()
        conn.close()
        logger.info("Conexión inicial a la base de datos exitosa")
    except Exception as e:
        logger.error(f"Error en la conexión inicial a la base de datos: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown():
    logger.info("Apagando aplicación")
