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

Poly Haven: CC0, citazione facoltativa ma gradita. Poly Pizza: verificare la licenza di ogni modello;
se CC-BY, l'autore va citato qui.

Scaricate ma non usate negli asset (in `blender/textures/src/`): palm_bark, rusty_metal_02, seaworn_sandstone_brick,
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
