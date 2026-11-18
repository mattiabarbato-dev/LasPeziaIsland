# Progetto: Piazza di La Spezia in Fortnite (UEFN)

Ricostruzione di una piazza reale di La Spezia come isola Fortnite giocabile.
Pipeline: dati OpenStreetMap -> Blender (Blosm + Blender MCP) -> FBX -> UEFN (UEFN MCP) -> Verse.

## Server MCP disponibili
- `blender`         -> controlla Blender (oggetti, materiali, esecuzione Python, Poly Haven / Poly Pizza)
- `unreal-mcp`      -> controlla l'editor UEFN (attori, device, Verse, sessioni di gioco)
- `unreal-insights` -> profilazione / performance UEFN

Prima di usare Blender o UEFN verifica che il server risponda. Se non risponde, FERMATI e chiedi
all'utente di aprire l'applicazione (Blender: pannello "MCP for Blender" su Connected).

## Struttura cartelle
- `ref/`      foto di riferimento, misure, dati OSM grezzi
- `blender/`  file .blend di lavoro (uno per area/asset principale)
- `exports/`  FBX pronti per UEFN (solo output finali, niente file di lavoro)
- `docs/`     note tecniche, decisioni, CREDITS.md
- `PLAN.md`   stato del progetto: fasi, task, chi li fa, cosa è fatto

## Regole tecniche
- **Scala**: in Blender si lavora in metri (Unit Scale 1.0). 1 m Blender = 100 unità Unreal.
  Al primo export verifica in UEFN con un cubo di 1 m che la scala sia corretta, e annota in docs/ il preset usato.
- **Export FBX**: Selected Objects, Apply Scalings = "FBX Units Scale", Apply Modifiers, Embed Textures,
  Path Mode = Copy. Un FBX per asset o per blocco di edifici, mai l'intera piazza in un unico file.
- **Naming**: `SM_` mesh, `M_` materiali, `T_` texture, `UCX_<NomeMesh>_00` collisioni convesse.
- **Budget poligoni** (l'isola deve girare anche su mobile):
  edificio di sfondo <= 5k tri, edificio affacciato sulla piazza <= 20k tri, prop <= 2k tri.
  Usa Decimate o rimodella; mai importare mesh fotogrammetriche grezze.
- **Collisioni**: sempre box/convex semplici (UCX_), mai collisione per-poligono su mesh complesse.
- **Texture**: max 2048 px per edifici principali, 1024 px per il resto. PNG o JPG.

## Licenze dei dati (importante per la pubblicazione)
- OpenStreetMap: ok, licenza ODbL -> attribuzione "© OpenStreetMap contributors" in docs/CREDITS.md.
- Poly Haven: CC0, ok.
- Poly Pizza / Sketchfab: controlla la licenza di OGNI modello; se CC-BY aggiungi autore in docs/CREDITS.md;
  se non commerciale o licenza non chiara, NON usarlo.
- Google Maps / Google Earth / 3D Tiles: SOLO come riferimento visivo. Mai esportare geometria
  o texture Google in exports/.

## Regole di sicurezza
- Non cancellare attori in UEFN né file in `exports/` / `blender/` senza conferma esplicita dell'utente.
- Non pubblicare mai l'isola (né "Carica in versione privata" né "Pubblica progetto"): lo fa l'utente.
- Prima di modifiche grosse in Blender salva il .blend; prima di modifiche grosse in UEFN chiedi un commit Git.
- Dopo ogni task aggiorna `PLAN.md` (stato + note brevi).

## Lavoro in team
L'orchestratore (sessione principale) legge PLAN.md, assegna i task ai subagent in `.claude/agents/`,
e verifica il risultato prima di segnarlo come fatto. Un task alla volta per server MCP
(Blender e UEFN non gestiscono bene comandi concorrenti).
Lingua di lavoro: italiano.
