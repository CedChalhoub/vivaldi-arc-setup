#!/bin/bash
# Sets up Vivaldi to look and behave like Arc (VivalArc mod, Arc Sage theme, sidebar, Cmd+T bar,
# Google search, ad/tracker blocking with uBlock lists). Safe to run more than once.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
APP="/Applications/Vivaldi.app"
PROFILE="$HOME/Library/Application Support/Vivaldi"
MOD="$HOME/Library/Application Support/VivalArc/mod"
PORT=9333

say() { printf '\n==> %s\n' "$1"; }

quit_vivaldi() {
    osascript -e 'quit app "Vivaldi"' 2>/dev/null || true
    for _ in $(seq 1 30); do pgrep -x Vivaldi >/dev/null || return 0; sleep 1; done
    echo "Vivaldi ne se ferme pas, ferme-le à la main puis relance ce script."; exit 1
}

if ! python3 -c 1 2>/dev/null; then
    echo "python3 est requis. Lance : xcode-select --install   puis relance ce script."; exit 1
fi

if [ ! -d "$APP" ]; then
    say "Installation de Vivaldi"
    if command -v brew >/dev/null; then
        brew install --cask vivaldi
    else
        echo "Installe Vivaldi depuis https://vivaldi.com (ou installe Homebrew), puis relance ce script."; exit 1
    fi
fi

# VivalArc has no license, so it isn't bundled here: fetch it from its repo, pinned to a known commit
VIVALARC_REV="41363620174517d7235e81077dd8bbcd7327bfa8"
VIVALARC_URL="https://raw.githubusercontent.com/tovifun/VivalArc/$VIVALARC_REV"
VIVALARC_TMP="$(mktemp -d)"
trap 'rm -rf "$VIVALARC_TMP"' EXIT

say "Téléchargement de VivalArc"
curl -fsSL "$VIVALARC_URL/vivalarc.css" -o "$VIVALARC_TMP/vivalarc.css"
for theme in ArcLight ArcDark; do
    curl -fsSL "$VIVALARC_URL/themes/theme-$theme.zip" -o "$VIVALARC_TMP/theme-$theme.zip"
done
export VIVALARC_THEMES="$VIVALARC_TMP"

say "Copie du mod CSS"
mkdir -p "$MOD"
cp "$HERE"/mod/*.css "$VIVALARC_TMP/vivalarc.css" "$MOD/"

say "Lancement de Vivaldi pour le configurer"
quit_vivaldi
open -a Vivaldi --args --remote-debugging-port=$PORT
echo "Si macOS demande « Ouvrir », clique sur Ouvrir ; j'attends."
for i in $(seq 1 180); do
    curl -s -m 2 "localhost:$PORT/json" | grep -q 'main.html' && break
    [ "$i" = 180 ] && { echo "Vivaldi n'a pas démarré à temps."; exit 1; }
    sleep 1
done
sleep 4
# the welcome wizard applies its own layout when finished, so let it finish before configuring
if curl -s -m 2 "localhost:$PORT/json" | grep -q 'components/welcome'; then
    echo
    echo "Vivaldi affiche son écran d'accueil : va jusqu'au bout (n'importe quel style, ça sera remplacé)."
    read -r -p "Quand c'est fini, appuie sur Entrée ici… "
fi

say "Application des réglages"
python3 -I "$HERE/tools/configure.py"

say "Activation des modifications CSS et du PiP automatique (redémarrage de Vivaldi)"
quit_vivaldi
python3 -I - "$PROFILE/Local State" <<'EOF'
import json, sys
path = sys.argv[1]
state = json.load(open(path))
flags = state.setdefault("browser", {}).setdefault("enabled_labs_experiments", [])
# CSS mods + video goes picture-in-picture when you switch away from its tab
for flag in ("vivaldi-css-mods", "browser-initiated-automatic-picture-in-picture@1"):
    if flag not in flags:
        flags.append(flag)
json.dump(state, open(path, "w"))
EOF
open -a Vivaldi

say "Terminé ! ⌘T = barre de commande, ⌘S = épingler/masquer la barre latérale."
