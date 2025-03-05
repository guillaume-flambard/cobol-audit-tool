"""
Module d'export des résultats d'analyse.
"""
import json
import csv
from io import StringIO
from typing import Dict, Any
from datetime import datetime
from scoring import AuditScorer

class JsonExporter:
    """Exporte les résultats au format JSON."""
    
    @staticmethod
    def export(results: Dict[str, Any], file_path: str, detailed: bool = False) -> str:
        """Convertit les résultats en JSON."""
        score, grade = AuditScorer.calculate_score(results['metrics'])
        recommendations = AuditScorer.generate_recommendations(results['metrics'], detailed)
        detailed_analysis = AuditScorer.get_detailed_metrics_analysis(results['metrics']) if detailed else []

        export_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'file_analyzed': file_path,
                'tool_version': '1.0.0'
            },
            'audit_score': {
                'score': score,
                'grade': grade
            },
            'metrics': results['metrics'],
            'issues': [
                {
                    'severity': issue['severity'],
                    'message': issue['message'],
                    'type': issue['type'],
                    'line': issue.get('line', 'N/A')
                }
                for issue in results['issues']
            ],
            'recommendations': recommendations,
            'summary': {
                'total_issues': len(results['issues']),
                'severity_counts': {
                    'ERROR': len([i for i in results['issues'] if i['severity'] == 'ERROR']),
                    'WARNING': len([i for i in results['issues'] if i['severity'] == 'WARNING']),
                    'INFO': len([i for i in results['issues'] if i['severity'] == 'INFO'])
                }
            }
        }

        if detailed:
            export_data['detailed_analysis'] = detailed_analysis
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)

class CsvExporter:
    """Exporte les résultats au format CSV."""
    
    @staticmethod
    def export(results: Dict[str, Any], file_path: str, detailed: bool = False) -> str:
        """Convertit les résultats en CSV."""
        output = StringIO()
        csv_writer = csv.writer(output)
        score, grade = AuditScorer.calculate_score(results['metrics'])
        recommendations = AuditScorer.generate_recommendations(results['metrics'], detailed)

        # En-tête du fichier
        csv_writer.writerow(['COBOL Audit Report'])
        csv_writer.writerow(['File:', file_path])
        csv_writer.writerow(['Date:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        csv_writer.writerow(['Score:', f"{score:.1f}", 'Grade:', grade])
        csv_writer.writerow([])

        # Métriques
        csv_writer.writerow(['Metrics'])
        csv_writer.writerow(['Category', 'Metric', 'Value'])
        
        # Structure metrics
        for key in ['total_lines', 'procedures', 'data_items']:
            csv_writer.writerow([
                'Structure',
                key.replace('_', ' ').title(),
                results['metrics'][key]
            ])
        
        # Quality metrics
        for key in ['complexity', 'unused_vars', 'empty_sections', 
                   'nested_conditions', 'magic_numbers', 'dead_code_sections']:
            csv_writer.writerow([
                'Quality',
                key.replace('_', ' ').title(),
                results['metrics'][key]
            ])
        
        csv_writer.writerow([])

        # Recommandations
        if recommendations:
            csv_writer.writerow(['Recommendations'])
            for rec in recommendations:
                csv_writer.writerow([rec])
            csv_writer.writerow([])

        # Analyse détaillée
        if detailed:
            detailed_analysis = AuditScorer.get_detailed_metrics_analysis(results['metrics'])
            if detailed_analysis:
                csv_writer.writerow(['Detailed Analysis'])
                for analysis in detailed_analysis:
                    csv_writer.writerow([analysis])
                csv_writer.writerow([])

        # Problèmes détectés
        if results['issues']:
            csv_writer.writerow(['Issues'])
            csv_writer.writerow(['Severity', 'Type', 'Message', 'Line'])
            
            for issue in results['issues']:
                csv_writer.writerow([
                    issue['severity'],
                    issue['type'],
                    issue['message'],
                    issue.get('line', 'N/A')
                ])

        return output.getvalue()

class SonarQubeExporter:
    """Exporte les résultats au format SonarQube."""
    
    @staticmethod
    def export(results: Dict[str, Any], file_path: str, detailed: bool = False) -> Dict[str, Any]:
        """Convertit les résultats au format SonarQube."""
        score, grade = AuditScorer.calculate_score(results['metrics'])
        recommendations = AuditScorer.generate_recommendations(results['metrics'], detailed)
        
        return {
            'issues': [
                {
                    'engineId': 'cobol-audit',
                    'ruleId': issue['type'],
                    'severity': issue['severity'].lower(),
                    'type': 'CODE_SMELL',
                    'primaryLocation': {
                        'message': issue['message'],
                        'filePath': file_path,
                        'textRange': {
                            'startLine': issue.get('line', 1),
                            'endLine': issue.get('line', 1)
                        }
                    }
                }
                for issue in results['issues']
            ],
            'metrics': [
                {
                    'metric': key,
                    'value': value
                }
                for key, value in results['metrics'].items()
            ],
            'quality_gate': {
                'status': 'OK' if grade in ['A', 'B'] else 'WARN' if grade == 'C' else 'ERROR',
                'score': score,
                'grade': grade
            },
            'recommendations': recommendations
        } 