from src.generators.runOnce import generate_item_ids_mapping as generate_item_ids_mapping_func, generate_runes as generate_runes_func
from src.generators import generate_brisage_coeff as generate_brisage_coeff_func, generate_hdv_prices as generate_hdv_prices_func, create_rune_mapping as create_rune_mapping_func
from src.db import insert_to_db as insert_to_db_func
from src.transform import rune_calculations as rune_calculations_func, rune_pricing as rune_pricing_func
from dagster import *

@asset
def generate_item_ids_mapping():
    generate_item_ids_mapping_func.main()

@asset
def generate_brisage_coeff():
    generate_brisage_coeff_func.initial_dump()

@asset(deps=[generate_brisage_coeff])
def generate_hdv_prices():
    generate_hdv_prices_func.main()

@asset(deps=[generate_item_ids_mapping,generate_hdv_prices])
def generate_runes():
    generate_runes_func.main()

@asset
def create_runes_mapping():
    create_rune_mapping_func.main()


@asset(deps=[generate_brisage_coeff,generate_hdv_prices])
def insert_to_db():
    insert_to_db_func.main()

@asset(deps=[generate_brisage_coeff,generate_hdv_prices,insert_to_db])
def rune_calculations():
    rune_calculations_func.main()

@asset(deps=[create_runes_mapping,rune_calculations])
def rune_pricing():
    rune_pricing_func.main()

selection=[
    generate_item_ids_mapping,
    generate_runes,
    generate_brisage_coeff,
    generate_hdv_prices,
    insert_to_db,
    rune_calculations,
    create_runes_mapping,
    rune_pricing
            ]
defs = Definitions(assets=selection,jobs = [define_asset_job(name="main",selection=selection)])
