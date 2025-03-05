"""
Interface en ligne de commande pour l'outil d'audit COBOL.
"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from cobol_analyzer import CobolAnalyzer
from cobol_report import CobolReport
from exporters import JsonExporter, CsvExporter, SonarQubeExporter
from exceptions import CobolAuditError
from logger import logger
from scoring import AuditScorer

console = Console()

@click.group()
def cli():
    """Outil d'audit pour analyser le code COBOL."""
    pass

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output-format', '-f', 
              type=click.Choice(['markdown', 'pdf', 'json', 'csv', 'sonarqube']), 
              default='markdown',
              help='Format du rapport de sortie')
@click.option('--output-file', '-o', 
              type=click.Path(), 
              help='Fichier de sortie pour le rapport')
@click.option('--verbose', '-v', 
              is_flag=True, 
              help='Mode verbeux')
@click.option('--detailed', '-d', 
              is_flag=True, 
              help='Mode détaillé avec plus d\'informations')
@click.option('--log-level', '-l',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO',
              help='Niveau de log')
def audit(file_path: str, output_format: str, output_file: str, verbose: bool, detailed: bool, log_level: str):
    """Analyse un fichier COBOL et génère un rapport d'audit."""
    try:
        # Configuration du niveau de log
        logger.setLevel(log_level)
        logger.info(f"Début de l'audit du fichier: {file_path}")

        with console.status("[bold green]Analyse en cours..."):
            analyzer = CobolAnalyzer()
            results = analyzer.analyze_file(file_path)

            if verbose or detailed:
                _display_summary(results, detailed)

            # Sélection de l'exporteur approprié
            if output_format == 'json':
                exporter = JsonExporter()
                output = exporter.export(results, file_path, detailed)
            elif output_format == 'csv':
                exporter = CsvExporter()
                output = exporter.export(results, file_path, detailed)
            elif output_format == 'sonarqube':
                exporter = SonarQubeExporter()
                output = exporter.export(results, file_path, detailed)
            else:
                report = CobolReport()
                output = report.generate(results, file_path, output_format)

            # Sauvegarde ou affichage du rapport
            if output_file:
                mode = 'wb' if output_format == 'pdf' else 'w'
                with open(output_file, mode) as f:
                    if output_format == 'sonarqube':
                        import json
                        json.dump(output, f, indent=2)
                    else:
                        f.write(output)
                console.print(f"[green]Rapport sauvegardé dans {output_file}")
            else:
                if output_format == 'sonarqube':
                    import json
                    console.print(json.dumps(output, indent=2))
                else:
                    console.print(output)

        logger.info("Audit terminé avec succès")

    except CobolAuditError as e:
        logger.error(f"Erreur d'audit: {str(e)}")
        console.print(f"[red]Erreur d'audit: {str(e)}")
        raise click.Abort()
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        console.print(f"[red]Erreur inattendue: {str(e)}")
        raise click.Abort()

def _display_summary(results: dict, detailed: bool = False):
    """Affiche un résumé des résultats de l'analyse."""
    # Calcul du score
    score, grade = AuditScorer.calculate_score(results['metrics'])
    
    # Affichage du score
    score_color = {
        'A': 'bright_green',
        'B': 'green',
        'C': 'yellow',
        'D': 'red',
        'F': 'bright_red'
    }.get(grade, 'white')
    
    score_text = Text()
    score_text.append('Score d\'Audit: ', style='bold')
    score_text.append(f"{score:.1f}", style='bold ' + score_color)
    score_text.append(' (Grade: ', style='bold')
    score_text.append(grade, style='bold ' + score_color)
    score_text.append(')', style='bold')
    
    console.print(Panel(score_text, title="Résultat Global"))
    
    # Table des métriques
    metrics_table = Table(title="Métriques du Code")
    metrics_table.add_column("Catégorie", style="cyan")
    metrics_table.add_column("Métrique", style="blue")
    metrics_table.add_column("Valeur", style="magenta")
    
    # Structure du programme
    for key in ['total_lines', 'procedures', 'data_items']:
        metrics_table.add_row(
            "Structure",
            key.replace('_', ' ').title(),
            str(results['metrics'][key])
        )
    
    # Qualité du code
    for key in ['complexity', 'unused_vars', 'empty_sections', 
                'nested_conditions', 'magic_numbers', 'dead_code_sections']:
        metrics_table.add_row(
            "Qualité",
            key.replace('_', ' ').title(),
            str(results['metrics'][key])
        )
    
    console.print(metrics_table)
    
    # Recommandations
    recommendations = AuditScorer.generate_recommendations(results['metrics'], detailed)
    if recommendations:
        console.print(Panel('\n'.join(recommendations), title="Recommandations"))
    
    # Analyse détaillée
    if detailed:
        detailed_analysis = AuditScorer.get_detailed_metrics_analysis(results['metrics'])
        if detailed_analysis:
            console.print(Panel('\n'.join(detailed_analysis), title="Analyse Détaillée"))
    
    # Table des problèmes
    if results['issues']:
        issues_table = Table(title="Problèmes Détectés")
        issues_table.add_column("Sévérité", style="red")
        issues_table.add_column("Type", style="yellow")
        issues_table.add_column("Message", style="blue")
        issues_table.add_column("Ligne", style="green")
        
        for issue in results['issues']:
            issues_table.add_row(
                issue['severity'],
                issue['type'],
                issue['message'],
                str(issue.get('line', 'N/A'))
            )
        
        console.print(issues_table)

if __name__ == '__main__':
    cli()