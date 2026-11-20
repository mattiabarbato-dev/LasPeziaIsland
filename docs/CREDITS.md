# Crediti — Morin Rush

## Dati geografici
- Dati cartografici © OpenStreetMap contributors, disponibili con licenza ODbL
  (https://www.openstreetmap.org/copyright).
- Modello del terreno (fondale delle colline, dati in `ref/dem/`): Copernicus DEM GLO-30, licenza
  "Copernicus WorldDEM-30" (https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/DEM/resources/license/License-COPDEM-30.pdf),
  accesso da https://registry.opendata.aws/copernicus-dem/ il 19.11.2026. Nota obbligatoria per i dati modificati (mesh del fondale):
  "produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under
  COPERNICUS by the European Union and ESA; all rights reserved."
  In caso di ridistribuzione dei dati: "The organisations in charge of the Copernicus programme by law or by delegation do not
  incur any liability for any use of the Copernicus WorldDEM-30". Il progetto non è approvato né sostenuto dal programma Copernicus.
- Copertura del suolo (colori del fondale): CORINE Land Cover 2018 (vettoriale), "Generated using European Union's Copernicus
  Land Monitoring Service information", https://doi.org/10.2909/71c95a07-e296-44fc-b22b-415f42acfdf0 (accesso 19.11.2026,
  servizio EEA image.discomap.eea.europa.eu). Dati modificati (rasterizzati e ricolorati).

## Asset di terze parti
| Asset | Fonte | Autore | Licenza | Usato in |
|---|---|---|---|---|
| Concrete Floor Worn 001 (texture) | https://polyhaven.com/a/concrete_floor_worn_001 | Poly Haven | CC0 | grana fine (high-pass) in `T_Banchina_Ciglio_D`, `T_Pav_Lastre_D`, `T_Pav_Cubetti_D`, `T_Pav_Fascia_D`; normal e ORM di `T_Banchina_Ciglio_N/ORM` |
| Large Sandstone Blocks (texture) | https://polyhaven.com/a/large_sandstone_blocks | Rob Tuytel / Poly Haven | CC0 | `T_Banchina_Paramento_D/N/ORM` (luminanza; colore campionato dalle foto, fascia bagnata e alghe aggiunte) |
| Rusty Painted Metal (texture) | https://polyhaven.com/a/rusty_painted_metal | Poly Haven | CC0 | `T_Banchina_Ghisa_D/N/ORM` (ricolorata come vernice nera consumata) |
| Palm Tree Bark (texture) | https://polyhaven.com/a/palm_tree_bark | Poly Haven | CC0 | grana fine (high-pass) in `T_Morin_PalmaA_Tronco_D/N` |
| Rusty Metal 02 (texture) | https://polyhaven.com/a/rusty_metal_02 | Poly Haven | CC0 | `T_Morin_Corten_D/N/ORM` 1024 (Blocco 2, scultura REDAMARE): maschera della ruggine ricolorata come corten, normal e AO ridotti a 1024 (2026-11-20) |

Poly Haven: CC0, citazione facoltativa ma gradita. Poly Pizza: verificare la licenza di ogni modello;
se CC-BY, l'autore va citato qui.

Scaricate ma non usate negli asset (in `blender/textures/src/`): palm_bark, seaworn_sandstone_brick,
granite_wall (Poly Haven, CC0).

## Texture derivate dalle foto dell'utente (v2, 2026-11-19)
Fonte: foto fornite dall'utente in `ref/foto/`, pubbliche, con autorizzazione del Comune della Spezia dichiarata
dall'utente (CLAUDE.md §5). Strumento: `blender/scripts/morin_texphoto.py` (raddrizzamento prospettico, de-lighting,
sintesi tileable). Nei ritagli non ci sono persone, targhe, loghi o scritte (la scritta "PASSEGGIATA MORIN" di
060033 è esclusa dal ritaglio).

| Texture | Foto sorgente | Cosa è preso dalla foto | Parte procedurale o CC0 |
|---|---|---|---|
| `T_Banchina_Ciglio_D` | `banchina/passegiata_1.png` (fascia del ciglio, raddrizzata) | superficie e colore della pietra, sintetizzati a pezze | grana fine Poly Haven (concrete_floor_worn_001) |
| `T_Banchina_Paramento_D` | `banchina/passegiata_1.png` (zone bagnate del ciglio) | tinta grigia campionata | luminanza Poly Haven large_sandstone_blocks; fascia bagnata/alghe procedurali |
| `T_Pav_Lastre_D/N/ORM` | `banchina/passegiata_2.png` (lastre in primo piano, raddrizzate); verificato su `pavimentazione/pav_1.png` | superficie delle lastre (pezze), colore | posa a correre procedurale (corsi da 0,4 m, lastre 0,6-0,8 m), giunti, normal/ORM derivati |
| `T_Pav_Cubetti_D/N/ORM` | `banchina/Immagine 2026-11-19 060033.png` (cubetti in basso, sotto la scritta); disegno verificato su `Immagine 2026-11-19 060216.png` | colore di ogni cubetto (campionato dai pixel della foto), colore dei giunti | disegno a coda di pavone procedurale (archi R 1,15 m, cubetti 10 cm), normal/ORM derivati |
| `T_Pav_Fascia_D/N/ORM` | `banchina/Immagine 2026-11-19 060216.png` (fascia chiara al sole) | superficie e colore della pietra chiara | giunto ogni 1 m, grana Poly Haven |
| `T_Morin_PalmaA_Tronco_D/N/ORM` (metà sinistra, fusto) | `palme/Immagine 2026-11-19 055957.png` (tronco in primo piano, striscia centrale) | corteccia e cicatrici del fusto, colore | resa tileable, grana Poly Haven palm_tree_bark, normal/AO derivati dall'albedo |
| `T_Morin_PalmaA_Tronco_D/N/ORM` (metà destra, ananas) | `palme/Immagine 2026-11-19 055957.png` (ananas sotto la chioma) | colori delle placche e dei solchi (campionati) | squame a rombi procedurali (più grandi del fusto) |
| `T_Pav_Terra_D/N/ORM` (2026-11-19, aiuole) | `banchina/Immagine 2026-11-19 060216.png` (terra dell'aiuola in basso a sinistra) | solo i colori della terra (campionati, de-lit a occhio) | tutto il resto procedurale (rumore periodico, sassolini, normal/AO derivati dall'altezza); nessun asset di terzi |
| `T_Morin_PalmaA_Fronde_D/N/ORM` | `palme/palma_1.png` e `palme/Immagine 2026-11-19 055957.png` (chiome) | verdi delle foglioline e bruni delle fronde secche (campionati) | fronde modellate in Blender e renderizzate dall'alto (atlas con alfa) |

