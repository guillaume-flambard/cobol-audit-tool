"""
Règles d'analyse avancées pour le code COBOL.
"""
from typing import List, Dict, Any
import re

class CobolRules:
    """Règles d'analyse pour le code COBOL."""

    @staticmethod
    def check_nested_conditions(line: str) -> int:
        """Vérifie la profondeur des conditions imbriquées."""
        return line.count('IF ') + line.count('EVALUATE ')

    @staticmethod
    def check_magic_numbers(line: str) -> bool:
        """Détecte les nombres magiques dans le code."""
        # Ignore les numéros de niveau (01, 05, etc.)
        if re.match(r'^\s*\d{2}\s+', line):
            return False
        return bool(re.search(r'(?<!\d)\d{2,}(?!\d)', line))

    @staticmethod
    def check_paragraph_length(lines: List[str]) -> int:
        """Vérifie la longueur d'un paragraphe."""
        return len([l for l in lines if l.strip()])

    @staticmethod
    def check_naming_convention(name: str) -> bool:
        """Vérifie si le nom suit les conventions COBOL."""
        return bool(re.match(r'^[A-Z][A-Z0-9-]*$', name))

    @staticmethod
    def check_dead_code(lines: List[str]) -> List[str]:
        """Détecte le code mort potentiel."""
        dead_sections = []
        current_section = None
        has_entry_point = False

        for line in lines:
            if 'SECTION.' in line:
                if current_section and not has_entry_point:
                    dead_sections.append(current_section)
                current_section = line
                has_entry_point = False
            elif current_section and ('PERFORM ' in line or 'GOTO ' in line):
                has_entry_point = True

        return dead_sections

    @staticmethod
    def check_data_usage(data_lines: List[str], proc_lines: List[str]) -> Dict[str, int]:
        """Analyse l'utilisation des données."""
        usage = {}
        for line in data_lines:
            if match := re.match(r'^\s*\d+\s+(\w+)', line):
                var_name = match.group(1)
                if var_name != 'FILLER':
                    usage[var_name] = 0

        for line in proc_lines:
            for var in usage:
                if var in line:
                    usage[var] += 1

        return usage

    @staticmethod
    def check_perform_thru(line: str) -> bool:
        """Détecte l'utilisation de PERFORM THRU (déconseillé)."""
        return 'PERFORM' in line and 'THRU' in line

    @staticmethod
    def check_altered_goto(lines: List[str]) -> List[str]:
        """Détecte les GOTOs modifiés (ALTER)."""
        altered_gotos = []
        for line in lines:
            if 'ALTER' in line and 'TO' in line:
                altered_gotos.append(line)
        return altered_gotos

    @staticmethod
    def check_working_storage_organization(data_lines: List[str]) -> List[str]:
        """Vérifie l'organisation de la WORKING-STORAGE SECTION."""
        issues = []
        current_level = 0
        for line in data_lines:
            if match := re.match(r'^\s*(\d+)', line):
                level = int(match.group(1))
                if level != 1 and level <= current_level:
                    issues.append(f"Niveau {level} mal organisé: {line.strip()}")
                current_level = level
        return issues 