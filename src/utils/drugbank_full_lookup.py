import json
import os

# Point to the JSON you generated from parse_drugbank_xml.py
DRUGBANK_JSON = os.path.join("backend", "drugbank_data", "drugbank_slim.json")

cid_to_entry = {}

def load_full_drugbank():
    global cid_to_entry
    if not os.path.exists(DRUGBANK_JSON):
        print(f"[DrugBank Full] File not found: {DRUGBANK_JSON}")
        return

    with open(DRUGBANK_JSON, "r") as f:
        data = json.load(f)
        cid_to_entry = {entry["pubchem"]: entry for entry in data if entry.get("pubchem")}

    print(f"[DrugBank Full] Loaded {len(cid_to_entry)} entries.")

def lookup_full_drug_info(cid: str):
    return cid_to_entry.get(str(cid))

# Load immediately
load_full_drugbank()
