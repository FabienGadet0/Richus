with max_focus as (
select item_id,
name,
focus_profitability,
coefficient,
rank() over (partition by item_id order by focus_profitability desc) as r
from public.gold_item_rune_price g
)

select
g.item_id,
b.name as nom_objet,
b.type as objet_type,
b.level as objet_level,
m.name as focus_rune_nom,
m.coefficient,
s."Lot [1]" as prix,
s."Craft" as craft,
g.rune_last_update,
s.last_updated_fr as hdv_last_update,
m.focus_profitability as focus_rentabilite,
sum(profitability) as total_profit_non_focus
from public.gold_item_rune_price g
left join max_focus as m on m.item_id = g.item_id and m.r = 1
left join silver_hdv_prices as s on s.item_id = g.item_id AND s.last_updated_fr = (SELECT MAX(last_updated_fr) FROM silver_hdv_prices as e WHERE e.item_id = g.item_id)
inner join bronze_items as b on b.item_id = g.item_id
group by 1,2,3,4,5,6,7,8,9,10,11
