import xml.etree.ElementTree as ET
import json
import sys

def parse_drugbank_xml(xml_path, output_json="backend/drugbank_data/drugbank_slim.json"):
    ns = {'db': 'http://www.drugbank.ca'}
    tree = ET.parse(xml_path)
    root = tree.getroot()

    drug_data = []

    for drug in root.findall('db:drug', ns):
        entry = {
            "drugbank_id": drug.findtext('db:drugbank-id[@primary="true"]', default="", namespaces=ns),
            "name": drug.findtext('db:name', default="", namespaces=ns),
            "cas": drug.findtext('db:cas-number', default="", namespaces=ns),
            "description": drug.findtext('db:description', default="", namespaces=ns),
            "type": drug.get('type', ""),
            "pubchem": None,
            "targets": [],
            "interactions": []
        }

        # PubChem
        for ext in drug.findall('db:external-identifiers/db:external-identifier', ns):
            if ext.findtext('db:resource', namespaces=ns) == "PubChem Compound":
                entry["pubchem"] = ext.findtext('db:identifier', namespaces=ns)
                break

        # Targets
        for t in drug.findall('db:targets/db:target', ns):
            name = t.findtext('db:name', default="", namespaces=ns)
            organism = t.findtext('db:organism', default="", namespaces=ns)
            if name:
                entry["targets"].append(f"{name} ({organism})")

        # Interactions
        for i in drug.findall('db:drug-interactions/db:drug-interaction', ns):
            inter_name = i.findtext('db:name', default="", namespaces=ns)
            inter_desc = i.findtext('db:description', default="", namespaces=ns)
            if inter_name:
                entry["interactions"].append({
                    "name": inter_name,
                    "description": inter_desc
                })

        drug_data.append(entry)

    with open(output_json, "w") as f:
        json.dump(drug_data, f, indent=2)

    print(f"✅ Saved {len(drug_data)} drug entries to {output_json}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_drugbank_xml.py <path-to-xml>")
    else:
        parse_drugbank_xml(sys.argv[1])
