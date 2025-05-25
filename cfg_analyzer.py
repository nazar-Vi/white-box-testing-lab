import ast
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

def build_cfg_for_authenticate_user():
    """
    Побудова графа потоку керування для функції authenticate_user
    """
    
    # Створення направленого графа
    G = nx.DiGraph()
    
    # Визначення вузлів (кожен вузол представляє блок коду)
    nodes = {
        'START': 'START',
        'CHECK_CREDS': 'if not username\nor not password',
        'MISSING_CREDS': 'return "Missing\ncredentials"',
        'CHECK_USER': 'if username\nnot in db',
        'USER_NOT_FOUND': 'return "User\nnot found"',
        'GET_ATTEMPTS': 'attempts = db[username]\n.get("attempts", 0)',
        'CHECK_LOCKED': 'if attempts >= 3',
        'ACCOUNT_LOCKED': 'return "Account\nlocked"',
        'CHECK_PASSWORD': 'if db[username]["password"]\n!= password',
        'INCREMENT_ATTEMPTS': 'db[username]["attempts"]\n= attempts + 1',
        'INVALID_PASSWORD': 'return "Invalid\npassword"',
        'RESET_ATTEMPTS': 'db[username]["attempts"]\n= 0',
        'AUTHENTICATED': 'return "Authenticated"'
    }
    
    # Додавання вузлів до графа
    for node_id, label in nodes.items():
        G.add_node(node_id, label=label)
    
    # Визначення ребер (переходи між блоками)
    edges = [
        ('START', 'CHECK_CREDS'),
        ('CHECK_CREDS', 'MISSING_CREDS'),      # True branch
        ('CHECK_CREDS', 'CHECK_USER'),         # False branch
        ('CHECK_USER', 'USER_NOT_FOUND'),      # True branch
        ('CHECK_USER', 'GET_ATTEMPTS'),        # False branch
        ('GET_ATTEMPTS', 'CHECK_LOCKED'),
        ('CHECK_LOCKED', 'ACCOUNT_LOCKED'),    # True branch
        ('CHECK_LOCKED', 'CHECK_PASSWORD'),    # False branch
        ('CHECK_PASSWORD', 'INCREMENT_ATTEMPTS'), # True branch
        ('INCREMENT_ATTEMPTS', 'INVALID_PASSWORD'),
        ('CHECK_PASSWORD', 'RESET_ATTEMPTS'),  # False branch
        ('RESET_ATTEMPTS', 'AUTHENTICATED')
    ]
    
    # Додавання ребер до графа
    G.add_edges_from(edges)
    
    return G, nodes

def calculate_cyclomatic_complexity(G):
    """
    Розрахунок цикломатичної складності за формулою: M = E - N + 2P
    де E - кількість ребер, N - кількість вузлів, P - кількість компонентів зв'язності
    """
    E = G.number_of_edges()  # кількість ребер
    N = G.number_of_nodes()  # кількість вузлів
    P = nx.number_weakly_connected_components(G)  # кількість компонентів зв'язності
    
    M = E - N + 2 * P
    
    print(f"Кількість вузлів (N): {N}")
    print(f"Кількість ребер (E): {E}")
    print(f"Кількість компонентів зв'язності (P): {P}")
    print(f"Цикломатична складність (M = E - N + 2P): {M}")
    
    return M

def find_all_paths(G):
    """
    Знаходження всіх шляхів від START до кінцевих вузлів
    """
    start_node = 'START'
    
    # Знаходження всіх кінцевих вузлів (вузли без вихідних ребер)
    end_nodes = [node for node in G.nodes() if G.out_degree(node) == 0]
    
    all_paths = []
    for end_node in end_nodes:
        try:
            paths = list(nx.all_simple_paths(G, start_node, end_node))
            all_paths.extend(paths)
        except nx.NetworkXNoPath:
            print(f"Немає шляху від {start_node} до {end_node}")
    
    print(f"\nЗнайдено {len(all_paths)} унікальних шляхів виконання:")
    for i, path in enumerate(all_paths, 1):
        print(f"Шлях {i}: {' -> '.join(path)}")
    
    return all_paths

