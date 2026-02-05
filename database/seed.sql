-- ================================
-- Datos de prueba
-- ================================

-- Usuarios (contraseñas hasheadas con bcrypt)
-- password real: "123456"
INSERT INTO usuarios (email, hashed_password)
VALUES 
('user1@test.com', '$2b$12$KIX8J4Cq6K4JH2F/1D2eV.kZfZZ4T5l8tIwwK5Z6lCq4l0r2kzB6e'),
('user2@test.com', '$2b$12$KIX8J4Cq6K4JH2F/1D2eV.kZfZZ4T5l8tIwwK5Z6lCq4l0r2kzB6e');

-- Tarjetas asociadas a usuarios (solo datos ficticios)
INSERT INTO tarjetas (masked_number, user_id)
VALUES
('**** **** **** 1111', 1),
('**** **** **** 2222', 1),
('**** **** **** 3333', 2),
('**** **** **** 4444', 2);

-- Pagos asociados a usuarios y tarjetas
INSERT INTO pagos (amount, status, user_id, card_id)
VALUES
(100.00, 'approved', 1, 1),
(50.00, 'approved', 1, 2),
(25.50, 'rejected', 1, 1),
(200.00, 'approved', 2, 3),
(75.75, 'rejected', 2, 3),
(150.00, 'approved', 2, 4);
