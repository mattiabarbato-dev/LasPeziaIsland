# Scheda — Palme e alberi dei filari (Blocco 1)

Legenda: **[V]** verificato (fonte citata) · **[S]** stima motivata, da confermare.
Scopo: riferimento per blender-artist per `SM_Morin_PalmaA` + 2 varianti (CLAUDE.md §4: palma <= 10k tri LOD0,
2 LOD, foglie su card masked two-sided, texture 2048). Posizioni dei filari: `sezione.md` §1 e §3.
Fonti consultate il 2026-11-19. Nessuna immagine o geometria Google è stata salvata: Google solo come riferimento visivo.
Le foto di Wikimedia Commons non si sono potute scaricare dal sandbox: **nessuna verifica visiva fatta da me**.

## 0. Aggiornamento dalle foto dell'utente (2026-11-19, `ref/foto/palme/`, `ref/foto/banchina/`) — prevale sui §1-3

| Dato | Valore | Stato |
|---|---|---|
| Specie dominante dei filari | **Phoenix canariensis**: tronco grosso, cicatrici fogliari a rombi, "ananas" ben visibile sotto la chioma, chioma molto piena e tondeggiante | [V foto utente] (`palma_1.png`, `Immagine 2026-11-19 055957.png`, `passegiata_1.png`) |
| Altre palme | alcune più alte e slanciate, chioma più rada: probabile P. dactylifera → varianti B/C | presenza [V foto utente]; specie [S] |
| Fronde | pennate, **verde scuro**, arcuate e pendenti; a volte qualche fronda secca marrone in basso | [V foto utente] |
| Tronco | Ø ~0,6-0,8 m, spesso leggermente inclinato; nessuna gonna di foglie secche | aspetto [V foto utente]; Ø [S] a occhio |
| Stipite / chioma | stipite ~7-9 m, chioma Ø ~8-9 m | [S] a occhio dalle foto |
| Luminarie a spirale sui tronchi | presenti | [V foto utente]. Non modellate (decisione del 2026-11-19) |
| Aiuole | palme dentro aiuole quadrate bordate di pietra chiara, nella fascia a cubetti | [V foto utente] |

Conseguenza: `SM_Morin_PalmaA` = **P. canariensis** (prima versione fatta il 2026-11-19: stipite 8 m, Ø 0,70 m,
ananas Ø ~1,1 m a 7-9 m, chioma ~9 m). Le dactylifera diventano le varianti.

## 1. Specie

