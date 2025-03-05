"""
Module d'analyse pour détecter les problèmes dans le code COBOL.
"""
from typing import List, Dict, Any, Set
from cobol_parser import CobolParser
import re

class CobolAnalyzer:
    def __init__(self):
        self.parser = CobolParser()
        self.issues = []
        self.metrics = {
            'total_lines': 0,
            'procedures': 0,
            'data_items': 0,
            'complexity': 0,
            'unused_vars': 0,
            'empty_sections': 0
        }

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyse un fichier COBOL et retourne les résultats."""
        try:
            divisions = self.parser.parse_file(file_path)
            self._analyze_divisions(divisions)
            self._calculate_metrics(divisions)
            return {
                'issues': self.issues,
                'metrics': self.metrics
            }
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'analyse: {str(e)}")

    def _analyze_divisions(self, divisions: Dict[str, List[str]]) -> None:
        """Analyse chaque division pour détecter les problèmes."""
        self._check_division_structure(divisions)
        self._analyze_procedure_division(divisions['PROCEDURE'])
        self._analyze_data_division(divisions['DATA'])
        self._analyze_unused_variables(divisions)
        self._analyze_empty_sections(divisions['PROCEDURE'])

    def _check_division_structure(self, divisions: Dict[str, List[str]]) -> None:
        """Vérifie la structure des divisions."""
        required_divisions = ['IDENTIFICATION', 'PROCEDURE']
        for div in required_divisions:
            if not divisions[div]:
                self.issues.append({
                    'severity': 'ERROR',
                    'message': f'Division {div} manquante ou vide',
                    'type': 'structure'
                })

    def _analyze_procedure_division(self, procedures: List[str]) -> None:
        """Analyse la division PROCEDURE."""
        for line in procedures:
            if 'GOTO' in line:
                self.issues.append({
                    'severity': 'WARNING',
                    'message': 'Utilisation de GOTO détectée',
                    'type': 'best_practice',
                    'line': line
                })

    def _analyze_data_division(self, data: List[str]) -> None:
        """Analyse la division DATA."""
        for line in data:
            if 'FILLER' in line and len(line.split()) < 3:
                self.issues.append({
                    'severity': 'INFO',
                    'message': 'FILLER sans description explicite',
                    'type': 'documentation',
                    'line': line
                })

    def _analyze_unused_variables(self, divisions: Dict[str, List[str]]) -> None:
        """Détecte les variables déclarées mais non utilisées."""
        # Collecte toutes les variables déclarées
        declared_vars = set()
        for line in divisions['DATA']:
            if match := re.match(r'^\s*\d+\s+(\w+)', line):
                var_name = match.group(1)
                if var_name != 'FILLER':
                    declared_vars.add(var_name)

        # Vérifie l'utilisation dans la PROCEDURE DIVISION
        used_vars = set()
        for line in divisions['PROCEDURE']:
            for var in declared_vars:
                if var in line and not line.endswith('SECTION.'):
                    used_vars.add(var)

        # Ajoute les problèmes pour les variables non utilisées
        unused_vars = declared_vars - used_vars
        self.metrics['unused_vars'] = len(unused_vars)
        for var in unused_vars:
            self.issues.append({
                'severity': 'WARNING',
                'message': f'Variable {var} déclarée mais non utilisée',
                'type': 'unused_variable'
            })

    def _analyze_empty_sections(self, procedures: List[str]) -> None:
        """Détecte les sections vides ou ne contenant que EXIT."""
        current_section = None
        section_content = []
        
        for line in procedures:
            if 'SECTION.' in line:
                if current_section and section_content:
                    self._check_section_content(current_section, section_content)
                current_section = line
                section_content = []
            elif current_section:
                section_content.append(line)

        # Vérifie la dernière section
        if current_section and section_content:
            self._check_section_content(current_section, section_content)

    def _check_section_content(self, section_name: str, content: List[str]) -> None:
        """Vérifie si une section est vide ou ne contient que EXIT."""
        meaningful_content = [
            line for line in content 
            if line.strip() and not line.strip().upper() in ['EXIT.', 'EXIT']
        ]
        
        if not meaningful_content:
            self.metrics['empty_sections'] += 1
            self.issues.append({
                'severity': 'INFO',
                'message': f'Section vide ou ne contenant que EXIT: {section_name}',
                'type': 'empty_section',
                'line': section_name
            })

    def _calculate_metrics(self, divisions: Dict[str, List[str]]) -> None:
        """Calcule les métriques du code."""
        self.metrics['total_lines'] = sum(len(div) for div in divisions.values())
        self.metrics['procedures'] = len(self.parser.get_procedures())
        self.metrics['data_items'] = len(self.parser.get_data_items())
        self.metrics['complexity'] = self._calculate_complexity(divisions['PROCEDURE'])

    def _calculate_complexity(self, procedures: List[str]) -> int:
        """Calcule la complexité cyclomatique du code COBOL.
        
        La complexité est calculée en comptant:
        - Les conditions IF/EVALUATE
        - Les boucles PERFORM UNTIL/VARYING
        - Les instructions GOTO
        - Les sections
        
        La formule est: 1 + nombre de points de décision
        """
        complexity = 1  # Valeur de base
        
        for line in procedures:
            line = line.upper()
            # Compte les structures de contrôle
            if any(keyword in line for keyword in ['IF ', 'EVALUATE ']):
                complexity += 1
            if 'PERFORM' in line and any(keyword in line for keyword in ['UNTIL ', 'VARYING ']):
                complexity += 1
            if 'GOTO ' in line:
                complexity += 1
            if 'SECTION.' in line:
                complexity += 1
            # Compte les opérateurs AND/OR dans les conditions
            if 'IF ' in line:
                complexity += line.count(' AND ') + line.count(' OR ')
        
        return complexity