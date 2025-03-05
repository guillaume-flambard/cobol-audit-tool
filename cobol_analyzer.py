"""
Module d'analyse pour détecter les problèmes dans le code COBOL.
"""
from typing import List, Dict, Any, Set
import re
from cobol_parser import CobolParser
from rules import CobolRules
from exceptions import AnalysisError, ParseError
from logger import logger

class CobolAnalyzer:
    def __init__(self):
        self.parser = CobolParser()
        self.rules = CobolRules()
        self.issues = []
        self.metrics = {
            'total_lines': 0,
            'procedures': 0,
            'data_items': 0,
            'complexity': 0,
            'unused_vars': 0,
            'empty_sections': 0,
            'nested_conditions': 0,
            'magic_numbers': 0,
            'dead_code_sections': 0
        }

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyse un fichier COBOL et retourne les résultats."""
        try:
            logger.info(f"Début de l'analyse du fichier: {file_path}")
            divisions = self.parser.parse_file(file_path)
            self._analyze_divisions(divisions)
            self._calculate_metrics(divisions)
            
            logger.info(f"Analyse terminée. {len(self.issues)} problèmes détectés.")
            return {
                'issues': self.issues,
                'metrics': self.metrics
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse: {str(e)}")
            raise AnalysisError(f"Erreur lors de l'analyse: {str(e)}")

    def _analyze_divisions(self, divisions: Dict[str, List[str]]) -> None:
        """Analyse chaque division pour détecter les problèmes."""
        try:
            self._check_division_structure(divisions)
            self._analyze_procedure_division(divisions['PROCEDURE'])
            self._analyze_data_division(divisions['DATA'])
            self._analyze_advanced_rules(divisions)
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des divisions: {str(e)}")
            raise AnalysisError(f"Erreur lors de l'analyse des divisions: {str(e)}")

    def _analyze_advanced_rules(self, divisions: Dict[str, List[str]]) -> None:
        """Applique les règles d'analyse avancées."""
        logger.info("Application des règles d'analyse avancées")
        
        # Analyse du code mort
        dead_sections = self.rules.check_dead_code(divisions['PROCEDURE'])
        self.metrics['dead_code_sections'] = len(dead_sections)
        for section in dead_sections:
            self.issues.append({
                'severity': 'WARNING',
                'message': f'Section potentiellement morte détectée: {section}',
                'type': 'dead_code',
                'line': section
            })

        # Vérification des nombres magiques
        magic_numbers = 0
        for line in divisions['PROCEDURE']:
            if self.rules.check_magic_numbers(line):
                magic_numbers += 1
                self.issues.append({
                    'severity': 'INFO',
                    'message': 'Nombre magique détecté',
                    'type': 'magic_number',
                    'line': line
                })
        self.metrics['magic_numbers'] = magic_numbers

        # Vérification des conditions imbriquées
        max_nested = 0
        for line in divisions['PROCEDURE']:
            nested_count = self.rules.check_nested_conditions(line)
            max_nested = max(max_nested, nested_count)
            if nested_count > 2:
                self.issues.append({
                    'severity': 'WARNING',
                    'message': f'Conditions trop imbriquées ({nested_count} niveaux)',
                    'type': 'complexity',
                    'line': line
                })
        self.metrics['nested_conditions'] = max_nested

        # Vérification de l'organisation WORKING-STORAGE
        storage_issues = self.rules.check_working_storage_organization(divisions['DATA'])
        for issue in storage_issues:
            self.issues.append({
                'severity': 'WARNING',
                'message': issue,
                'type': 'data_organization'
            })

        # Vérification des PERFORM THRU
        for line in divisions['PROCEDURE']:
            if self.rules.check_perform_thru(line):
                self.issues.append({
                    'severity': 'WARNING',
                    'message': 'Utilisation de PERFORM THRU déconseillée',
                    'type': 'best_practice',
                    'line': line
                })

        # Vérification des ALTER GOTO
        altered_gotos = self.rules.check_altered_goto(divisions['PROCEDURE'])
        for goto in altered_gotos:
            self.issues.append({
                'severity': 'ERROR',
                'message': 'Utilisation de ALTER GOTO détectée',
                'type': 'best_practice',
                'line': goto
            })

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

    def _calculate_metrics(self, divisions: Dict[str, List[str]]) -> None:
        """Calcule les métriques du code."""
        try:
            self.metrics['total_lines'] = sum(len(div) for div in divisions.values())
            self.metrics['procedures'] = len(self.parser.get_procedures())
            self.metrics['data_items'] = len(self.parser.get_data_items())
            self.metrics['complexity'] = self._calculate_complexity(divisions['PROCEDURE'])
            
            # Analyse de l'utilisation des données
            data_usage = self.rules.check_data_usage(divisions['DATA'], divisions['PROCEDURE'])
            self.metrics['unused_vars'] = len([v for v, count in data_usage.items() if count == 0])
            
            logger.info(f"Métriques calculées: {self.metrics}")
        except Exception as e:
            logger.error(f"Erreur lors du calcul des métriques: {str(e)}")
            raise AnalysisError(f"Erreur lors du calcul des métriques: {str(e)}")

    def _calculate_complexity(self, procedures: List[str]) -> int:
        """Calcule la complexité cyclomatique du code COBOL."""
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