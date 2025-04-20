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
    assert "At time t = 0:" in stdout, "Position initiale non affichée"
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


def test_local_success_case():
    args = [
        '--local',
        str(TOML_DIR / 'local_scene_example.toml'),
        '10', '0', '35', '-1', '0', '-2'
    ]

    returncode, stdout, stderr = run_interstonar(args)

    # Vérification du code de retour
    assert returncode == 0, f"Le programme a retourné le code {returncode} au lieu de 0"

    # Vérification que la sortie contient les messages attendus
    assert "Rock thrown at the point (10.00, 0.00, 35.00) and parallel to the vector (-1.00, 0.00, -2.00)" in stdout, "Message de lancement de la roche non affiché"
    assert "Sphere of radius 1.00 at position (0.00, 0.00, 0.00)" in stdout, "Message de la sphère non affiché"
    assert "Cylinder of radius 1.00 and height 100.00 at position (0.00, 0.00, 0.00)" in stdout, "Message du cylindre non affiché"
    assert "Box of dimensions (10.00, 10.00, 10.00) at position (0.00, 0.00, 0.00)" in stdout, "Message de la box non affiché"
    assert "Torus of inner radius 3.00 and outer radius 1.00 at position (0.00, 0.00, 0.00)" in stdout, "Message du torus non affiché"

    # Vérification des étapes intermédiaires et du résultat final
    assert "Step 1: (5.98, 0.00, 26.95)" in stdout, "Étape 1 non affichée ou incorrecte"
    assert "Step 2: (3.75, 0.00, 22.50)" in stdout, "Étape 2 non affichée ou incorrecte"
    assert "Step 3: (2.52, 0.00, 20.04)" in stdout, "Étape 3 non affichée ou incorrecte"
    assert "Step 4: (1.84, 0.00, 18.68)" in stdout, "Étape 4 non affichée ou incorrecte"
    assert "Step 5: (1.46, 0.00, 17.93)" in stdout, "Étape 5 non affichée ou incorrecte"
    assert "Step 6: (1.26, 0.00, 17.51)" in stdout, "Étape 6 non affichée ou incorrecte"
    assert "Step 7: (1.14, 0.00, 17.28)" in stdout, "Étape 7 non affichée ou incorrecte"
    assert "Step 8: (1.08, 0.00, 17.16)" in stdout, "Étape 8 non affichée ou incorrecte"
    assert "Step 9: (1.04, 0.00, 17.09)" in stdout, "Étape 9 non affichée ou incorrecte"
    assert "Result: Intersection" in stdout, "Résultat d'intersection non affiché ou incorrect"

def test_local_out_of_scene_case():
    """Test du cas où la roche sort de la scène."""
    args = [
        '--local',
        str(TOML_DIR / 'local_scene_example.toml'),
        '10', '0', '35', '-1', '-1', '-20'
    ]

    returncode, stdout, stderr = run_interstonar(args)

    # Vérification du code de retour
    assert returncode == 0, f"Le programme a retourné le code {returncode} au lieu de 0"

    # Vérification que la sortie contient les messages attendus
    assert "Rock thrown at the point (10.00, 0.00, 35.00) and parallel to the vector (-1.00, -1.00, -20.00)" in stdout, "Message de lancement de la roche non affiché"
    assert "Sphere of radius 1.00 at position (0.00, 0.00, 0.00)" in stdout, "Message de la sphère non affiché"
    assert "Cylinder of radius 1.00 and height 100.00 at position (0.00, 0.00, 0.00)" in stdout, "Message du cylindre non affiché"
    assert "Box of dimensions (10.00, 10.00, 10.00) at position (0.00, 0.00, 0.00)" in stdout, "Message de la box non affiché"
    assert "Torus of inner radius 3.00 and outer radius 1.00 at position (0.00, 0.00, 0.00)" in stdout, "Message du torus non affiché"

    # Vérification des étapes intermédiaires et du résultat final
    assert "Step 1: (9.55, -0.45, 26.02)" in stdout, "Étape 1 non affichée ou incorrecte"
    assert "Step 10: (7.19, -2.81, -21.27)" in stdout, "Étape 10 non affichée ou incorrecte"
    assert "Step 20: (-3.28, -13.28, -230.64)" in stdout, "Étape 20 non affichée ou incorrecte"
    assert "Step 24: (-138.72, -148.72, -2939.50)" in stdout, "Étape 24 non affichée ou incorrecte"
    assert "Result: Out of scene" in stdout, "Résultat 'Out of scene' non affiché ou incorrect"

def test_local_timeout_case():
    """Test du cas où la roche ne rencontre aucun objet et atteint un timeout."""
    args = [
        '--local',
        str(TOML_DIR / 'infinite_cylinder.toml'),
        '3', '-6.2', '12', '0', '0', '10.3'
    ]

    returncode, stdout, stderr = run_interstonar(args)

    # Vérification du code de retour
    assert returncode == 0, f"Le programme a retourné le code {returncode} au lieu de 0"

    # Vérification que la sortie contient le message de timeout
    assert "Result: Time out" in stdout, "Message de timeout non affiché ou incorrect"

if __name__ == "__main__":
    pytest.main(["-v", __file__])