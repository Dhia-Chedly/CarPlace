-- =========================
-- Brands (30 rows)
-- =========================
INSERT INTO "CarPlace".brands (name) VALUES
('Audi'), ('BMW'), ('Mercedes-Benz'), ('Volkswagen'), ('Renault'),
('Peugeot'), ('Citroën'), ('Fiat'), ('Ford'), ('Toyota'),
('Hyundai'), ('Kia'), ('Nissan'), ('Mitsubishi'), ('Suzuki'),
('Honda'), ('Chevrolet'), ('Opel'), ('Seat'), ('Skoda'),
('Volvo'), ('Jaguar'), ('Land Rover'), ('Jeep'), ('Dacia'),
('Alfa Romeo'), ('MG'), ('Chery'), ('Geely'), ('Isuzu');

-- =========================
-- Categories (10 rows)
-- =========================
INSERT INTO "CarPlace".categories (name) VALUES
('Citadine'), ('Compacte'), ('Berline'), ('SUV'), ('Coupé'),
('Monospace'), ('Utilitaire'), ('Pick-up'), ('Cabriolet'), ('4x4');

-- =========================
-- Users (10 rows: dealers, sellers, admins)
-- =========================
INSERT INTO "CarPlace".users (username, hashed_password, role, name, phone) VALUES
('dealer_audi', 'hashed_pw1', 'dealer', 'Audi Dealer', '20123456'),
('dealer_bmw', 'hashed_pw2', 'dealer', 'BMW Dealer', '20234567'),
('dealer_renault', 'hashed_pw3', 'dealer', 'Renault Dealer', '20345678'),
('seller_john', 'hashed_pw4', 'seller', 'John Doe', '20456789'),
('seller_mary', 'hashed_pw5', 'seller', 'Mary Smith', '20567890'),
('seller_ali', 'hashed_pw6', 'seller', 'Ali Ben', '20678901'),
('admin_1', 'hashed_pw7', 'admin', 'Super Admin', '20789012'),
('dealer_toyota', 'hashed_pw8', 'dealer', 'Toyota Dealer', '20890123'),
('seller_sami', 'hashed_pw9', 'seller', 'Sami K', '20901234'),
('admin_2', 'hashed_pw10', 'admin', 'Second Admin', '21012345');

-- =========================
-- Models (30 rows, linked to brands)
-- =========================
INSERT INTO "CarPlace".models (name, brand_id) VALUES
('A3', 1), ('A6', 1), ('X5', 2), ('320d', 2), ('C-Class', 3),
('E-Class', 3), ('Golf', 4), ('Passat', 4), ('Clio', 5),
('Megane', 5), ('208', 6), ('3008', 6), ('C3', 7), ('C5 Aircross', 7),
('Tipo', 8), ('Panda', 8), ('Focus', 9), ('Fiesta', 9),
('Corolla', 10), ('Hilux', 10), ('i20', 11), ('Tucson', 11),
('Picanto', 12), ('Sportage', 12), ('Qashqai', 13), ('Navara', 13),
('Lancer', 14), ('ASX', 14), ('Swift', 15), ('Vitara', 15);

-- =========================
-- New Cars (30 rows, linked to models + categories + dealers)
-- =========================
INSERT INTO "CarPlace".new_cars (model_id, category_id, dealer_id, price_tnd, valid_until) VALUES
(1, 2, 1, 95000, '2026-12-31'), (2, 3, 1, 145000, '2026-12-31'),
(3, 4, 2, 180000, '2026-12-31'), (4, 3, 2, 120000, '2026-12-31'),
(5, 3, 3, 135000, '2026-12-31'), (6, 3, 3, 190000, '2026-12-31'),
(7, 2, 1, 80000, '2026-12-31'), (8, 3, 1, 110000, '2026-12-31'),
(9, 1, 3, 55000, '2026-12-31'), (10, 2, 3, 75000, '2026-12-31'),
(11, 1, 3, 52000, '2026-12-31'), (12, 4, 3, 125000, '2026-12-31'),
(13, 1, 3, 48000, '2026-12-31'), (14, 4, 3, 115000, '2026-12-31'),
(15, 3, 3, 68000, '2026-12-31'), (16, 1, 3, 40000, '2026-12-31'),
(17, 2, 3, 95000, '2026-12-31'), (18, 1, 3, 45000, '2026-12-31'),
(19, 3, 8, 78000, '2026-12-31'), (20, 8, 8, 160000, '2026-12-31'),
(21, 1, 8, 52000, '2026-12-31'), (22, 4, 8, 135000, '2026-12-31'),
(23, 1, 8, 42000, '2026-12-31'), (24, 4, 8, 110000, '2026-12-31'),
(25, 4, 8, 130000, '2026-12-31'), (26, 8, 8, 155000, '2026-12-31'),
(27, 3, 8, 95000, '2026-12-31'), (28, 4, 8, 120000, '2026-12-31'),
(29, 1, 8, 48000, '2026-12-31'), (30, 4, 8, 105000, '2026-12-31');

-- =========================
-- Used Cars (30 rows, linked to models + categories + sellers)
-- =========================
INSERT INTO "CarPlace".used_cars (model_id, user_id, year, mileage_km, price_tnd, condition) VALUES
(1, 4, 2018, 85000, 65000, 'Bon état'),
(2, 4, 2016, 120000, 90000, 'Très bon'),
(3, 5, 2019, 60000, 140000, 'Excellent'),
(4, 5, 2015, 150000, 70000, 'Bon état'),
(5, 5, 2017, 95000, 100000, 'Très bon'),
(6, 6, 2014, 180000, 85000, 'Moyen'),
(7, 6, 2019, 50000, 75000, 'Excellent'),
(8, 6, 2013, 200000, 60000, 'Bon état'),
(9, 6, 2020, 30000, 48000, 'Excellent'),
(10, 6, 2016, 110000, 55000, 'Bon état'),
(11, 6, 2018, 80000, 45000, 'Très bon'),
(12, 6, 2017, 95000, 95000, 'Bon état'),
(13, 6, 2015, 130000, 40000, 'Moyen'),
(14, 6, 2019, 60000, 100000, 'Excellent'),
(15, 6, 2014, 160000, 35000, 'Bon état'),
(16, 6, 2013, 180000, 25000, 'Moyen'),
(17, 6, 2016, 120000, 60000, 'Bon état'),
(18, 6, 2017, 95000, 40000, 'Très bon'),
(19, 6, 2018, 85000, 70000, 'Excellent'),
(20, 6, 2015, 150000, 120000, 'Bon état'),
(21, 6, 2020, 25000, 50000, 'Excellent'),
(22, 6, 2019, 60000, 110000, 'Très bon');