import io
import sys
from cfg_analysis import print_cyclomatic_complexity

def test_print_cyclomatic_complexity_output(capsys):
    print_cyclomatic_complexity()
    captured = capsys.readouterr()
    assert "Цикломатична складність:" in captured.out
