"""
Ce fichier permet l'analyse d'une scène, le but est de l'appliquer à chaque frame pour analyser à terme les infos extraites
"""

# Import module
from nudenet import NudeDetector

BATCH_SIZE = 1

# initialize detector (downloads the checkpoint file automatically the first time)
detector = NudeDetector() # detector = NudeDetector('base') for the "base" version of detector.

# Detect single image
detector.detect('examples/test.jpeg')