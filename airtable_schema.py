# The Airtable Schema App - By CC
# Last modified - 2023-04-01
# hirechriscameron@gmail.com

import requests
import json
import csv
import os
import sys
import subprocess
from collections import OrderedDict
from urllib.parse import quote

API_KEY = "patRMIH4j5OF5CF0p.299892fc7538defe3fcda40f629bf1e531d39e9174b5f63330276d3e638ffb72"

def list_bases():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get("https://api.airtable.com/v0/meta/bases", headers=headers)
    response.raise_for_status()
    return response.json()["bases"]

def print_base_menu(bases):
    print("Select a base to generate a schema for:")
    for index, base in enumerate(bases, start=1):
        print(f"{index}. {base['name']}")

def get_records(base_id, table_name):
    url = f"https://api.airtable.com/v0/{base_id}/{quote(table_name)}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"maxRecords": 100, "view": "Grid view"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["records"]

def get_tables(base_id, include_records=False):
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    tables = response.json()["tables"]

    if include_records:
        for table in tables:
            table["records"] = get_records(base_id, table["name"])
    return tables

def open_directory(path):
    if sys.platform == 'win32':
        subprocess.Popen(['explorer', path])
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', path])
    else:
        subprocess.Popen(['xdg-open', path])

def output_json(base_name, tables):
    output_file = f"airtable_base_schema_{base_name}.json"
    with open(output_file, "w") as outfile:
        json.dump(tables, outfile, indent=2)
    return output_file

def output_csv(base_name, tables):
    output_file = f"airtable_base_schema_{base_name}.csv"
    with open(output_file, "w", newline='', encoding='utf-8') as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(["Table", "Field ID", "Field Name", "Field Type", "Field Options", "Records"])
        for table in tables:
            for field in table["fields"]:
                records = json.dumps(table["records"], ensure_ascii=False) if "records" in table else ""
                csv_writer.writerow([
                    table["name"],
                    field["id"],
                    field["name"],
                    field["type"],
                    json.dumps(field.get("options", ""), ensure_ascii=False),
                    records
                ])
    return output_file

def output_compact(base_name, tables):
    output_file = f"airtable_base_schema_{base_name}_compact.txt"
    with open(output_file, "w", encoding='utf-8') as outfile:
        for table in tables:
            for field in table["fields"]:
                outfile.write(f"{table['name']}.{field['name']}({field['type']})\n")
            if "records" in table:
                outfile.write(f"Records for {table['name']}:\n")
                for record in table["records"]:
                    compact_record = []
                    for field, value in record["fields"].items():
                        compact_record.append(f"{field}: {value}")
                    outfile.write(", ".join(compact_record) + "\n")
                outfile.write("\n")
    return output_file

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("Include records in the output?")
    print("1. Yes")
    print("2. No")

    while True:
        try:
            records_choice = int(input("Enter the number corresponding to your choice: "))
            if 1 <= records_choice <= 2:
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    include_records = records_choice == 1

    clear_screen()
    print("Select a base:")
    bases = list_bases()
    for idx, base in enumerate(bases, start=1):
        print(f"{idx}. {base['name']}")

    while True:
        try:
            base_choice = int(input("Enter the number corresponding to your desired base: "))
            if 1 <= base_choice <= len(bases):
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    selected_base = bases[base_choice - 1]

    tables = get_tables(selected_base['id'], include_records=include_records)

    base_name = selected_base['name']

    clear_screen()
    print("\nSelect an option:")
    print("1. Whole base schema")
    print("2. Single table schema")

    while True:
        try:
            option_choice = int(input("Enter the number corresponding to your desired option: "))
            if 1 <= option_choice <= 2:
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    if option_choice == 2:
        clear_screen()
        print("\nSelect a table:")
        for idx, table in enumerate(tables, start=1):
            print(f"{idx}. {table['name']}")

        while True:
            try:
                table_choice = int(input("Enter the number corresponding to your desired table: "))
                if 1 <= table_choice <= len(tables):
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        tables = [tables[table_choice - 1]]

    clear_screen()
    print("\nChoose output format:")
    print("1. CSV")
    print("2. JSON")
    print("3. Compact")

    while True:
        try:
            choice = int(input("Enter the number corresponding to your desired format: "))
            if 1 <= choice <= 3:
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    if choice == 1:
        output_file = output_csv(base_name, tables)
    elif choice == 2:
        output_file = output_json(base_name, tables)
    else:
        output_file = output_compact(base_name, tables)

    print(f"Schema for the selected base or table has been generated and saved as {output_file}.")

    clear_screen()
    print("What would you like to do now?")
    print("1. Open the folder containing the generated file")
    print("2. Exit the application")

    while True:
        try:
            final_choice = int(input("Enter the number corresponding to your choice: "))
            if 1 <= final_choice <= 2:
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    if final_choice == 1:
        open_directory(os.getcwd())
    else:
        print("Exiting the application. Goodbye!")

if __name__ == "__main__":
    main()