`palme/palma_1.png`, `banchina/Immagine 2026-11-19 055927.png` e `passegiata_2.png` sono state usate anche come riferimento
visivo per forma della chioma, quota del ciglio e colori.

## Texture procedurali (2026-11-19, kit pavimentazione v2)
Generate con `blender/scripts/morin_pav_kit.py` (numpy), nessun asset di terzi e nessun pixel delle foto: le foto
`ref/foto/pavimentazione/tombini.png` e `ref/foto/arredi/gazzebo*.png` sono state usate solo come riferimento visivo.

| Texture | Contenuto |
|---|---|
| `T_Morin_Tombino_D/N/ORM` (1024) | chiusino in ghisa con telaio e bugne rettangolari alternate, usura e ruggine procedurali |
| `T_Morin_Gazebo_Fregio_D/N/ORM` (2048 × 512, alfa) | fregio della pensilina: traversi, tre anelli raggiati per lato, riccioli e gocce pendenti |

`M_Morin_Ghisa` (lampione, pensilina) riusa `T_Banchina_Ghisa_*` (Poly Haven Rusty Painted Metal, CC0) con una tinta.

## Fondale (2026-11-19, `blender/scripts/morin_fondale.py`)
- Mesh `SM_Fondale_Colline_*` e `SM_Fondale_Tenda`: produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence
  and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved (dati modificati: filtrati,
  triangolati, riproiettati).
- Texture `T_Fondale_Colline_*_D`: colori derivati da CORINE Land Cover 2018 ("Generated using European Union's Copernicus Land
  Monitoring Service information"), rumore, terrazze e case dipinte procedurali. Nessuna foto e nessun dato Google.
- Edifici `SM_Fondale_Citta_*`: footprint © OpenStreetMap contributors (ODbL), Overpass API 19.11.2026, entro 1,5 km dalla partenza;
  altezze da `building:levels`/`height` OSM o dal DSM Copernicus. `T_Fondale_Facciata_D` e `T_Fondale_Tenda_D`: procedurali.

## Catture Street View [SV] (deroga dell'utente 2026-11-19, CLAUDE.md §5)
Fonti per la radice del molo (scheda `ref/radice_molo.md` §8, porzioni consigliate): `ref/foto/vista/inizio_passegiata_ristoranti_che_vanno_verso_il_ponte.png`,
`ref/foto/vista/ristoranti_visti_da_di_fronte.png`, `ref/foto/vista/strada_cheProsegue_verso_il_ponte.png`,
`ref/foto/pavimentazione/pavimento verso il ponte.png`. Sigle: F1 = `inizio_passegiata_ristoranti_che_vanno_verso_il_ponte.png`,
F2 = `ristoranti_visti_da_di_fronte.png`, F3 = `strada_cheProsegue_verso_il_ponte.png`, F4 = `pavimento verso il ponte.png`.

Texture ricavate il 2026-11-19 (radice del molo, tranche 1, `blender/scripts/morin_molo.py`, in `blender/textures/molo/`).
Dalle foto si prendono **solo** il colore medio (mediana di una porzione) e la grana fine (luminanza in alta frequenza, rimescolata
a pezze casuali e resa ripetibile). Nessun pixel della foto finisce in chiaro nella texture: niente UI, persone, targhe, scritte o loghi.
Pixel in coordinate della foto originale (x, y). N e ORM sono generate dallo script.
- **[SV]** `T_Molo_Masselli_D/N/ORM` (2048, tile 2,8 m): grana da **F4** x 10-380, y 10-190 (tutta la foto, senza bordi) e da
  **F3** x 0-380, y 700-895 (sotto la scritta di UI a x 195-290 / y 500-680 e a sinistra del cerchio a x ≥ 395). Disegno dei masselli
  28 × 14 cm a correre, giunti con erba e colore: procedurali, tarati a occhio su F4. Usata anche da `M_Molo_Masselli_Grigio` (stessa texture, tinta).
- **[SV]** `T_Molo_Asfalto_D/N/ORM` (2048, tile 4 m): grana da **F1** x 950-1250, y 690-800 (lontano dalla croce a x 750-890 e dal cerchio
  di UI a y < 640). Rattoppi, inerti e colore: procedurali.
- **[SV]** `T_Molo_Facciate_D/N/ORM` (2048, atlante 8 × 8 m a 256 px/m): grana dell'intonaco da **F2** x 800-840, y 430-500 (giallo
  fra lo scudo e la porta, escluso lo scudo a x 732-790 e la filigrana "© Google" a x 930-990) e **F2** x 150-182, y 400-445 (bianco di A4).
  Colori di intonaco giallo, rosa, bianco, cornicione rosso-bruno, legno delle porte, tenda crema, porte rosso scuro: mediane delle
  porzioni della scheda `ref/radice_molo.md` §8 corrette a mano (luce). Porte, finestre, grate, tende, cornicione: disegnati dallo script.
  **Niente insegne reali:** lo scudo rosso del ristorante è sostituito da uno scudo generico inventato (banda arancio, pesce bianco stilizzato,
  nessuna scritta); l'insegna della pescheria rosa è un rettangolo bianco liscio; la fascia blu sopra le vetrate di A3 è liscia, senza testo.
