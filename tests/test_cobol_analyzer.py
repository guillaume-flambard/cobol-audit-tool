"""
Tests pour le module d'analyse COBOL.
"""
import os
import pytest
from cobol_analyzer import CobolAnalyzer

@pytest.fixture
def sample_file():
    return os.path.join(os.path.dirname(__file__), 'fixtures', 'sample.cbl')

def test_analyzer_initialization():
    analyzer = CobolAnalyzer()
    assert analyzer.issues == []
    assert all(value == 0 for value in analyzer.metrics.values())

def test_analyze_file(sample_file):
    analyzer = CobolAnalyzer()
    results = analyzer.analyze_file(sample_file)
    
    assert 'metrics' in results
    assert 'issues' in results
    
    # Vérification des métriques
    metrics = results['metrics']
    assert metrics['total_lines'] > 0
    assert metrics['procedures'] > 0
    assert metrics['data_items'] > 0
    
    # Vérification des problèmes détectés
    issues = results['issues']
    assert any(issue['type'] == 'best_practice' and 'GOTO' in issue['message'] 
              for issue in issues)
    assert any(issue['type'] == 'documentation' and 'FILLER' in issue['message']
              for issue in issues)

def test_nonexistent_file():
    analyzer = CobolAnalyzer()
    with pytest.raises(FileNotFoundError):
        analyzer.analyze_file('nonexistent.cbl') 