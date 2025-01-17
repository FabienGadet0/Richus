DROP TABLE IF EXISTS bronze_runes_mapping;
CREATE TABLE bronze_runes_mapping (
    stat_name VARCHAR(50),
    name VARCHAR(50)
);

INSERT INTO bronze_runes_mapping (stat_name, name) VALUES
('% Critique', 'Rune Cri'),
('Vitalité','Rune Vi'),
('Intelligence', 'Rune Ine'),
('Agilité', 'Rune Age'),
('Dommages Air', 'Rune Do Air'),
('Tacle', 'Rune Tac'),
('Force', 'Rune Fo'),
('Initiative','Rune Ini'),
('Pods','Rune Pod'),
('Fuite', 'Rune Fui'),
('Chance', 'Rune Cha'),
('PM', 'Rune Ga Pme'),
('Prospection', 'Rune Prospe'),
('Soins', 'Rune So'),
('Dommages Terre', 'Rune Do Terre'),
('Sagesse', 'Rune Sa'),
('Dommages Neutre', 'Rune Do Neutre'),
('PA', 'Rune Ga Pa'),
('Portée', 'Rune Po'),
('Dommages Eau', 'Rune Do Eau'),
('Dommages Feu', 'Rune Do Feu'),
('Dommages', 'Rune Do'),
('Invocations', 'Rune Invo'),
('Dommages critiques', 'Rune Do Cri'),
('Résistance Critiques', 'Rune Ré Cri'),
('Puissance', 'Rune Pui'),
('Dommages Poussée', 'Rune Do Pou'),
('% Résistance Terre', 'Rune Ré Terre'),
('Retrait PA', 'Rune Ret Pa'),
('Retrait PM', 'Rune Ret Pme'),
('% Résistance Feu', 'Rune Ré Feu'),
('% Résistance Eau', 'Rune Ré Eau'),
('% Résistance Air', 'Rune Ré Air'),
('Esquive PM', 'Rune Ré Pme'),
('Résistance Neutre', 'Rune Ré Neutre'),
('Résistance Poussée', 'Rune Ré Pou'),
('Esquive PA', 'Rune Ré Pa'),
('Renvoie  dommages', 'Rune Do Ren'),
('Puissance (pièges)', 'Rune Per Pi'),
('Dommages Pièges', 'Rune Do Pi'),
('% Résistance mêlée', 'Rune Ré Per Mé'),
('% Dommages mêlée', 'Rune Do Per Mé'),
('% Dommages d''armes', 'Rune Do Per Ar'),
('% Dommages aux sorts', 'Rune Do Per So'),
('% Dommages distance', 'Rune Do Per Di'),
('% Résistance distance', 'Rune Ré Per Di');
