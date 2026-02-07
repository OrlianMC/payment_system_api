-- ============================================
-- INIT DATABASE - PAYMENT SYSTEM
-- Estructura limpia
-- ============================================

-- ========================
-- ENUMS
-- ========================

CREATE TYPE cardbrand AS ENUM (
    'visa',
    'mastercard',
    'amex',
    'discover'
);

CREATE TYPE paymentstatus AS ENUM (
    'approved',
    'rejected',
    'pending'
);

CREATE TYPE userrole AS ENUM (
    'admin',
    'user'
);

-- ========================
-- USERS
-- ========================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    role userrole NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- ========================
-- PROFILES
-- ========================

CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR,
    last_name VARCHAR,
    ci VARCHAR,
    phone VARCHAR,
    address VARCHAR,
    age INTEGER,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE UNIQUE INDEX unique_active_profile
ON profiles(user_id)
WHERE deleted_at IS NULL;

-- ========================
-- CARDS
-- ========================

CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    card_holder_name VARCHAR NOT NULL,
    brand cardbrand NOT NULL,
    last_four VARCHAR NOT NULL,
    masked_number VARCHAR NOT NULL,
    expiration_month INTEGER NOT NULL,
    expiration_year INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- ========================
-- PAYMENTS
-- ========================

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    card_id INTEGER NOT NULL REFERENCES cards(id),
    amount DOUBLE PRECISION NOT NULL,
    currency VARCHAR NOT NULL,
    status paymentstatus NOT NULL,
    status_reason VARCHAR,
    processor_reference VARCHAR,
    idempotency_key VARCHAR,
    processed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE UNIQUE INDEX unique_payment_idempotency
ON payments(idempotency_key)
WHERE idempotency_key IS NOT NULL;