- **[SV]** `T_Albero_Latifoglia_Chioma_D/N/ORM` (2048, 4 ciuffi con alfa): colori delle foglie campionati dai pixel della chioma di **F2**
  x 330-900, y 130-330 (scartati i pixel di cielo). Forma delle foglie, ciuffi e **alfa ricostruiti** dallo script (nessun ritaglio dalla foto).
- `T_Albero_Platano_Corteccia_*` (1024), `T_Morin_PinoDomestico_Chioma_*` (2048, alfa), `T_Morin_PinoDomestico_Corteccia_*` (1024):
  **procedurali**. La tinta del pino è scelta a occhio guardando F2 (chioma scura a destra, x 955-1030), senza campionare pixel.
- Cubetti dell'angolo: riuso di `T_Pav_Cubetti_*` / `T_Pav_Fascia_*` (sezioni sopra). Lampione a due globi: riuso di `M_Morin_Ghisa` e `M_Morin_Globo`.
Ogni texture che ne deriva va elencata qui con la marca **[SV]** (foto e porzione usata), senza UI di Street View, filigrane, persone,
targhe, loghi o insegne, e l'utente la ricontrolla prima di qualsiasi pubblicazione.
Dati: verifica live Overpass API (© OpenStreetMap contributors, ODbL) del 19.11.2026 per alberi, lampioni e recinzioni della radice del molo.

### Chiosco-bar e dehors (blender-artist, 2026-11-19) — `blender/textures/chiosco/`, `blender/scripts/morin_chiosco.py`
Foto: `ref/foto/vista/chiosco_con_ombrelloni_e_tavolini.png` (C1) e `..._2.png` (C2), catture Street View fornite dall'utente.
- **[SV]** `T_Morin_Chiosco_D/N/ORM` (2048, atlante): **procedurale**; dalle foto solo i colori campionati (mediane dei pixel):
  crema del corpo da C1 x 215-235 / 300-480, y 320-400 (lato al sole e lato in ombra), bianco di tettoia e mantovana da C1
  x 330-520, y 232-266, lilla della striscia-menu in vetrina a occhio da C1. Vetrina, bottiglie, porta e fughe disegnate dallo script.
  Insegna: nome inventato "Chiosco del Golfo" (font interno di Blender), l'insegna reale non è riprodotta.
- **[SV]** `T_Morin_Dehors_D/N/ORM` (2048, atlante condiviso da ombrellone, fioriera, tavolino, sedia, sgabello): **procedurale**;
  grigio delle fioriere campionato da C2 x 160-200 / 880-915, y 280-330; tela degli ombrelloni da C2 x 600-900, y 95-160.
- Arbusti delle fioriere (v2, 3 varianti): riuso di `T_Albero_Latifoglia_Chioma_*` (sezione molo, [SV]) e `T_Morin_PinoDomestico_Chioma_*` (procedurale). Pavimento `SM_Pav_Chiosco`: riuso di `T_Pav_Cubetti_*`.
- Nessun ritaglio di foto nelle texture: niente persone, targhe, UI o insegne.

### Giardini a Mare v1 (2026-11-19, `blender/scripts/morin_giardini.py`)
- **[SV]** `T_Morin_Oleandro_Chioma_D/N/ORM` (2048, atlante RGBA: quadranti in alto fiori bianchi, in basso rosa): **procedurale**
  (foglie lanceolate e fiori a 5 petali disegnati dallo script); dalla cattura `ref/foto/vista/prato con alberelli.png` solo i colori
  campionati (bianco x 345-440, y 110-170; rosa x 840-925 e 1040-1100, y 120-190; foglie x 840-925), riportati a luce piena.
- `T_Morin_Oleandro_Fusto_D/N/ORM` (1024): procedurale.
- `SM_Morin_PanchinaLunga_Mod`: riuso di `T_Pav_Fascia_*` (kit pavimentazione).
- Nessun ritaglio di foto nelle texture. La cattura nel confronto `docs/qa/arte_giardini_v1_confronto.png` ha freccia, logo e filigrana sfocati
  (file di QA, non va pubblicato).
- v2 (2026-11-19): `T_Morin_Oleandro_Chioma_*` rigenerata con più fiori e rosa fucsia (stessa origine [SV], solo colori campionati).
  Confronto `docs/qa/arte_giardini_v2_confronto.png` (file di QA con la cattura sfocata nelle parti di UI, non va pubblicato).

### Vista verso la città: prato, Viale Italia, palazzi (blender-artist, 2026-11-19) — `blender/textures/viale/`, `blender/scripts/morin_viale.py`
Foto: `ref/foto/vista/prato con alberelli.png` (cattura Street View) e `ref/foto/vista/vista_dall_alto_2.png` (solo riferimento).
- **[SV]** `T_Fondale_Palazzo_A/B/C_D/N/ORM` (1024, facciata intera + strisce coppi/stucco/muro): **procedurali** (finestre, persiane,
  cornici, timpani, bugnato, cornicione disegnati dallo script); dalla cattura solo i colori a occhio (giallo, rosa, ocra delle facciate,
  verde delle persiane, stucco chiaro) e lo schema (5-6 piani, persiane verdi, cornici chiare). Nessun ritaglio di foto.
- **[SV]** `T_Morin_Prato_D/N/ORM` (2048, tileable 4 m): procedurale; verde del prato tarato sulla mediana dei pixel del prato nella
  cattura (x 860-940, y 240-262), riportata a luce piena.
- `T_Morin_Bosso_*` (1024), `T_Viale_Segnaletica_*` (512), `T_Morin_Auto_*` (1024, atlante): procedurali. Auto generiche senza marchi,
  vano targa vuoto (niente targhe).
