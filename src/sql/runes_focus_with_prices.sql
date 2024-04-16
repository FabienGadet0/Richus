SELECT  silver_runes_pdb_focus.*,
bronze_runes_mapping.*,
silver_hdv_prices."Lot [1]", silver_hdv_prices.Actualisation,
silver_hdv_prices.name
FROM silver_runes_pdb_focus
INNER JOIN bronze_runes_mapping ON silver_runes_pdb_focus.rune_stat_name = bronze_runes_mapping.stat_name
INNER JOIN silver_hdv_prices ON silver_hdv_prices."nom de l'objet" = bronze_runes_mapping.name and silver_hdv_prices.type = "Rune de forgemagie"
