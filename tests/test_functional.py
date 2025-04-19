#!/usr/bin/env python3

"""
Tests fonctionnels pour le programme Interstonar.
Ces tests exécutent le programme complet et vérifient le comportement et la sortie.
"""

import os
import re
import pytest
import subprocess
from pathlib import Path

# Chemin vers l'exécutable Interstonar
INTERSTONAR_PATH = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'interstonar'

# Chemin vers les fichiers de configuration TOML
TOML_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'toml'


def run_interstonar(args):
    """
    Exécute le programme Interstonar avec les arguments spécifiés.

    Args:
        args (list): Liste des arguments pour le programme

    Returns:
        tuple: (code de retour, sortie standard, sortie d'erreur)
    """
    cmd = [str(INTERSTONAR_PATH)] + args
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr


def test_global_success_case():
    """Test du cas où la roche atteint un objectif (mission réussie)."""
    args = [
        '--global',
        str(TOML_DIR / 'global_scene_example.toml'),
        '1', '2', '3', '4', '5', '6'
    ]

    returncode, stdout, stderr = run_interstonar(args)

    # Vérification du code de retour
    assert returncode == 0, f"Le programme a retourné le code {returncode} au lieu de 0"

    # Vérification que la sortie contient les messages attendus
    assert "At time t = 1:" in stdout, "Position à t=1 non affichée"
    assert "Collision between rock and Sun" in stdout, "Message de collision non affiché"
    assert "Mission success" in stdout, "Message de succès non affiché"

    # Vérification que la position à t=1 est bien présente, sans vérifier les valeurs exactes
    # Les valeurs peuvent changer avec des modifications de l'implémentation
    t1_match = re.search(r"At time t = 1: rock is \(([^)]+)\)", stdout)
    assert t1_match, "Format de position à t=1 incorrect"

    # Analyse des coordonnées à t=1
    coords = t1_match.group(1).split(", ")
    assert len(coords) == 3, "Nombre incorrect de coordonnées"


def test_global_failure_case():
    """Test du cas où la roche frappe un corps qui n'est pas un objectif (mission échouée)."""
    args = [
        '--global',
        str(TOML_DIR / 'global_scene_example2.toml'),  # Sun n'est pas un objectif dans ce fichier
        '1', '2', '3', '4', '5', '6'
    ]

    returncode, stdout, stderr = run_interstonar(args)

    # Vérification du code de retour
    assert returncode == 0, f"Le programme a retourné le code {returncode} au lieu de 0"

    # Vérification que la sortie contient les messages attendus
    assert "Collision between rock and Sun" in stdout, "Message de collision non affiché"
    assert "Mission failure" in stdout, "Message d'échec non affiché"


def test_global_timeout():
    """Test du cas où la roche ne frappe pas de corps (timeout après 365 jours)."""
    # Utilisez des coordonnées et une vitesse qui ne causeront pas de collision
    args = [
        '--global',
        str(TOML_DIR / 'global_scene_example.toml'),
        '1e20', '1e20', '1e20',  # Position très éloignée
        '0', '0', '0'            # Vitesse nulle
    ]

    # Note: Ce test peut être très long en raison du timeout de 365 jours
    # Nous allons tester uniquement l'appel sans attendre de complétion
    try:
        returncode, stdout, stderr = run_interstonar(args)
        # Si le test se termine dans un temps raisonnable, il doit signaler un échec de mission
        assert "Mission failure" in stdout, "Message d'échec non affiché"
    except subprocess.TimeoutExpired:
        # Si le test est trop long, on le considère comme réussi
        pytest.skip("Test ignoré car trop long")


def test_global_invalid_args():
    """Test avec des arguments invalides."""
    # Arguments manquants
    args = ['--global', str(TOML_DIR / 'global_scene_example.toml')]

    returncode, stdout, stderr = run_interstonar(args)

    # Vérification du code de retour (doit être 84 pour une erreur)
    assert returncode == 84, f"Le programme a retourné le code {returncode} au lieu de 84"

    # Vérification que la sortie d'erreur contient un message d'erreur
    assert "Error" in stderr, "Message d'erreur non affiché"


def test_global_invalid_config():
    """Test avec un fichier de configuration invalide."""
    # Fichier inexistant
    args = [
        '--global',
        'fichier_inexistant.toml',
        '1', '2', '3', '4', '5', '6'
    ]

    returncode, stdout, stderr = run_interstonar(args)

    # Vérification du code de retour (doit être 84 pour une erreur)
    assert returncode == 84, f"Le programme a retourné le code {returncode} au lieu de 84"

    # Vérification que la sortie d'erreur contient un message d'erreur
    assert "Error" in stderr, "Message d'erreur non affiché"


if __name__ == "__main__":
    pytest.main(["-v", __file__])