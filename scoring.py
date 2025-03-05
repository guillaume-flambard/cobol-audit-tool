"""
Module de scoring et recommandations pour l'audit COBOL.
"""
from typing import Dict, List, Tuple

class AuditScorer:
    """Calcule le score d'audit et génère des recommandations."""
    
    GRADE_SCALE = {
        90: 'A',
        80: 'B',
        70: 'C',
        60: 'D',
        0: 'F'
    }

    METRIC_WEIGHTS = {
        'complexity': 0.2,
        'unused_vars': 0.15,
        'empty_sections': 0.1,
        'nested_conditions': 0.15,
        'magic_numbers': 0.1,
        'dead_code_sections': 0.3
    }

    THRESHOLD_RECOMMENDATIONS = {
        'complexity': {
            'high': (10, "Réduisez la complexité en divisant les procédures complexes en sous-procédures"),
            'medium': (5, "Envisagez de simplifier les procédures les plus complexes")
        },
        'unused_vars': {
            'high': (5, "Nettoyez les variables non utilisées pour améliorer la maintenabilité"),
            'medium': (2, "Vérifiez et supprimez les variables potentiellement inutiles")
        },
        'nested_conditions': {
            'high': (4, "Simplifiez les conditions imbriquées en utilisant des tables de décision"),
            'medium': (2, "Évaluez si certaines conditions peuvent être combinées")
        },
        'magic_numbers': {
            'high': (8, "Définissez des constantes nommées pour tous les nombres magiques"),
            'medium': (4, "Identifiez et remplacez les nombres magiques les plus utilisés")
        },
        'dead_code_sections': {
            'high': (3, "Supprimez les sections de code mort pour améliorer la maintenabilité"),
            'medium': (1, "Vérifiez et documentez les sections potentiellement mortes")
        }
    }

    @classmethod
    def calculate_score(cls, metrics: Dict) -> Tuple[int, str]:
        """Calcule le score global et retourne la note correspondante."""
        base_score = 100
        
        for metric, weight in cls.METRIC_WEIGHTS.items():
            if metric in metrics:
                # Pénalité proportionnelle à la valeur de la métrique
                penalty = min(metrics[metric] * weight * 10, weight * 100)
                base_score -= penalty

        # Assurer que le score est entre 0 et 100
        final_score = max(0, min(100, base_score))
        
        # Déterminer la note
        for threshold, grade in sorted(cls.GRADE_SCALE.items(), reverse=True):
            if final_score >= threshold:
                return final_score, grade
        
        return final_score, 'F'

    @classmethod
    def generate_recommendations(cls, metrics: Dict, detailed: bool = False) -> List[str]:
        """Génère une liste de recommandations basées sur les métriques."""
        recommendations = []

        for metric, thresholds in cls.THRESHOLD_RECOMMENDATIONS.items():
            if metric not in metrics:
                continue

            value = metrics[metric]
            
            # Recommandations pour les problèmes graves
            if value >= thresholds['high'][0]:
                recommendations.append(f"⚠️ URGENT: {thresholds['high'][1]}")
            # Recommandations pour les problèmes moyens en mode détaillé
            elif detailed and value >= thresholds['medium'][0]:
                recommendations.append(f"📝 SUGGESTION: {thresholds['medium'][1]}")

        return recommendations

    @classmethod
    def get_detailed_metrics_analysis(cls, metrics: Dict) -> List[str]:
        """Génère une analyse détaillée des métriques."""
        analysis = []
        
        if metrics.get('complexity', 0) > 0:
            analysis.append(f"🔍 Complexité cyclomatique moyenne: {metrics['complexity']:.2f}")
        
        if metrics.get('procedures', 0) > 0:
            analysis.append(f"📊 Nombre de procédures: {metrics['procedures']}")
            if metrics.get('total_lines', 0) > 0:
                lines_per_proc = metrics['total_lines'] / metrics['procedures']
                analysis.append(f"📏 Moyenne de lignes par procédure: {lines_per_proc:.1f}")

        return analysis 