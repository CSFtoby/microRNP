from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import oracledb
from app.config.settings import Settings
from app.config.logger import get_logger
import time
import requests
import xml.etree.ElementTree as ET
from app.models.requests import PaymentRequest
from datetime import datetime

# Configurar logger
logger = get_logger(__name__)

# Inicializar el cliente de Oracle
oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_21_10")

app = FastAPI(title="Microservice RECO payment integration")
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


@app.post("/query")
async def query(payment_request: PaymentRequest):
    CURRENCY = 'LPS'
    CODE_COOPSAFA = '8'
    logger.info("Query requested")
    try:
        # Deshabilitar verificación SSL (similar al código C#)
        requests.packages.urllib3.disable_warnings()

        # Preparar el XML SOAP
        soap_body = f"""<?xml version='1.0' encoding='utf-8'?>
        <soap:Envelope xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'
                      xmlns:xsd='http://www.w3.org/2001/XMLSchema'
                      xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'>
            <soap:Body>
                <ConsultaPago xmlns='http://tempuri.org/'>
                    <CodigoBanco>{CODE_COOPSAFA}</CodigoBanco>
                    <CodigoSucursal>{payment_request.code_subsidiary}</CodigoSucursal>
                    <CodigoUsuario>{payment_request.code_user}</CodigoUsuario>
                    <CodigoCliente>{payment_request.code_customer}</CodigoCliente>
                    <CodigoMoneda>{CURRENCY}</CodigoMoneda>
                </ConsultaPago>
            </soap:Body>
        </soap:Envelope>"""

        # Configurar headers
        headers = {
            'Content-Type': 'text/xml',
            'SOAPAction': 'http://tempuri.org/ConsultaPago'
        }

        # Hacer la petición al servicio SOAP
        response = requests.post(
            settings.SOAP_URL,
            data=soap_body,
            headers=headers,
            verify=False  # Equivalente a ServerCertificateValidationCallback
        )

        response.raise_for_status()
        response_text = response.text

        # Analizar el XML
        root = ET.fromstring(response_text)

        query_result = root.find(".//ConsultaPago")
        if query_result is None:
            logger.error(f"No se encontró resultado en la consulta: {response_text}")
            return HTTPException(status_code=400, detail="No se encontró resultado en la consulta")

        customer_code = query_result.find("CodigoCliente").text
        customer_name = query_result.find("NombreCliente").text
        invoice_date = query_result.find("Fecha").text
        invoice_price = float(query_result.find("Valor").text)
        invoice_local_price = float(query_result.find("ValorLocal").text)
        code_currency = query_result.find("Moneda").text

        # Guardar en base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        # Definir una variable para almacenar el valor de la secuencia
        new_id = cursor.var(int)

        cursor.execute("""
            INSERT INTO SPUB.AV_RECO_ENVIOS(
                CODIGO_RECO_BANCO, CODIGO_FILIAL, CODIGO_USUARIO,
                CODIGO_CLIENTE, CODIGO_MONEDA, ESTADO, PAGADO,
                NOMBRE_CLIENTE, FECHA_FACTURA, VALOR_FACTURA, VALOR_FACTURA_LOCAL
            )
            VALUES (
                :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11
            )
            RETURNING SECUENCIA INTO :12
        """, [
            CODE_COOPSAFA, payment_request.code_subsidiary, payment_request.code_user,
            customer_code, code_currency, 'CON', 'N',
            customer_name, invoice_date, invoice_price, invoice_local_price, new_id
        ])

        conn.commit()
        new_id = new_id.getvalue()
        data = {
            "id": new_id,
            "customer_code": customer_code,
            "customer_name": customer_name,
            "invoice_date": invoice_date,
            "invoice_price": invoice_price,
            "invoice_local_price": invoice_local_price
        }
        return {"status": "success", "data": data}

    except requests.RequestException as e:
        logger.error(f"Error en la petición SOAP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error en la consulta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.post("/payment")
async def payment(request: Request):
    logger.info("Payment requested")
    try:
        data = await request.json()
        conn = get_db_connection()
        cursor = conn.cursor()
        # Aquí iría la lógica para realizar el pago
        # Por ejemplo: cursor.execute("INSERT INTO payments ...", data)
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Payment successful"}
    except Exception as e:
        logger.error(f"Error in payment: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/cancel-payment")
async def cancel_payment(request: Request):
    logger.info("Payment cancellation requested")
    try:
        data = await request.json()
        conn = get_db_connection()
        cursor = conn.cursor()
        # Aquí iría la lógica para anular el pago
        # Por ejemplo: cursor.execute("DELETE FROM payments WHERE ...", data)
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Payment cancelled successfully"}
    except Exception as e:
        logger.error(f"Error in payment cancellation: {str(e)}")
        return {"status": "error", "message": str(e)}
