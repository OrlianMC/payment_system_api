
---

## 📄 `database/init.sql`

```sql
-- ================================
-- Inicialización de base de datos
-- ================================

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL
);

CREATE TABLE tarjetas (
    id SERIAL PRIMARY KEY,
    masked_number VARCHAR(20) NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE pagos (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    user_id INTEGER NOT NULL,
    card_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES tarjetas(id) ON DELETE CASCADE
);
