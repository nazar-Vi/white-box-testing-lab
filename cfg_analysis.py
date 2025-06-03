import ast
import networkx as nx

def build_cfg_from_file(filename="auth.py"):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    tree = ast.parse(code)
    func = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "authenticate_user":
            func = node
            break

    if func is None:
        raise ValueError("Функція authenticate_user не знайдена")

    G = nx.DiGraph()
    prev = []
    counter = 0

    for stmt in func.body:
        label = ast.unparse(stmt)
        node = f"n{counter}"
        G.add_node(node, label=label)
        for p in prev:
            G.add_edge(p, node)
        prev = [node]
        counter += 1

    return G


def calculate_cyclomatic_complexity(G):
    """
    M = E - N + 2
    """
    return G.number_of_edges() - G.number_of_nodes() + 2


def find_paths(G):
    start = "n0"
    end_nodes = [n for n in G.nodes() if G.out_degree(n) == 0]
    all_paths = []
    for end in end_nodes:
        try:
            paths = list(nx.all_simple_paths(G, start, end))
            all_paths.extend(paths)
        except nx.NetworkXNoPath:
            continue
    return all_paths


def export_cfg_to_dot(G, path="cfg.dot"):
    nx.nx_pydot.write_dot(G, path)
    return path


def analyze_cfg():
    """
    Повна процедура: побудова графа, підрахунок складності та шляхів
    """
    G = build_cfg_from_file()
    complexity = calculate_cyclomatic_complexity(G)
    paths = find_paths(G)
    return {
        "graph": G,
        "complexity": complexity,
        "paths": paths,
        "paths_count": len(paths),
    }

def print_cyclomatic_complexity():
    G = build_cfg_from_file()
    M = calculate_cyclomatic_complexity(G)
    print("Цикломатична складність:", M)



