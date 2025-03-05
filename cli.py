"""
Interface en ligne de commande pour l'outil d'audit COBOL.
"""
import click
from rich.console import Console
from rich.table import Table
from cobol_analyzer import CobolAnalyzer
from cobol_report import CobolReport

console = Console()

@click.group()
def cli():
    """Outil d'audit pour analyser le code COBOL."""
    pass

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output-format', '-f', type=click.Choice(['markdown', 'pdf']), default='markdown',
              help='Format du rapport de sortie')
@click.option('--output-file', '-o', type=click.Path(), help='Fichier de sortie pour le rapport')
@click.option('--verbose', '-v', is_flag=True, help='Mode verbeux')
def audit(file_path: str, output_format: str, output_file: str, verbose: bool):
    """Analyse un fichier COBOL et génère un rapport d'audit."""
    try:
        with console.status("[bold green]Analyse en cours..."):
            analyzer = CobolAnalyzer()
            results = analyzer.analyze_file(file_path)

            if verbose:
                _display_summary(results)

            report = CobolReport()
            report_content = report.generate(results, file_path, output_format)

            if output_file:
                with open(output_file, 'wb' if output_format == 'pdf' else 'w') as f:
                    f.write(report_content)
                console.print(f"[green]Rapport sauvegardé dans {output_file}")
            else:
                console.print(report_content)

    except Exception as e:
        console.print(f"[red]Erreur: {str(e)}")
        raise click.Abort()

def _display_summary(results: dict):
    """Affiche un résumé des résultats de l'analyse."""
    table = Table(title="Résumé de l'Analyse")
    
    table.add_column("Métrique", style="cyan")
    table.add_column("Valeur", style="magenta")
    
    for key, value in results['metrics'].items():
        table.add_row(key, str(value))
    
    console.print(table)
    
    if results['issues']:
        issues_table = Table(title="Problèmes Détectés")
        issues_table.add_column("Sévérité", style="red")
        issues_table.add_column("Message", style="yellow")
        issues_table.add_column("Type", style="blue")
        
        for issue in results['issues']:
            issues_table.add_row(
                issue['severity'],
                issue['message'],
                issue['type']
            )
        
        console.print(issues_table)

if __name__ == '__main__':
    cli() 