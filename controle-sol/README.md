# Logiciel de contrôle au sol

## Description


## Launching

Au besoin, créer le Python virtual environment and installer les différents packages.
```
python.exe -m pip install --upgrade pip
python -m venv .venv
.\.venv\Scripts\activate
pip install PyQt6
pip install pyqtgraph
pip install PyOpenGL
pip install numpy-stl
```

Activer le Python virtual environment
```
.\.venv\Scripts\activate
```

Lancement
```
python main.py
```


## TODO

- EcranPrincipal : signals pour le bouton Connecter !
- EcranPrincipal : signals pour les boutons Lancer et Stop ! Ouvrir une boîte de dialogue pour le mot de passe (précharger avec self.password).
- EcranPrincipal : Ajouter splitter entre les deux groupes de widgets graphiques du panneau droit
- EcranPrincipal : toggle de défilement auto pour les logs généraux du panneau gauche (cf. panneau droit)
- CentraleInertielle : intégrations vitesses et positions (en supposant le référentiel galiléen pour l'instant)
- Orienter la vue 3D en fonction de l'orientation réelle de la fusée
- Instructions RFP supplémentaires destinées au centre de contrôle pour indiquer les fichiers 3D lors des différents étages.