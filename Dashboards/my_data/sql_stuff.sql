-- Listing des modifications faites sur la base de données
-- POC requête pour afficher les fréquences 17/07/2024
SELECT 
    o.id AS id_site, 
    ls.name AS main_lichenspecies, 
    COUNT(l.id) AS frequency 
FROM 
    main_observation o 
    JOIN main_tree t ON o.id = t.observation_id 
    JOIN main_lichen l ON o.id = l.observation_id 
    JOIN main_lichenspecies ls ON l.species_id = ls.id 

GROUP BY 
    o.id, ls.name 

ORDER BY o.id, frequency DESC;

-- Pour la commandline PSQL
SELECT o.id AS id_site, ls.name AS main_lichenspecies, COUNT(l.id) AS frequency FROM main_observation o JOIN main_tree t ON o.id = t.observation_id JOIN main_lichen l ON o.id = l.observation_id JOIN main_lichenspecies ls ON l.species_id = ls.id GROUP BY o.id, ls.name ORDER BY o.id, frequency DESC;

-- Créer une table view récupérable dans le modèle intégrée dans la base de données le 17/07/2024
CREATE VIEW lichen_frequency AS
SELECT 
    o.id AS id_site, 
    ls.name AS main_lichenspecies, 
    COUNT(l.id) AS frequency 
FROM 
    main_observation o 
    JOIN main_tree t ON o.id = t.observation_id 
    JOIN main_lichen l ON o.id = l.observation_id 
    JOIN main_lichenspecies ls ON l.species_id = ls.id 
GROUP BY 
    o.id, ls.name 
ORDER BY 
    o.id, frequency DESC;


-- Update SQL command
CREATE VIEW lichen_frequency AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY o.id, ls.name) AS id,
    o.id AS id_site, 
    ls.name AS main_lichenspecies, 
    COUNT(l.id) AS frequency 
FROM 
    main_observation o 
    JOIN main_tree t ON o.id = t.observation_id 
    JOIN main_lichen l ON o.id = l.observation_id 
    JOIN main_lichenspecies ls ON l.species_id = ls.id 
GROUP BY 
    o.id, ls.name 
ORDER BY 
    o.id, frequency DESC;

CREATE VIEW lichen_frequency AS SELECT ROW_NUMBER() OVER (ORDER BY o.id, ls.name) AS id, o.id AS id_site, ls.name AS main_lichenspecies, COUNT(l.id) AS frequency FROM main_observation o JOIN main_tree t ON o.id = t.observation_id JOIN main_lichen l ON o.id = l.observation_id JOIN main_lichenspecies ls ON l.species_id = ls.id GROUP BY o.id, ls.name ORDER BY o.id, frequency DESC;

-- Update post ajustement avec Hugo 7/8/24
SELECT 
    ta.id AS id_ta,
    o.id AS id_site,
    ls.name AS lichen,
    le."pH" AS pH, 
    -- Addition des longueurs des tableaux pour chaque ligne
    COALESCE(array_length(ta.sq1, 1), 0) +
    COALESCE(array_length(ta.sq2, 1), 0) +
    COALESCE(array_length(ta.sq3, 1), 0) +
    COALESCE(array_length(ta.sq4, 1), 0) +
    COALESCE(array_length(ta.sq5, 1), 0) AS freq,
    -- Afficher les donnée écologiques 
    le.eutrophication AS eutrophication,
    le.poleotolerance AS poleotolerance
FROM
    main_observation o 
    JOIN main_tree t ON o.id = t.observation_id 
    JOIN main_lichen l ON o.id = l.observation_id
    JOIN main_lichenspecies ls ON l.species_id = ls.id
    JOIN main_table ta ON ta.tree_id = t.id
    JOIN lichen_ecology le ON ls.name = le.cleaned_taxon
ORDER BY 
    freq DESC;

-- Creation de la vue pour lichenfrequency
CREATE VIEW lichen_frequency AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY o.id, ls.name) AS id,
    o.id AS id_site,
    ls.name AS lichen,
    le."pH" AS pH, 
    -- Addition des longueurs des tableaux pour chaque ligne
    COALESCE(array_length(ta.sq1, 1), 0) +
    COALESCE(array_length(ta.sq2, 1), 0) +
    COALESCE(array_length(ta.sq3, 1), 0) +
    COALESCE(array_length(ta.sq4, 1), 0) +
    COALESCE(array_length(ta.sq5, 1), 0) AS freq,
    -- Afficher les donnée écologiques 
    le.eutrophication AS eutrophication,
    le.poleotolerance AS poleotolerance
FROM
    main_observation o 
    JOIN main_tree t ON o.id = t.observation_id 
    JOIN main_lichen l ON o.id = l.observation_id
    JOIN main_lichenspecies ls ON l.species_id = ls.id
    JOIN main_table ta ON ta.tree_id = t.id
    JOIN lichen_ecology le ON ls.name = le.cleaned_taxon;

-- PSQL commandline
CREATE VIEW lichen_frequency AS SELECT ROW_NUMBER() OVER (ORDER BY o.id, ls.name) AS id, o.id AS id_site, ls.name AS lichen, le."pH" AS pH, COALESCE(array_length(ta.sq1, 1), 0) + COALESCE(array_length(ta.sq2, 1), 0) + COALESCE(array_length(ta.sq3, 1), 0) + COALESCE(array_length(ta.sq4, 1), 0) + COALESCE(array_length(ta.sq5, 1), 0) AS freq, le.eutrophication AS eutrophication, le.poleotolerance AS poleotolerance FROM main_observation o  JOIN main_tree t ON o.id = t.observation_id JOIN main_lichen l ON o.id = l.observation_id JOIN main_lichenspecies ls ON l.species_id = ls.id JOIN main_table ta ON ta.tree_id = t.id JOIN lichen_ecology le ON ls.name = le.cleaned_taxon;

-- Nettoyage de données
SELECT 
    id, 
    taxon AS original_taxon, 
    REPLACE(REPLACE(taxon, ' / ', '/'), ' /', '/') AS cleaned_taxon
FROM 
    lichen_ecology
WHERE 
    taxon LIKE '% / %' OR taxon LIKE '% /';

SELECT id, taxon AS original_taxon, REPLACE(REPLACE(taxon, ' / ', '/'), ' /', '/') AS cleaned_taxon FROM lichen_ecology;

-- ajout column
ALTER TABLE lichen_ecology ADD COLUMN cleaned_taxon VARCHAR(255); 

-- UPDATE
UPDATE lichen_ecology SET cleaned_taxon = REPLACE(REPLACE(taxon, ' / ', '/'), ' /', '/');
ALTER TABLE lichen_ecology DROP COLUMN cleaned_taxon;