| Dato | Valore | Stato e fonte |
|---|---|---|
| Specie dei due filari della passeggiata (way 378875629 e 378875631) | **Phoenix dactylifera** ("Palma da datteri") | [V] come dato di mappatura: tag OSM `species` e `species:it` (utente ivanbranco, 2024-04-24). © OpenStreetMap contributors. Un tag OSM non è un rilievo botanico |
| Composizione del patrimonio comunale | "circa 200 palme delle Canarie e palme da datteri, principalmente concentrate in passeggiata Morin e nei Giardini Storici" | [V] Comune della Spezia citato da Città della Spezia, 22-10-2014 ([link](https://www.cittadellaspezia.com/?p=168460)). Il dato non dice quale specie stia nei filari della Morin |
| Conclusione operativa | Filari **a prevalenza Phoenix dactylifera** (OSM), con **possibile presenza di Phoenix canariensis** (articolo 2014) | **[S] certezza media.** Le due fonti sono compatibili: probabilmente dactylifera nei filari e canariensis nei Giardini storici, ma può anche essere un filare misto |
| Washingtonia (robusta / filifera) | Nessuna fonte la colloca sulla Morin o nei Giardini a Mare | [S] probabilità bassa. Non modellarla |
| Altri alberi nei filari delle palme | Nessuno mappato. Gli unici altri filari sono quelli sotto | [V] OSM |
| Pini | Filare di **Pinus pinea** (pino domestico, a ombrello) a Y ≈ 113, X 18-85 | [V] OSM way 850396605 |
| Oleandri | Filare di *Nerium oleander* a Y ≈ 119,5, X 131-556 | [V] OSM way 850406862 (tag `species=oleandro`, `genus=Apocynaceae`) |
| Filare senza specie | way 378875630, semi_evergreen, a X ≈ -108 → -4, Y ≈ 137: lato città oltre il molo, **fuori dalla passeggiata** | [V] OSM. Non riguarda i filari di palme |
| Storico | P. dactylifera è già presente nei giardini e viali di Spezia nel 1887 | [V] A. Bracciforti, *Flora dei giardini pubblici e viali di Spezia*, 1887 ([Wikisource](https://it.wikisource.org/wiki/Flora_dei_giardini_pubblici_e_viali_di_Spezia)) |
| Luminarie | Il Comune rinnova le luminarie "del tronco e della chioma delle palme in modo alternato" (2025-2028) | [V] Città della Spezia, 24-11-2025 ([link](https://www.cittadellaspezia.com/2025/11/24/altri-tre-anni-di-lucine-sulle-palme-di-passeggiata-morin-il-comune-investe-134mila-euro-628920/)). Le luci sul tronco fanno pensare a **tronchi puliti**, senza gonna [S] |

**Rischio da conoscere:** il punteruolo rosso attacca solo il genere *Phoenix* [V, stesso articolo del 2014].
Alcuni esemplari potrebbero essere stati sostituiti dopo il 2014 (a Genova si propongono Washingtonia e dactylifera
come sostitute delle canariensis [V, mozione Comune di Genova 2019]). Per questo serve la foto (§5).

## 2. Morfologia delle due specie candidate (dati di specie, non misurati sul posto)

| Carattere | **Phoenix dactylifera** (PalmaA, specie OSM) | **Phoenix canariensis** (variante C) | Fonte |
|---|---|---|---|
| Altezza totale | di solito 15-20 m, max 30 m | 10-20 m, max 40 m | [V] it.wikipedia |
| Tronco (stipite) | **slanciato**, Ø ~0,3-0,5 m [S]; spesso polloni o più fusti dalla stessa radice (in un filare urbano di solito monocaule [S]) | **robusto, Ø 70-90 cm** | [V] it.wikipedia; Ø dactylifera [S] |
| Foglie | **pennate** (non a ventaglio), lunghe 3-5 m, ~150 foglioline lunghe 30 cm e larghe 2 cm, picciolo spinoso | **pennate**, lunghe 4-5 (6) m, 80-100 segmenti per lato del rachide | [V] it.wikipedia |
| Colore foglie | **verde-grigio**, glauche sotto | **verde cupo** | [V] it.wikipedia |
| Numero di foglie verdi | chioma rada, ~20-40 [S] | 75-125 foglie vive (record 443) | canariensis [V] en.wikipedia; dactylifera [S] |
| Diametro chioma | fino a 10 m | 8-12 m [S] | [V] it.wikipedia (dactylifera) |
| Base della chioma potata | moncherini delle foglie (basi) a spirale sul tronco | dopo la potatura la base della chioma ha la forma di un **ananas** (losanghe delle basi fogliari) | [V] en.wikipedia (canariensis) |
| Gonna di foglie secche | in un viale curato **assente** (foglie secche potate) | idem | [S] da verificare in foto |

### Misure proposte per i modelli (da confermare con la foto §5)

| Variante | Specie | Stipite (piede → base chioma) | Ø tronco a 1 m | Chioma | N. foglie | Note |
|---|---|---|---|---|---|---|
| **SM_Morin_PalmaA** | P. dactylifera | **10 m** [S] | 0,40 m [S] | Ø 7 m, foglie 4 m, arco ampio | 24-28 card [S] | Tronco a squame regolari, leggera curvatura |
| **SM_Morin_PalmaB** | P. dactylifera | **8 m** [S] | 0,38 m [S] | Ø 6 m | 20-24 card [S] | Curvatura e rotazione diverse; serve a rompere la ripetizione |
| **SM_Morin_PalmaC** | P. canariensis | **7 m** [S] | 0,80 m [S] | Ø 9 m, foglie 5 m, chioma piena e sferica | 40-50 card [S] | "Ananas" alla base della chioma. Usarla solo se la foto conferma canariensis o filare misto |

Coerenza con il blockout: oggi il segnaposto è Ø 0,5 × 9 m con chioma 6 m a Z 8-10 (PLAN.md). Va bene per PalmaA.
Linea di vista (CLAUDE.md §3): la chioma a 8-11 m non copre le antenne del ponte (35 m s.l.m.) se si guarda dalla corsia,
ma conviene controllarlo dalla partenza con le palme vere.

## 3. Passo e disposizione del filare

| Dato | Valore | Stato |
|---|---|---|
| Filari | 2, a Y 92,6 e 99,6 (7,0 m tra le file), lunghi ~536 m | [V] OSM |
| Alberi singoli in OSM | **assenti** (le way dei filari hanno 2-3 nodi, nessun `natural=tree`) | [V] OSM, ricontrollato oggi sull'estratto `ref/osm/morin_bbox.osm` |
| Passo | **~9 m: nessun dato migliore trovato** | **[S]** |
| Controllo di coerenza | con passo 9 m: ~60 palme per fila, ~120 in tutto sulla Morin. Il Comune ne conta ~200 tra Morin e Giardini storici (2014). Con passo 6 m sarebbero ~180 solo sulla Morin: poco compatibile. Il passo 8-10 m è quindi **plausibile** | [S] ragionamento su dato [V] |
| Disposizione tra le file | allineata o sfalsata: non nota (il blockout usa sfalsata) | [S] |

## 4. Note per blender-artist
- Foglie pennate: una card per foglia (o per mezza foglia) con texture della fronda intera in alfa; rachide piegato
  con 3-5 segmenti. Niente foglioline modellate (CLAUDE.md §4).
- Tronco: cilindro 8-12 lati con normal map delle basi fogliari; il "collare" sotto la chioma (basi tagliate) è il dettaglio
  che rende riconoscibile una Phoenix potata.
- Collisione: solo UCX sul tronco (cilindro convesso), nessuna sulla chioma.
- Fonti di asset e texture: `ref/asset_fonti.md`.

## 5. Foto che servono all'utente (`ref/foto/`) — i dati restano [S] senza
1. **Una palma intera**, da circa 20 m sul camminamento, con una persona ai suoi piedi: specie, altezza dello stipite, forma della chioma.
2. **Dettaglio del tronco** a 1-2 m d'altezza, con una mano o un oggetto noto accanto: diametro e trama delle basi fogliari.
3. **Base della chioma** dal basso: c'è l'"ananas" (canariensis) o il collare stretto (dactylifera)? Ci sono foglie secche pendenti?
4. **Il filare d'infilata**, dall'angolo vicino alla statua della Sirena (X ≈ 14) guardando verso nord-est: tutte uguali o miste? allineate o sfalsate?
5. **Conteggio**: numero di palme di una fila tra la pensilina (X ≈ 40) e l'ancora (X ≈ 226), anche solo contate a piedi. Dà il passo.
6. Facoltativo: un pino del filare a Y 113 e un oleandro, interi.

---

## 6. Correzione 2026-11-20: inizio passeggiata e passo (prevale sul §3 e sui layout v3/v4)

Geo-scout, 2026-11-20. Fonti: OSM (estratti `ref/osm/*.osm` + Overpass in sola lettura il 2026-11-20 alle 21:49 UTC, dati identici),
foto `ref/foto/vista/vista__statua.png` (S1), `vista__statua2.png` (S2), `vista_inizio_passeggiata.png` (S3), conteggio dell'utente.
Calcoli di prospettiva su S1/S3 con camera a ~2,5 m e FOV ~90-100° [S]: dettagli in `ref/foto_nuove_2026-11-20.md` §13.
Legenda come sopra; **[V-utente]** = detto dall'utente, **[V-foto]** = si vede nella foto.

### 6.1 Il passo è 8 m, non 9: tre fonti indipendenti concordano
| Fonte | Dato | Passo che ne esce | Stato |
|---|---|---|---|
| OSM filare 1 (way 378875629) | da **(20,4; 92,9)** a **(556,9; 91,6)**: 536,5 m | 536,5 / 67 = **8,01 m** con 68 palme | [V] estremi; passo [S] (OSM non mappa le singole palme: 0 nodi `natural=tree`, ricontrollato con Overpass) |
| OSM filare 2 (way 378875631) | da **(20,4; 99,6)** a **(555,8; 99,5)**: 535,4 m | 535,4 / 67 = **7,99 m** | come sopra |
| Conteggio dell'utente | **68 per filare, 136 in tutto** | con gli estremi OSM: 8,0 m | [V-utente] ("se ho contato bene") |
| Panchine OSM in pietra, Blocco 2 (9 nodi, check 2025-11-01) | X 256,1 · 271,7 · 288,2 · 304,5 · 319,9 · 336,5 · 352,2 · 368,6 · 384,2 (Y 92,4-93,1, cioè **sulla linea del filare 1**) | regressione: **16,05 m** (residuo max 0,7 m) = 2 × 8,03 | [V] OSM |
| Panchine OSM, Blocco 1 | X 31,7 · 49,0 · 64,0 (Y 92,8) | stessa griglia: 32,4 / 48,4 / 64,4 (scarti −0,7 / +0,6 / −0,4) | [V] OSM |
| Fase della griglia | le 12 panchine cadono tutte **a metà fra due palme** della griglia 20,4 + 8k (punti 32,4 + 16k) | conferma indipendente di inizio e passo | [V] calcolo su dati OSM |

**Conclusione:** passo **8,0 m** [V, tre fonti concordi; ±0,1 m], prima coppia a **X 20,4**, ultima a **X 556,4**, **68 palme per filare**.
Il conteggio dell'utente è esatto. Il "9 m [S]" del §3 era solo una proposta e va abbandonato.
Nota: il filare 1 in OSM scende da Y 92,9 a 91,6 lungo 536 m (filare 2 dritto a 99,6). È dentro l'errore di mappatura (e il cordolo OSM
va nel verso opposto, da 88,7 a 90,3): **tenere Y 92,6 e 99,6 costanti** come oggi [S].

### 6.2 Pianta dell'inizio della passeggiata (X ≈ 5 → 45)
| Elemento | Posizione reale (X; Y) | Stato | Nel gioco oggi | Errore |
|---|---|---|---|---|
| Strada di servizio (asfalto) | asse X ≈ 9, bordo est (cordolo) X ≈ 10-11,6 | [V] asse OSM 238848818; bordo [S] `radice_molo.md` | asfalto fino a 9,55, fascia da 9,75 | ok (scarto ≤ 2 m già noto) |
| **Angolo in cubetti senza palme** ("marciapiede") | **X ≈ 10 → 18,6** (bordo dell'aiuola della prima palma), Y 89 → ~108 | [V-utente] + [V-foto] S1, S3: nessuna palma fra la strada e la prima coppia | c'è una coppia di palme a X 12 | **2 palme e 2 aiuole in più** |
| **Sirena** ("La Sirena del Golfo dei Poeti") | **(13,8; 91,9)** | [V] OSM node 9592234744; S1 coerente (statua sul basamento a ~1 m dal bordo dell'asfalto, davanti alla prima palma) | (13,8; 91,9), yaw −170 | posizione **giusta**; il guaio è l'aiuola F1_01 (X 10,2-13,8; Y 91,1-94,1) che si sovrappone al basamento (X 13,1-14,5) per ~0,7 × 1,0 m, con il tronco a 1,9 m |
| **Lampione a 2 globi sovrapposti** ("in corrispondenza della statua") | **(15,3; 101,9) ± 1,5 m**: stessa X della Sirena, all'altezza del filare lato città, ~3 m prima dell'aiuola della prima palma del filare 2 | posizione [S] da S3 (camera ≈ (16; 108)) e S1 (palo in primo piano con resti di manifesti e ombra del globo, camera ≈ (14,9; 102,6)); esistenza e tipo [V-foto] S1-S3 | `Arte_Molo_Lampione2Globi_00` a **(13,0; 106,0)** (stima 2023 da F1, `radice_molo.md`) | **≈ +2,3 m in X, −4,1 m in Y** [S]: le due stime non concordano, serve la conferma dell'utente (D-P2) |
| Cestino | **(18,0; 91,3)** | [V] OSM node 5913688317; [V-foto] S1, S3 | (18,55; 92,1) | 0,9 m, ma con le aiuole nuove tocca l'aiuola (0,2 m) → spostare a **(17,9; 91,3)** |
| Palo "accesso autorizzati / area pedonale" | a ridosso dell'aiuola della prima palma del filare 1, lato ponte, ≈ (18,4; 92,5) | [V-foto] S1, S2; posizione [S] ±1,5 m | assente | prop nuovo opzionale (cartello generico, testo pubblico) |
| **Prima coppia di palme** | **X 20,4** (filare 1 Y 92,6, filare 2 Y 99,6) | [V] OSM (entrambi i filari); [V-foto] S3 (le prime due palme, una dietro l'altra, sono la coppia allineata; X calcolata ≈ 20 ± 1,5) e S1 (prima palma del filare 1 a ≈ (20,6; 91,4)) | X 12 | **+8,4 m** |
| Seconda / terza / quarta coppia | 28,4 / 36,4 / 44,4 | [V] (passo §6.1) | 21 / 30 / 39 | +7,4 / +6,4 / +5,4 |
| Prima panchina (pietra, con schienale) | **(32,4; 92,1)** (OSM 31,7; 92,8) | [V] OSM | Panchina_00 a 16,5, Panchina_01 a 34,5 | la 16,5 non esiste (nell'angolo non ci sono panchine: OSM e S1) |
| **Pensilina (gazebo)** | OSM way 626400743 `amenity=shelter`, `shelter_type=pavilion`: centro **(39,6; 93,2)**, Ø ~3,0 m, con 4 panchine OSM all'interno (38,7-40,5) | [V] OSM | (25,5; 93,0) | **−14,1 m**; con la griglia 8 m cade fra la 3ª e la 4ª palma (36,4 e 44,4, centro 40,4). Vedi D-P1 |
| Secondo cestino | (41,9; 92,4) | [V] OSM node 5913688321 | 36,55 | con la pensilina a 40,4 cade sotto la gronda: proporre (41,9; 90,5), fra pensilina e cordolo [S] |
| Primo lampione "normale" (2 globi su bracci) | ≈ X 31-33, dietro la prima panchina | [S] da S3 (a sinistra, accanto a una panchina) + regola "ogni 4 palme dietro una panchina" [V-utente 2026-11-19] | Lampione_00 a 16,8 | ≈ +16 m |

Sequenza reale lungo il filare 1 (lato mare) [V OSM + S]: cestino 18,0 · **palma 20,4** · (varco 24,4 libero) · palma 28,4 · **panchina 32,4 + lampione** ·
palma 36,4 · **pensilina 40,4** · palma 44,4 · panchina 48,4 · palma 52,4 · varco 56,4 (rastrelliera OSM a 59,0) · palma 60,4 · panchina 64,4 · …

### 6.3 Layout corretto proposto (griglia "v5", sostituisce il v4 mai applicato)
| Voce | Valore | Stato |
|---|---|---|
| Palme | X = **20,4 + 8k**, k = 0…67; filare 1 Y 92,6, filare 2 Y 99,6, **allineati** (coppie) | X [V]; allineamento [V-utente 2026-11-19 + V-foto S3] |
| Prima / ultima coppia | **20,4** / **556,4** | [V] |
| Numero | **68 per filare, 136 in tutto** (oggi 61 per filare, 122) | [V] |
| Divisione fra blocchi | Blocco 1: k 0-29, X 20,4 → 252,4 (**30 per filare, 60**; oggi 54). Blocco 2: k 30-67, X 260,4 → 556,4 (**38 per filare, 76**; oggi 68) | proposta |
| Aiuole | una per palma, 3,6 × 3,0 m come oggi: varco libero fra due aiuole **4,4 m** (oggi 5,4) | misure [S] (S3: aiuola ~3,5 m, coerente) |
| Strisce trasversali della fascia | a metà fra due palme: X = **24,4 + 8k** | regola [V-utente 2026-11-19] |
| Moduli fascia | 8 m centrati sulle palme: [16,4 + 8k ; 24,4 + 8k]. Testa senza palme X 9,75 → 16,4 (6,65 m, cubetti). Coda: X 552,4 → 558,75 (variante `_Fine`) | proposta |
| Panchine (filare 1, lato mare) | X = **32,4 + 16k**, Y 92,1: k 0-13 nel Blocco 1 (**14**, oggi 13), k 14-32 nel Blocco 2 (**19**, oggi 17) | [V] OSM (12 panchine su 12 cadono sulla griglia) |
| Lampioni a 2 globi su bracci | X = **32,7 + 32k** (panchina + 0,3), Y 92,85: **7** nel Blocco 1 (32,7 … 224,7), **10** nel Blocco 2 (256,7 … 544,7) | regola [V-utente]; fase [S] (S3). OSM non mappa lampioni qui |
| Lampione a 2 globi sovrapposti | uno solo, **(15,3; 101,9)** | [S] (D-P2) |
| Pensilina | **(40,4; 93,2)** (OSM 39,6; spostata sul punto medio fra le palme 36,4 e 44,4 per non toccare le aiuole: distanza netta plinti-aiuola ~0,4 m) | [V] OSM; vedi D-P1 |
| Varchi "dispari" (24,4 + 16k) | liberi per pensilina (40,4), rastrelliere e cestini | proposta |
| Rastrelliere | sui varchi dispari vicini a OSM: **56,4** (OSM 59,0), **88,4** (OSM 90,5), **104,4** (OSM 107,0); OSM ne mappa altre 4 (122,1 · 136,5 · 157,2 · 185,3) | OSM [V]; scelta dei varchi [S] |
| Cestini | (17,9; 91,3) [V OSM] e (41,9; 90,5) [S], poi sui varchi dispari liberi, circa uno ogni 2-3 varchi (Blocco 1 ≈ 9, Blocco 2 ≈ 11 come oggi). La regola "panchina + 2,05 m" non si può più usare: nel varco da 4,4 m la panchina da 2,8 m lascia 0,8 m per lato | [S] |
| Tombini | coppie nel corridoio fra i filari (Y 95-97) come oggi, ma ricalcolati sulle campate da 8 m (non sopra le strisce trasversali nuove) | regola [V-utente]; posizioni [S] |

**Gazebo e conteggio dell'utente (D-P1).** Il 2026-11-19 l'utente ha messo il gazebo "dopo le prime due palme dal lato del ponte".
Con passo 8 m questo darebbe X 32,4, dove OSM mette invece una panchina con schienale (31,7). OSM (pensilina mappata come poligono,
con 4 panchine dentro e un cestino accanto) la mette a 39,6, cioè dopo **tre** coppie. Le due versioni differiscono di 8 m.
Proposta: **40,4 (OSM)**, salvo conferma contraria dell'utente.

### 6.4 Cosa va rifatto a cascata (passo 9 → 8 m e prima coppia 12 → 20,4)
Controllo automatico delle impronte (oggetti attuali contro le aiuole nuove): **48 conflitti** fra Blocco 1 e Blocco 2: 18 panchine,
7 lampioni, 21 cestini (nel Blocco 1 sia la v1 sia la v2), 2 rastrelliere e il gazebo. In pratica tutto ciò che sta sulla linea del filare 1 va rigenerato.

| Cosa | File / CSV | Blocco 1 | Blocco 2 | Tipo di lavoro |
|---|---|---|---|---|
| Palme | `exports/pavimentazione/palme_posizioni_v3.csv` → `_v5`; `exports/blocco2/blocco2_palme_v1.csv` → `_v2` | 54 → **60** | 68 → **76** | solo posizioni (HISM `Arte_Palme_PalmaA` e B2) |
| Aiuole | `pav_posizioni_v3.csv` → `_v5`; `blocco2_pav_v1.csv` → `_v2` | 54 → 60 | 68 → 76 | solo posizioni |
| Fascia palme (strisce trasversali dentro la mesh) | `SM_Pav_FasciaPalme_9m` → **nuova `SM_Pav_FasciaPalme_8m`** + testa `SM_Pav_FasciaPalme_Testa` (6,65 m) + `SM_Pav_FasciaPalme_Fine` rifatta; script `blender/scripts/morin_pav_kit.py` (`X0_MOD, PASSO, N_MOD`, `X_TRASV`, `X_PALMA0`, `N_PALME`, `GAZEBO`) e `morin_blocco2.py` (`PALME_X`, `PANCH_X`, `LAMP_X`, `X_FASCIA`, `N_FASCIA`, `build_fascia_fine`) | 27 → 1 testa + 30 moduli | 33 + Fine → 37 + Fine | **mesh nuova** + posizioni |
| Cordolo | `SM_Pav_Cordolo_9m` | — | — | nessun motivo legato alle palme: **può restare a 9 m** (controllare solo che i giunti non cadano sulle strisce trasversali nuove) |
| Panchine | `pav_posizioni` + `blocco2_arredi_v1.csv` | 13 → **14** | 17 → **19** | posizioni |
| Lampioni | idem | 7 (16,8 + 36k) → **7 (32,7 + 32k)** | 8 → **10** | posizioni |
| Lampione 2 globi sovrapposti | `exports/molo/` (attore `Arte_Molo_Lampione2Globi_00`) | (13,0; 106,0) → **(15,3; 101,9)** [S] | — | solo dopo D-P2 |
| Tombini | `pav_posizioni`, `blocco2_arredi_v1.csv` | 8 | 10 | ricalcolo sulle campate da 8 m |
| Gazebo | `pav_posizioni` | (25,5; 93) → **(40,4; 93,2)** | — | posizione (dopo D-P1) |
| Cestini | `exports/dettagli/dettagli_posizioni_v2.csv` (`Cestino_v2_*`), `exports/imbarco/imbarco_posizioni_v1.csv` (`Cestino_*`, sostituiti dalla v2), `blocco2_arredi_v1.csv` (`B2_Cestino_*`, 11) | 9 | 11 | posizioni sui varchi dispari |
| Rastrelliere | `imbarco_posizioni_v1.csv` (`Rastrelliera_00-02`, X 61,5 / 79,5 / 97,5) | 3 → 56,4 / 88,4 / 104,4 | — | posizioni |
| Cartelli del parcheggio in testa alle aiuole | `exports/parcheggio/parcheggio_posizioni_v4.csv`: `Cartello_Divieto_00` (22,6; 101,55), `Cartello_P_00` (26,2; 101,55), `Cartello_Divieto_01` (89,0; 101,55) | nessun conflitto (Y fuori dall'aiuola), ma erano allineati alle aiuole vecchie: riallineare se devono stare in testa alle aiuole nuove (es. 22,0 e 26,8) [S] | — | facoltativo |
| Sirena | `dettagli_posizioni_v2.csv` | **nessuna modifica** (giusta) | — | — |
| Panchina lunga dei Giardini (Y 101,7), oleandri, pini | `giardini_posizioni_v1*.csv`, `blocco2_giardini_v1.csv` | nessun conflitto (fuori dalle aiuole) | idem | nessuna |
| Chiosco ottagonale e dehors B2 (X 541-558, Y ≥ 102,5) | `blocco2_chiosco_*.csv` | — | controllare solo la coda della fascia con l'ultima aiuola (X 554,6-558,2) | verifica |
| Riferimento interno | `morin_blocco2.py` (riga ~777) legge `palme_posizioni_v3.csv` | — | — | aggiornare il nome del CSV |
| Documenti | `ref/sezione.md` §6, `ref/elementi.md` (pensilina, panchine), `docs/decisioni.md` (nuova riga) | | | testo |

### 6.5 Dati ancora [S]
- Posizione del lampione a 2 globi sovrapposti (±1,5 m; le stime 2023 e 2026 differiscono di ~4,5 m).
- Fase dei lampioni normali (32,7 + 32k) e il loro numero: OSM non li mappa.
- Gazebo a 40,4 (OSM) o 32,4 (prima indicazione dell'utente).
- Misura delle aiuole (3,6 × 3,0) e della panchina (2,8 m): con passo 8 m restano 0,8 m per lato.
- Posizioni di cestini, rastrelliere e tombini, a parte i 2 cestini e le 7 rastrelliere di OSM.
- Y del filare 1 costante (OSM ha una deriva di 1,3 m, trattata come errore di mappatura).
