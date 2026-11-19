# Crediti — Morin Rush

## Dati geografici
- Dati cartografici © OpenStreetMap contributors, disponibili con licenza ODbL
  (https://www.openstreetmap.org/copyright).

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
