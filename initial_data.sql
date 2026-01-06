-- initial_data.sql
-- Datos de ejemplo para PostgreSQL (requiere migraciones aplicadas hasta head)

BEGIN;

-- Asegurar enum loanstatus (si no existe)
DO $$
BEGIN
    CREATE TYPE loanstatus AS ENUM ('ACTIVE', 'RETURNED', 'OVERDUE');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- Limpiar tablas (en una BD vacía esto no afecta)
TRUNCATE TABLE
    book_categories,
    reviews,
    loans,
    categories,
    books,
    users
RESTART IDENTITY CASCADE;

-- Categorías (5)
INSERT INTO categories (id, name, description, created_at, updated_at) VALUES
(1, 'Ficción', 'Narrativa y novelas', now(), now()),
(2, 'No Ficción', 'Ensayos y textos informativos', now(), now()),
(3, 'Ciencia', 'Divulgación científica', now(), now()),
(4, 'Historia', 'Libros históricos', now(), now()),
(5, 'Fantasía', 'Mundos y magia', now(), now());

-- Libros (10) con ISBN ISBN-BD2-2025-XXXX (1120..1165 salto 5)
INSERT INTO books (
    id, title, author, isbn, pages, published_year,
    publisher, language, description, stock,
    created_at, updated_at
) VALUES
(1, 'La Ciudad de Papel', 'A. Torres', 'ISBN-BD2-2025-1120', 320, 2018, 'Editorial Norte', 'es', 'Novela de ficción urbana.', 4, now(), now()),
(2, 'Manual de Historia Moderna', 'B. Ríos', 'ISBN-BD2-2025-1125', 410, 2015, 'Academia Sur', 'es', 'Guía introductoria a historia moderna.', 2, now(), now()),
(3, 'Introducción a la Ciencia', 'C. Vega', 'ISBN-BD2-2025-1130', 280, 2020, 'Ciencia Viva', 'en', 'Conceptos básicos de ciencia.', 3, now(), now()),
(4, 'Crónicas del Imperio', 'D. Salas', 'ISBN-BD2-2025-1135', 500, 2012, 'Historia Global', 'es', 'Relato histórico de un imperio.', 1, now(), now()),
(5, 'El Bosque Encantado', 'E. Luna', 'ISBN-BD2-2025-1140', 360, 2019, 'Fantasía & Co.', 'es', 'Aventura fantástica.', 5, now(), now()),
(6, 'Ficción y Física', 'F. Klein', 'ISBN-BD2-2025-1145', 295, 2021, 'Ciencia Viva', 'de', 'Puente entre narrativa y ciencia.', 2, now(), now()),
(7, 'Ensayos de Sociedad', 'G. Pinto', 'ISBN-BD2-2025-1150', 260, 2016, 'Ideas Abiertas', 'pt', 'Colección de ensayos sociales.', 2, now(), now()),
(8, 'Experimentos Sencillos', 'H. Moreau', 'ISBN-BD2-2025-1155', 220, 2022, 'Lab Kids', 'fr', 'Experimentos fáciles para aprender.', 3, now(), now()),
(9, 'Atlas de Historia', 'I. Romano', 'ISBN-BD2-2025-1160', 440, 2013, 'Historia Global', 'it', 'Atlas histórico ilustrado.', 1, now(), now()),
(10, 'Reinos de Bruma', 'J. Winter', 'ISBN-BD2-2025-1165', 390, 2017, 'Fantasía & Co.', 'en', 'Saga fantástica en dos continentes.', 4, now(), now());

-- Relación libros-categorías
INSERT INTO book_categories (book_id, category_id) VALUES
(1, 1), (1, 5),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 1), (6, 3),
(7, 2), (7, 4),
(8, 3),
(9, 4),
(10, 1), (10, 5);

