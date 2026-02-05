# Database Scripts - Payment System

Esta carpeta contiene los scripts necesarios para inicializar y poblar la base de datos PostgreSQL del sistema de pagos.

---

## 📄 init.sql

Crea las tablas principales:

- `usuarios` → almacena los usuarios del sistema.
- `tarjetas` → tarjetas asociadas a los usuarios (solo datos ficticios).
- `pagos` → historial de pagos asociados a usuarios y tarjetas.

### Uso

```bash
psql -U <usuario> -d <nombre_db> -f database/init.sql
````

---

## 📄 seed.sql

Puebla la base de datos con datos de prueba:

* 2 usuarios con contraseñas hasheadas (bcrypt)
* 2 tarjetas por usuario
* 3 pagos por usuario (aproximadamente 80% aprobados, 20% rechazados)

### Uso

```bash
psql -U <usuario> -d <nombre_db> -f database/seed.sql
```

---

## 🔹 Recomendaciones

* Ejecuta primero `init.sql` y luego `seed.sql`.
* Las tarjetas son ficticias y enmascaradas (no usar reales).
* Los scripts permiten pruebas rápidas del API sin necesidad de crear usuarios o pagos manualmente.
* Puedes modificar o agregar más datos para pruebas adicionales.

---

## 📌 Notas adicionales

* Estos scripts son independientes del ORM (SQLModel) usado en la API.
* Sirven para inicialización manual de PostgreSQL o para pruebas rápidas.
