import requests
import functools

@functools.lru_cache(maxsize=1024)
def resolve_pubchem_cid(cid_str):
    """Resolve CID (e.g., 'CID000000432') to compound name using PubChem REST API"""
    try:
        cid = int(cid_str.replace("CID", ""))
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title/JSON"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()["PropertyTable"]["Properties"][0]["Title"]
    except Exception as e:
        return cid_str

@functools.lru_cache(maxsize=1024)
def resolve_umls_cui(cui):
    """Placeholder for UMLS/MeSH API or local mapping"""
    # TODO: Implement real lookup using UMLS API or offline file
    return cui  # fallback for now
