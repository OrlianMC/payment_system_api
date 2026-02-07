-- ============================================
-- SEED DATABASE - PAYMENT SYSTEM
-- Datos ficticios coherentes
-- ============================================

-- ========================
-- USERS
-- ========================

INSERT INTO users (id, email, hashed_password, role, is_active, created_at)
VALUES
(1, 'admin@gmail.com', '$2b$12$SqnGMRvm9P6TMf.33umYdeJJHP.hkcXmWrI1gZDz9vG2uP.isCL6m', 'admin', TRUE, NOW()),
(2, 'user@gmail.com', '$2b$12$BfPhhA8dNAfLlXpLxTT.huKBcb.xH0OLZ3SzPJpyx63HJekU8sO1u', 'user', TRUE, NOW());

-- ========================
-- PROFILES
-- ========================

INSERT INTO profiles (user_id, name, last_name, ci, phone, address, age, created_at)
VALUES
(1, 'Pepe', 'Alonso', '0102012325', '45454545', 'Calle A', 30, NOW()),
(2, 'Alice', 'Wonderland', '01050623564', '5555555', 'Calle C', 25, NOW());

-- ========================
-- CARDS
-- ========================

INSERT INTO cards (
    user_id,
    card_holder_name,
    brand,
    last_four,
    masked_number,
    expiration_month,
    expiration_year,
    is_active,
    created_at
)
VALUES
(2, 'Alice Wonderland', 'visa', '4242', '**** **** **** 4242', 10, 2030, TRUE, NOW()),
(2, 'Alice Wonderland', 'mastercard', '5100', '**** **** **** 5100', 12, 2028, TRUE, NOW());

-- ========================
-- PAYMENTS
-- ========================

INSERT INTO payments (
    user_id,
    card_id,
    amount,
    currency,
    status,
    processor_reference,
    idempotency_key,
    processed_at,
    created_at
)
VALUES
(2, 1, 100.00, 'USD', 'approved', 'REF-100001', 'idem-001', NOW(), NOW()),
(2, 1, 58.20, 'USD', 'rejected', NULL, 'idem-002', NULL, NOW()),
(2, 2, 33.00, 'USD', 'pending', NULL, 'idem-003', NULL, NOW());

