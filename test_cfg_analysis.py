import pytest
import networkx as nx
from cfg_analysis import (
    build_cfg_from_file,
    calculate_cyclomatic_complexity,
    find_paths,
    export_cfg_to_dot,
    analyze_cfg
)
import subprocess
import os
import networkx as nx
from cfg_analysis import find_paths
from cfg_analysis import print_cyclomatic_complexity

def test_build_cfg_valid():
    """Тест перевіряє, чи успішно будується CFG для валідного файлу"""
    G = build_cfg_from_file("auth.py")
    assert isinstance(G, nx.DiGraph)
    assert G.number_of_nodes() > 0
    assert G.number_of_edges() > 0

def test_build_cfg_function_missing(tmp_path):
    """Тест перевіряє, чи викликається ValueError, якщо немає функції authenticate_user"""
    file = tmp_path / "fake_auth.py"
    file.write_text("def something_else(): pass")

    with pytest.raises(ValueError, match="Функція authenticate_user не знайдена"):
        build_cfg_from_file(str(file))

def test_calculate_cyclomatic_complexity():
    """Перевірка правильності підрахунку цикломатичної складності"""
    G = nx.DiGraph()
    G.add_edges_from([("n0", "n1"), ("n1", "n2"), ("n0", "n2")])
    M = calculate_cyclomatic_complexity(G)
    assert M == 2  # 3 edges - 3 nodes + 2 = 2

def test_find_paths_normal():
    """Перевірка знаходження всіх шляхів у нормальному графі"""
    G = nx.DiGraph()
    G.add_edges_from([("n0", "n1"), ("n1", "n2")])
    paths = find_paths(G)
    assert paths == [["n0", "n1", "n2"]]

def test_find_paths_with_no_path():
    G = nx.DiGraph()
    G.add_node("n0")
    G.add_node("n1")
    paths = find_paths(G)
    assert paths == [["n0"]]

def test_export_cfg_to_dot(tmp_path):
    """Перевірка експорту CFG у DOT-файл"""
    G = nx.DiGraph()
    G.add_edges_from([("n0", "n1")])
    dot_path = tmp_path / "cfg_test.dot"
    path = export_cfg_to_dot(G, str(dot_path))
    assert os.path.exists(path)
    assert path.endswith(".dot")

def test_analyze_cfg_structure():
    """Перевірка, що analyze_cfg повертає всі ключі"""
    result = analyze_cfg()
    assert "graph" in result
    assert "complexity" in result
    assert "paths" in result
    assert "paths_count" in result
    assert isinstance(result["graph"], nx.DiGraph)
    assert result["paths_count"] == len(result["paths"])



def test_find_paths_with_networkx_no_path(monkeypatch):
    # Створюємо граф, де нема шляхів від n0 до n1
    G = nx.DiGraph()
    G.add_node("n0")
    G.add_node("n1")  # недосяжний вузол

    # monkeypatch all_simple_paths to always raise NetworkXNoPath
    def fake_all_simple_paths(*args, **kwargs):
        raise nx.NetworkXNoPath

    monkeypatch.setattr(nx, "all_simple_paths", fake_all_simple_paths)

    result = find_paths(G)
    assert result == []

def test_print_cyclomatic_complexity(capsys):
    print_cyclomatic_complexity()
    captured = capsys.readouterr()
    assert "Цикломатична складність:" in captured.out