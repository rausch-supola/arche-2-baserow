import requests
from config import (BASEROW_URL, BASEROW_TOKEN)
from tqdm import tqdm


def update_table_rows(br_table_id: int, table: dict) -> None:
    """Updating a Baserow table with a dictionary of rows.
    Baserow table id and dictionary of rows are required."""
    br_rows_url = f"{BASEROW_URL}database/rows/table/{br_table_id}/"
    for x in tqdm(table, total=len(table)):
        row_id = x["id"]
        try:
            url = f"{br_rows_url}{row_id}/?user_field_names=true"
            print("Updating row... \n", url)
            r = requests.patch(
                url,
                headers={
                    "Authorization": f"Token {BASEROW_TOKEN}",
                    "Content-Type": "application/json"
                },
                json=x
            )
            if r.status_code == 200:
                print(f"Updated {row_id}")
            else:
                print(f"Error {r.status_code} with {row_id}")
                print("Row does not exist. Creating...")
                url = f"{br_rows_url}?user_field_names=true"
                print(url)
                r = requests.post(
                    url,
                    headers={
                        "Authorization": f"Token {BASEROW_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json=x
                )
                if r.status_code == 200:
                    print(f"Created {row_id}")
                else:
                    print(f"Error {r.status_code} with {row_id}")
        except Exception as e:
            print(f"{e} with {row_id}")


def update_table_rows_batch(br_table_id: int, table: dict) -> None:
    """Batch updating a Baserow table with a dictionary of rows.
    Baserow table id and dictionary of rows are required."""
    br_rows_url = f"{BASEROW_URL}database/rows/table/{br_table_id}/batch/"
    items = {
        "items": [v for v in table]
    }
    try:
        url = f"{br_rows_url}?user_field_names=true"
        print("Updating row... \n", url)
        r = requests.patch(
            url,
            headers={
                "Authorization": f"Token {BASEROW_TOKEN}",
                "Content-Type": "application/json"
            },
            json=items
        )
        if r.status_code == 200:
            print(f"Updated... Length rows: {len(table)}")
        else:
            print(f"Error {r.status_code}")
            print("Row does not exist. Creating...")
            print(url)
            r = requests.post(
                url,
                headers={
                    "Authorization": f"Token {BASEROW_TOKEN}",
                    "Content-Type": "application/json"
                },
                json=items
            )
            if r.status_code == 200:
                print("Created")
            else:
                print(f"Error {r.status_code}")
    except Exception as e:
        print(e)


def create_database_table(
    database_id: int,
    token: str,
    table_name: str,
    table_values: dict = None
) -> None:
    """Creating a new Baserow table. Baserow database id, JWT token and table name are required."""
    br_db_url = f"{BASEROW_URL}database/tables/database/{database_id}/"
    table = {
        "name": table_name
    }
    if table_values is not None:
        table["first_row_header"] = True
        table["data"] = []
        for x in table_values:
            x.pop("id")
            x.pop("order")
        table["data"].append([k for k in table_values[0].keys()])
        for x in table_values:
            table["data"].append([v for v in x.values()])
    print("Creating table... ", br_db_url)
    r = requests.post(
        br_db_url,
        headers={
            "Authorization": f"JWT {token}",
            "Content-Type": "application/json"
        },
        json=table
    )
    if r.status_code == 200:
        response = r.json()
        print("Table created... ", response["id"])
        return response
    else:
        print(f"Error {r.status_code} with {database_id}")
        return r.json()


def update_table_field_types(
    table_id: int,
    token: str,
    default_fields: dict
) -> None:
    """Upading Baserow table field types. Baserow table id, JWT token, default fields and"""
    br_table_url = f"{BASEROW_URL}database/fields/table/{table_id}/"
    for x in tqdm(default_fields, total=len(default_fields)):
        print("Updating table... ", br_table_url)
        r = requests.patch(
            br_table_url,
            headers={
                "Authorization": f"JWT {token}",
                "Content-Type": "application/json"
            },
            json=x
        )
        if r.status_code == 200:
            print(f"Updated field {x['name']} in {table_id}")
        else:
            url = f"{br_table_url}?user_field_names=true"
            print(f"Error {r.status_code} with {table_id}")
            print("Field does not exist. Creating...")
            r = requests.post(
                url,
                headers={
                    "Authorization": f"JWT {token}",
                    "Content-Type": "application/json"
                },
                json=x
            )
            if r.status_code == 200:
                print(f"Created field {x['name']} in {table_id}")
            else:
                print(f"Error {r.status_code} with {table_id}")