- Riusi: `T_Molo_Asfalto_*` (asfalto del viale, sezione molo [SV]), `T_Pav_Fascia_*` (cordoli). Fronti dei palazzi da OSM
  (© OpenStreetMap contributors, ODbL; isole di `SM_Blockout_Fondale_v2_Edifici`).
- Il confronto `docs/qa/arte_viale_v1_confronto.png` contiene la cattura con UI e una persona: file di QA, non va pubblicato.

### Parcheggio iniziale (blender-artist, 2026-11-20) — `blender/textures/parcheggio/`, `blender/scripts/morin_parcheggio.py`
Foto: `ref/foto/vista/parcheggio_iniziale.png` (cattura Street View), `ref/foto/vista/vista_dall_alto_2.png` (solo riferimento).
Pianta del parcheggio e della corsia da OSM (© OpenStreetMap contributors, ODbL: amenity=parking 850396611, parking_aisle 378872040).
- **[SV]** `T_Parcheggio_Asfalto_D/N/ORM` (2048, tileable 8 m): la grana fine dell'asfalto è un high-pass della cattura
  (porzione x 300-520, y 560-680: solo asfalto, niente UI, persone, targhe o marchi) risintetizzata a splat; crepe, rattoppi,
  macchie d'olio e inerti sono procedurali; colore medio a occhio dalla cattura.
- `T_Morin_Cartelli_*` (512, atlante: P blu, divieto di sosta, pannello integrativo senza testo leggibile, zincato) e
  `T_Morin_NewJersey_*` (1024, cemento con sporco al piede): procedurali, nessun ritaglio di foto.
- Riusi: `T_Viale_Segnaletica_*` (strisce), `T_Pav_Fascia_*` (cordoli), `T_Pav_Terra_*` (aiuola), mesh e `T_Morin_Auto_*` delle auto.
- Il confronto `docs/qa/arte_parcheggio_v1_confronto.png` contiene la cattura con UI e targhe sfocate: file di QA, non va pubblicato.

### Auto generiche v2 (blender-artist, 2026-11-20) — `blender/textures/auto/`, `blender/scripts/morin_auto_v2.py`
- `T_Morin_Auto_v2_D/N/ORM` (2048, atlante 3 × 3: modello × colore): **procedurali**, nessun pixel da foto. Dalla cattura
  `ref/foto/vista/parcheggio_iniziale.png` solo la scelta dei colori (bianco, grigi, nero, argento, rosso, blu) e le proporzioni.
  Nessun marchio, logo, scritta o targa: la targa è un rettangolo bianco vuoto.
- Il confronto `docs/qa/arte_auto_v2_confronto.png` contiene la cattura con UI e targhe sfocate: file di QA, non va pubblicato.

### Banchina v2: ciglio a blocchi, nicchia, testate, ancora (blender-artist, 2026-11-20) — `blender/textures/banchina_v2/`, `blender/scripts/morin_banchina_v2.py`
- `T_Banchina_Blocchi_D` (2048): derivata da `T_Banchina_Ciglio_D` (foto utente `banchina/passegiata_1.png` + grana Poly Haven
  concrete_floor_worn_001, CC0), ritarata sul colore dei blocchi campionato in `ref/foto/vista/banchina_vista_montagne_verso_ponte.jpg`
  (faccia al sole ~206,208,205 sRGB → albedo 200,199,193), più contrasto e macchie procedurali. Dalla foto **solo il colore** (nessun pixel copiato).
- `T_Banchina_Blocchi_N/ORM`: copie di `T_Banchina_Ciglio_N/ORM` (Poly Haven CC0, vedi sopra).
- Ancora, scaletta v2, testate: nessuna texture nuova (riusano `T_Banchina_Ghisa_*`, `T_Banchina_Paramento_*`, `T_Banchina_Blocchi_*`).
- `docs/qa/arte_banchina_v3_confronto_*.png` contengono la foto di riferimento accanto al render: file di QA, non vanno pubblicati.

### Imbarco v1: battello, pontile, biglietteria, cestino, rastrelliera, parabordo (blender-artist, 2026-11-20) — `blender/textures/imbarco/`, `blender/scripts/morin_imbarco.py`
- `T_Morin_Imbarco_{D,N,ORM}` (atlante 2048) e `T_Morin_Imbarco_Legno_{D,N,ORM}` (2048): **interamente procedurali** (numpy), nessuna foto né texture esterna.
- Colori della livrea solo ispirati a `ref/foto/vista/parcheggio_iniziale.png` [SV] (bianco con fascia blu): nessun pixel copiato. Nome del battello di fantasia ("STELLA DEL GOLFO"), nessun marchio o livrea reale.
- Scritte in geometria con il font predefinito di Blender (libero, incluso in Blender).
- `docs/qa/arte_imbarco_v1_confronto.png` contiene una cattura Street View: file di QA, non va pubblicato.

### Incrocio Viale Italia v1 e parcheggio v3 (blender-artist, 2026-11-20) — `blender/textures/incrocio/`, `blender/scripts/morin_incrocio.py`
- `T_Incrocio_Props_{D,N,ORM}`, `T_Viale_Fiori_{D,N,ORM}`, `T_Fondale_EdificioVetrate_{D,N,ORM}` (1024): **interamente procedurali** (numpy), nessun pixel da foto.
  Forme, colori e posizioni da `ref/foto/vista/vissta_entrata_parcheggio_e_passeggiata_da_viale_italia.png` [SV] e `parcheggio_iniziale.png` [SV] (solo riferimento).
- Segnali stradali generici (Codice della strada, simboli pubblici); nessun nome o insegna del ristorante reale.
- Planimetria dell'incrocio: © OpenStreetMap contributors (ODbL).
- `docs/qa/arte_incrocio_v1_confronto.png` e `arte_parcheggio_v3_confronto.png` contengono catture Street View: file di QA, non vanno pubblicati.

