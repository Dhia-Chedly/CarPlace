



INSERT INTO "CarPlace".brands (id, name, country, wmi) VALUES
(1, 'Hyundai', 'South Korea', 'KMH'),
(2, 'Renault', 'France', 'VF1'),
(3, 'Fiat', 'Italy', 'ZFA'),
(4, 'Toyota', 'Japan', 'JTD'),
(5, 'Kia', 'South Korea', 'KNA'),
(6, 'Isuzu', 'Japan', 'JAAN'),
(7, 'Peugeot', 'France', 'VF3'),
(8, 'Suzuki', 'Japan', 'JS2'),
(9, 'Citroën', 'France', 'VF7'),
(10, 'Volkswagen', 'Germany', 'WVW'),
(11, 'Nissan', 'Japan', 'JN1'),
(12, 'Skoda', 'Czech Republic', 'TMB'),
(13, 'Dacia', 'Romania', 'UU1'),
(14, 'Opel', 'Germany', 'W0L'),
(15, 'Mitsubishi', 'Japan', 'JA3'),
(16, 'Chery', 'China', 'LFB'),
(17, 'Geely', 'China', 'LGH'),
(18, 'BYD', 'China', 'LJD'),
(19, 'BMW', 'Germany', 'WBA'),
(20, 'Mercedes-Benz', 'Germany', 'WDB'),
(21, 'Audi', 'Germany', 'WAU');






-- Hyundai (South Korea)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('i10', 1, 'I10'),
('i20', 1, 'I20'),
('i30', 1, 'I30'),
('Accent', 1, 'ACC'),
('Elantra', 1, 'ELA'),
('Sonata', 1, 'SON'),
('Tucson', 1, 'TUC'),
('Santa Fe', 1, 'SAN'),
('Kona', 1, 'KON'),
('Palisade', 1, 'PAL');

-- Renault (France)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Clio', 2, 'CLI'),
('Megane', 2, 'MEG'),
('Symbol', 2, 'SYM'),
('Kadjar', 2, 'KAD'),
('Koleos', 2, 'KOL'),
('Captur', 2, 'CAP'),
('Talisman', 2, 'TAL'),
('Scenic', 2, 'SCE'),
('Espace', 2, 'ESP'),
('Zoe', 2, 'ZOE');

-- Fiat (Italy)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Panda', 3, 'PAN'),
('Tipo', 3, 'TIP'),
('500', 3, '500'),
('500X', 3, '5X'),
('500L', 3, '5L'),
('Doblo', 3, 'DOB'),
('Qubo', 3, 'QUB'),
('Punto', 3, 'PUN'),
('Bravo', 3, 'BRA'),
('Uno', 3, 'UNO');

-- Toyota (Japan)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Yaris', 4, 'YAR'),
('Corolla', 4, 'COR'),
('Camry', 4, 'CAM'),
('Hilux', 4, 'HIL'),
('Land Cruiser', 4, 'LCR'),
('RAV4', 4, 'RAV'),
('Avensis', 4, 'AVE'),
('C-HR', 4, 'CHR'),
('Prius', 4, 'PRI'),
('Fortuner', 4, 'FOR');

-- Kia (South Korea)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Picanto', 5, 'PIC'),
('Rio', 5, 'RIO'),
('Cerato', 5, 'CER'),
('Sportage', 5, 'SPO'),
('Sorento', 5, 'SOR'),
('Optima', 5, 'OPT'),
('Stinger', 5, 'STI'),
('Telluride', 5, 'TEL'),
('Seltos', 5, 'SEL'),
('EV6', 5, 'EV6');

-- Isuzu (Japan)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('D-Max', 6, 'DMX'),
('MU-X', 6, 'MUX'),
('Trooper', 6, 'TRO'),
('Rodeo', 6, 'ROD'),
('Axiom', 6, 'AXI'),
('Ascender', 6, 'ASC'),
('Amigo', 6, 'AMI'),
('F-Series Truck', 6, 'FST'),
('Elf', 6, 'ELF'),
('Giga', 6, 'GIG');

