with max_focus as (
select item_id,
name,
focus_profitability,
row_number() over (partition by item_id order by focus_profitability desc) as r
from public.gold_item_rune_price g
),
latest_rune_update as (
select item_id,max(rune_last_update) as last_rune_update
from public.gold_item_rune_price
group by 1
),
latest_hdv_update as (
select item_id, max(last_updated_fr) as last_hdv_update
from silver_hdv_prices
group by item_id
)

select
g.item_id,
b.name as nom_objet,
b.type as objet_type,
b.level as objet_level,
m.name as focus_rune_nom,
g.coefficient,
s."Lot [1]" as prix,
s."Craft" as craft,
lr.last_rune_update as rune_last_update,
lh.last_hdv_update as hdv_last_update,
m.focus_profitability as focus_rentabilite,
sum(profitability) as total_profit_non_focus
from public.gold_item_rune_price g
inner join latest_rune_update lr on lr.item_id = g.item_id and g.rune_last_update = lr.last_rune_update
left join max_focus as m on m.item_id = g.item_id and m.r = 1
left join silver_hdv_prices as s on s.item_id = g.item_id
inner join latest_hdv_update lh on lh.item_id = s.item_id and s.last_updated_fr = lh.last_hdv_update
inner join bronze_items as b on b.item_id = g.item_id
group by 1,2,3,4,5,6,7,8,9,10,11
