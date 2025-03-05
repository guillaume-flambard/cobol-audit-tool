"""
Exceptions personnalisées pour l'outil d'audit COBOL.
"""

class CobolAuditError(Exception):
    """Classe de base pour les exceptions de l'outil."""
    pass

class ParseError(CobolAuditError):
    """Erreur lors du parsing du code COBOL."""
    pass

class AnalysisError(CobolAuditError):
    """Erreur lors de l'analyse du code."""
    pass

class ReportError(CobolAuditError):
    """Erreur lors de la génération du rapport."""
    pass

class FileError(CobolAuditError):
    """Erreur lors de la manipulation des fichiers."""
    pass 