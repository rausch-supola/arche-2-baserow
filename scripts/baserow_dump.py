from config import (
    br_client,
    BASEROW_DB_ID,
    MAPPING_PROJECT,
    MAPPING_PERSONS,
    MAPPING_ORGS,
    MAPPING_PLACES,
)
from utils.denormalize import denormalize_json


if isinstance(BASEROW_DB_ID, str) or isinstance(BASEROW_DB_ID, int) and BASEROW_DB_ID != 0:
    print("Downloading data from Baserow...")
    files = br_client.dump_tables_as_json(BASEROW_DB_ID, folder_name="json_dumps", indent=2)
    print("Data downloaded.")

    print("Denormalizing data...")
    denormalize_json("Project", "json_dumps", MAPPING_PROJECT)
    denormalize_json("Persons", "json_dumps", MAPPING_PERSONS)
    denormalize_json("Organizations", "json_dumps", MAPPING_ORGS)
    denormalize_json("Places", "json_dumps", MAPPING_PLACES)
    print("Data denormalized.")
