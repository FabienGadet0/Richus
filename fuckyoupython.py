from dagster._core.definitions.schedule_definition import DefaultScheduleStatus
from src.generators.runOnce import (
    generate_item_ids_mapping as generate_item_ids_mapping_func,
    generate_runes as generate_runes_func,
)
from src.generators import (
    generate_brisage_coeff as generate_brisage_coeff_func,
    generate_hdv_prices as generate_hdv_prices_func,
    create_rune_mapping as create_rune_mapping_func,
)
from src.db import insert_to_db as insert_to_db_func
from src.transform import (
    rune_calculations as rune_calculations_func,
    rune_pricing as rune_pricing_func,
    rune_price_brisage_together as rune_price_brisage_together_func,
)
from src import init_local
from dagster import (
    asset,
    define_asset_job,
    Definitions,
    ScheduleDefinition,
    AssetSelection,
)


@asset(group_name="initialisation")
def generate_item_ids_mapping():
    generate_item_ids_mapping_func.main()


@asset(group_name="daily_update")
def generate_brisage_coeff():
    generate_brisage_coeff_func.initial_dump()


@asset(group_name="daily_update")
def generate_hdv_prices():
    generate_hdv_prices_func.main()


@asset(group_name="initialisation", deps=[generate_hdv_prices])
def generate_runes():
    generate_runes_func.main()


@asset(group_name="daily_update")
def create_runes_mapping():
    create_rune_mapping_func.main()


@asset(group_name="daily_update", deps=[generate_hdv_prices])
def insert_to_db():
    insert_to_db_func.main()


@asset(group_name="daily_update", deps=[generate_hdv_prices, insert_to_db])
def rune_calculations():
    rune_calculations_func.main()


@asset(group_name="daily_update", deps=[create_runes_mapping, rune_calculations])
def rune_pricing():
    rune_pricing_func.main()


@asset(group_name="daily_update", deps=[rune_pricing])
def rune_price_brisage_together():
    rune_price_brisage_together_func.main()


selection = [
    generate_item_ids_mapping,
    generate_runes,
    generate_brisage_coeff,
    generate_hdv_prices,
    insert_to_db,
    rune_calculations,
    create_runes_mapping,
    rune_pricing,
    rune_price_brisage_together,
]

main_job = define_asset_job(name="main", selection=selection)
daily_job = define_asset_job("asset_job", AssetSelection.groups("daily_update"))
daily_schedule = ScheduleDefinition(
    job=daily_job,
    # cron_schedule="0 15 * * *",
    cron_schedule="0 0 * * *",
    default_status=DefaultScheduleStatus.RUNNING,
)

defs = Definitions(
    schedules=[daily_schedule], assets=selection, jobs=[main_job, daily_job]
)
