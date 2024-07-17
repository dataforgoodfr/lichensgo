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

-- Pour la commandline PSQL
CREATE VIEW lichen_frequency AS SELECT o.id AS id_site, ls.name AS main_lichenspecies, COUNT(l.id) AS frequency FROM main_observation o JOIN main_tree t ON o.id = t.observation_id JOIN main_lichen l ON o.id = l.observation_id JOIN main_lichenspecies ls ON l.species_id = ls.id GROUP BY o.id, ls.name ORDER BY o.id, frequency DESC;
