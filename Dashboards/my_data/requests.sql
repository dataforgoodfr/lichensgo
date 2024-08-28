-- Base requête qui est fausse 
SELECT 
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

-- transformer la table main_table pour avoir une fréquence entre 0 et 20
SELECT 
    ta.id,
    ta.tree_id,
    COALESCE(array_length(ta.sq1, 1), 0) +
    COALESCE(array_length(ta.sq2, 1), 0) +
    COALESCE(array_length(ta.sq3, 1), 0) +
    COALESCE(array_length(ta.sq4, 1), 0) +
    COALESCE(array_length(ta.sq5, 1), 0) AS freq
FROM 
    main_table ta
ORDER BY
    freq DESC;

-- Debugger le count 
SELECT * 
FROM main_table
WHERE id = 17149;