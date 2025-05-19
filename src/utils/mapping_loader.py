import os
import gzip
import csv

def load_entity_mappings(mapping_dir):
    entity_mappings = {}

    for file in os.listdir(mapping_dir):
        if not file.endswith(".csv.gz") or "entidx2name" not in file:
            continue

        entity_type = file.split("_")[0]  
        entity_mappings[entity_type] = {}

        with gzip.open(os.path.join(mapping_dir, file), 'rt') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) < 2:
                    continue
                idx, name = int(row[0]), row[1]
                entity_mappings[entity_type][idx] = name

    return entity_mappings
