# Psykokwak & Métamorph

Suivi de collection des cartes Psykokwak et Métamorph du JCC Pokémon, en français, anglais et japonais : une case par carte (version normale), exclusivités japonaises et caméos compris (129 cartes, hors Jumbo et éditions chinoises, coréennes, indonésiennes et thaïes).

**App : https://guillaumecazelles.github.io/psykokwak-metamorph/**

- Toucher une carte l'ajoute à la collection ; la toucher encore la retire. Maintenir appuyé l'agrandit.
- Filtres par langue (double-toucher une langue pour n'afficher qu'elle), par Pokémon, caméos, cartes manquantes.
- Onglet Prix : prix Cardmarket par langue (moyenne des 5 offres Near Mint les moins chères en français ou en japonais), sinon prix moyen 30 jours du guide des prix Cardmarket.
- La collection est enregistrée dans le navigateur de chaque appareil ; sauvegarde et restauration depuis le menu ☰.
- Sur iPhone : Safari → Partager → « Sur l'écran d'accueil ».

## Mettre à jour les données

L'app est un seul fichier, `index.html`, généré par :

```bash
cd build
python build.py   # télécharge le guide des prix Cardmarket et régénère ../index.html
```

`build.py --offline` réutilise le guide des prix déjà téléchargé.

| Fichier | Contenu |
|---|---|
| `build/template.html` | l'app (HTML, CSS, JS), dérivée de Ponyta & Galopa |
| `build/src/cards.json` | une entrée par carte : données TCGdex, produit Cardmarket FR/EN et produit japonais équivalent |
| `build/src/prices.json` | prix relevés sur Cardmarket par langue (`idProduct_langue`, 2 = français, 7 = japonais) |
| `img/` | images des cartes absentes de TCGdex (exclusivités japonaises, promos récentes, caméos) |

## Sources

TCGdex, Cardmarket, base communautaire des caméos de RotomAmiti, Bulbapedia. Projet de fan non officiel ; Pokémon et les illustrations des cartes appartiennent à Nintendo, Creatures et GAME FREAK.
