# Scheda — Fonti di asset e texture per palme e banchina

Ricerca del 2026-11-19 tramite le API pubbliche di Poly Haven, ambientCG e Sketchfab. **Niente è stato scaricato**
in `blender/` o `exports/`. Licenze e conteggi letti dalle API il 2026-11-19 [V]; il giudizio sui budget è mio [S].
Budget di riferimento (CLAUDE.md §4): palma <= 10k tri LOD0 + 2 LOD; modulo banchina <= 2k; prop <= 4k; texture 2048 ORM.
Ogni asset CC-BY usato va citato in `docs/CREDITS.md` (autore, titolo, URL, licenza).

## 1. Classifica: i 3 candidati migliori

| # | Asset | Uso | Licenza | Perché |
|---|---|---|---|---|
| 1 | **PlantCatalog — "Realistic HD Date palm (14/78)"** (P. dactylifera, preset *Urban no fruit*, Mature, 13,2 m) | **Sorgente** per PalmaA/B: si estraggono silhouette, texture delle fronde e del tronco, poi si rifà la mesh a card | CC BY 4.0, autore PlantCatalog (e-on software) | Specie giusta (quella di OSM), versione "urbana" potata, altezza giusta. Va ricostruita: vedi §2 |
| 2 | **Poly Haven / ambientCG — texture CC0** per ciglio, paramento, lastre, ghisa (elenco §3) | Kit banchina e pavimentazione | **CC0**, nessun obbligo | Qualità fotografica PBR fino a 8k, si riducono a 2048 e si impacchettano in ORM |
| 3 | **PlantCatalog — "Realistic HD Canary Island date palm (34/40)"** (P. canariensis, *Urban 2 no fruit*, Mature, 12,0 m) | Sorgente per PalmaC, solo se la foto conferma la canariensis | CC BY 4.0, autore PlantCatalog | Specie e potatura "urbana" giuste; stessa rielaborazione della #1 |

Alternativa rapida a basso costo: **"Date Palm" di evolveduk** (10.046 tri, CC BY 4.0, fatta con TreeIt): già nel budget,
ma qualità e aderenza alla Phoenix da verificare a occhio (potrebbe essere una palma generica).

## 2. Modelli di palma (Sketchfab, tutti scaricabili)

Attenzione sui PlantCatalog: il `faceCount` include **tutti i LOD**; le foglioline sono modellate una per una (migliaia),
con 15-20 materiali e ~30 texture. **Nessuno è usabile così com'è**: CLAUDE.md §4 vuole card masked, non foglie modellate.
Flusso consigliato: importare in un file di lavoro, renderizzare/bakare **una fronda** su una texture alfa 2048
(diffuse + normal + ORM), rifare tronco (cilindro 8-12 lati + normal delle basi fogliari) e chioma a card.
Risultato atteso 4-8k tri per palma.

| Modello | Specie / preset | H | Facce (tutti i LOD) | Mat / tex | Licenza / autore | URL | Giudizio |
|---|---|---|---|---|---|---|---|
| Realistic HD Date palm (14/78) | P. dactylifera, Urban no fruit, Mature | 13,2 m | 209.440 | 15 / 30 | CC BY 4.0, PlantCatalog | https://sketchfab.com/3d-models/realistic-hd-date-palm-1478-22c9b6b95d164a8cb818e6a3507530ec | **Migliore per PalmaA**. Fuori budget: solo come sorgente di bake |
| Realistic HD Date palm (16/78) | P. dactylifera, Urban no fruit, Old | 18,2 m | 166.844 | 7 / 15 | CC BY 4.0, PlantCatalog | https://sketchfab.com/3d-models/realistic-hd-date-palm-1678-2f34e3f54bef40eb8d94ca6507c2f822 | Più alta, meno materiali: sorgente per PalmaB |
| Realistic HD Date palm (12/78) | P. dactylifera, Urban no fruit, Adult | 8,6 m | 155.418 | — | CC BY 4.0, PlantCatalog | https://sketchfab.com/3d-models/28fb3114ae82495e859ae3cfda213d19 | Variante più bassa |
| Realistic HD Canary Island date palm (34/40) | P. canariensis, Urban 2 no fruit, Mature | 12,0 m | 195.717 | 19 / 28 | CC BY 4.0, PlantCatalog | https://sketchfab.com/3d-models/realistic-hd-canary-island-date-palm-3440-d5bfe8c158a3444a844aa202b58eda33 | **Migliore per PalmaC** (sorgente di bake) |
| Realistic HD Canary Island date palm (29/40) | P. canariensis, Urban 1 no fruit, Mature | 11,7 m | 292.183 | 20 / 29 | CC BY 4.0, PlantCatalog | https://sketchfab.com/3d-models/realistic-hd-canary-island-date-palm-2940-70e4e0ca953144c8b485fc6e4d2d3aca | Alternativa |
| Date Palm | "date palm" generica (TreeIt) | — | 10.046 | 4 / 14 | CC BY 4.0, evolveduk | https://sketchfab.com/3d-models/date-palm-11acf710e6c149daa8d6fb8cdc5d087f | **Nel budget** subito; aderenza da verificare |
| Phoenix Dactylifera F / M; Phoenix Canariensis | modelli architettonici | — | 1,1 M / 7,0 M / 3,7 M | — | CC BY 4.0, Hervé Rey | https://sketchfab.com/3d-models/9910487ed1e245859e812d83858a3f14 · https://sketchfab.com/3d-models/9d5798df6c1e4c22af50d3e251877b77 | Troppo pesanti: solo riferimento visivo |
| Date Palm Tree | low poly | — | 1.120 | 1 / 0 | CC BY 4.0, neutralize | https://sketchfab.com/3d-models/date-palm-tree-610b8f36efde491aafa4544ef8c5dcfc | Stile low poly: **non adatto** al look realistico |
| Exotic Low-Poly Plants Pack | vari | — | 28.190 | 22 / 0 | CC BY 4.0, dicramble | https://sketchfab.com/3d-models/exotic-low-poly-plants-pack-fceb7deeae26441c8b394426568c2cab | Non adatto (low poly) |

