SELECT
silver_runes_pdb_focus.item_id,
silver_hdv_prices.name,
silver_runes_pdb_focus.rune_weight,
silver_runes_pdb_focus.jet,
silver_runes_pdb_focus.coefficient,
silver_runes_pdb_focus.pdb,
silver_hdv_prices.last_updated_fr,
silver_hdv_prices."Actualisation",
CAST(silver_hdv_prices."Lot [1]" AS INT) as price,
silver_runes_pdb_focus.runes_qty as runes_qty,
silver_runes_pdb_focus.focus_runes_qty as focus_runes_qty,
CAST(silver_hdv_prices."Lot [1]" AS INT) * silver_runes_pdb_focus.runes_qty AS profitability,
CAST(silver_hdv_prices."Lot [1]" AS INT) * silver_runes_pdb_focus.focus_runes_qty AS focus_profitability
FROM silver_runes_pdb_focus
INNER JOIN bronze_runes_mapping ON silver_runes_pdb_focus.rune_stat_name = bronze_runes_mapping.stat_name
INNER JOIN silver_hdv_prices ON silver_hdv_prices.nom_de_lobjet = bronze_runes_mapping.name
AND silver_hdv_prices.last_updated_fr = (SELECT MAX(last_updated_fr) FROM silver_hdv_prices WHERE nom_de_lobjet = bronze_runes_mapping.name)