### Ponte Thaon di Revel v1 (blender-artist, 2026-11-20) — `blender/textures/ponte/`, `blender/scripts/morin_ponte.py`
Texture **procedurali** (numpy, nessun pixel da foto o da terzi); dalle foto dell'utente `ref/foto/ponte/ponte1.png`,
`ponte_verso_passegiata.png`, `ringhiera_ponte.png` solo i colori campionati e la disposizione (doghe longitudinali, file di borchie,
forma del parapetto). Nessuna geometria o texture Google.
- `T_Ponte_Legno_{D,N,ORM}` 4096: tavolato grigio invecchiato 6 × 6 m (tono mediano della foto al sole ~118/116/112).
- `T_Ponte_Acciaio_{D,N,ORM}` 4096: acciaio verniciato bianco con usura leggera, 4 × 4 m.
- `T_Ponte_Cavo_{D,N,ORM}` 1024: fune spiroidale.
- Riusata `T_Banchina_Paramento_*` (spalla Mirabello), già elencata sopra.

## Audio

### Ambiente Viale Italia (2026-11-20) — `exports/audio/`
Fonte: **BigSoundBank** (libreria di Joseph Sardin, https://bigsoundbank.com). Ogni pagina dichiara
"License CC0 (public domain): Free and royalty-free". Attribuzione non richiesta, citata per cortesia. Data di accesso: 2026-11-20.
File scaricati in WAV originale (link `UPLOAD/bwf-en/<n>.wav`). Gli originali, non toccati, sono in `exports/audio/originali/`
(stessi nomi del download: `A_Viale_Clacson_01..05.wav`, `A_Viale_TrafficoLontano_Loop.wav`).

| Originale (`originali/`) | Sorgente (n., titolo) | URL | Autore (come in pagina) | Licenza |
|---|---|---|---|---|
| `A_Viale_TrafficoLontano_Loop.wav` | #2457 "City garden atmosphere" (Dreux) | https://bigsoundbank.com/city-garden-atmosphere-s2457.html | Joseph SARDIN | CC0 |
| `A_Viale_Clacson_01.wav` | #3506 "Horn #3" | https://bigsoundbank.com/horn-3-s3506.html | Le tiroir du fond | CC0 |
| `A_Viale_Clacson_02.wav` | #0260 "Car horn #4" | https://bigsoundbank.com/car-horn-4-s0260.html | DenisChardonnet | CC0 |
| `A_Viale_Clacson_03.wav` | #0258 "Recent Car Horn #2" | https://bigsoundbank.com/recent-car-horn-2-s0258.html | DenisChardonnet | CC0 |
| `A_Viale_Clacson_04.wav` | #0850 "Recent car horn #5" (3 colpi) | https://bigsoundbank.com/recent-car-horn-5-s0850.html | Joseph SARDIN | CC0 |
| `A_Viale_Clacson_05.wav` | #0969 "Recent Car Horn #7" (5 colpi) | https://bigsoundbank.com/recent-car-horn-7-s0969.html | Joseph SARDIN | CC0 |

**Elaborazione (blender-artist, 2026-11-20)** in Blender 5.3 (Video Sequence Editor + `bpy.ops.sound.mixdown`, Audaspace;
niente ffmpeg esterno): scena temporanea poi rimossa, tagli, fade con keyframe di volume, mixdown WAV PCM S16 48 kHz, troncamento
al campione esatto con il modulo `wave` (il mixdown arrotonda al blocco). Picco normalizzato a −6 dBFS. File finali in `exports/audio/`:

| File finale | Da (originale, secondi) | Durata | Canali |
|---|---|---|---|
| `A_Viale_TrafficoLontano_Loop.wav` | #2457, 0-60 s + crossfade equal-power di 2 s (la coda 60-62 s sfuma sopra l'inizio) | 60,00 s | stereo |
| `A_Viale_Clacson_01.wav` | #3506, 0,00-0,85 | 0,85 s | mono |
| `A_Viale_Clacson_02.wav` | #0258, 0,00-1,55 | 1,55 s | mono |
| `A_Viale_Clacson_03.wav` | #0850, 0,10-0,60 (1° colpo) | 0,50 s | mono |
| `A_Viale_Clacson_04.wav` | #0850, 4,30-6,30 (3° colpo, lungo, tagliato a 2 s) | 2,00 s | mono |
| `A_Viale_Clacson_05.wav` | #0969, 1,35-2,05 (2° colpo) | 0,70 s | mono |
| `A_Viale_Clacson_06.wav` | #0969, 4,95-5,55 (5° colpo) | 0,60 s | mono |

#0260 ("Car horn #4") non è usato nei file finali (0,49 s, 2 campioni in clipping).

### Testata di Porto Mirabello v1 (blender-artist, 2026-11-20)
- Geometria da OpenStreetMap (© OpenStreetMap contributors, ODbL): ways 850283512 (scala), 1120598342 (passerella), 851093571 (siepe),
  850283513 (recinzione), 379766626/379766628 (parcheggio e strada), 175935357/379778073 (multipiano), 912795085…089 (pontili),
  175935420/421/422 (prati), node 1327347935 (fanale).
- Nessuna texture nuova: riusate `T_Parcheggio_Asfalto`, `T_Viale_Segnaletica`, `T_Molo_Masselli`, `T_Morin_Bosso`, `T_Morin_Prato`,
  `T_Ponte_Legno`, `T_Ponte_Acciaio`, `T_Banchina_Paramento`, `T_Pav_Fascia`, `T_Morin_Imbarco`, `T_Morin_Imbarco_Legno` (già elencate sopra).

## Blocco 2 (2026-11-20)
- Estratto OSM `ref/osm/morin_blocchi23.osm` (© OpenStreetMap contributors, ODbL): posizioni di cannoni, ancora 2, vialetti, prato,
  chiosco ottagonale, coastline dello smusso, Viale Italia (`blender/scripts/morin_blocco2.py`).
- `SM_Morin_Redamare`: riproduce solo la **forma** della scultura "REDAMARE" di Sabrina D'Alessandro (2022) come elemento urbano
  riconoscibile; lettere generate col font incorporato in Blender (licenza libera), proporzioni dalla foto
  `ref/foto/arredi/scultura_caratteri_cubitali_affianco_cannone.png`. Vedi `docs/decisioni.md` 2026-11-20.
- `SM_Pav_Scritta_Morin`: testo "PASSEGGIATA / MORIN" (nome del luogo, non un marchio) col font incorporato in Blender.
- Nessuna texture nuova derivata da foto o da Street View nel Blocco 2: il chiosco ottagonale usa gli atlanti esistenti
  `T_Morin_Chiosco` e `T_Morin_Dehors`; l'affusto dei cannoni usa `T_Morin_Imbarco_Legno` (tinta scura nel materiale).

## Blocco 2 v2 e Blocco 3 — Molo Italia v1 (2026-11-20)
- OSM `ref/osm/morin_blocchi23.osm` (© OpenStreetMap contributors, ODbL): coastline 137121074 (bordi del molo, dita, calata), ways 851135245
  (ristorante), 205843153 / 205839145 / 205839033 (edifici della radice), 352041386/87/88 (info point), node 1327347929 (faro).
- Faro: dati della luce da "Lighthouses of Italy: Liguria" (R. Rowlett, ibiblio.org) e tag `seamark` di OSM (solo dati, nessun testo copiato).
- Foto dell'utente usate come **riferimento di forma, proporzioni e colori** (nessuna texture ritagliata dalle foto): `ref/foto/vista/molo_italia_1..7`,
  `faro_2`, `faro_3`, `ristorante_giallo_blu_gallegiante`, `guardia_costiera_molo_italia(_2)`, `info_point_e_parcheggio_guardia_costiera`,
  `3_aste_bandiere_molo`, `monumento_molo`, `incrocio_molo_italia_passegiata_morin*` (catture Street View **[SV]**) e
  `Molo_Italia_dall_alto.png` (**vista satellitare Google Maps**, ammessa dall'utente il 2026-11-20: usata per pianta dei moli a dito,
  posizione dei battelli e del monumento sul ramo 2; nessuna geometria ricalcata, la pianta viene da OSM).
- Texture nuove, tutte **procedurali** (nessun pixel da foto): `T_MoloItalia_Tinte` (atlante di tinte, colori campionati a occhio dalle foto [SV]),
  `T_MoloItalia_Facciata` (mattoni, marcapiano, finestre verde acqua; colori dalle foto [SV] della Capitaneria), `T_Molo_Scogliera` (massi),
  `T_MoloItalia_Cemento` (base Poly Haven **concrete_floor_worn_001**, CC0, ritarata; normal dal set originale). Tutte in `blender/textures/molo_italia/`.
- `T_Morin_Bandiere` (bandiere delle 3 aste, procedurale): tricolore; stemma del Comune della Spezia **semplificato** dalla blasonatura pubblica
  (stemma civico, R.D. 4/12/1923; fonte: voce "La Spezia" di it.wikipedia.org); aquila "FORZA AQUILE" **disegnata ex novo** per il progetto
  (non deriva dallo stemma dello Spezia Calcio). Testi col font incorporato in Blender.
- Scritte 3D col font incorporato in Blender: "LA SPEZIA" (nome della città), "GUARDIA COSTIERA" (ente pubblico, decisione dell'utente),
  "RISTORANTE", "I PICCIONI", "TIRAMOLLA", "SPINGITUTTO", "OSTINATO", "PICCIONISSIMA" (nomi parodia, nessun marchio reale).

## Chiosco ottagonale v3, nave da crociera v2, colline NE v3 (2026-11-20)
- **[SV]** `T_Morin_ChioscoOtt_v3_D/N/ORM` (2048) e `T_Morin_ChioscoOtt_v3_Vetro_D/N/ORM` (512), `blender/textures/blocco2/`
  (`blender/scripts/morin_chiosco_ott_v3.py`): **procedurali**; dalla cattura Street View `ref/foto/vista/chiosco_2_fine_passegiata_morin.png`
  solo i colori campionati (legno del bancone, crema dei pannelli, bianco). Nessun ritaglio di foto, niente persone, targhe o insegne reali.
  Nome inventato "IL GABBIANO INGORDO", locandine e menu inventati; testo col font incorporato in Blender.
- `T_MoloItalia_NaveCrociera_v2_D/N/ORM` (2048), `blender/textures/molo_italia/` (`morin_nave_v2.py`): procedurali; livrea, gabbiano del fumaiolo
  e nome "PICCIONISSIMA" inventati, nessuna compagnia reale. Forma e posizione da OSM (© OpenStreetMap contributors, ODbL): coastline 137121074
  e nodo 3701128402 "Molo Garibaldi" (estratto dall'API OSM il 2026-11-20); proporzioni confrontate con `ref/foto/vista/faro_2.png` (solo riferimento).
- `SM_Fondale_Colline_NE_v3`: stessa origine della v2 (DEM e texture già elencati), solo geometria modificata.

## Texture v2, passaggio realismo (2026-11-20)
Texture in `blender/textures/v2/` (`blender/scripts/morin_texture_v2.py`, elenco in `docs/texture_v2.md`). Sorgenti **Poly Haven, CC0**
(licenza verificata su polyhaven.com/license il 2026-11-20: "Our assets are all licensed as CC0", attribuzione non richiesta),
scaricate in `blender/textures/src/<asset>/`:
- `patterned_cobblestone` → `T_Pav_Cubetti_v2`; `rock_surface` → `T_Pav_Lastre_v2` (grana per lastra);
- `rock_boulder_dry` → `T_Pav_Fascia_v2`, `T_Banchina_Blocchi_v2`; `seaside_rock` → `T_Molo_Scogliera_v2`, `T_Banchina_Paramento_v2`;
- `asphalt_04` → `T_Parcheggio_Asfalto_v2`, `T_Molo_Asfalto_v2` (`asphalt_02` scaricato e scartato); `dirty_concrete` → `T_MoloItalia_Cemento_v2`,
  `T_Morin_NewJersey_v2`; `rust_coarse_01` → `T_Morin_Corten_v2`; `wood_planks_grey` → `T_Ponte_Legno_v2`; `pine_bark` →
  `T_Morin_PinoDomestico_Corteccia_v2`; `leafy_grass` → `T_Morin_Prato_v2`.
- Procedurali o ritarature delle v1 (nessuna sorgente nuova): `T_Ponte_Acciaio_v2`, `T_Morin_PalmaA_Tronco_v2`, `T_Albero_Latifoglia_Chioma_v2`,
  `T_Morin_Auto_v3`, `T_Morin_MacroVar`.
- Foto dell'utente (`ref/foto/pavimentazione/*`, `ref/foto/ponte/*`, `ref/foto/arredi/giardini.webp`) usate **solo per tarare colore e scala**:
  nessun pixel copiato, nessuna texture [SV].

## Marina del Blocco 1 (2026-11-20)
- `T_Morin_Marina_D/N/ORM` (2048), `blender/textures/marina/` (`blender/scripts/morin_marina.py`): **interamente procedurale** (tinte con
  rumore, doghe, teak, cuscini, finestre). Nessuna foto copiata; le foto `ref/foto/vista/*` e `ref/foto/ponte/*` solo come riferimento di colori
  e proporzioni. Testi rasterizzati col font incorporato in Blender. Nomi inventati (nessun marchio, nessuna barca reale): circolo
  "CIRCOLO NAUTICO VENTO CONTRARIO" (sostituisce il nome reale dell'impianto), barche "SGABEO", "BOLLICINA", "MUGUGNO", "MESCIUA",
  "ZIA PINA", "MUSCOLO FELICE", "FOCACCINA", "NON CI PENSO", "ACCIUGA RAZZO", "CALMA PIATTA", "SCIROCCO PIGRO", "PESTO E VELA";
  striscione generico "SCUOLA VELA".
- Geometria dei pontili e posizioni: OSM (© OpenStreetMap contributors, ODbL), ways in `ref/marina_blocco1.md` §2.
- `SM_Morin_Marina_Pontile12`, `_PontileLargo`, `_Passerella`, `SM_Mirabello_Pontile_Col`: riusano le texture già elencate di
  `M_Morin_Imbarco` / `M_Morin_Imbarco_Legno` (procedurali).

## Texture v3 (2026-11-20)
`blender/textures/v3/` (`blender/scripts/morin_texture_v3.py`, elenco in `docs/texture_v3.md`). Sorgenti **Poly Haven, CC0** già elencate
nella sezione Texture v2: `wood_planks_grey` → `T_Ponte_Legno_v3`; `asphalt_04` → `T_Viale_Segnaletica_v2`; `patterned_cobblestone` →
`T_Pav_Cubetti_v3`; `T_Morin_Prato_v3` deriva da `T_Morin_Prato_v2` (`leafy_grass`, CC0, più procedurale); `T_Morin_Prato_MacroVar` procedurale.
Foto dell'utente (`ref/foto/ponte/ponte1.png`, `ponte_verso_passegiata.png`) usate **solo** come riferimento per la disposizione delle doghe
e delle borchie e per la tinta: nessun pixel copiato, nessuna texture [SV].

## Ristorante dell'edificio C e dehors a righe (2026-11-20) — `blender/textures/molo/`, `blender/scripts/morin_ristorante_c.py`
- `T_Molo_RistoranteC_D/N/ORM` (2048, atlante 8 × 8 m) e `T_Molo_TendaRighe_D/N/ORM` (1024): **interamente procedurali** (intonaco, finestra a
  griglia, porte-vetrate, vano del bancone con bottiglie generiche, lavagna con scarabocchi illeggibili, tasselli di legno, metallo, sedute,
  tela bianca e righe blu-bianche). Nessun pixel di foto: `ref/foto/vista/strada_cheProsegue_verso_il_ponte.png` (cattura Street View, F3)
  usata solo per forme, proporzioni e colori; niente UI, persone, targhe, loghi né il testo della lavagna reale. Nessuna marca [SV].
- Insegna con **nome inventato**: "AL MUSCOLO STANCO" (scherzo su *muscoli* = cozze in spezzino), lettere in rilievo dal font incorporato in
  Blender. Nessun nome o marchio del ristorante reale.
- Riusi: fogliame `M_Albero_Latifoglia_Chioma` (procedurale, già elencato) per le piante sul tetto; fronde `T_Morin_PalmaA_Fronde` (già elencate)
  per `SM_Molo_PalmaVaso`; fioriere `SM_Morin_Fioriera/B/C` e palma `SM_Morin_PalmaA` solo come istanze nel CSV.
- Pianta dell'edificio: OSM way 205840540 (© OpenStreetMap contributors, ODbL).

## Imbarco v2 e ingresso della marina dalle foto nuove (2026-11-20) — `blender/scripts/morin_imbarco_v2.py`, `morin_marina_ingresso.py`, `morin_atlas_v2.py`
Foto sorgente: catture Street View messe dall'utente in `ref/foto/vista/` (deroga CLAUDE.md §5): **T1** `traghetto_bigliettaria_azzurra.png`,
**T2** `biglietteria_traghetto_di_fronte.png`, **M1** `nautica_marina.png`, **M2** `marina_nautica.png`. Nessuna geometria Google; nelle texture
niente UI, filigrane "© Google", persone, targhe, loghi o nomi reali di privati. Texture marcate **[SV]**: l'utente le ricontrolla prima della pubblicazione.
- **[SV]** `blender/textures/imbarco_v2/T_Morin_Bigl_Righe_D/N/ORM` (1024, 1,08 m): righe blu-bianche da 18 cm ricostruite, con lo **sporco vero**
  della fascia bassa della casetta ovest in T2 (x 955-1158, y 401-479), raddrizzata e normalizzata per classe di colore; tinte campionate da T2.
- **[SV]** `T_Morin_Pontile_Legno_v2_D/N/ORM` (2048, 2 m): doghe trasversali procedurali con tinta e dispersione campionate dal tavolato di T2
  (x 560-660, y 450-560).
- **[SV]** `T_Morin_Imbarco_v2_D/N/ORM` (atlante 2048): pannelli ridisegnati in vettoriale (insegna ad arco, zoccoli, fianchi, bacheca, orari,
  tenda, bandiera) con impaginazione e colori presi da T1/T2; testi rasterizzati da font di sistema (Arial). Logo e nomi della compagnia in
  **parodia**: "NAVIGAZIONE GOLFO dei POETASTRI" (gabbiano con la penna d'oca sul timone), traghetto "PICCIONE VIAGGIATORE", schermo
  "Enjoy the mugugno". Testi generici/pubblici tenuti: "Biglietteria / Ticket Office", "Trasporto di linea via mare / Ferry lines",
  "Linea 01 Golfo della Spezia". Bandierina italiana sull'albero (simbolo pubblico).
- `T_Morin_Bigl_Rete` (maglia romboidale con alfa) e `T_Morin_Bigl_Schermo` (mare e battello inventati, niente persone): procedurali.
- **[SV]** `blender/textures/marina_ingresso/T_Morin_Marina_Doghe_D/N/ORM` (1024, 1,2 m): doghe orizzontali da 12 cm; tinte delle doghe dalla
  fascia sotto la scritta dell'ufficio in M1 (x 162-698, y 300-364), raddrizzata e "de-light"; venatura procedurale.
- **[SV]** `T_Morin_Marina_LamieraBlu_D/N/ORM` (1024, 1 m): tinta dal montante del portale in M2 (x 685-700, y 300-400), graffi procedurali.
- **[SV]** `T_Banchina_Bitta_Ruggine_D/N/ORM` (512 × 1024): ruggine **ritagliata** dalla bitta di M2 (x 968-1012, y 383-503), de-light, resa ripetibile.
- `T_Morin_Marina_Ingresso_D/N/ORM` (atlante 2048): ridisegnato. Parodie: **"ASSONNAUTICA"** (logo tondo con una vela che sbadiglia) e
  **"Porto Turistico Vento Contrario"** al posto dei nomi reali dell'associazione e del porto; "PORTO TURISTICO" e il cartello generico di
  videosorveglianza tenuti. La foto d'epoca del pannello (con persone) è sostituita da un'immagine d'epoca **inventata** (banchina, faro, veliero).
- Posizioni: OSM (© OpenStreetMap contributors, ODbL) e `ref/foto_nuove_2026-11-20.md`.

## Dettagli della radice dalle foto nuove (2026-11-20) — `blender/scripts/morin_dettagli_radice.py`
Foto sorgente (deroga CLAUDE.md §5): **R2** `ref/foto/vista/ristoranti_visti_da_di_fronte_2.png` (cattura Street View), **K** `ref/foto/arredi/cestino.png`,
**G** `ref/foto/arredi/cartelli_inizio_passegiata.png`, **S** `ref/foto/arredi/scultura_donna_con_pinne_su_sedia.png`. Nessuna geometria Google;
nelle texture niente UI (l'icona arancione di R2 è esclusa), filigrane, persone, targhe, loghi o nomi reali di privati. Marca **[SV]**: l'utente
le ricontrolla prima della pubblicazione.
- **[SV]** `blender/textures/dettagli/T_Molo_Dettagli_D/N/ORM` (atlante 2048), porzioni di foto: fascia in rilievo del cestino con lo stemma
  comunale (K x 62-96, y 52-176, stemma pubblico); fronte e fianco del basamento della Sirena (S, raddrizzati: fronte (182,318)-(363,286)-(363,348)-(182,406),
  fianco (107,286)-(178,318)-(178,404)-(108,372)); fianco della fioriera (R2 x 578-648, y 318-346, tinta portata ad antracite #222B35);
  grana della plastica delle new jersey (G x 22-98, y 232-290, solo passa-alto; tinta blu ricostruita).
- Pannelli dello stesso atlante ridisegnati in vettoriale (font di sistema Arial, Georgia, Segoe Script/Print): cavalletto **"RISTO LISCHERIA"**
  (parodia), scudo **"dai pescatori PIGRI"** col polpo che dorme sull'amaca (parodia), pannello **"CONSORZIO RETI BUCATE — Sapori di Mare e di
  Tèra"** (parodia), lavagna con menù inventato, targhe pubbliche "banchina G. Thaon di Revel", "banchina Costantino Morin", avviso
  "ATTENZIONE — I bambini devono essere accompagnati per mano lungo la banchina" (testi pubblici, ricomposti), targhetta gialla illeggibile,
  targa "La Sirena del Golfo dei Poeti — Aidyn Zeinalov" (opera pubblica), nomi inventati dei pescherecci "MUGUGNO II", "ACCIUGA FELICE",
  "NON CE N'È" e sigla finta "SP 0000". Telo degli ombrelloni procedurale (in R2 è bianco saturato).
- **[SV]** `T_Molo_Arbusto_D/N/ORM` (1024, ripetibile 0,5 m): massa degli arbusti dalle fioriere di R2 (x 500-780, y 222-318), de-light e schiarita;
  `T_Molo_Arbusto_Card` (512, alfa procedurale a foglie ovali, colori dalla stessa porzione) **[SV]**.
- "La Sirena del Golfo dei Poeti" di Aidyn Zeinalov (opera pubblica, OSM node 9592234744): forma **ricreata stilizzata** come elemento urbano,
  nessuna texture presa dalla statua. Posizioni da OSM (© OpenStreetMap contributors, ODbL) e `ref/foto_nuove_2026-11-20.md`.