-- Peugeot (France)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('208', 7, '208'),
('301', 7, '301'),
('308', 7, '308'),
('508', 7, '508'),
('2008', 7, '2008'),
('3008', 7, '3008'),
('5008', 7, '5008'),
('Partner', 7, 'PAR'),
('Expert', 7, 'EXP'),
('Traveller', 7, 'TRV');

-- Suzuki (Japan)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Swift', 8, 'SWI'),
('Celerio', 8, 'CEL'),
('Baleno', 8, 'BAL'),
('Vitara', 8, 'VIT'),
('Jimny', 8, 'JIM'),
('SX4', 8, 'SX4'),
('Alto', 8, 'ALT'),
('Ignis', 8, 'IGN'),
('Ertiga', 8, 'ERT'),
('XL7', 8, 'XL7');

-- Citroën (France)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('C1', 9, 'C1'),
('C3', 9, 'C3'),
('C4', 9, 'C4'),
('C5', 9, 'C5'),
('Berlingo', 9, 'BER'),
('DS3', 9, 'DS3'),
('DS4', 9, 'DS4'),
('DS5', 9, 'DS5'),
('C-Elysée', 9, 'CEL'),
('Spacetourer', 9, 'SPA');

-- Volkswagen (Germany)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Golf', 10, 'GOL'),
('Polo', 10, 'POL'),
('Passat', 10, 'PAS'),
('Jetta', 10, 'JET'),
('Tiguan', 10, 'TIG'),
('Touareg', 10, 'TOU'),
('Arteon', 10, 'ART'),
('ID.3', 10, 'ID3'),
('ID.4', 10, 'ID4'),
('Beetle', 10, 'BEE');

-- Nissan (Japan)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Micra', 11, 'MIC'),
('Sunny', 11, 'SUN'),
('Sentra', 11, 'SEN'),
('Altima', 11, 'ALT'),
('Maxima', 11, 'MAX'),
('Qashqai', 11, 'QAS'),
('X-Trail', 11, 'XTR'),
('Patrol', 11, 'PAT'),
('Navara', 11, 'NAV'),
('Juke', 11, 'JUK');

-- Skoda (Czech Republic)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Fabia', 12, 'FAB'),
('Octavia', 12, 'OCT'),
('Superb', 12, 'SUP'),
('Scala', 12, 'SCA'),
('Kamiq', 12, 'KAM'),
('Karoq', 12, 'KAR'),
('Kodiaq', 12, 'KOD'),
('Enyaq iV', 12, 'ENY'),
('Rapid', 12, 'RAP'),
('Citigo', 12, 'CIT');

-- Dacia (Romania)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Logan', 13, 'LOG'),
('Sandero', 13, 'SAN'),
('Duster', 13, 'DUS'),
('Spring EV', 13, 'SPR'),
('Dokker', 13, 'DOK'),
('Lodgy', 13, 'LOD'),
('Solenza', 13, 'SOL'),
('Nova', 13, 'NOV'),
('1310', 13, '131'),
('MCV', 13, 'MCV');

-- Opel (Germany)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Corsa', 14, 'COR'),
('Astra', 14, 'AST'),
('Insignia', 14, 'INS'),
('Zafira', 14, 'ZAF'),
('Mokka', 14, 'MOK'),
('Crossland', 14, 'CRO'),
('Grandland', 14, 'GRA'),
('Vectra', 14, 'VEC'),
('Meriva', 14, 'MER'),
('Kadett', 14, 'KAD');

-- Mitsubishi (Japan)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Mirage', 15, 'MIR'),
('Lancer', 15, 'LAN'),
('Outlander', 15, 'OUT'),
('Eclipse Cross', 15, 'ECL'),
('Pajero', 15, 'PAJ'),
('ASX', 15, 'ASX'),
('Galant', 15, 'GAL'),
('Endeavor', 15, 'END'),
('Raider', 15, 'RAI'),
('Delica', 15, 'DEL');

-- Chery (China)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('QQ', 16, 'QQ'),
('Arrizo 5', 16, 'AR5'),
('Arrizo 7', 16, 'AR7'),
('Tiggo 2', 16, 'TG2'),
('Tiggo 3', 16, 'TG3'),
('Tiggo 5', 16, 'TG5'),
('Tiggo 7', 16, 'TG7'),
('Tiggo 8', 16, 'TG8'),
('eQ1', 16, 'EQ1'),
('Omoda 5', 16, 'OM5');

