# ref/dem — modello del terreno per il fondale delle colline

Scheda d'uso: `ref/fondale.md`. Generato dal geo-scout il 2026-11-19.

## Fonte
| Voce | Valore |
|---|---|
| Dataset | **Copernicus DEM GLO-30** (istanza pubblica "COP-DEM-GLO-30-F", Copernicus WorldDEM-30) |
| Tipo | **DSM** (superficie: include edifici e chiome degli alberi, non solo il suolo) |
| Tile sorgente | `Copernicus_DSM_COG_10_N44_00_E009_00_DEM` e `..._N44_00_E010_00_DEM` |
| Accesso | AWS Open Data, https://registry.opendata.aws/copernicus-dem/ (bucket `copernicus-dem-30m`), scaricato il 2026-11-19 |
| Risoluzione | 1 arcosecondo (≈ 30,9 m N-S × 22,2 m E-O a 44° N); quote in metri sul geoide EGM2008 (≈ s.l.m.) |
| CRS | WGS 84 geografico (EPSG:4326), quote EGM2008 |
| Licenza | "Licence for the use of the Copernicus WorldDEM-30" (COP-DEM-GLO-30-F Global 30m Full, Free & Open). Testo: https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/DEM/resources/license/License-COPDEM-30.pdf |

Le tile originali (36 e 46 MB) **non** sono nel repository: si riscaricano dall'URL sopra.

## Licenza (letta dal PDF ufficiale, 2026-11-19) [V]
- Art. 3: diritti mondiali e senza limiti di tempo. Art. 5: gratuiti.
- Art. 4: diritti non esclusivi di (a) riproduzione, (b) distribuzione, (c) comunicazione al pubblico,
  (d) adattamento, modifica e combinazione con altri dati. Nessuna esclusione per l'uso commerciale.
- Art. 6 (obblighi): citare la fonte; per dati modificati (il nostro caso: mesh del fondale) usare la nota
  **"produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018
  provided under COPERNICUS by the European Union and ESA; all rights reserved."**;
  chi ridistribuisce deve aggiungere "The organisations in charge of the Copernicus programme by law or by delegation
  do not incur any liability for any use of the Copernicus WorldDEM-30"; non far credere a un'approvazione ufficiale.
- Il WorldDEM-10 (risoluzione più alta) è escluso: non usarlo.

## File
| File | Contenuto | Formato |
|---|---|---|
| `cop30_golfo_spezia_wgs84.tif` | Ritaglio **lat 44.02–44.19, lon 9.70–9.97** (972 × 612 px, ≈ 21,7 × 18,9 km), quote originali | GeoTIFF float32 non compresso, EPSG:4326, nodata −32767 |
| `morin_local_30m.npy` | Stesso terreno ricampionato (bilineare) nella **terna del progetto** (`ref/area.md`): griglia 669 × 669, passo 30 m, X e Y da −10 020 a +10 020 m. Riga 0 = Y +10 020 (lato città, NO), colonna 0 = X −10 020 (SO). Quota in metri s.l.m. | NumPy float32 |
| `morin_local_30m_h16.png` | Stessa griglia come heightmap 16 bit: **quota_m = valore / 20 − 20** (passo 5 cm). Stesso orientamento | PNG grigio 16 bit |
| `morin_local_30m_clc.npy` | Classe CORINE 2018 (codice a 3 cifre, 0 = nessun poligono) per ogni cella della griglia locale | NumPy int16 |
| `morin_local_30m_colore_clc.png` | Colore base proposto per classe CORINE (tabella in `ref/fondale.md` §5), stessa griglia | PNG RGB 8 bit, 669 × 669 |
| `morin_local_30m_visibile_spawn.png` | Celle di terreno visibili dalla partenza del giocatore (255 = visibile) | PNG grigio 8 bit |
| `orizzonte_<punto>_colline.csv` | Profilo dell'orizzonte ogni 1° considerando solo terreno oltre 1,5 km (cresta delle colline) | CSV |
| `orizzonte_<punto>_tutto.csv` | Idem ma da 250 m (include città, alberi e il colle del centro: è un DSM) | CSV |
| `cime_osm.csv` | Cime e selle OSM (`natural=peak/saddle`) con azimut, distanza, elevazione angolare e visibilità dalla partenza | CSV |
| `copertura_per_azimut_spawn.csv` | Copertura del suolo (CORINE) del terreno visibile oltre 1,5 km, per fasce di 15° (% delle celle visibili) | CSV |
| `edifici_osm_1200m.csv` | 168 edifici OSM entro 1,2 km dall'origine con `building:levels` o `height`, altezza stimata (piani × 3,2 + 1,3 m), quote DSM, elevazione angolare dalla partenza | CSV |

