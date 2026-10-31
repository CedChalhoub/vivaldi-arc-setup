# Vivaldi façon Arc

Reconfigure Vivaldi sur un autre Mac exactement comme sur le premier.

## Sur le nouveau Mac

1. Récupère ce dossier (`git clone https://github.com/CedChalhoub/vivaldi-arc-setup.git`).
2. Ouvre **Terminal** dans le dossier et lance :

   ```bash
   bash setup.sh
   ```

3. Si macOS demande d'**Ouvrir** Vivaldi, clique sur Ouvrir.
4. Si Vivaldi affiche son **écran d'accueil**, va jusqu'au bout (le style choisi sera remplacé), puis appuie sur Entrée dans Terminal.

Vivaldi est installé avec Homebrew s'il manque. Sans Homebrew, installe-le d'abord depuis vivaldi.com.
Le script peut être relancé sans risque.

## Ce que ça configure

- **Look** : mod VivalArc + thème « Arc Sage » (vert sauge avec grain), sans la colonne d'icônes de panneaux
- **Barre latérale** : onglets à gauche, masquage automatique, URL et flèches en haut de la barre
- **⌘T** : barre de commande flottante façon Arc (recherche web, onglets, favoris, historique)
- **Raccourcis** : ⌘S épingler/masquer la barre, ⌘D épingler l'onglet, ⌘⇧C copier l'URL, ⌘B barre d'adresse, ⌘P panneau
- **Vidéos** : une vidéo en lecture passe en picture-in-picture quand tu changes d'onglet
- **Recherche** : Google partout
- **Bloqueur** : pubs et traceurs bloqués partout, avec les listes uBlock Origin, EasyPrivacy et Liste FR

## Pas inclus

Favoris, mots de passe, historique et extensions : active **Vivaldi Sync** (Réglages > Synchronisation) sur les deux Macs.

## Contenu

- `setup.sh` : le script à lancer (il télécharge aussi VivalArc et ses thèmes ArcLight/ArcDark)
- `mod/` : les fichiers CSS (barre ⌘T, Arc Sage, sans colonne de panneaux)
- `tools/configure.py` : applique les réglages à Vivaldi
- `tools/cdp.py` : petit client pour piloter Vivaldi pendant la configuration