-- Usuarios (5) con info completa y contraseñas argon2
-- Las contraseñas están hasheadas con Argon2 (pwdlib).
INSERT INTO users (
    id, username, fullname, email, phone, address, is_active, password,
    created_at, updated_at
) VALUES
(1, 'ana', 'Ana Pérez', 'ana@example.com', '+56 9 1111 1111', 'Av. Central 123', true, '$argon2id$v=19$m=65536,t=3,p=4$I2EuDEKQOClr6FVUDYT2cg$/+b9wJeXkefd2aGOkt9r4oCrB8vpoez5c2ViV00wfOU', now(), now()),
(2, 'bruno', 'Bruno Díaz', 'bruno@example.com', '+56 9 2222 2222', 'Calle Norte 456', true, '$argon2id$v=19$m=65536,t=3,p=4$XeGDwtvWAVPrA5r9MEEmUw$Dn15FKokplHY03Da4gqwGvOuBBBX7phPsO/T3UVBJw0', now(), now()),
(3, 'carla', 'Carla Soto', 'carla@example.com', '+56 9 3333 3333', 'Pasaje Sur 789', true, '$argon2id$v=19$m=65536,t=3,p=4$isoYG7Fd1z6O69pjXzCC+Q$lZJ8Z1YBqHYO58L566AH572q7JvuBXDe2yvfIJIeGO4', now(), now()),
(4, 'diego', 'Diego Morales', 'diego@example.com', '+56 9 4444 4444', 'Los Robles 101', true, '$argon2id$v=19$m=65536,t=3,p=4$P7JDN/czSOdQEPOd4bPxsQ$D7HQlVaDCrY6ATGK5OuQaFeRWhPCkMc0jExMW/mPne0', now(), now()),
(5, 'elena', 'Elena Vargas', 'elena@example.com', '+56 9 5555 5555', 'Las Flores 202', true, '$argon2id$v=19$m=65536,t=3,p=4$akFJiwXA86vCO1L8cwuxhQ$BWz+YDp3eX6ILZlhiMFT/lde527wjM/6TNHbwmlHfMU', now(), now());

-- Préstamos (8): activos, devueltos, vencidos
INSERT INTO loans (
    id, loan_dt, return_dt, due_date, fine_amount, status,
    user_id, book_id,
    created_at, updated_at
) VALUES
(1, '2025-12-01', '2025-12-10', '2025-12-15', NULL, 'RETURNED', 1, 1, now(), now()),
(2, '2025-12-20', NULL, '2026-01-03', NULL, 'ACTIVE', 2, 2, now(), now()),
(3, '2025-11-01', NULL, '2025-11-15', NULL, 'OVERDUE', 3, 3, now(), now()),
(4, '2025-10-01', '2025-11-01', '2025-10-15', 8500.00, 'RETURNED', 4, 4, now(), now()),
(5, '2026-01-01', NULL, '2026-01-15', NULL, 'ACTIVE', 5, 5, now(), now()),
(6, '2025-12-15', '2026-01-05', '2025-12-29', 3500.00, 'RETURNED', 1, 6, now(), now()),
(7, '2025-12-10', NULL, '2025-12-24', NULL, 'ACTIVE', 2, 7, now(), now()),
(8, '2025-12-05', '2025-12-19', '2025-12-19', NULL, 'RETURNED', 3, 8, now(), now());

-- Reseñas (15) distribuidas (sin superar 3 reseñas por user+book)
INSERT INTO reviews (
    id, rating, comment, review_date, user_id, book_id,
    created_at, updated_at
) VALUES
(1, 5, 'Excelente lectura.', '2025-12-02', 1, 1, now(), now()),
(2, 4, 'Muy bueno, recomendado.', '2025-12-03', 2, 1, now(), now()),
(3, 3, 'Interesante, pero lento al inicio.', '2025-12-04', 3, 1, now(), now()),
(4, 4, 'Útil y claro.', '2025-12-21', 1, 2, now(), now()),
(5, 5, 'Muy completo.', '2025-12-22', 4, 2, now(), now()),
(6, 4, 'Buen resumen de conceptos.', '2025-11-10', 5, 3, now(), now()),
(7, 2, 'Esperaba más ejemplos.', '2025-11-12', 2, 3, now(), now()),
(8, 5, 'Me encantó el enfoque.', '2025-10-20', 3, 4, now(), now()),
(9, 3, 'Entretenido.', '2026-01-02', 4, 5, now(), now()),
(10, 4, 'Muy buena ambientación.', '2026-01-03', 5, 6, now(), now()),
(11, 5, 'Gran autor.', '2025-12-26', 1, 7, now(), now()),
(12, 4, 'Práctico para aprender.', '2025-12-06', 2, 8, now(), now()),
(13, 5, 'Ilustraciones excelentes.', '2025-12-07', 3, 9, now(), now()),
(14, 4, 'Buen cierre de historia.', '2025-12-08', 4, 10, now(), now()),
(15, 3, 'Correcto, pero no memorable.', '2025-12-09', 5, 10, now(), now());

COMMIT;
