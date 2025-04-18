from src.utils.sage_loader import load_sage_and_homograph
from src.explain.explain_pg import run_pgexplainer

model, graph = load_sage_and_homograph()
result = run_pgexplainer(model, graph, drug1_id=25, drug2_id=88)
print(result)