-- Geely (China)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Emgrand', 17, 'EMG'),
('Coolray', 17, 'COL'),
('Binrui', 17, 'BIN'),
('Boyue', 17, 'BOY'),
('Preface', 17, 'PRE'),
('Geometry A', 17, 'GEA'),
('Geometry C', 17, 'GEC'),
('Vision', 17, 'VIS'),
('Icon', 17, 'ICO'),
('Xingyue L', 17, 'XGL');

-- BYD (China)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('Tang', 18, 'TAN'),
('Song', 18, 'SON'),
('Han', 18, 'HAN'),
('Qin', 18, 'QIN'),
('Yuan', 18, 'YUA'),
('Seal', 18, 'SEA'),
('Dolphin', 18, 'DOL'),
('e6', 18, 'E6'),
('Atto 3', 18, 'AT3'),
('Blade EV', 18, 'BLD');

-- BMW (Germany)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('1 Series', 19, '1SR'),
('3 Series', 19, '3SR'),
('5 Series', 19, '5SR'),
('7 Series', 19, '7SR'),
('X1', 19, 'X1'),
('X3', 19, 'X3'),
('X5', 19, 'X5'),
('X7', 19, 'X7'),
('i4', 19, 'I4'),
('M4', 19, 'M4');

-- Mercedes-Benz (Germany)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('A-Class', 20, 'ACL'),
('C-Class', 20, 'CCL'),
('E-Class', 20, 'ECL'),
('S-Class', 20, 'SCL'),
('GLA', 20, 'GLA'),
('GLC', 20, 'GLC'),
('GLE', 20, 'GLE'),
('GLS', 20, 'GLS'),
('AMG GT', 20, 'AMG'),
('EQC', 20, 'EQC');

-- Audi (Germany)
INSERT INTO "CarPlace".models (name, brand_id, vds) VALUES
('A3', 21, 'A3'),
('A4', 21, 'A4'),
('A6', 21, 'A6'),
('A8', 21, 'A8'),
('Q3', 21, 'Q3'),
('Q5', 21, 'Q5'),
('Q7', 21, 'Q7'),
('Q8', 21, 'Q8'),
('TT', 21, 'TT'),
('R8', 21, 'R8');



INSERT INTO "CarPlace".categories (id, name) VALUES
(1, 'Sedan'),
(2, 'Hatchback'),
(3, 'SUV'),
(4, 'Crossover'),
(5, 'Coupe'),
(6, 'Convertible'),
(7, 'Pickup Truck'),
(8, 'Van / Minivan'),
(9, 'Station Wagon'),
(10, 'Sports Car'),
(11, 'Luxury'),
(12, 'Electric Vehicle'),
(13, 'Hybrid'),
(14, 'Diesel'),
(15, 'Compact'),
(16, 'Mid-size'),
(17, 'Full-size'),
(18, 'Off-road'),
(19, 'Commercial Vehicle'),
(20, 'Microcar');


INSERT INTO "CarPlace".features (id, name) VALUES
(1, 'ABS'),
(2, 'Airbags'),
(3, 'Cruise Control'),
(4, 'Adaptive Cruise Control'),
(5, 'Lane Assist'),
(6, 'Blind Spot Monitoring'),
(7, 'Apple CarPlay'),
(8, 'Android Auto'),
(9, 'Heated Seats'),
(10, 'Ventilated Seats'),
(11, 'Sunroof'),
(12, 'Panoramic Roof'),
(13, 'Navigation System'),
(14, 'Keyless Entry'),
(15, 'Push Button Start'),
(16, 'Rearview Camera'),
(17, 'Parking Sensors'),
(18, 'Wireless Charging'),
(19, 'Automatic Emergency Braking'),
(20, 'LED Headlights'),
(21, 'Fog Lights'),
(22, 'Climate Control'),
(23, 'Leather Seats'),
(24, 'Power Windows'),
(25, 'Electric Mirrors'),
(26, 'Alloy Wheels'),
(27, 'Four-Wheel Drive'),
(28, 'Traction Control'),
(29, 'Stability Control'),
(30, 'Heads-Up Display');