Nota: la maschera `..._visibile_spawn.png` comprende anche le celle di mare.
CORINE Land Cover 2018 (vettoriale, MMU 25 ha) scaricato il 2026-11-19 dal servizio EEA
`image.discomap.eea.europa.eu/arcgis/rest/services/Corine/CLC2018_WM/MapServer/0` (166 poligoni nel ritaglio).
Licenza: dati CLMS "full, open and free" (Reg. delegato UE 1159/2013), https://land.copernicus.eu/en/data-policy;
nota richiesta per prodotti derivati: "Generated using European Union's Copernicus Land Monitoring Service information",
DOI vettoriale https://doi.org/10.2909/71c95a07-e296-44fc-b22b-415f42acfdf0.

Punti di vista (`<punto>`), occhi a **3,3 m s.l.m.** (banchina +1,5 m [S] + 1,8 m):
`spawn` X 240, Y 84,5 (UE 24000, −8450) · `imbocco_ponte` X 0, Y 0 · `meta_blocco` X 125, Y 84,5 · `fine_passeggiata` X 550, Y 84,5.

Colonne dei CSV d'orizzonte: `azimut_deg` (da nord, orario) · `elev_deg` (angolo sopra l'orizzontale, con curvatura
terrestre e rifrazione k = 0,13) · `dist_m` (distanza del punto di cresta) · `quota_cresta_m` · `tipo` (terra/mare) ·
`lat, lon` del punto di cresta · `prima_terra_m` (distanza del primo terreno > 2 m lungo il raggio, a partire dalla distanza minima).
Per `tipo = mare` l'elevazione è l'abbassamento dell'orizzonte marino (−0,058°) e la distanza è quella dell'orizzonte geometrico (6,5 km).

## Conversioni
Terna del progetto (da `ref/area.md`): origine node OSM 10249190464 (lat 44.1016154, lon 9.8252769), X ad azimut 41,3°.
`E = X·sin41,3° − Y·cos41,3°`, `N = X·cos41,3° + Y·sin41,3°`; `lat = 44.1016154 + N/111 114,2`, `lon = 9.8252769 + E/80 069,2`
(metri per grado a 44,1° N). In Blender Z = quota s.l.m. − 1,5 m (Z 0 = banchina) [S sulla quota della banchina].

## Limiti noti
- È un **DSM**: in città e nei boschi le quote includono tetti e chiome (+5…25 m). Per le colline lontane è irrilevante;
  sotto 1,5 km (città) non usarlo come suolo.
- Fuori dalle due tile (a sud di 44° N) il terreno è trattato come mare: interessa solo raggi oltre ~11 km verso sud,
  dove c'è comunque mare aperto (costa toscana sotto l'orizzonte o nascosta dalle colline di Lerici).
- Precisione verticale dichiarata del GLO-30: < 4 m (90 % LE) [V da specifica del prodotto, non riletta qui: S].
- Script di calcolo in `ref/dem/script/` (Python + NumPy; eseguiti con l'interprete Python incluso in Blender, da riga di
  comando, senza aprire Blender): `tiff.py` (lettore GeoTIFF minimo), `horizon.py` (mosaico, ritaglio, griglia locale, orizzonti),
  `landcover.py` (CORINE, visibilità), `peaks.py` (cime OSM), `plot.py` (grafico `docs/qa/fondale_profilo.png`, reso con Edge headless).
  Richiedono le tile e i JSON scaricati in una cartella di lavoro (vedi argomenti in testa a ogni script).
