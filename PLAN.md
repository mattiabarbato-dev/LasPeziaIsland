# PLAN — Morin Rush (Passeggiata Costantino Morin)

Stato: `[ ]` da fare · `[~]` in corso · `[x]` fatto · `[!]` bloccato
Ogni fase ha un **cancello**: non si passa alla successiva finché non è superato.
Regole, paesaggio e metriche: vedi `CLAUDE.md`.

---

## Punto di ripresa (aggiornato 2026-11-19, fine seconda sessione)
**Priorità (decisione dell'utente):** una mappa **il più simile possibile alla Spezia**, grafica **realistica per PC/console**.
La modalità di corsa (Fase 2) è rimandata; il tempo di corsa non è un criterio. Vedi CLAUDE.md §1.
**Ordine di lavoro voluto dall'utente, sempre:** modella → **importa in UEFN → verifica in sessione (utente) → commit e push**.

**Dove siamo** (tutto verificato in sessione dall'utente e pushato):
- Cancello 1 superato. Ora fissa alle 18, Acqua V2 a Z −100, costruzione Nessuno.
- Banchina (58 moduli a Z 0, bitte, scalette) e camminamento a lastre (tinta grigio-bruna).
- Fascia palme v3: **54 palme su filari allineati**, aiuole 3,6 × 3,0 m a terra, strisce chiare laterali + trasversale a metà fra le
  palme, cordolo 15 cm, 13 panchine (una ogni 2 palme, lato mare), 7 lampioni (ogni 4 palme), 8 coppie di tombini, gazebo con tetto
  a piramide fra la 2ª e la 3ª palma dal ponte. Dettagli `docs/uefn_arte.md` §11-12.
- Fondale v1: 8 settori di colline dal DEM Copernicus, tenda a 13 km, 12 blocchi città; foschia (override nebbia) e barriere sui
  bordi dell'acqua. Dettagli `ref/fondale.md`, `docs/uefn_fondale.md`.

**Prima cosa alla ripresa:** verificare che `blender` e `unreal-mcp` rispondano (`blender` usa `uvx --system-certs`).
Import in UEFN: SOLO il metodo di `docs/uefn_arte.md` §12 (ImportFile da zero in `_Temp` + `set_lod_from_static_mesh`;
mai reimport/sostituzioni: aprono finestre modali che bloccano l'editor e ruotano gli asset).

**Prossimi step proposti**
0. (in corso, sessione 3) Radice del molo/incrocio verso il ponte come nella foto `ref/foto/vista/inizio_passegiata_ristoranti_che_vanno_verso_il_ponte.png`
   (Street View, usabile anche per texture per deroga dell'utente, CLAUDE.md §5): strada di servizio, pavé, edifici bassi dei ristoranti con alberi dietro.
   - [x] (geo-scout) Scheda `ref/radice_molo.md` (2026-11-19): punto di presa, planimetria dell'incrocio e del molo, edifici A/B/C
     (un piano, 3,3-4 m), alberi 15-20 m, lampione a 2 globi (asset nuovo), confronto col progetto, texture [SV], proposta asset.
   - [x] (utente) Risposte D1, D2, D4, D8 in `ref/radice_molo.md` §7.1: Sirena c'è; nessuna segnaletica a terra; filari da X 20,4 con
     gazebo fra 2ª e 3ª palma (X ≈ 33,9); dehors completi; auto ignorate. D3, D5-D7 (foto) aperte: si procede con le stime.
   - [~] (blender-artist) Tranche 1: pavimenti (asfalto, masselli, angolo cubetti), edifici A1A2/A3/A4A5/C, tendone, lampione 2 globi,
     latifoglie A/B, pino domestico → `blender/arte_molo.blend`, `exports/molo/`.
   - [ ] (blender-artist) Tranche 2: dehors (tavolini, sedie, ombrelloni, tettoie a righe), fioriere, Sirena stilizzata, lampioni alti, piccoli prop.
   - [x] (blender-artist, 2026-11-19) **Chiosco-bar + dehors v1** (scheda `ref/zona_parcheggio_chiosco.md` §3): `blender/arte_chiosco.blend`
     (contesto CTX_Contesto *linkato* da arte_molo.blend), script `blender/scripts/morin_chiosco.py`, texture `blender/textures/chiosco/`
     (2 atlanti 2048 D/N/ORM), 22 FBX in `exports/chiosco/` + `chiosco_posizioni_v1.csv` (39 righe, coordinate UE, quota Z 15 uu).
     Tri LOD0/1/2: Chiosco 2.776/1.288/100 · Ombrellone 894/304/126 · Fioriera 246/116/50 · TavoloSet 672/450/324 ·
     Tavolino 184/106/76 · Sedia 122/86/62 · Sgabello 168/144/68 · `SM_Pav_Chiosco` 8 (solo LOD0). Render `docs/qa/arte_chiosco_v1*.png`
     (confronti foto/render). Nome inventato "Chiosco del Golfo".
   - [x] (blender-artist, 2026-11-19) **Chiosco v2** (ritocchi approvati dall'utente, stessi nomi, FBX sovrascritti): ombrelloni con tela
     5 × 4 m e bordo a 2,36 m (910/304/126 tri), che coprono tutto il dehors; fioriere con vaso da 1 m e arbusti misti su card fino
     a 1,6-1,8 m in **3 varianti** `SM_Morin_Fioriera` 222/116/50, `SM_Morin_FiorieraB` 182/96/46, `SM_Morin_FiorieraC` 206/106/48;
     montanti crema da 12 cm, vetrine con 2 mensole e meno bottiglie (chiosco 2.776/1.288/100). 9 tavoli (prima 6) fra i pali.
     28 FBX, `chiosco_posizioni_v1.csv` riscritto (42 righe). Confronti `docs/qa/arte_chiosco_v2_confronto.png`, `_v2_dehors_confronto.png`.
   - [x] (blender-artist, 2026-11-19) **Blockout passeggiata v3**: `exports/blockout/SM_Blockout_Passeggiata_Pav_v3.fbx` (138 tri, 14 UCX;
     sorgente `blender/arte_pavimentazione.blend`, collezione `Blockout_Passeggiata_Pav_v3`, v2 intatta; backup
     `blender/arte_pavimentazione_pre_blockout_v3.blend`). Tolte le aiuole fra X 94,5 e 117,5 (Y 102-107 e 111-116). Ray test (griglia 0,25 m): nessuna
     superficie sopra il tassello del chiosco, suolo a lastre (Z 0) continuo sotto; fuori zona identica alla v2; bbox identica, posa (0,0,0).
   - [x] (uefn-builder, 2026-11-19 22:00-22:10) Import kit chiosco v2 e blockout v3 (`docs/uefn_arte.md` §16): 10 mesh, 6 texture 2048 e
     `MI_Morin_Chiosco`/`MI_Morin_Dehors` in `LaSpezia/Arte/Chiosco`; `SM_Blockout_Passeggiata_Pav_v3` in `LaSpezia/Blockout`. Posa dal CSV
     (42 righe) in Outliner `Arte/Chiosco`: 2 attori singoli + 6 HISM (ombrelloni 4, tavoli 9, sgabelli 5, fioriere 8/7/7).
     `Blockout_Passeggiata_v3` posato; **`Blockout_Passeggiata_v2` nascosto** (non cancellato: serve la conferma diretta dell'utente).
     Line trace: nessuna aiuola sopra il tassello, suolo continuo. Render `docs/qa/uefn_chiosco_v2.png`, `uefn_chiosco_v2_b.png`.
   - [ ] (utente) Conferma per cancellare l'attore `Blockout_Passeggiata_v2` e l'asset `SM_Blockout_Passeggiata_Pav_v2`; pulizia dei 18 `TMPC_*` in `_Temp`.
   - [ ] (qa-tester) Prova in sessione del dehors: gradino del tassello (+15), passaggio fra tavoli e fioriere, collisione degli ombrelloni.
   - [x] (blender-artist, 2026-11-19) **Giardini a Mare v1: oleandri ad alberello + panchina lunga** (scheda `ref/zona_parcheggio_chiosco.md` §4,
     foto `prato con alberelli.png`): `blender/arte_giardini.blend` (copia di arte_chiosco.blend, contesto linkato), script
     `blender/scripts/morin_giardini.py`, texture `blender/textures/giardini/` (chioma 2048 RGBA con 2 quadranti bianchi e 2 rosa,
     fusto 1024). 9 FBX in `exports/giardini/`. Tri LOD0/1/2: `SM_Morin_OleandroAlberello_Bianco` e `_Rosa` 1.021/522/155
     (2,18 × 2,14 × 3,71 m, fusto 1,7 m con tutore, UCX solo sul fusto) · `SM_Morin_PanchinaLunga_Mod` 306/134/42 (4,0 × 0,45 × 0,45 m,
     M_Pav_Fascia riusato, UCX box). CSV `giardini_posizioni_v1.csv` (Blocco 1, X ≤ 250: 22 oleandri + 29 moduli panchina) e
     `giardini_posizioni_v1_blocco2.csv` (X > 250: 55 + 69). Oleandri Y 119,5 X 131-549 passo 5,5 m alternati, Z 0; panchina asse Y 101,7,
     Z +0,15, tratti X 122-178 / 183-227 / 233-249 (varchi del blockout v3). Confronto `docs/qa/arte_giardini_v1_confronto.png`.
   - [x] (blender-artist, 2026-11-19) **Giardini a Mare v2** (stessi nomi, FBX sovrascritti; texture chioma rigenerata): oleandri con
     chioma grande, schiacciata e a lobi, ciuffi sporgenti, card fitte, **due forme diverse** (Bianco 7 lobi, Rosa 8 lobi), fusto Ø 12→10 cm
     fino a 1,9 m, più fiori, rosa fucsia. Tri LOD0/1/2: Bianco 2.694/1.309/427 (3,72 × 3,37 × 4,13 m), Rosa 2.734/1.335/427
     (3,21 × 3,35 × 4,05 m). Panchina: lastra 7 cm, pilastrini 14 cm ogni 1,0 m, 372/164/52 tri. CSV invariati (posizioni uguali).
     Confronto `docs/qa/arte_giardini_v2_confronto.png`. Bordura di bosso **non fatta**: disposizione delle aiuole nel prato non chiara.
   - [x] (blender-artist, 2026-11-19) **Blockout passeggiata v4**: `exports/blockout/SM_Blockout_Passeggiata_Pav_v4.fbx` (128 tri, 13 UCX,
     solo LOD0, posa (0,0,0), bbox uguale alla v3 salvo Z max 0,40); sorgente `blender/arte_pavimentazione.blend`, collezione
     `Blockout_Passeggiata_Pav_v4` (v3 intatta; backup `blender/arte_pavimentazione_pre_blockout_v4.blend`). Tolta la `SiepeLimite`;
     aiuole da X 117,5 (Y 102-107 e 111-116) abbassate a Z +0,05 (prato provvisorio, `M_Blockout_Verde`); a X < 94,5 invariate.
     Ray test 0,5 m su X 0-250, Y 62-118 (visivo e UCX): stessi identici punti scoperti della v3 (516, fuori dal bordo del blockout), nessun buco nuovo.
   - [x] (uefn-builder, 2026-11-19 22:47) Import kit giardini v2 e blockout v4 (`docs/uefn_arte.md` §17): 3 mesh in `LaSpezia/Arte/Giardini`
     (tri LOD0/1/2 Bianco 2.694/1.309/427, Rosa 2.734/1.335/427, panchina 372/164/52; 1 UCX ciascuna, fusto/box), 6 texture,
     `MI_Morin_Oleandro_Chioma` (master masked two-sided) e `MI_Morin_Oleandro_Fusto`; HISM `Arte_Giardini_OleandriBianco` 11,
     `_OleandriRosa` 11, `_Panchine` 29 (solo CSV Blocco 1). `Blockout_Passeggiata_v4` posato, **`Blockout_Passeggiata_v3` nascosto**
     (non cancellato). Line trace X 117-250 m: suolo continuo (prato +5, fascia +15), nessuna siepe, panchine su fascia +15.
     Validazione 222/222, 0 errori, 10 avvisi noti. Render `docs/qa/uefn_giardini_v2.png`, `_b.png`.
   - [ ] (utente) Conferma per cancellare gli attori nascosti `Blockout_Passeggiata_v2`/`_v3`, le loro mesh e i 6 `TMPG_*` in `_Temp`.
   - [ ] (qa-tester) Prova in sessione: panchina lunga (sedersi/saltarci), passaggio tra gli oleandri, gradino fascia +15 → prato +5.
   - [ ] (geo-scout/utente) Disposizione delle aiuole geometriche con bordura di bosso nel prato (foto in pianta o vista aerea), poi
     `SM_Morin_BorduraBosso_Mod` (blender-artist).
   - [ ] (utente) Verificare [S]: altezza oleandri (~4 m), passo 5,5 m, posizione e varchi della panchina, tutore presente o no.
   - [x] (blender-artist, 2026-11-19) **Vista verso la città v1: prato, aiuole, Viale Italia, palazzi** (foto `prato con alberelli.png`):
     `blender/arte_viale.blend` (copia di arte_giardini.blend + fondale linkato per il render), script `blender/scripts/morin_viale.py`,
     texture `blender/textures/viale/`. 25 FBX in `exports/viale/`, CSV `exports/viale/viale_posizioni_v1.csv` (107 righe, coordinate UE).
     Tri LOD0/1/2 e dimensioni LOD0: `SM_Morin_Prato_Giardini` 48 (pezzo unico, 132,5 × 18,95 m, Z +0,08, UCX fino a Y 118) ·
     `SM_Morin_Aiuola_Bosso` 76/40/28 (12 × 3 × 0,36 m, UCX box; 8 istanze Y 110) · `SM_Viale_Italia_Strada` 88/80/32 (modulo 19 × 24,15 m,
     7 istanze X 117-250, origine Y 120,85) · `SM_Morin_Auto_A/B/C` 324/204/124 (3,95/4,35/4,45 × 1,76-1,84 × 1,45-1,64 m; 41 istanze
     in sosta a Y 122,15 e 137,45) · `SM_Fondale_Palazzo_A` 2.264/878/22 (21,2 × 19,2 × 26,9 m), `_B` 2.740/1.186/22 (25,7 × 19,6 × 26,8 m),
     `_C` 1.940/754/22 (21,2 × 17,2 × 22,8 m); 13 istanze sui fronti OSM (Y 206-208 e 253-266). Alberi dei Giardini pubblici nel CSV con
     asset già in UEFN: 24 tra `SM_Albero_LatifogliaA/B` e `SM_Morin_PinoDomestico` + 13 `SM_Morin_PalmaA` (Y 147-200).
     Materiali: `M_Morin_Prato`, `M_Morin_Bosso`, `M_Viale_Segnaletica`, `M_Morin_Auto`, `M_Fondale_Palazzo_A/B/C` (nuovi) + riuso
     `M_Molo_Asfalto`, `M_Pav_Fascia`. Blockout nuovo `exports/blockout/SM_Blockout_Fondale_v3.fbx` (417 tri, 43 UCX; v2 557/57;
     sorgente `blender/blockout_blocco1.blend` collezione `Blockout_Fondale_v3`, backup `blockout_blocco1_pre_fondale_v3.blend`).
     Confronto `docs/qa/arte_viale_v1_confronto.png` (camera `CAM_Viale_F1` a X 221,8, Y 93,4).
   - [x] (uefn-builder, 2026-11-19 23:14-23:22 ora locale) Import vista città v1 (`docs/uefn_arte.md` §18): 9 mesh (`Arte/Viale`,
     `Arte/Fondale/Palazzi`) + `Blockout/SM_Blockout_Fondale_v3`, 21 texture, 8 MI; tri e LOD come da report (Prato 48, Aiuola 76/40/28,
     Strada 88/80/32, Auto 324/204/124, Palazzi 2.264/878/22 · 2.740/1.186/22 · 1.940/754/22, Fondale_v3 417 con 43 convessi).
     13 HISM + 1 attore in Outliner `Arte/Viale` (107 istanze dal CSV; alberi e palme dei Giardini pubblici con gli asset esistenti),
     `Blockout_Fondale_v3` posato, **`Blockout_Fondale_v2` nascosto** (non cancellato). Strada, auto, palazzi e alberi oltre la barriera
     senza collisione. Slot Verde di `SM_Blockout_Fondale_v3` su **`MI_Morin_Prato_Mondo`** (proiezione mondo: le UV del blockout sono nulle).
     Trace: prato +8 continuo su X 117,5-250 m / Y 102-118 m. Validazione 278/278, 0 errori, 11 avvisi (10 noti + "un solo LOD" sul Fondale_v3).
     Render `docs/qa/uefn_viale_v1.png` (camera F1).
   - [ ] (utente) Conferma per cancellare `Blockout_Fondale_v2` (nascosto), la sua mesh e i 16 `TMPV_*` in `_Temp`.
   - [x] (blender-artist, 2026-11-20) **Correzioni Viale v1** (decisioni.md 2026-11-20): (1) palazzi X 330/357,5 e latifoglia X 333 stanno già
     sul terreno `SM_Fondale_Colline_N` (Z 0..+1,29 sotto le impronte, ray test): nessun suolo nuovo, Palazzo_06 (B) alzato a Z +1,154 m;
     (2) strada +4 moduli a NE (X 250-326) e +6 a SO (X 3-117, davanti al parcheggio), +50 auto in sosta; (3) il "cubo bianco" è l'isola/UCX
     **30** di `SM_Blockout_Fondale_v3_Edifici` (X 197,9-201,9, Y 151,7-155,6, h 4,2 m), tolta con la **36** (X 97,6-101,1, Y 167,6-173,6) in
     `exports/blockout/SM_Blockout_Fondale_v4.fbx` (397 tri, prima 417; 41 UCX, prima 43; collezione `Blockout_Fondale_v4` in
     `blender/blockout_blocco1.blend`, backup `blockout_blocco1_pre_fondale_v4.blend`). CSV nuovo `exports/viale/viale_posizioni_v2.csv`
     (167 righe; v1 intatto). Tangenti degeneri: non toccate.
   - [x] (uefn-builder, 2026-11-20 04:28-04:40 ora locale) Viale v2 (`docs/uefn_arte.md` §19): HISM di `Arte/Viale` = CSV v2 (167 righe,
     confronto per posizione): +10 moduli strada (17), +13/+21/+16 auto A/B/C (26/34/31, senza collisione), Palazzo_06 a Z 115,4; nessun duplicato.
     `Blockout_Fondale_v4` posato (slot Verde → `MI_Morin_Prato_Mondo`), **`Blockout_Fondale_v3` nascosto** (non cancellato).
   - [ ] (utente) Conferma per cancellare `Blockout_Fondale_v3` e `Blockout_Passeggiata_v4` (nascosti), le loro mesh e i 12 `TMPP_*` in `_Temp`.
   - [x] (blender-artist, 2026-11-20) **Parcheggio iniziale v1** (X 20-95 m, `ref/zona_parcheggio_chiosco.md` §1): `blender/arte_parcheggio.blend`
     (copia di arte_viale + molo e blockout v5 collegati), script `blender/scripts/morin_parcheggio.py`, texture `blender/textures/parcheggio/`
     (asfalto 2048 [SV], cartelli 512, new jersey 1024). 19 FBX in `exports/parcheggio/`, CSV `exports/parcheggio/parcheggio_posizioni_v1.csv`
     (54 righe, coordinate UE). Tri LOD0/1/2: `SM_Parcheggio_Asfalto` 153 (pezzo unico in coordinate di progetto, posa 0,0,0; 86 × 18,85 m,
     asfalto Z +0,02, cordolo +0,15, aiuola +0,12/+0,14; 6 UCX box fino a Y 118) · `SM_Morin_CartelloP` 78/50/20 (0,6 × 2,7 m) ·
     `SM_Morin_CartelloDivieto` 154/94/48 · `SM_Morin_NewJersey` 54/26/18 (2,0 × 0,61 × 0,81 m, UCX convesso) ·
     `SM_Morin_Auto_A/B/C_Col` 324/204/124 (mesh delle auto del viale + 2 UCX box). Istanze: 40 auto `_Col` (in linea Y 103,6 e 112,3,
     pettine Y ~119), 4 cartelli, 3 new jersey (Y 80,6), 6 latifoglie A/B (Y 115,1, aiuola rialzata). Nuovo blockout
     `exports/blockout/SM_Blockout_Passeggiata_Pav_v5.fbx` (98 tri, 10 UCX; tolte le aiuole a X < 94,5; sorgente `arte_pavimentazione.blend`,
     collezione `Blockout_Passeggiata_Pav_v5`, backup `arte_pavimentazione_pre_blockout_v5.blend`). Confronto `docs/qa/arte_parcheggio_v1_confronto.png`.
   - [x] (uefn-builder, 2026-11-20 04:28-04:40 ora locale) Import parcheggio v1 + `SM_Blockout_Passeggiata_Pav_v5` (`docs/uefn_arte.md` §19):
     7 mesh in `Arte/Parcheggio` (Asfalto 153 · CartelloP 78/50/20 · CartelloDivieto 154/94/48 · NewJersey 54/26/18 · Auto_A/B/C_Col 324/204/124,
     2 convessi), 9 texture, 3 MI nuove (`MI_Parcheggio_Asfalto`, `MI_Morin_Cartelli`, `MI_Morin_NewJersey`); 1 attore + 8 HISM in Outliner
     `Arte/Parcheggio` (53 istanze, collisione Query Only come il resto). `Blockout_Passeggiata_v5` posato, **`Blockout_Passeggiata_v4` nascosto**.
     Trace X 20-95 m / Y 100-118 m: asfalto +2, aiuola alberi +14, nessun buco, nessun blockout sopra, salti max 16 cm. Validazione 310/310,
     0 errori, 12 avvisi (11 noti + "un solo LOD" sul Fondale_v4). Render `docs/qa/uefn_parcheggio_v1.png` (camera `CAM_Park_F1`).
   - [x] (orchestratore/utente) Problemi del parcheggio v1 (§19): fila a pettine (Y ~119) dentro `Barriera_LatoCitta` (Y 118,0-120,6);
     `NewJersey_00` (6200, −8060) sopra la bitta 3 (6200, −8052,7) — **corretto nel CSV v2** (X 6070). 2026-11-20: barriera spostata
     davanti al parcheggio (vedi sotto, `docs/uefn_arte.md` §20).
   - [x] (blender-artist, 2026-11-20) **Auto v2 + parcheggio CSV v2 + viale CSV v3**: script `blender/scripts/morin_auto_v2.py`
     (in `blender/arte_parcheggio.blend`, collezione `AUTO_v2_Kit`; backup `arte_parcheggio_pre_auto_v2.blend`), texture
     `blender/textures/auto/T_Morin_Auto_v2_D/N/ORM` (2048, atlante 3 × 3 modello × colore), materiale `M_Morin_Auto_v2`.
     54 FBX in `exports/auto/`: `SM_Morin_Auto_{A,B,C}_v2_<Colore>` e `SM_Morin_Auto_{A,B,C}_Col_v2_<Colore>` (+ `_LOD1/_LOD2`; i `_Col`
     LOD0 con 2 UCX box scocca + abitacolo). Colori: A Bianco/Rosso/Azzurro, B GrigioScuro/Argento/Arancio, C Nero/BluScuro/BiancoPerla.
     Tri LOD0/1/2: A 1.804/812/260 (3,95 × 1,74 × 1,50 m, 2,12 con specchietti), B 1.844/840/260 (4,35 × 1,82 × 1,64),
     C 1.844/840/276 (4,45 × 1,78 × 1,47). CSV: `exports/parcheggio/parcheggio_posizioni_v2.csv` (colonne in più `pitch,roll`;
     auto v2 `_Col`, 7 pini domestici al posto delle 6 latifoglie, `NewJersey_00` a X 6070) e `exports/viale/viale_posizioni_v3.csv`
     (posizioni della v2, auto v2). Confronto `docs/qa/arte_auto_v2_confronto.png`. Decisioni in `docs/decisioni.md` (2026-11-20).
   - [x] (uefn-builder, 2026-11-20 ~04:50-05:05 ora locale) Import auto v2 e ripopolamento (`docs/uefn_arte.md` §20): 18 mesh in
     `Arte/Auto` (3 LOD, Nanite off, UCX 2 box solo sulle `_Col`, convesso automatico tolto dalle altre), 1 set texture
     `T_Morin_Auto_v2_D/N/ORM` 2048 + `MI_Morin_Auto_v2` condivisa (nessun duplicato: FBX importati senza materiali/texture).
     Parcheggio: 9 HISM `Arte_Parcheggio_Auto{A,B,C}_Col_v2_<Colore>` (40 istanze) + `Arte_Parcheggio_Pini` (7, pitch dal CSV);
     `NewJersey_00` a (6070, −8060). Viale: 9 HISM `Arte_Viale_Auto{A,B,C}_v2_<Colore>` (91, No Collision).
     **Nascosti, non cancellati:** `Arte_Parcheggio_AutoA/B/C_Col`, `Arte_Parcheggio_LatifogliaA/B`, `Arte_Viale_AutoA/B/C`.
     Barriera lato città spezzata in 5 device (`Barriera_LatoCitta` X 10624..31104, `_SO` X −3510..1610, `_Parcheggio` Y −12441..−12185
     su X 1536..10752, raccordi `_RaccordoSO`/`_RaccordoNE`): fila a pettine e asfalto ora giocabili, catena senza varchi.
     Salvataggio 05:03 (91 pacchetti), validazione 368/368, 0 errori, 12 avvisi noti. Render `docs/qa/uefn_parcheggio_v2.png`.
   - [ ] (qa-tester) In sessione: le barriere nuove bloccano davvero (in modalità Crea non hanno collisione, verificate solo dai bounds);
     (risolto 2026-11-20: le 13 auto del viale davanti al parcheggio spostate negli HISM `_Col_v2`, ora solide; §20)
   - [x] (uefn-builder, risolto: LODBias 1 → 0 sulle texture auto v2, §20) Auto v2 in scena: tetti e cofani molto chiari/lattiginosi con la luce delle 18 (riflesso del cielo?), mentre la
     miniatura dell'asset è corretta; valutare `Roughness_Mult` di `MI_Morin_Auto_v2`.
   - [x] (uefn-builder, 2026-11-20 05:25) LODBias 0 sulla selezione dell'utente (~100 MiB): 30 texture `T_Pav_*`, `T_Banchina_Ghisa/Paramento_*`,
     palme, chiosco e dehors. Le altre 30 restano a 1 (Ciglio v1, oleandro chioma, prato, fregio, molo, asfalto parcheggio, chiome alberi).
     Totale stimato texture del progetto **192-233 MiB** (prima 110-133), sotto la soglia di 245. Salvato, validazione 393/393. §21.
   - [ ] (utente/geo-scout) Verificare [S] del parcheggio: larghezza corsia (6,25), seconda fila a pettine dietro gli alberi, senso unico,
     posizione dei cartelli e dei new jersey, lampione a due globi affiancati (non modellato).
   - [ ] (utente/geo-scout) Verificare [S]: sezione del viale (sosta lato giardini, spartitraffico, sosta lato città, strisce bianche o blu),
     senso di marcia, disegno delle aiuole di bosso, densità degli alberi dei Giardini pubblici.
   - [ ] (blender-artist → uefn-builder) Layout fascia palme **v4**: filari da X 20,4 (via le palme a X 12), tutto il resto −0,6 m,
     gazebo a X ≈ 33,9; in UEFN solo spostamenti di attori (niente reimport).
   - [x] (uefn-builder, 2026-11-19 18:15) Import e posa del kit molo v2 (`docs/uefn_arte.md` §13): 14 mesh in `LaSpezia/Arte/Molo` e
     `LaSpezia/Arte/Alberi`, 21 texture, 8 MI; 14 attori in Outliner `Arte/Molo` e `Arte/Alberi`; LOD, UCX e materiali verificati,
     validazione 43/43 senza avvisi, tutto salvato. Render `docs/qa/uefn_molo_v2_F1.png`, `_F3.png`, `_alto.png`.
   - [ ] (utente → uefn-builder) **Conferma per nascondere/cancellare il blockout della zona**: le scatole di `Blockout_Fondale`
     (Z 4-8 m) coprono per intero A1A2, A3, A4A5, C, tendone e i tronchi delle latifoglie 02, 05, 06; la siepe/aiuole di
     `Blockout_Passeggiata` (Y 116-118, +40 cm) coprono asfalto e ramo verso il parcheggio. Sono mesh uniche: serve una nuova
     versione dei due blockout (blender-artist) oppure nascondere gli attori interi (si perde anche il resto del blockout).
     - [x] (blender-artist, 2026-11-19 18:30) Blockout ritagliati, **asset nuovi** (originali intatti): `exports/blockout/SM_Blockout_Fondale_v2.fbx`
       (557 tri, prima 517; 57 UCX, prima 53; sorgente `blender/blockout_blocco1.blend`, collezione `Blockout_Fondale_v2`) e
       `exports/blockout/SM_Blockout_Passeggiata_Pav_v2.fbx` (128 tri, 13 UCX come prima; sorgente `blender/arte_pavimentazione.blend`,
       collezione `Blockout_Passeggiata_Pav_v2`). Tolte le scatole di A1A2-A5, C e del tendone; tacche 3 × 3 m ai tronchi 02, 03, 05, 06
       nelle scatole D/D3; siepe da X 20, aiuola Y 111-116 da X 24. Bbox identiche agli originali, posa (0,0,0) yaw 0.
       Verifica in Blender (ray test su griglia 0,25 m: nessuna superficie del blockout sopra il kit; nessun vertice di edifici o tendone
       entro 1 m dalle scatole; nessun tronco dentro). Render `docs/qa/blockout_ritaglio_molo.png` (alto), `_F1.png`. Backup
       `blender/blockout_blocco1_v1.blend`, `blender/arte_pavimentazione_v3.blend`.
     - [x] (uefn-builder, 2026-11-19 18:35) Blockout v2 in UEFN (`docs/uefn_arte.md` §14), **niente cancellazioni** (decisione utente):
       asset `LaSpezia/Blockout/SM_Blockout_Fondale_v2` (557 tri, 57 convessi) e `SM_Blockout_Passeggiata_Pav_v2` (128 tri, 13 convessi),
       solo LOD0, MinLOD 0, Nanite off, collisione semplice come complessa; nuovi attori `Blockout_Fondale_v2`, `Blockout_Passeggiata_v2`
       (Outliner `Blockout`, posa 0,0,0). Originali `Blockout_Fondale` e `Blockout_Passeggiata` **nascosti** (Hidden in Game, componente
       Visible = falso, collisioni off), asset originali intatti. Line trace: nessuna collisione vecchia sopra asfalto/masselli, suolo continuo.
       Render `docs/qa/uefn_molo_v2b_F1.png` (ristoranti visibili, niente scatola né siepe), `_F3.png`, `_alto.png`. Validazione 2/2
       (1 avviso atteso "un solo LOD" sul Fondale_v2), tutto salvato.
     - [ ] (utente/geo-scout) In F1 il primo piano (X 10-20 m, Y 114-118 m, dove c'era la siepe) ora mostra le lastre `MI_Pav_Lastre`
       della lastra base del blockout (stesso colore e scala del camminamento; l'ocra in F1 è la luce radente). Da decidere cosa c'è
       davvero lì (marciapiede di Viale Italia? asfalto?) e modellarlo.
     - [ ] (utente) le chiome basse delle latifoglie 01-05 entrano ancora nei tetti delle scatole D/E (6-8 m, area militare), visibile in
       `uefn_molo_v2b_alto.png` e `_F3.png` (non in F1): spostare gli alberi fuori dalle scatole oppure abbassare o togliere D ed E.
     - [x] (uefn-builder, 2026-11-19 20:10, autorizzato dall'utente) Pulizia (`docs/uefn_arte.md` §15): cancellati gli attori nascosti
       `Blockout_Fondale`, `Blockout_Passeggiata`, le mesh `SM_Blockout_Fondale`, `SM_Blockout_Passeggiata_Pav`/`_Passeggiata`/`_Arte`,
       i 130 temporanei di `LaSpezia/_Temp` e i 5 materiali orfani `M_Banchina_*`, `M_Morin_PalmaA_*`. Referencer controllati uno per uno,
       validazione `LaSpezia/` 167/167 valida, log puliti. Render `docs/qa/uefn_pulizia_alto.png`.
1. [~] Fondale: tinta MI fatta (facciate ok, colline poco cambiate: colpa della nebbia, `docs/uefn_fondale.md` §9); colle cittadino v2
   importato in UEFN (`docs/uefn_fondale.md` §10), **da verificare in sessione (utente)**; poi alberi del colle troppo chiari (MI dedicata).
   **TO DO (rimandato dall'utente): task nebbia** su `Luce_OraDelGiorno` — densità 0,002-0,003 o diminuzione 0,03, colore più blu/scuro,
   inscattering direzionale ridotto; poi ritarare la Tinta delle colline.
2. Blockout del fondale (scatole bianche vicino al ponte/area militare) da sostituire con edifici bassi come in foto.
3. Ponte Thaon di Revel realistico (foto in `ref/foto/ponte/`: legno a doghe con borchie, ringhiera bianca a montanti piegati e cavi).
4. Dettagli Blocco 1: ancora monumentale vicino al ponte, ciglio a grandi blocchi bianchi, fascia longitudinale nelle lastre [S],
   Giardini a Mare (prato, rose, agavi, panchine a schienale), texture del cordolo (bianco-azzurra, da correggere).
5. Banchina: testata/angolo (X 19,2 e 251 m), normali di bitta e scaletta; Palme B/C.
6. Blocco 2 (dopo): cannone + scultura REDAMARE a ~275 m, scritta "PASSEGGIATA MORIN" a ~550 m.

**Decisioni in attesa dell'utente:** anello di mare solo visivo (per ora non serve, prova ok).
(`_Temp`, `M_Banchina_*`, `M_Morin_PalmaA_*` e blockout v1 nascosti: cancellati il 2026-11-19, `docs/uefn_arte.md` §15.)

**Note:** il progetto UEFN (`Documents/Fortnite Projects/LasPezia_Island`) non è in questo repository. Foto stock (Alamy) in
`ref/foto/vista/` solo come riferimento visivo, mai per texture.

**Riferimenti tecnici:** preset export in `docs/scala.md` (usare sempre `blender/scripts/morin_export.py`); stato UEFN in
`docs/uefn_blockout.md`, `docs/uefn_arte.md`, `docs/uefn_fondale.md`; scelte in `docs/decisioni.md`.

---

## Fase 0 — Riferimenti e verifica dei dati
Obiettivo: trasformare i dati [S] di CLAUDE.md in dati verificati per il Blocco 1.

- [x] (orchestratore) Creare `docs/CREDITS.md` e `docs/decisioni.md`
- [x] (geo-scout) Bounding box del Blocco 1 in lat/lon: ponte + ~250 m di passeggiata + testata Mirabello -> `ref/area.md`
      (bbox lat 44.09993-44.10433, lon 9.82337-9.82953; origine node OSM 10249190464; asse X a 41,3°)
- [x] (geo-scout) Orientamento e lunghezza reale della passeggiata; correggere i dati [S] del quadro generale
      (sezione "Quadro generale verificato" in `ref/area.md`; CLAUDE.md da aggiornare a cura dell'orchestratore)
- [~] (geo-scout) Scheda `ref/ponte.md`: lunghezza, larghezza impalcato, altezza e inclinazione dell'antenna,
      numero di stralli, eventuale parte mobile, materiali e colori. Ogni dato marcato V o S
      Nota: le antenne sono DUE da 35 m. Restano [S] l'inclinazione, il numero esatto di stralli e i parapetti: serve una foto laterale
- [~] (geo-scout) Scheda `ref/sezione.md`: larghezza di ogni fascia della sezione trasversale,
      altezza banchina sull'acqua, passo delle palme, tipo di pavimentazione, lampioni e panchine
      Nota: fasce [V] da OSM. Restano [S] il passo delle palme (proposta 9 m), la quota del ciglio (1,5 m) e i lampioni (non mappati)
- [~] (geo-scout) Scheda `ref/elementi.md`: battelli, bitte, parapetti, chioschi, monumenti nel Blocco 1
      Nota: posizioni [V]. Restano [S] le dimensioni del battello, le bitte e la presenza del parapetto sul ciglio
- [ ] (utente) Foto in `ref/foto/`: ponte (dall'imbocco, di lato, da sotto), pavimentazione in pianta,
      una palma intera, bordo banchina, un lampione, una panchina, vista d'insieme verso il ponte
- [x] (orchestratore) Aggiornare la sezione 2 di CLAUDE.md con i dati verificati (2.1, 2.2, riga ponte in 2.3)

**Cancello 0:** le tre schede esistono e nessun dato necessario al blockout è ancora [S] senza una stima motivata.

---

## Fase 1 — Scala e blockout (solo forme grigie)
Obiettivo: percorrere il Blocco 1 dall'inizio alla fine con volumi semplici, in scala.

- [x] (blender-artist) Cubo di test 1 m -> `exports/test/SM_Test_Cubo1m.fbx`
      (1×1×1 m, 12 tri, origine alla base, UCX incluso; sorgente `blender/test_scala.blend`)
- [x] (uefn-builder) Import del cubo, verifica 100 uu, preset annotato in `docs/scala.md`
      Giro 2 OK: `SM_Test_AssiCm` (FBX_SCALE_NONE + bake_space_transform=True) misura 100 uu, 36 tri, 1 collisione convessa
      100×100×100, nessuna mesh UCX. `SM_Test_Assi` (FBX_SCALE_ALL) misura di nuovo 1 uu: preset scartato.
      Attore `Test_AssiCm` in (2560, −2048, 0), cartella `Test`. Mappatura assi misurata: Blender +X → UE −Y, Blender +Y → UE −X
      (nessuno specchio). Regola: UE_X = −B_Y·100, UE_Y = −B_X·100, UE_Z = B_Z·100; yaw UE = −rotZ Blender.
- [x] (orchestratore) Decidere gli assi — DECISO 2026-11-18: preset giro 2 + rotazione −90° Z solo in export (giro 3 verificato in UEFN). Regola: UE_X = B_X·100, UE_Y = −B_Y·100, UE_Z = B_Z·100, yaw UE = −rotZ Blender. Prossimo: script di export (blender-artist).
  Storico: tenere la regola sopra oppure giro 3 con `axis_forward='X'` (ipotesi: Blender +X → UE +X,
      Blender +Y → UE −Y). Vedi "Decisione aperta" in `docs/scala.md`. Da chiudere prima dell'export del blockout
      Nota blender-artist (giro 3, sorgente `blender/test_assi.blend` non modificato, 36 tri + UCX 12 tri, 1,4 × 1,2 × 1 m):
      - `exports/test/SM_Test_AssiX.fbx` (preset con axis_forward='X', axis_up='Z'): vertici X −50..70 · Y −90..50 · Z 0..100 cm
        (= B_Y, −B_X), header Front=−X, Coord=−Y, Up=+Z, nessuna Lcl Rotation. Blender cambia insieme vertici e header, in modo coerente:
        l'importer UEFN converte dall'header (modello che riproduce il giro 2: target Z-up/front +X, poi Y negata), quindi la PREVISIONE è
        la stessa mappatura del giro 2 (B+X → UE −Y, B+Y → UE −X). L'ipotesi 'X' probabilmente NON funziona: da confermare in UEFN.
      - `exports/test/SM_Test_Assi_RotZm90.fbx` (CANDIDATO): preset del giro 2 (axis_forward='-Y') con mesh e UCX ruotati di −90° in Z
        solo durante l'export (Lcl Rotation Z = −90 nel file, vertici come AssiCm, .blend ripristinato). Previsione: B+X → UE +X,
        B+Y → UE −Y (obiettivo), sia col modello "header" sia col modello "scambio grezzo". Da importare e misurare in UEFN.
      Esito uefn-builder (giro 3, misurato in UEFN, dettagli in `docs/scala.md`):
      - `SM_Test_AssiX`: bounds X −70..50 · Y −90..50 · Z 0..100, 36 tri, 1 convesso ±50/0..100. Mappatura IDENTICA al giro 2
        (B+X → UE −Y, B+Y → UE −X): modello "header" confermato, `axis_forward='X'` non serve. Attore `Test_AssiX` (3072, −2048, 0).
      - `SM_Test_Assi_RotZm90`: bounds X −50..90 · Y −70..50 · Z 0..100, 36 tri, 1 convesso ±50/0..100. **B+X → UE +X, B+Y → UE −Y**
        (come previsto). Attore `Test_Assi_RotZm90` (3584, −2048, 0). Regola: UE = (B_X·100, −B_Y·100, B_Z·100), yaw UE = −rotZ Blender.
      - Preset raccomandato: preset giro 2 + rotazione −90° Z applicata solo in export, da automatizzare con uno script di export.
        In attesa della decisione dell'orchestratore.
      Storico giro 1 — KO: il cubo misura 1 uu (fattore 0,01). L'FBX ha UnitScaleFactor=100 con geometria in metri
      (FBX_SCALE_UNITS) e l'import MCP non converte le unità. Riesportare con FBX_SCALE_ALL e ripetere.
      Pivot, 12 tri e collisione UCX: OK. Da verificare anche una Lcl Rotation Z=180° negli oggetti. Dettagli in `docs/scala.md`
      Nota blender-artist (giro 2, sorgente `blender/test_assi.blend`, cubo asimmetrico `SM_Test_Assi`, 36 tri + UCX 12 tri):
      - `exports/test/SM_Test_Assi.fbx` (FBX_SCALE_ALL, come richiesto): letto dall'FBX è IDENTICO al giro 1
        (UnitScaleFactor=100, vertici in metri, Lcl Rotation 0,0,180). Con global_scale=1 FBX_SCALE_ALL = FBX_SCALE_UNITS: atteso di nuovo 1 uu.
      - `exports/test/SM_Test_AssiCm.fbx` (FBX_SCALE_NONE + bake_space_transform=True): UnitScaleFactor=1, vertici in cm
        (X -90..50, Y -70..50, Z 0..100), nessuna Lcl Rotation/Scaling. Candidato da importare per primo.
      - La rotazione 180° nasce dalla conversione assi axis_forward='-Y' (gli oggetti in Blender hanno rot 0 / scale 1);
        con bake_space_transform finisce nei vertici (X e Y negati). Da misurare in UEFN dove arrivano i marcatori +X (lungo) e +Y (corto).
- [x] (blender-artist) Script di export `blender/scripts/morin_export.py` (preset giro 3: FBX_SCALE_NONE + bake_space_transform,
      −Y/Z, Rz(−90°) solo in export con ripristino try/finally; modi `asset`/`scene`, UCX automatici, controlli, report tri/budget/bbox).
      Verifica 2026-11-18 su `blender/test_assi.blend` (non salvato): `exports/test/SM_Test_Assi_Script.fbx` (13 772 byte, 36 tri + UCX 12)
      uguale a `SM_Test_Assi_RotZm90.fbx` per header, UnitScaleFactor=1, vertici (diff 0,0) e Lcl Rotation (−89,999989° vs −90,000009°).
      Matrici, selezione e attivo ripristinati; is_dirty False/False. Rifiuta l'asset con origine spostata senza toccare nulla. Uso in `docs/scala.md`
- [x] (uefn-builder) Pulizia UEFN 2026-11-18 (confermata dall'utente): rimossi i 4 attori della cartella Outliner `Test`
      e i 5 asset `SM_Test_*` + cartella `LaSpezia/Test` (referencer verificati: solo gli attori di test). Livello salvato,
      24 attori restanti invariati (template: GridPlane 1-4, spawn pad, PlayerStart, IslandSettings, DaySequence...), log senza errori.
      FBX in `exports/test/` non toccati.
- [x] (blender-artist) Import OSM con Blosm del bounding box; fissare l'origine come da CLAUDE.md §3
      2026-11-18, `blender/blockout_blocco1.blend` (Metric, scale 1.0). Bbox esteso lat 44.09906-44.10539, lon 9.82159-9.83045,
      .osm scaricato da Overpass (online access di Blender disattivato, non toccato) e importato con Blosm da file, 3Dsimple, singleObject off.
      Proiezione TM centrata sul node 10249190464 (scene lat/lon impostati prima dell'import), quindi traslazione 0; Empty `OSM_Root`
      con rotZ −48,7°, genitore dei 13 empty di layer; tutto in collezione `OSM_Riferimento` (way_profiles nascosta).
      393 oggetti (139 edifici, 1 coastline, 5 vegetazione, 3 aree pedonali, 245 curve strade/percorsi), ~5,3k tri valutati. SOLO riferimento, non esportare.
      Verifiche: way ponte (0,0)→(−5,2; −178,9), pennoni (−2,3; −80,2) e (−3,8; −128,5); ciglio coastline Y 80,5→79,1 da X 19 a 549
      (−0,15°), bordo area pedonale Y 80,0 da X 0 a 561, footway Morin (9,0; 85,9)→(560,6; 85,4); radice molo NE e punta molo entro 0,5 m.
      Nota: nell'import non ci sono pontili (man_made=pier) né filari/alberi; i 5 poligoni di vegetazione sono anonimi. Le curve stanno a Z +0,3 (offset Blosm).
      La coastline è una sola mesh a soli spigoli, estesa ~5 km (way intera).
- [x] (blender-artist) Blockout: piano banchina, bordo, camminamento, fascia verde, volume del ponte
      (impalcato + antenna come scatole), testata Mirabello, edifici di fondale come blocchi
      2026-11-18, `blender/blockout_blocco1.blend`, collezione `Blockout` (sotto-collezioni Passeggiata, Ponte, Mirabello, Fondale,
      Asset, Palme_Istanze). Camminamento a Z 0, lastre fino a Z −3, cordolo 0,2 m a Y 89, Giardini a Mare con aiuole 0,3-0,4 m,
      vialetto da 4 m e 4 varchi da 4 m, siepe limite 1,5 m a Y 116-118. Ponte: impalcato 6 m (8 m agli anelli), rampa Y 0→−70 al 6,1 %,
      calpestio Z 4,3 da Y −70 a −136,1, discesa al 7 % fino a Z 1,30 a Y −179, parapetti 1,1 m, 2 antenne fino a Z 33,5.
      Mirabello: rampa al 7 % al posto della scala (Z 0 a Y −197,5), testata 30 × 49,4 m a Z 0. Quote [S] e scelte in `docs/decisioni.md`.
      Linea di vista da (240, 84, 1,8): entrambe le antenne libere da Z 10 a 33 (raycast + camera `CAM_Partenza`).
      Da verificare in UEFN: con bCombineMeshes gli UCX_ di più mesh nello stesso FBX devono diventare tutti collisione.
- [x] (blender-artist) Segnaposto cilindrici per le palme al passo reale
      `SM_Blockout_PalmaSegnaposto` (Ø 0,5 × 9 m + chioma 6 m a Z 8-10, 38 tri, UCX tronco). 53 istanze collegate (passo 9 m [S],
      filari sfalsati) in `Blockout_Palme_Istanze`, non esportate; posizioni UE in `exports/blockout/palme_posizioni.csv`
- [x] (blender-artist) Export del blockout in 3-4 FBX per zona -> `exports/blockout/`
      Con `morin_export.py`: Passeggiata 121 tri, Ponte 408, Mirabello 58, Fondale 517 (mode scene), PalmaSegnaposto 38 (mode asset).
      Primo uso del mode scene verificato leggendo gli FBX: bbox in uu ricostruita dal file = bbox prevista per tutti e 5 (UnitScaleFactor 1,
      Lcl Rotation Z −90, Translation 0)
- [x] (uefn-builder) Import e posa; Water Body del golfo alla quota corretta; spawn alla partenza
      2026-11-18, dettagli in `docs/uefn_blockout.md`. 5 asset in `LaSpezia/Blockout`, bbox = attese (±1 uu), tri 121/408/58/517/38,
      convessi 13/34/5/53/1 = numero di UCX (con più mesh per FBX li prende tutti). Nanite già off; LOD auto rimosse (solo LOD0,
      altrimenti su mobile si vedeva LOD2 dimezzata). 4 attori in `Blockout` a (0,0,0); palme = 1 attore HISM con 53 istanze
      (campioni 0/26/52 = CSV). Acqua: **device Acqua V2** (superficie Z −150, X −17100..34100, Y −11954..31054, niente onde):
      il WaterBodyLake nativo dava errori del validatore UEFN (riferimenti illegali a /Water) ed è stato rimosso.
      Spawn pad a (24000, −8250/−8650, 0), yaw 30 → PlayerStart yaw 180 (verso il ponte), su pavimento Z 0. GridPlane spostati
      a Z −10000 (`Template_Spostati`, non cancellati). Antenne visibili dalla partenza (trace + render `docs/qa/uefn_blockout_*.png`).
      Da confermare in sessione (qa-tester): HISM palme in gioco, nuoto e risalita sul ciglio
- [x] (uefn-builder) Barriere invisibili sul lato città e ai limiti del blocco
      6 Barrier device (Invisibile, Sempre, alte 3840 uu da Z −700): lato città Y −11930 (X −3510..27210), fine blocco X 25130
      (Y −12110..−6990; dal 2026-11-19 fino a Y 33970), molo/area militare X −1360 (Y −12020..3340), testata Mirabello su 3 lati. Lato mare aperto.
      Aperto: chi nuota può raggiungere la riva del fondale (area militare, Mirabello) a Z 0 → serve il rientro dall'acqua (Verse)
- [!] (qa-tester) Prova di percorrenza: tempo partenza -> fine ponte, punti d'incastro, linea di vista
      sull'antenna, caduta in acqua. Report in `docs/qa/`
      2026-11-18, report `docs/qa/2026-11-18_blockout_percorrenza.md`. PARZIALE: la sessione non parte
      (matchmaking `invalid_region`, regione NONE). In editor, con sweep di capsula r32/hh75 e r42/hh88: nessun incastro
      sul percorso, antenne visibili da 6 punti, corsie agli anelli 3,36-3,39 m, impalcato 5,7 m. Percorso 502 m fino a
      fine ponte, 530 m fino al traguardo: STIMA 80 s di scatto (630 uu/s) / 112 s di corsa base (450 uu/s).
      Da rifare in sessione: spawn, palme HISM, nuoto e risalita, barriere attive, tempo cronometrato, scala con il personaggio
- [x] (utente) Impostare la regione di matchmaking (Europa) in Fortnite/UEFN: senza, `StartSession` fallisce con
      `invalid_region`. Chiudere l'eventuale finestra di errore "Impossibile giocare" rimasta aperta nell'editor
      2026-11-19: fatto. La sessione parte (matchmaking OK, server DE)
- [!] (qa-tester) Ripetere in sessione le voci non verificate del report 2026-11-18 (§1, 2, 3, 6, 7, 8)
      2026-11-19, report `docs/qa/2026-11-19_blockout_sessione.md`. OK: avvio della sessione, log client senza errori
      dell'isola, spawn sul camminamento rivolto al ponte con le 2 antenne visibili (screenshot `qa_sessione_spawn_partenza.png`).
      NON VERIFICABILE via MCP: il client non registra gli strumenti MCP (`MCPListToolsets` non registrato, `ListClients` vuoto),
      quindi niente posizione del giocatore. `FortPlayerToolset` comunque non muove il giocatore. Restano: tempo cronometrato,
      palme HISM, nuoto e risalita, barriere, costruzione disattivata, scala accanto a parapetti e palme. Nessun tempo misurato.
      Nota: lo scatto consuma resistenza (`TacSprintStamScene`), quindi la stima di 80 s è ottimistica
- [ ] (utente) Prova manuale in sessione con la checklist del report `docs/qa/2026-11-19_blockout_sessione.md` (~10 min):
      tempo partenza → fine ponte / → Mirabello (con e senza scatto), palma, parapetto (screenshot), tuffo e risalita,
      costruzione, barriere. In alternativa l'orchestratore sceglie un altro metodo (vedi task verse-dev qui sotto)
- [ ] (verse-dev) Opzionale, per la QA automatica: device Verse di debug che con `Print()` scrive in `GetVerseOutput`
      i tempi (partenza → fine ponte) e gli eventi (in acqua, fuori area), leggibili via MCP anche senza strumenti client
- [x] (uefn-builder) Bloccare l'ora del giorno sul tardo pomeriggio: in sessione il ciclo giorno/notte del template è attivo
      (`DaySequence` in riproduzione) e alla prova era notte; il ciglio si legge peggio (QA 2026-11-19, gravità bassa)
      2026-11-19: device Sequenza giorno `Luce_OraDelGiorno` (cartella `Luci`), Modalità ciclo = ORARIO FISSO, ora 18,0,
      fase TUTTO, priorità 2000, nessun override di sole/cielo/nebbia. Island Settings "Orario" lasciato PREDEFINITO (una sola fonte).
      In editor: sole a 27° di elevazione, le ombre delle palme cadono sul camminamento verso il mare (`docs/qa/uefn_ora18_*.png`).
      Da confermare nella prova manuale che in sessione resti giorno e non avanzi
- [x] (uefn-builder) Chiudere l'uscita a nuoto oltre la fine del blocco: `Barriera_LatoCitta` finisce a X 27210,
      ma il fondale cittadino a Z 0 continua fino a X 33000 (oppure allungare in mare `Barriera_FineBlocco`, oggi fino a Y −6990)
      2026-11-19: `Barriera_FineBlocco` portata a profondità 90 unità e centro (25130, 10930, −700): copre Y −12110..33970,
      cioè tutto il volume d'acqua (Y −11954..31054), e si sovrappone a `Barriera_LatoCitta`. Oltre X 25258 non si arriva più.
      *Influenza della distanza dissolvenza* = NO sulle due barriere lunghe. Da confermare in sessione che blocchino davvero
- [x] (uefn-builder) Island Settings: "Consenti costruzione" è TUTTI. Proposta: Nessuno per la corsa (da confermare con l'utente)
      2026-11-19 (confermato dall'utente): riletto `AllowBuilding` = None (NESSUNO). Scatto: `bAllowSprinting` = True,
      governato dal preset di locomozione "BR attuale" (moltiplicatore 1,4×), lasciato com'è

**Cancello 1:** si corre dalla partenza al fondo del ponte senza incastri; tempo misurato e annotato;
la scala "sembra giusta" con un personaggio accanto a parapetti e palme.
**[x] Superato 2026-11-19** con prova manuale dell'utente (grafica v2 già posata): palme solide, risalita dalle
scalette con acqua a −1 m, ponte attraversato, barriere ok; ~50 s di corsa sulla banchina con due scatti.
Aperto: la texture delle lastre non appare in gioco (si vede il grigio del blockout), in correzione da uefn-builder.

---

## Fase 2 — Prototipo di gioco (RIMANDATA il 2026-11-19: priorità alla fedeltà della mappa, vedi CLAUDE.md §1)
Obiettivo: la corsa è divertente prima di essere bella.

- [ ] (utente) Confermare o cambiare la modalità proposta (corsa a tempo con ancore dorate)
- [ ] (verse-dev) Documento breve `docs/gameplay.md`: regole, condizioni di vittoria, device usati
- [ ] (uefn-builder) Partenza con conto alla rovescia, 3-4 checkpoint, traguardo a fine ponte
- [ ] (uefn-builder) 10-15 collezionabili: facili sulla corsia, difficili su battelli e fascia verde
- [ ] (verse-dev) Logica: timer, conteggio ancore, rientro da caduta in acqua entro 3 s, classifica finale
- [ ] (uefn-builder) Almeno una scorciatoia rischiosa (salto sui battelli) e una deviazione sicura
- [ ] (qa-tester) 5 corse complete: durata, punti morti, chiarezza del percorso. Report con proposte

**Cancello 2:** una corsa dura 60-90 s, il percorso si capisce senza spiegazioni, l'utente dice che è divertente.

---

## Fase 3 — Arte del Blocco 1
Obiettivo: sostituire il grigio con asset definitivi, uno alla volta, senza rompere il gioco.
Ordine per impatto visivo:

- [ ] (blender-artist) **Ponte Thaon di Revel** da `ref/ponte.md`: impalcato, antenna, stralli, parapetti
- [x] (geo-scout) Schede per la grafica di palme e banchina (2026-11-19): `ref/palme.md`, `ref/banchina.md`, `ref/asset_fonti.md`
      Specie: filari a prevalenza Phoenix dactylifera (tag OSM) con possibile P. canariensis (Comune, 2014): certezza media.
      Restano [S]: passo delle palme (9 m, coerente con il conteggio comunale), altezze, materiali del ciglio, bitte, scalette, lastre.
      Servono le foto elencate in fondo a `palme.md` e `banchina.md`
- [ ] (blender-artist) Kit banchina: modulo dritto 4 m, testata, bitta, scaletta (scheda `ref/banchina.md`)
      Da QA 2026-11-18: ciglio del molo continuo (oggi "a denti" X 1020 → 900 → 800) e parapetti del ponte svasati
      all'imbocco (oggi spigoli verticali di 1,1 m a Y 0)
      - [x] v1 2026-11-19 (in Blender, da importare): `SM_Banchina_Mod4m` (276 / 138 / 40 tri), `SM_Banchina_Bitta`
            (970 / 484 / 144), `SM_Banchina_Scaletta` (736 / 368 / 110), con UCX; FBX in `exports/banchina/` (LOD in file
            `_LOD1`/`_LOD2` separati). Texture 2048 `T_Banchina_Ciglio/Paramento/Ghisa_D/N/ORM` da Poly Haven CC0.
            Sorgente `blender/arte_banchina_palme.blend`; render `docs/qa/arte_banchina_v1.png`, `arte_contesto_v1.png`
      - [x] v2 2026-11-19: texture del ciglio e del colore del paramento dalle foto dell'utente, stessi FBX ri-esportati
            (geometria invariata). Render `docs/qa/arte_banchina_v2.png`, `arte_contesto_v2.png`. Copia v1: `blender/arte_banchina_palme_v1.blend`
      - [x] (blender-artist) testata/angolo e raccordo col molo; modulo con nicchia per la scaletta — banchina v2 del 2026-11-20 (vedi sotto)
      - [x] (blender-artist) **Banchina v2, 2026-11-20** (in Blender ed esportata, DA IMPORTARE): `blender/arte_banchina_v2.blend`,
            script `blender/scripts/morin_banchina_v2.py`, FBX in `exports/banchina_v2/` (LOD in file `_LOD1/_LOD2` con rotazione nei vertici),
            posizioni UE `exports/banchina_v2/banchina_posizioni_v2.csv` (83 righe, formato a 6 colonne). Tri LOD0/1/2:
            `SM_Banchina_Mod4m_v2` 164/92/12 (ciglio a 3 grandi blocchi bianchi, toro r 0,15) · `SM_Banchina_Mod4m_Nicchia` 234/146/58 ·
            `SM_Banchina_Scaletta_v2` 448/202/82 (a filo nella nicchia, UV puliti) · `SM_Banchina_Bitta_v2` 970/484/144 (UV degeneri corretti) ·
            `SM_Banchina_Testata` 845/473/39 (smusso 45° + ciglio est del molo fino a Y 62) · `SM_Banchina_Testata_Fine` 67/39/19 ·
            `SM_Morin_AncoraMonumento` 1506/662/258 (2,70 × 3,16 × 2,72 m, X 226 Y 83). Texture `blender/textures/banchina_v2/T_Banchina_Blocchi_*`.
            Confronti `docs/qa/arte_banchina_v3_confronto_ciglio.png`, `_ancora.png`. Scelte e [S] in `docs/decisioni.md` (2026-11-20).
      - [x] (uefn-builder, 2026-11-20 ~05:10-05:25) import della banchina v2 (`docs/uefn_arte.md` §21): 7 mesh in `LaSpezia/Arte/Banchina`
            (tri LOD0/1/2 come da Blender, UCX 1/1/3/1/3/1/4 convessi, Nanite off, Simple-as-Complex, MinLOD L/M 2), `T_Banchina_Blocchi_D/N/ORM`
            2048 (LODBias 0) + `MI_Banchina_Blocchi`; Ghisa/Paramento riusano le MI v1. HISM nuovi `Arte_Banchina_Moduli_v2` (54),
            `_Nicchie` (4), `_Scalette_v2` (4), `_Bitte_v2` (**6**, solo X ≤ 90 m: decisione dell'utente, zona d'imbarco), attori
            `Arte_Banchina_Testata`, `_Testata_Fine`, `_AncoraMonumento`. **Nascosti, non cancellati:** `Arte_Banchina_Moduli`, `_Bitte`, `_Scalette`.
            Line trace: ciglio continuo X 19,0-251,4 m (testata/Mod_00 senza buchi), scalette nelle nicchie con collisione, ancora solida.
            Render `docs/qa/uefn_banchina_v2.png`. Validazione 393/393, 0 errori.
      - [x] (utente, 2026-11-20) DECISO: l'ancora resta dov'è, deroga alla corsia di 8 m in `docs/decisioni.md` (gioco rimandato).
            L'ancora monumentale (Y 81,8-84,9 m) occupa 3,2 m dei 9 m del camminamento e lo divide:
            1,8 m lato mare e 4,1 m lato palme, sotto gli 8 m di corsia libera (§3) per ~2,7 m di lunghezza. Nella foto
            `banchina_vista_montagne_verso_ponte.jpg` sta davvero sul camminamento: accettare la deroga o spostarla verso la fascia palme.
      - [x] (orchestratore + utente) quota dell'acqua: DECISO 2026-11-19, acqua a −1,0 m. Applicato da uefn-builder: device
            Acqua V2 da Z −534 a −484, superficie Z −100, fondo −484, barriere (base −700) invariate, nessun buco sotto il ponte né a Mirabello
      - [x] (uefn-builder) import, materiali con ORM, LOD — 2026-11-19, dettagli in `docs/uefn_arte.md`.
            `LaSpezia/Arte/Banchina`: Mod4m 276/138/40 tri, 400×55×300 uu, 1 convesso; Bitta 970/484/144, 40×40×46,6, 1 convesso;
            Scaletta 736/368/110, 55×50,5×333,7, 3 convessi (= UCX). Texture 2048 (D embedded, N/ORM da `blender/textures/`).
            MI su master `M_Morin_Master_PBR` (ORM R/G/B = AO/Rough/Metal). Nanite off, collisione Simple-as-Complex.
            Posa HISM: `Arte_Banchina_Moduli` 58 moduli X 1920..25120 sulla retta del ciglio del blockout (+8 cm verso il mare, Z +2,5),
            `Arte_Banchina_Bitte` 18 (ogni 12 m, X 26-230 m), `Arte_Banchina_Scalette` 4 (X 44/92/140/188 m).
            Nota: `import_lod` ignora la rotazione −90° del nodo → LOD importati con un giro (vedi doc). Render `docs/qa/uefn_arte_v2_*.png`
      - [x] (blender-artist) pulire normali/tangenti degeneri di Bitta e Scaletta (avvisi all'import); LOD esportati con la rotazione
            applicata ai vertici; pezzo testata/angolo (estremità a vista a X 19,2 m e 251 m) — fatto nella banchina v2 (2026-11-20)
      - [ ] (qa-tester) verifica in sessione: bitte e moduli solidi, risalita dalle scalette, nuoto con l'acqua a −1 m
- [ ] (blender-artist) Palma A + 2 varianti: schede `ref/palme.md` e `ref/asset_fonti.md`
      Dalle foto dell'utente: PalmaA = **P. canariensis**; le varianti B/C = dactylifera slanciate
      - [x] v1 `SM_Morin_PalmaA` 2026-11-19 (in Blender, da importare): 7.536 / 3.660 / 904 tri, UCX sul tronco, bbox
            9,2 × 9,5 × 11,6 m; FBX in `exports/palme/`. Fronde su card (atlas procedurale 2048 con alfa, two-sided),
            tronco a rombi procedurale + Poly Haven CC0. Render `docs/qa/arte_palmaA_v1.png`
      - [x] v2 2026-11-19: 8.480 / 3.588 / 1.000 tri, bbox 10,0 × 10,1 × 12,0 m; tronco Ø 0,8 m con piede svasato,
            ananas Ø ~1,3 m con squame più grandi, chioma asimmetrica e ricadente, 6 fronde secche; texture di tronco e
            colori delle fronde dalle foto dell'utente. Render `docs/qa/arte_palmaA_v2.png`
      - [ ] PalmaB / PalmaC (dactylifera)
      - [x] (uefn-builder) import, materiale masked two-sided, LOD, sostituzione delle 53 palme segnaposto — 2026-11-19
            `LaSpezia/Arte/Palme/SM_Morin_PalmaA` 8.480/3.588/1.000 tri, 1002×1010×1200 uu, 1 convesso solo sul tronco (nessun impatto
            nella chioma). Fronde su `M_Morin_Master_PBR_Masked` (masked, two-sided, alfa della diffusa). Nanite off.
            `Arte_Palme_PalmaA` (HISM, 53 istanze alle posizioni CSV, yaw casuale, scala 0,9-1,1). Segnaposto `Blockout_Palme_HISM`
            nascosto (Z −10000, cartella `Blockout/Sostituiti`), non cancellato. Linea di vista sulle antenne libera (chioma più vicina a 6,7 m)
      - [ ] (qa-tester) palme HISM visibili e solide in sessione
- [ ] (blender-artist) Kit pavimentazione e cordoli
      - [x] texture 2048 pronte (2026-11-19, dalle foto dell'utente): `T_Pav_Lastre_*` (tile 3,2 m, lastre 0,4 × 0,6-0,8 m,
            lati lunghi trasversali alla passeggiata), `T_Pav_Cubetti_*` (tile 3,2 m, coda di pavone), `T_Pav_Fascia_*`
            (tile 1 m, pietra chiara). Materiali `M_Pav_*` nel .blend; nessuna mesh ancora
      - [x] (uefn-builder) texture importate in `LaSpezia/Arte/Pavimentazione` e istanze `MI_Pav_Lastre`/`_Cubetti` (tile 3,2 m),
            `MI_Pav_Fascia` (1 m) su `M_Morin_Master_Pav`, che proietta in coordinate mondo (le UV del blockout sono nulle).
            `MI_Pav_Lastre` messo come override sull'attore `Blockout_Passeggiata` (slot Pietra), asset invariato. La fascia palme mostra
            lastre finché non arriva la mesh. 2026-11-19
      - [x] mesh v1 2026-11-19 (in Blender, da importare): sorgente `blender/arte_pavimentazione.blend` (script
            `blender/scripts/morin_pav_kit.py`), FBX in `exports/pavimentazione/`, posizioni UE in `pav_posizioni.csv`.
            `SM_Pav_Camminamento_4m` 2 tri (4 × 8,16 m, stesse trasformazioni dei 58 moduli banchina, Z 0),
            `SM_Pav_Cordolo_9m` 76/26/18 tri (striscia tattile + cordolo chiaro a +3 cm), `SM_Pav_FasciaPalme_9m` 50 tri
            (cubetti + fasce chiare 0,25 m, 27 istanze a X 975 + 900k uu), `SM_Pav_Aiuola` 64/26/18 (2,2 m, 53 alle palme),
            `SM_Morin_Panchina` 240/104/32 (2,2 × 0,5 × 0,45 m, 4 istanze X 34,5-61,5 m). LOD esportati con rotazione nei vertici
            (`morin_export.py`, nuova opzione `bake_rotation`). Texture nuova `T_Pav_Terra_*` (procedurale). Blockout
            ribassato `exports/blockout/SM_Blockout_Passeggiata_Pav.fbx` (128 tri, 17 UCX). Render `docs/qa/arte_pav_v1_corsia.png`,
            `arte_pav_v1_alto.png`. [S]: cordolo quasi a raso (OSM dice 20 cm), misure di aiuole, fasce e panchine stimate dalle foto
      - [x] (uefn-builder) 2026-11-19: kit importato in `LaSpezia/Arte/Pavimentazione` (senza texture/materiali duplicati), Nanite off,
            Simple-as-Complex, convessi = UCX (blockout: 13, come gli oggetti UCX dell'FBX, non 17). LOD di cordolo/aiuola/panchina
            via asset temporanei (`import_lod` li ruota ancora di +90°). `MI_Pav_Terra` (tile 2 m). Posa HISM in `Arte/Pavimentazione`:
            58 camminamento, 27 fascia, 27 cordolo, 53 aiuole, 4 panchine. Banchina −2,5 cm (moduli Z 0, bitte −1,2, scalette −1,3).
            `Blockout_Passeggiata` → `SM_Blockout_Passeggiata_Pav`. Tinta lastre (0,60; 0,56; 0,48) verso il grigio-bruno delle foto.
            Trace: nessun buco, cordolo +3, aiuole +4,5, panchine +45; linea di vista invariata; validazione pulita; sessione cotta,
            download 12,1 MiB. Dettagli e problemi aperti in `docs/uefn_arte.md` §11
      - [ ] (qa-tester) prova in sessione di cordolo, aiuole, panchine e raccordo ciglio; (utente) colore dei cubetti, cordolo +3 cm [S]
      - [x] v2 fascia palme + arredi 2026-11-19 (in Blender, da importare; dati [V-utente] in `ref/sezione.md` §6): filari allineati,
            fascia a **Z +0,15** con cordolo a gradino di 15 cm, strisce sul bordo aiuole lato corridoio + trasversale a metà fra due palme.
            Ri-esportati con lo stesso nome: `SM_Pav_Cordolo_9m` 74/24/20, `SM_Pav_FasciaPalme_9m` 36, `SM_Pav_Aiuola` 64/26/18 (3,6 × 3,0 m),
            `SM_Morin_Panchina` 306/134/42 (2,8 × 0,5 × 0,45 m, 3 piedi). Nuovi in `exports/arredi/`: `SM_Morin_Lampione` 2.400/1.078/294
            (1,48 × 0,38 × 4,82 m, 2 UCX), `SM_Morin_Tombino` 20/4/4 (1,76 × 0,60 m, 1 UCX), `SM_Morin_Gazebo` 2.522/1.344/574
            (4,0 × 3,46 × 4,25 m, 16 UCX). Posizioni `exports/pavimentazione/pav_posizioni_v2.csv` (194 istanze) e `palme_posizioni_v2.csv`
            (53 palme, Z 15). Copia v1: `blender/arte_pavimentazione_v1.blend`. Render `docs/qa/arte_pav_v2_*.png`
      - [x] (uefn-builder) v2 + v3 in UEFN 2026-11-19 (11:27-11:45 UTC; il primo tentativo delle 11:16 si era fermato per una finestra
            modale): import da zero in `LaSpezia/_Temp` con `ImportFile` e copia nell'asset esistente di LOD0/1/2 e collisione (metodo e cosa
            NON usare in `docs/uefn_arte.md` §12). Cordolo 74/24/20 (2 UCX), fascia 36 (1), aiuola 64/26/18 (1), panchina 306/134/42 (1),
            lampione 2.400/1.078/294 (2), tombino 20/4/4 (1), gazebo v3 2.570/1.392/432 (16): bbox di ogni LOD verificate, Nanite off,
            Simple-as-Complex. MI nuove `MI_Morin_Ghisa/Globo/Tombino/Gazebo_Fregio` (+ master `M_Morin_Master_Emissivo`), texture tombino
            1024 e fregio 2048×512; tinta `MI_Pav_Cubetti` (0,62; 0,58; 0,52). Posa: 54 aiuole, 13 panchine, 54 palme (Z 15), HISM
            `Arte_Arredi_Lampioni` 7 e `Arte_Arredi_Tombini` 8, `Arte_Arredi_Gazebo` a (2550, −9300, 15). Trace: gradino cordolo 15 cm,
            fascia da X 9,75, lampioni solidi solo nel fusto, tombini a raso, gazebo senza incastri (3 varchi liberi), 54/54 tronchi,
            linea di vista invariata. Validazione 68/68, push v6: download 13,0 MiB. 33 temporanei in `_Temp` (non cancellati, elenco nel doc).
            Render `docs/qa/uefn_pav_v3_*.png`
      - [ ] (utente) conferma misure [S]: aiuola 3,6 × 3,0, spostamento panchina 0,5 m verso il mare, pensilina Ø 3,2 m (dalle foto coincide con OSM)
      - [x] v3 gazebo e posizioni 2026-11-19 (in Blender, da importare; correzioni [V-utente]): tetto a piramide esagonale con falde
            a ~30°, lanternino e pinnacolo, h 5,12 m; `SM_Morin_Gazebo` **2.570 / 1.392 / 432 tri** (4,0 × 3,46 × 5,12 m, 16 UCX, tetto = 1 convesso)
            in `exports/arredi/gazebo_v3/` (stessi nomi file). Un solo gazebo a **X 25,5, Y 93** (UE 2550, −9300, 15), fra la 2ª e la 3ª palma;
            torna Palma_F1_04 (X 39) con l'aiuola: **54 palme**. CSV `pav_posizioni_v3.csv` (195 istanze) e `palme_posizioni_v3.csv` (54),
            controllo impronte 0 conflitti. Rispetto alla v2 cambiano solo: Gazebo_00 (X 4000 → 2550), + Aiuola_F1_04 e + Palma_F1_04 (3900, −9260, 15).
            Copia v2: `blender/arte_pavimentazione_v2.blend`. Render `docs/qa/arte_pav_v3_gazebo.png`, `arte_pav_v3_dalponte.png`
      - [x] (uefn-builder) v3 applicata insieme alla v2 (vedi sopra): gazebo da `gazebo_v3/`, 54 palme e 54 aiuole
      - [ ] (qa-tester) prova in sessione della v3: cordolo, gazebo (ingresso dai varchi), panchine, lampioni; (utente) tinta cubetti e globi;
            (utente) conferma per eliminare i 33 temporanei di `LaSpezia/_Temp`
- [~] (blender-artist) Arredi: lampione, panchina, cestino, parapetto
      2026-11-19: lampione, panchina v2, tombino e pensilina fatti (vedi kit pavimentazione v2). Restano cestino, rastrelliere, parapetto
- [ ] (blender-artist) Battello turistico stilizzato, senza marchi reali
- [~] (blender-artist) Pini, oleandri, aiuole della fascia verde (2026-11-19: oleandri ad alberello e panchina lunga fatti, vedi Giardini a Mare v1; pino domestico nel kit molo)
- [x] (geo-scout) Scheda del fondale `ref/fondale.md` + dati `ref/dem/` (2026-11-19): Copernicus DEM GLO-30 (licenza verificata),
      griglia locale 30 m ±10 km, profili d'orizzonte da 4 punti, cime OSM, copertura CORINE per azimut, edifici OSM entro 1,2 km,
      grafico `docs/qa/fondale_profilo.png`, proposta tecnica (anelli, ≤ 55k tri, 8 settori, texture 1024). Crediti in `docs/CREDITS.md`.
      Restano [S]: nomi dei crinali lontani, colle del centro, limiti di distanza in UEFN, colori da tarare
- [x] (blender-artist) Fondale: sagome di edifici e colline (dalla scheda `ref/fondale.md` §7)
      2026-11-19, `blender/arte_fondale.blend` + `blender/scripts/morin_fondale.py` (parametrico; build e export ripetibili).
      Terreno RTIN dal DEM 30 m (filtro binomiale 3x3, errore ammesso 1 m < 1,5 km, 2 m a 1,5-5 km, 3 m + 2,5 m/km oltre, x4 sulle
      celle non visibili dalla partenza; creste dei 4 profili forzate; costa raffinata e gonna a Z -10), 8 settori da 45° dalla
      partenza `SM_Fondale_Colline_<N..NO>` = **47 887 tri LOD0** (1 389-7 656 per settore), LOD1 26 067 (54 %), LOD2 7 184 (15 %);
      tenda dei crinali oltre 9,75 km `SM_Fondale_Tenda` a 13 km (412/210/106 tri, dal GeoTIFF + profili). Totale terreno 48 299.
      Città (anello A 0,25-1,5 km): 2 249 edifici OSM estrusi (piani OSM o DSM) in 12 blocchi `SM_Fondale_Citta_<settore>_NN`
      ≤ 5k tri, 33 728 / 16 947 / 6 143 tri; facciata generica `T_Fondale_Facciata_D` × colore vertice. Texture 1024 per settore
      in UV polari (CORINE + quota + case dipinte), `blender/textures/fondale/`. 63 FBX in `exports/fondale/`, posizioni UE in
      `exports/fondale/fondale_posizioni.csv` (pivot al centro della bbox, yaw 0, Z 0). Nessuna collisione.
      Verifica silhouette (raycast sulle mesh) contro i profili: dalla partenza scarto medio +0,04°, RMS 0,21° (picchi: Santa Croce
      10,16° vs 10,3°, Parodi 9,65° vs 9,7°, Castellana 6,8° vs 6,7°); dall'imbocco RMS 0,15°. Render `docs/qa/arte_fondale_v1_*.png`.
      Blockout fondale **integrato, non sostituito** (escluso il suo rettangolo X -166..332, Y -305..302)
- [x] (uefn-builder) Import e posa del fondale da `exports/fondale/` (vedi `fondale_posizioni.csv` e note in `docs/decisioni.md` 2026-11-19
      "Fondale"): ImportFile, Nanite off, cull 0, niente collisione, Is Spatially Loaded = NO, materiale facciate × VertexColor
      2026-11-19, dettagli in `docs/uefn_fondale.md` §8: 21 asset in `LaSpezia/Arte/Fondale` (LOD0 82 025 tri: terreno+tenda 48 297,
      città 33 728/16 947/6 143 con LOD; colline e tenda solo LOD0, motivato), bbox = CSV, nessuna collisione, Nanite off. Colore vertice
      della città reimportato con FbxFactory esplicita (ImportFile lo scarta). Master `M_Morin_Master_Fondale` + 10 MI. 21 attori
      `Arte_Fondale_*` (Outliner `Arte/Fondale`): NoCollision, Spatially Loaded NO, HLOD NO, cull 0, ombre solo sulla città.
      Barriere nuove `Barriera_Acqua_LatoMare` e `Barriera_Acqua_LatoMenoX` sui lati aperti del volume d'acqua. Validazione 0 errori;
      Project Size v7 21,4 MiB in download (era 13,0). Render `docs/qa/uefn_fondale_v1_*.png`. 60 temporanei in `_Temp`
      - [ ] (qa-tester) sessione: fondale senza pop-in, barriere d'acqua, nebbia alle 18, giunzione col mare
      - [ ] (utente) colline più chiare/gialle delle foto e facciate molto chiare: tarare `Tinta` delle MI o l'albedo in Blender?
- [x] (uefn-builder) Verificare la distanza massima di rendering/posizionamento in UEFN (fondale fino a ~10 km = 1 000 000 uu) e la nebbia
      2026-11-19, sola lettura, dettagli in `docs/uefn_fondale.md`: cubi in memoria a 1,5-15 km disegnati (LWC attivo, cull 0,
      piano lontano infinito); tetto = cupola del cielo a ~36 km → scala reale fino a 15 km, nessuna omotetia. Streaming World
      Partition oggi spento (se attivato: raggio 256 m → fondale con Is Spatially Loaded = NO). Nebbia del template troppo uniforme:
      proposta *Override nebbia* sul device (densità 0,003-0,004, diminuzione 0,01, opacità 1,0). Acqua V2 max 512 m per device:
      non allungabile all'orizzonte, oltre resta la mesh del cielo. Render `docs/qa/uefn_fondale_*.png`
- [x] (uefn-builder, dopo il fondale) Applicare *Override nebbia* su `Luce_OraDelGiorno` e tararla col fondale vero (`docs/uefn_fondale.md` §4)
      2026-11-19 (§8.4): densità 0,004, diminuzione 0,02 (0,01 ingrigiva il cielo), opacità 1,0, colore (0,30; 0,38; 0,52), seconda nebbia 0.
      Sole, cielo, ora 18 e priorità invariati. Antenne leggibili contro il Castellana; render prima/dopo `uefn_fondale_v1_nebbiaPrima_*`
- [ ] (utente) Decidere se serve un anello di mare solo visivo oltre l'acqua di gioco (deroga a CLAUDE.md §4, `docs/uefn_fondale.md` §5)
      2026-11-19: con il fondale e la nebbia nuova, dai render (135°) nessuna fascia scura alla giunzione: per ora sembra non servire
- [~] (uefn-builder) Sostituzione progressiva del blockout; palme e arredi come istanze
      2026-11-19: sostituiti ciglio (kit banchina), palme (PalmaA) e aspetto del camminamento (override lastre). Restano ponte, fondale,
      arredi. Pavimentazione come mesh posata il 2026-11-19 (§11 di `docs/uefn_arte.md`). Memoria: Project Size dopo la sessione
      delle 10:21 UTC = 12,1 MiB in download (era 531 KB col solo blockout); stima texture ≈ 99 MiB a piena risoluzione su 300 MiB
      di limite di pubblicazione (calcolo esatto dal pannello Memoria, utente).
      Per `GetCost` serve il percorso del Mali Offline Compiler (preferenze dell'editor, utente)
- [ ] (uefn-builder) Luce del tardo pomeriggio, cielo, nebbia leggera sul golfo
- [ ] (uefn-builder) Audio ambientale: gabbiani, acqua, sartie
- [ ] (qa-tester) Dopo ogni sostituzione importante: collisioni e percorrenza invariati

**Cancello 3:** nessun volume grigio visibile nel Blocco 1; il ponte è riconoscibile dalla partenza.

---

## Fase 4 — Ottimizzazione
- [ ] (blender-artist) Collisioni UCX_ su tutti gli asset; verifica budget triangoli
- [ ] (uefn-builder) Controllo "Dimensioni del progetto" e calcolo della memoria
- [ ] (qa-tester) Profilazione con unreal-insights; elenco dei 5 asset più pesanti
- [ ] (blender-artist) Riduzione degli asset segnalati

**Cancello 4:** memoria dentro i limiti di UEFN con margine per i blocchi 2 e 3.

---

## Fase 5 — Rilascio del Blocco 1
- [ ] (orchestratore) `docs/CREDITS.md` completo (OSM, Poly Haven, autori CC-BY)
- [ ] (orchestratore) Controllo finale: nessun dato Google, nessun marchio reale, nessun volto nelle texture
- [ ] (utente) Caricamento in versione privata e prova con amici
- [ ] (utente) Decisione: pubblicare o proseguire con i blocchi successivi

---

## Dopo l'MVP
- [ ] Blocco 2: tratto centrale e imbarco battelli (ripetere Fasi 0-4 sul nuovo blocco)
      Elementi confermati dall'utente il 2026-11-19 (foto in `ref/foto/arredi/` e `ref/foto/pavimentazione/`):
      cannone antico su affusto e scultura "REDAMARE" (lettere in corten) sul ciglio **a metà dell'intera passeggiata (~275 m dal ponte)**;
      scritta "PASSEGGIATA MORIN" in pietre bianche nei cubetti all'inizio lato città (~550 m)
- [ ] Blocco 1, dettagli da fare: ~~ancora monumentale~~ e ~~ciglio a grandi blocchi bianchi~~ fatti in Blender il 2026-11-20 (banchina v2,
      da importare; l'ancora è all'OSM X 226, non all'imbocco del ponte); fascia longitudinale di lastre a ~1/3 del camminamento dal mare [S];
      Giardini a Mare (prato, aiuole di rose bordate in metallo, agavi, panchine bianche a schienale curvo); ponte con le foto in `ref/foto/ponte/`.
      Aiuole delle palme: terra (confermato dall'utente)
- [ ] Blocco 3: Molo Italia e faro rosso come finale esteso
- [ ] Modalità aggiuntive: nascondino tra i giardini, gara a squadre

---

## Log decisioni
| Data | Decisione | Motivo |
|---|---|---|
| 2026-11-18 | Soggetto: Passeggiata Morin invece di Piazza Verdi | Scelta dell'utente |
| 2026-11-18 | Primo blocco: ponte + ~250 m | Tratto più riconoscibile, dimensione gestibile |
| 2026-11-18 | Stile Fortnite stilizzato, niente fotogrammetria | Licenze, prestazioni, coerenza visiva |
| 2026-11-18 | Export FBX con `FBX_SCALE_NONE` + `bake_space_transform=True` | Unico preset che dà 1 m = 100 uu con l'import MCP (test di scala, giro 2) |
| 2026-11-18 | Blockout: scala di Mirabello sostituita da rampa al 7 %, quote ponte [S], varchi nei giardini | Pilastro 3; dettagli in `docs/decisioni.md` |
| 2026-11-19 | Acqua a −1,0 m; grafica v2 di banchina e palme importata in UEFN (HISM), segnaposto nascosti | Scelta dell'utente; dettagli in `docs/uefn_arte.md` e `docs/decisioni.md` |
| 2026-11-19 | Pavimentazione v2: filari allineati, cordolo a gradino di 15 cm (fascia palme a Z +0,15), panchine/lampioni/tombini/pensilina | Dati confermati dall'utente; dettagli e stime [S] in `docs/decisioni.md` |
| 2026-11-19 | Pavimentazione v3: gazebo con tetto a piramide (h 5,12 m), uno solo a X 25,5 fra la 2ª e la 3ª palma; torna la palma F1_04 (54 palme) | Correzioni dell'utente; dettagli in `docs/decisioni.md` |
| 2026-11-19 | v2/v3 in UEFN: asset aggiornati copiando LOD e collisione da temporanei importati da zero (mai reimport); master emissivo per i globi; tinta cubetti (0,62; 0,58; 0,52) | Evita la finestra modale e la rotazione di Interchange; dettagli in `docs/uefn_arte.md` §12 e `docs/decisioni.md` |
