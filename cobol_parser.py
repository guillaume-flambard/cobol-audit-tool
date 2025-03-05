"""
Module de parsing pour analyser le code COBOL.
"""
from typing import List, Dict, Optional
import re

class CobolParser:
    def __init__(self):
        self.divisions = {
            'IDENTIFICATION': [],
            'ENVIRONMENT': [],
            'DATA': [],
            'PROCEDURE': []
        }
        self.current_division = None

    def parse_file(self, file_path: str) -> Dict[str, List[str]]:
        """Parse un fichier COBOL et retourne sa structure."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return self.parse_content(file.readlines())
        except FileNotFoundError:
            raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")

    def parse_content(self, lines: List[str]) -> Dict[str, List[str]]:
        """Parse le contenu COBOL ligne par ligne."""
        for line in lines:
            line = line.strip()
            if not line or line.startswith('*'):
                continue

            # Détection des divisions
            division_match = re.match(r'^\s*(\w+)\s+DIVISION\.', line)
            if division_match:
                self.current_division = division_match.group(1).upper()
                continue

            if self.current_division:
                self.divisions[self.current_division].append(line)

        return self.divisions

    def get_procedures(self) -> List[str]:
        """Retourne la liste des procédures (sections uniquement).
        
        En COBOL, nous considérons comme procédures uniquement les sections,
        qui sont des unités logiques de code commençant par 'SECTION.'
        Les labels de GOTO et autres points d'entrée ne sont pas comptés
        comme des procédures.
        """
        procedures = []
        
        for line in self.divisions['PROCEDURE']:
            line = line.strip().upper()
            
            # Ne compte que les sections explicitement déclarées
            if re.match(r'^\s*[\w-]+\s+SECTION\.', line):
                procedures.append(line)
                
        return procedures

    def get_data_items(self) -> List[str]:
        """Retourne la liste des éléments de données."""
        data_items = []
        for line in self.divisions['DATA']:
            if re.match(r'^\s*\d+\s+\w+', line):
                data_items.append(line.strip())
        return data_items 