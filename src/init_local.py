from src.db import insert_to_db
from src.transform import rune_pricing, rune_calculations
from src.generators import create_rune_mapping

def main():
    create_rune_mapping.main()
    insert_to_db.main()
    rune_calculations.main()
    rune_pricing.main()