Licenza CC BY 4.0 (Sketchfab, [V]): uso commerciale consentito, autore da citare. Prima del download controllare sulla pagina
che la licenza non sia cambiata.
**Poly Haven:** nessun modello di palma (verificato sull'elenco API). **ambientCG:** nessun modello o atlas di palma.
**Poly Pizza:** solo low poly, non adatto al look realistico.
Fuori dalla lista di CLAUDE.md §5 (serve decisione dell'utente): Fab/Megascans (licenza Fab, non CC) e le palme native di
Fortnite in UEFN (gratuite in UEFN, ma in stile cartoon).

## 3. Texture PBR CC0

Tutte CC0 [V]: Poly Haven e ambientCG pubblicano tutto in CC0. Scaricare a 2k (o 4k e ridurre), impacchettare AO-Roughness-Metallic in ORM.

### Ciglio e paramento della banchina
| Texture | Sito | Scala reale | Uso | URL |
|---|---|---|---|---|
| Large Sandstone Blocks (Rob Tuytel) | Poly Haven | 3 × 3 m, trimsheet | **paramento** in blocchi grigi macchiati; anche fascia del ciglio | https://polyhaven.com/a/large_sandstone_blocks |
| Concrete Floor Worn 001 | Poly Haven | 3 × 3 m | ciglio in cemento consumato, se la foto lo conferma | https://polyhaven.com/a/concrete_floor_worn_001 |
| Concrete 046 / Concrete 034 | ambientCG | 2,4 m / 1,1 m | blocchi prefabbricati lisci | https://ambientcg.com/view?id=Concrete046 · https://ambientcg.com/view?id=Concrete034 |
| Coast Land Rocks 01 | Poly Haven | — | massi o scogliera sotto il pelo dell'acqua, se ci sono | https://polyhaven.com/a/coast_land_rocks_01 |
| Granite 004A/B | ambientCG | — | ciglio in granito (è un granito "da piano", va invecchiato) | https://ambientcg.com/view?id=Granite004A |

### Pavimentazione
| Texture | Sito | Scala reale | Aderenza | URL |
|---|---|---|---|---|
| **Slab Tiles** | Poly Haven | 2,37 × 2,37 m | lastre di pietra lisce: la più vicina a "lastre di pietra chiara" | https://polyhaven.com/a/slab_tiles |
| **Paving Stones 144** | ambientCG | — | lastre rettangolari grigie moderne, posa a correre | https://ambientcg.com/view?id=PavingStones144 |
| Paving Stones 136 | ambientCG | — | quadrotte grigie urbane | https://ambientcg.com/view?id=PavingStones136 |
| Stone Tiles 02 | Poly Haven | 2 × 2 m | lastre irregolari, più rustiche | https://polyhaven.com/a/stone_tiles_02 |
| Square Concrete Pavers | Poly Haven | 1,8 × 1,8 m | masselli di cemento quadrati | https://polyhaven.com/a/square_concrete_pavers |
| Paving Stones 125A / 126A | ambientCG | 3,5 × 3,5 m | cubetti/sett per la strada sul molo (`surface=sett`) | https://ambientcg.com/view?id=PavingStones125A |

### Ghisa e metalli (bitte, anelli, scalette)
| Texture | Sito | Uso | URL |
|---|---|---|---|
| Metal 029 (nero verniciato a polvere) | ambientCG | bitta in ghisa verniciata nera | https://ambientcg.com/view?id=Metal029 |
| Painted Metal 014 (grigio con ruggine) | ambientCG | bitta grigia consumata | https://ambientcg.com/view?id=PaintedMetal014 |
| Rusty Metal 02 / Rust Coarse 01 | Poly Haven | anelli, piastre di base, scalette | https://polyhaven.com/a/rusty_metal_02 · https://polyhaven.com/a/rust_coarse_01 |
| Green Metal Rust | Poly Haven | metallo verniciato verde arrugginito (ringhiere) | https://polyhaven.com/a/green_metal_rust |

### Modelli Poly Haven utili (CC0) per altri task
| Modello | Tri | Nota | URL |
|---|---|---|---|
| Cannon 01 (ghisa) | 41.444 | i cannoni a X 249 e 259: fuori budget prop (4k), va decimato o rifatto; utile come riferimento | https://polyhaven.com/a/cannon_01 |
| Street Lamp 01 / 02 | — | lampioni, se lo stile coincide (foto lampione ancora mancante) | https://polyhaven.com/a/street_lamp_01 |
| Pine Tree 01 | 17,4 M | è un pino generico, **non** Pinus pinea: non adatto | https://polyhaven.com/a/pine_tree_01 |

## 4. Cosa conviene modellare da zero
- **Tronco della palma** (tutte le varianti): cilindro low poly con normal map; nessun asset gratuito ha un tronco già nel budget.
- **Card delle fronde**: bake da PlantCatalog oppure dipinte; una texture 2048 con 3-4 fronde diverse per tutte le varianti.
- **Kit banchina** (modulo 4 m, testata, angolo): geometria semplice, il realismo lo danno le texture CC0 del §3.
- **Bitta** (300-600 tri), **anello**, **scaletta** (500-1k), **parabordo**: forme semplici, più veloce rifarle che cercarle.
- **Lastre del camminamento**: piano con texture tiling a 4 m o 2 m + decal di macchie; niente geometria per lastra.
- **Striscia tattile** al cordolo: texture con normal map, nessuna geometria.
