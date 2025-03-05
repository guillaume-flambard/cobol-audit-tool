"""
Configuration des logs pour l'outil d'audit COBOL.
"""
import logging
import os
from datetime import datetime

def setup_logger(log_level=logging.INFO):
    """Configure le logger principal de l'application."""
    # Crée le dossier logs s'il n'existe pas
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Nom du fichier de log avec la date
    log_file = os.path.join(
        log_dir, 
        f'cobol_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    )

    # Configuration du logger
    logger = logging.getLogger('cobol_audit')
    logger.setLevel(log_level)

    # Handler pour fichier
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Warnings et erreurs seulement
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    return logger

# Logger global
logger = setup_logger() 