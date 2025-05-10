# src/utils/drugbank_lookup.py

import os
import pandas as pd

DRUGBANK_CSV = os.path.join("backend", "drugbank_data", "drugbank_all_drug_links.csv")

cid_to_drugbank = {}
drugbank_to_cid = {}

def load_drugbank_links():
    global cid_to_drugbank, drugbank_to_cid
    if not os.path.exists(DRUGBANK_CSV):
        print(f"[DrugBank] File not found: {DRUGBANK_CSV}")
        return

    df = pd.read_csv(DRUGBANK_CSV)
    df = df.dropna(subset=["PubChem Compound ID"])

    cid_to_drugbank = {
        str(int(row["PubChem Compound ID"])): {
            "drugbank_id": row["DrugBank ID"],
            "name": row["Name"],
            "cas": row["CAS Number"],
            "type": row["Drug Type"]
        }
        for _, row in df.iterrows()
    }

    drugbank_to_cid = {
        row["DrugBank ID"]: str(int(row["PubChem Compound ID"]))
        for _, row in df.iterrows()
    }

    print(f"[DrugBank] Loaded {len(cid_to_drugbank)} entries")

def lookup_drug_by_cid(cid: str):
    return cid_to_drugbank.get(str(cid), None)

# Load on import
load_drugbank_links()