def visualize_cfg(G, nodes, save_path="cfg.png"):
    """
    Візуалізація графа потоку керування
    """
    plt.figure(figsize=(16, 12))
    
    # Створення ієрархічного розташування
    pos = {}
    
    # Визначення рівнів для кращого відображення
    levels = {
        'START': (0, 6),
        'CHECK_CREDS': (0, 5),
        'MISSING_CREDS': (-2, 4),
        'CHECK_USER': (0, 4),
        'USER_NOT_FOUND': (-2, 3),
        'GET_ATTEMPTS': (0, 3),
        'CHECK_LOCKED': (0, 2),
        'ACCOUNT_LOCKED': (-2, 1),
        'CHECK_PASSWORD': (0, 1),
        'INCREMENT_ATTEMPTS': (2, 0.5),
        'INVALID_PASSWORD': (2, 0),
        'RESET_ATTEMPTS': (-2, 0.5),
        'AUTHENTICATED': (-2, 0)
    }
    
    pos = levels
    
    # Налаштування кольорів для різних типів вузлів
    node_colors = {
        'START': 'lightgreen',
        'CHECK_CREDS': 'lightblue',
        'CHECK_USER': 'lightblue', 
        'CHECK_LOCKED': 'lightblue',
        'CHECK_PASSWORD': 'lightblue',
        'GET_ATTEMPTS': 'lightyellow',
        'INCREMENT_ATTEMPTS': 'lightyellow',
        'RESET_ATTEMPTS': 'lightyellow',
        'MISSING_CREDS': 'lightcoral',
        'USER_NOT_FOUND': 'lightcoral',
        'ACCOUNT_LOCKED': 'lightcoral',
        'INVALID_PASSWORD': 'lightcoral',
        'AUTHENTICATED': 'lightgreen'
    }
    
    # Створення списку кольорів у правильному порядку
    colors = [node_colors.get(node, 'lightgray') for node in G.nodes()]
    
    # Малювання вузлів
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=2000, alpha=0.8)
    
    # Малювання ребер
    nx.draw_networkx_edges(G, pos, edge_color='black', arrows=True, 
                          arrowsize=20, arrowstyle='->', width=1.5)
    
    # Додавання підписів до вузлів
    labels = {node: nodes[node] for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
    
    # Додавання підписів до ребер (True/False для умовних переходів)
    edge_labels = {
        ('CHECK_CREDS', 'MISSING_CREDS'): 'True',
        ('CHECK_CREDS', 'CHECK_USER'): 'False',
        ('CHECK_USER', 'USER_NOT_FOUND'): 'True',
        ('CHECK_USER', 'GET_ATTEMPTS'): 'False',
        ('CHECK_LOCKED', 'ACCOUNT_LOCKED'): 'True',
        ('CHECK_LOCKED', 'CHECK_PASSWORD'): 'False',
        ('CHECK_PASSWORD', 'INCREMENT_ATTEMPTS'): 'True',
        ('CHECK_PASSWORD', 'RESET_ATTEMPTS'): 'False'
    }
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=7)
    
    plt.title("Control Flow Graph для функції authenticate_user", fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    print(f"CFG збережено як {save_path}")

def analyze_def_use_pairs():
    """
    Аналіз пар def-use для змінних у функції authenticate_user
    """
    print("\nАналіз пар def-use:")
    print("=" * 50)
    
    def_use_pairs = {
        'username': {
            'def': ['параметр функції'],
            'use': ['CHECK_CREDS', 'CHECK_USER']
        },
        'password': {
            'def': ['параметр функції'],
            'use': ['CHECK_CREDS', 'CHECK_PASSWORD']
        },
        'db': {
            'def': ['параметр функції'],
            'use': ['CHECK_USER', 'GET_ATTEMPTS', 'CHECK_PASSWORD', 'INCREMENT_ATTEMPTS', 'RESET_ATTEMPTS']
        },
        'attempts': {
            'def': ['GET_ATTEMPTS'],
            'use': ['CHECK_LOCKED', 'INCREMENT_ATTEMPTS']
        }
    }
    
    for var, info in def_use_pairs.items():
        print(f"\nЗмінна '{var}':")
        print(f"  Визначення (def): {', '.join(info['def'])}")
        print(f"  Використання (use): {', '.join(info['use'])}")

def generate_test_coverage_matrix():
    """
    Генерація матриці покриття тестів
    """
    print("\nМатриця покриття тестів:")
    print("=" * 80)
    
    # Визначення тестів та їх покриття
    test_coverage = {
        'test_missing_credentials': {
            'Statement': True,
            'Branch': True, 
            'Condition': True,
            'Path': ['Шлях 1'],
            'MC/DC': True
        },
        'test_user_not_found': {
            'Statement': True,
            'Branch': True,
            'Condition': True, 
            'Path': ['Шлях 2'],
            'MC/DC': True
        },
        'test_account_locked': {
            'Statement': True,
            'Branch': True,
            'Condition': True,
            'Path': ['Шлях 3'], 
            'MC/DC': True
        },
        'test_invalid_password': {
            'Statement': True,
            'Branch': True,
            'Condition': True,
            'Path': ['Шлях 4'],
            'MC/DC': True
        },
        'test_success': {
            'Statement': True,
            'Branch': True,
            'Condition': True,
            'Path': ['Шлях 5'],
            'MC/DC': True
        }
    }
    
    # Виведення таблиці
    print(f"{'Тест':<25} {'Statement':<10} {'Branch':<8} {'Condition':<10} {'Path':<10} {'MC/DC':<8}")
    print("-" * 80)
    
    for test_name, coverage in test_coverage.items():
        statement = "✓" if coverage['Statement'] else "✗"
        branch = "✓" if coverage['Branch'] else "✗"
        condition = "✓" if coverage['Condition'] else "✗"
        path = ", ".join(coverage['Path'])
        mcdc = "✓" if coverage['MC/DC'] else "✗"
        
        print(f"{test_name:<25} {statement:<10} {branch:<8} {condition:<10} {path:<10} {mcdc:<8}")

def main():
    """
    Головна функція для виконання аналізу CFG
    """
    print("Аналіз графа потоку керування для функції authenticate_user")
    print("=" * 60)
    
    # Побудова CFG
    G, nodes = build_cfg_for_authenticate_user()
    
    # Розрахунок цикломатичної складності
    complexity = calculate_cyclomatic_complexity(G)
    
    # Знаходження всіх шляхів
    paths = find_all_paths(G)
    
    # Візуалізація CFG
    visualize_cfg(G, nodes)
    
    # Аналіз def-use пар
    analyze_def_use_pairs()
    
    # Генерація матриці покриття
    generate_test_coverage_matrix()
    
    print(f"\nВисновки:")
    print(f"- Цикломатична складність: {complexity}")
    print(f"- Кількість незалежних шляхів: {len(paths)}")
    print(f"- Мінімальна кількість тестів для повного покриття: {complexity}")
    print(f"- Всі основні техніки білої скрині можуть бути покриті наявними тестами")

if __name__ == "__main__":
    main()