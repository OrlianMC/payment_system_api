# Prueba Técnica Backend – Sistema de Pagos

## 🔹 Descripción

Sistema básico de pagos que permite:

- Crear usuarios
- Registrar tarjetas de crédito (solo datos ficticios)
- Crear pagos asociados a usuarios y tarjetas
- Listar historial de pagos
- Procesamiento simulado de pagos con microservicio Python (80% aprobado, 20% rechazado)

Tecnologías utilizadas:

- **Python 3.12** + **FastAPI** para el API principal
- **PostgreSQL** como base de datos
- **SQLModel** como ORM
- **Passlib** y **bcrypt** para contraseñas seguras
- **HTTPX** para llamadas al microservicio de pagos
- **dotenv** para configuración

---

## 📂 Estructura del proyecto

```

payment-system/
│
├── .gitignore
├── README.md
├── api_service/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── logging.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   └── main.py
│   └── requirements.txt
│
├── payment_processor/
│   ├── app/
│   │   └── main.py
│   └── requirements.txt
│
├── database/
│   ├── init.sql
│   ├── seed.sql
│   └── README.md
│
└── postman/
└── collection.json

````

---

## ⚙️ Requisitos previos

- Python 3.12+
- PostgreSQL
- pip
- (Opcional) virtualenv

---

## 📝 Variables de entorno

Archivo `.env` en la raíz del repo:

```env
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=
DB_SSLMODE=require

PROCESSOR_URL=http://localhost:9000/process-payment
SECRET_KEY=alguna_clave_secreta_para_jwt
````

---

## 💾 Base de datos

### 1️⃣ Crear tablas

```bash
psql -U <usuario> -d <nombre_db> -f database/init.sql
```

### 2️⃣ Poblar datos de prueba

```bash
psql -U <usuario> -d <nombre_db> -f database/seed.sql
```

---

## 🏗️ Instalación y ejecución

### 1️⃣ API Service

```bash
cd api_service
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Endpoints principales

```http
GET /health
POST /api/users
POST /api/cards
POST /api/payments
GET /api/payments/user/{user_id}
```

Docs interactivos: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 2️⃣ Payment Processor

```bash
cd payment_processor
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows

pip install -r requirements.txt
uvicorn app.main:app --port 9000
```

#### Endpoint

```http
POST /process-payment
```

* Recibe: `{ "amount": 100.0 }`
* Responde: `{ "amount": 100.0, "status": "approved" }` o `"rejected"` (80/20%)

---

## 🛠️ Flujo de pagos

1. Cliente llama `POST /api/payments` en el API.
2. API envía request al processor (HTTPX async).
3. Processor devuelve aprobado o rechazado.
4. API guarda resultado en `pagos` y lo retorna al cliente.

---

## 💡 Buenas prácticas implementadas

* Contraseñas hasheadas con bcrypt
* Separación de capas (core / routes / models / services)
* Logging profesional centralizado (`core/logging.py`)
* Lifespan de FastAPI para inicialización y shutdown
* Scripts SQL independientes para reproducibilidad
* CORS configurado para testing

---

## 📦 Postman

* Carpeta `postman/collection.json` con endpoints listos para pruebas

---

## 🔗 Enlaces útiles

* [FastAPI](https://fastapi.tiangolo.com/)
* [SQLModel](https://sqlmodel.tiangolo.com/)
* [PostgreSQL](https://www.postgresql.org/)
* [Passlib](https://passlib.readthedocs.io/)
