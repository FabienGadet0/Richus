with max_focus as (
select item_id,
name,
focus_profitability,
rank() over (partition by item_id order by focus_profitability desc) as r
from public.gold_item_rune_price g
)

select
g.item_id,
b.name as nom_objet,
m.name as focus_rune_nom,
s."Lot [1]" as prix,
s."Craft" as craft,
g.rune_last_update,
m.focus_profitability as focus_rentabilite,
sum(profitability) as total_profit_non_focus
from public.gold_item_rune_price g
left join max_focus as m on m.item_id = g.item_id and m.r = 1
left join silver_hdv_prices as s on s.item_id = g.item_id
inner join bronze_items as b on b.item_id = g.item_id
group by 1,2,3,4,5,6,7
