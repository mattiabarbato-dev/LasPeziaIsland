# Scheda — Blocco 3: Molo Italia, ristorante galleggiante e faro rosso

Legenda: **[V]** verificato (fonte citata) · **[F]** letto da foto · **[S]** stima, da confermare.
Coordinate di progetto come in `area.md`: X lungo la passeggiata verso NE, Y verso la città, metri. In UE: (X·100, −Y·100).
Orientamento utile: il ramo 1 va verso −Y (SE, azimut ~131°); il ramo 2 va quasi verso **est** (azimut ~88°).
Geo-scout, 2026-11-20 (prima stesura); **aggiornata lo stesso giorno con le 17 foto dell'utente** (§9).

**Fonti**
- OSM: estratto `ref/osm/morin_blocchi23.osm`, scaricato dall'API OSM il 2026-11-20 (il vecchio `morin_bbox.osm` non arriva fin qui).
  © OpenStreetMap contributors, ODbL.
- Faro: database "Lighthouses of Italy: Liguria" di R. Rowlett ([ibiblio.org/lighthouse/itanw.htm](https://ibiblio.org/lighthouse/itanw.htm)),
  con i riferimenti ARLHS ITA-294, Admiralty E1290, NGA 7764. Concorda con i tag `seamark` di OSM.
- Ristorante: OSM (`building=houseboat`) e schede pubbliche di recensioni ([pos.do](https://pos.do/fr/la-spezia/restaurant/i-gabbiani)).
- Progetti AdSP sul Molo Italia (rettifica e prolungamento, 2015; riqualificazione del primo tratto, conferenza di servizi
  [MIT 2019-2020](https://mit.gov.it/node/12410)). Le foto mostrano il molo **non riqualificato** (asfalto, scogliera, testata dritta): vale la geometria OSM.
- **Foto dell'utente** in `ref/foto/vista/` (2026-11-20): 16 catture **Street View** e 1 vista satellitare **Google Maps** (§9, licenze in §9.2).
  Le misure [F] sono stime fatte in prospettiva, con persone, auto e porte come scala: errore tipico ±15-20 %.

Nomi reali citati solo per identificare il luogo. Nel gioco: nomi inventati, niente marchi di compagnie, bar o distributori (CLAUDE.md §5).

---

## 1. Box

| Voce | Valore | Stato |
|---|---|---|
| Box giocabile | X 540 … 710, Y −345 … 150 | proposta |
| lat / lon | **44,10322 – 44,10731 N · 9,82832 – 9,83437 E** | calcolo |
| Punti chiave (lat, lon) | gomito 44,104251 / 9,831883 · faro 44,104261 / 9,833946 · ristorante (centro) 44,105257 / 9,830577 | calcolo da OSM |

## 2. Geometria del molo

### 2.1 Pianta (OSM)

Il molo è dentro il poligono della coastline 137121074, che ne dà i bordi. Il percorso pedonale è la way 132740887 + 801989878 "Molo Italia".

| Tratto | Bordo ovest/sud (lato passeggiata, mare aperto) | Bordo est/nord (bacino interno) | Larghezza | Lunghezza | Stato |
|---|---|---|---|---|---|
| **Radice** (Y 85 → 2) | smusso del ciglio da (548,7; 78,3) a (555,0; 41,9), poi X 555 | terraferma: Capitaneria e calata | — | — | [V] OSM. Dettaglio del raccordo in `blocco2.md` §4.5 [F] |
| **Ramo 1**, ortogonale alla passeggiata (verso −Y) | X 555,0 → 556,1 (da Y 41,9 a −204,5) | X 571,6-573,6 (da Y 1,6 a −198,5) | **16,5-17,5 m** | **285 m** di percorso (Y 85,2 → −200,3) | [V] OSM |
| **Gomito** | (556,1; −204,5) | (571,6; −198,5) | — | la carreggiata curva dolcemente, **senza gradini né ostacoli** | [V]; [F] `molo_italia_5` |
| **Ramo 2**, a ~136° (verso E) | (556,1; −204,5) → (677,2; −332,2): 176 m | (571,6; −198,5) → (688,7; −321,6): 170 m | **15,4 m** | **161 m** di percorso, fino a (679,9; −320,7) | [V] OSM. Angolo interno 136,5° |
| **Testata** | (677,2; −332,2) – (688,7; −321,6), lato dritto | | 15,6 m | — | [V] OSM; **dritta, confermata [F]** `faro_2`, `faro_3`: niente piazza circolare |
| **Moli a dito** sul lato est del ramo 1 | D1: X 572,7-622,6, Y −107,7 … −114,5 · D2: X 573,4-622,3, Y −152,2 … −157,9 | — | 5-7 m | ~50 m ciascuno | [V] OSM. All'attacco di D1 [F] `molo_italia_4`: casetta a lamelle e pontile con ringhiera (§5) |

**Larghezze OSM e scogliera.** Il bordo ovest/sud di OSM coincide con il **ciglio del marciapiede**, sopra la scogliera [S]: i massi stanno fuori
dal poligono, in acqua. Nel gioco la scogliera si aggiunge **all'esterno** della larghezza OSM (fascia di ~4-6 m) [S].

### 2.2 Sezione trasversale [F]

Letta da `molo_italia_1/2/3` (ramo 1) e `molo_italia_5/6/7`, `faro_2` (ramo 2). È la "ricetta" del molo, come `sezione.md` per la passeggiata.
Dal bacino interno (est/nord) al mare aperto (ovest/sud):

| # | Fascia | Ramo 1 (16,5-17,5 m) | Ramo 2 (15,4 m) | Aspetto | Stato |
|---|---|---|---|---|---|
| 1 | **Ciglio d'ormeggio** (lato bacino) | coronamento ~1,0-1,5 m | ~1,5 m | cemento chiaro consumato, **striscia gialla** dipinta sul bordo in vari tratti; **bitte** nere a fungo; catene e cime dei rimorchiatori; nessun parapetto | [F]; quota sull'acqua ~1,0 m [S] |
| 2 | **Carreggiata** | **~10-11 m** | ~9 m | **asfalto grigio** rattoppato, linea di mezzeria bianca tratteggiata (ramo 1 vicino alla radice), **linea gialla continua** a ~1,5-2 m dal ciglio d'ormeggio (ramo 1 dal piloti in poi e ramo 2); tombini | [F] |
| 3 | **Marciapiede** (lato mare aperto) | **~4-4,5 m** | ~4,5 m | **cemento chiaro** con riquadri di **lastre di pietra** chiare sparse (pavimento vecchio rattoppato); **rialzato di un gradino basso** ~10-15 cm sulla carreggiata [S] | [F]; altezza del gradino [S] |
| 4 | **Bordo esterno** | — | — | nessun parapetto per quasi tutta la lunghezza; i **lampioni** stanno sul bordo esterno del marciapiede | [F] |
| 5 | **Scogliera** | fuori dalla larghezza OSM | idem | **massi** grigio-ocra con alghe alla base, ~1-2,5 m, a scarpata fino all'acqua; pescatori seduti sopra | [F]; larghezza della scarpata ~4-6 m [S] |

**Correzione importante:** la prima stesura metteva il kit banchina su **tutti** i bordi del molo. Le foto mostrano che il lato ovest del ramo 1
e il lato sud del ramo 2 sono **scogliera**. Il ciglio a blocchi c'è solo sul lato del bacino (est del ramo 1, nord del ramo 2) e sulle dita.

### 2.3 Altri dati del piano

| Dato | Valore | Stato |
|---|---|---|
| Superficie | radice X 555-570, Y 45-85: **cubetti** di porfido (percorso pedonale lungo l'acqua); **carreggiata in asfalto già dalla radice** (Largo Fiorillo, Y ≤ ~85, e ramo 1); marciapiede in cemento | [V] OSM (`paving_stones`, `asphalt`); [F] `molo_italia_1`, `guardia_costiera_molo_italia_2` |
| Quota del piano | come la banchina, **Z 0** nel gioco; la carreggiata e il marciapiede sono quasi alla stessa quota | [S] / [F] |
| Uso | carreggiata aperta a mezzi autorizzati: **auto parcheggiate** sul lato est vicino alla radice (strisce gialle, `molo_italia_1`) e sul lato ovest accanto al monumento (`monumento_molo`); furgoni e pick-up di servizio. Cartello blu "area pedonale, eccetto autorizzati" a ~Y −90 (`molo_italia_3`) | [F]; OSM `motor_vehicle=permit` [V] |
| Accesso | dalla fine della passeggiata attraverso il piazzale in cubetti (`blocco2.md` §4.5) | [V] / [F] |

### 2.4 Arredi del molo

| Elemento | Dove | Aspetto e dimensioni | Passo / numero | Fonte | Stato |
|---|---|---|---|---|---|
| **Lampioni a pastorale** | bordo esterno del marciapiede, su tutti e due i rami, fino alla testata | palo in ghisa **grigio antracite/verde scuro** con base modanata, **braccio a pastorale con ricciolo** decorativo, **un globo bianco** appeso (Ø ~0,45 m); **h ~5-5,5 m** | **~25-30 m** (stima da prospettiva su `molo_italia_1`); ~10 sul ramo 1 e ~6 sul ramo 2 | [F] tutte le foto del molo | tipo [F]; passo e altezza [S] → integrazione 3 |
| **Panchine** | sul marciapiede, a ridosso del bordo esterno, fra un lampione e l'altro | due tipi: **monoliti in pietra rosata** a spigoli smussati ~2,0 × 0,5 × 0,45 m (`molo_italia_2`, `_4`) e **lastra in cemento bianco su due appoggi** (`molo_italia_7`); tutte senza schienale | ~ogni 10-15 m nel tratto di `molo_italia_4` | [F]; OSM ne mappa 3 [V] | [S] numero esatto |
| **Bitte** | ciglio d'ormeggio (est del ramo 1, nord del ramo 2), attacco delle dita | ghisa nera a fungo, h ~0,4-0,5 m, come `SM_Banchina_Bitta_v2` | ~ogni 12-15 m [S] | [F] `molo_italia_2`, `_6`, `_7` | tipo [F]; passo [S] |
| **Barriere New Jersey** | marciapiede del ramo 2, ultimi ~60 m prima della testata, sul bordo esterno | moduli in cemento **bianchi a strisce diagonali nere**, ~2,0 × 0,6 × 0,8 m, 4-6 moduli | — | [F] `molo_italia_7` | [F] |
| **Ringhiere** | solo alla **testata**: lato sud degli ultimi ~15 m e bordo della testata | **moduli staccati** in tubolare zincato grigio, ~2 m ciascuno, h ~1,0 m, due correnti, montanti agli estremi | 6-10 moduli | [F] `faro_2`, `faro_3` | [F] |
| Cartelli | "area pedonale" (~Y −90), triangoli di pericolo sui pali dei lampioni | — | — | [F] | [S] posizioni |
| Cestini, raccolta differenziata | davanti al ristorante: 4 **bidoni carrellati** (verde, bianco, grigio) con strisce bianco-rosse | ~0,7 × 0,8 × 1,1 m | — | [F] `ristorante_giallo_blu_gallegiante` | [F] |
| Sculture o targhe sulla testata | **nessuna**; solo la targa nera sul fusto del faro | — | — | [F] `faro_3` | [F] |

## 3. Il ristorante galleggiante

| Voce | Valore | Stato |
|---|---|---|
| Identificazione | ristorante su chiatta (`amenity=restaurant`, **`building=houseboat`**, way 851135245). Nome reale visibile in foto: **nel gioco va inventato** (proposta: "Il Gabbiano Blu" o "La Chiatta"), senza insegne reali | [V] OSM; [F] |
| Struttura | **chiatta** (scafo a scatola, fianchi dritti), non una barca con prua: confermato | [F] `ristorante_giallo_blu_gallegiante`, `molo_italia_2` |
| Posizione | **lato est del ramo 1**, X 574,2-593,7, Y −46,3 … −56,7, centro **(583,9; −51,5)** | [V] OSM |
| Dimensioni in pianta | **19,5 × 10,3 m**, **lato lungo perpendicolare al molo** (verso +X): confermato, il lato corto (~10 m) guarda il molo | [V] OSM; [F] (il fronte sul molo misura ~9,7 m in foto) |
| Distanza dal molo | ~2,6 m dal ciglio est (X 571,6) | [V] calcolo |
| **Scafo** | **blu oltremare**, sporge ~0,8-1,2 m sull'acqua, fianchi lisci con piccole aperture tonde | [F] |
| **Piano principale** | scatola **gialla** (giallo canarino) h **~3,2 m**; sul fronte verso il molo: porta a vetri con tendina bianca e scritta "RISTORANTE", una finestra con tende, un grande pannello a lamelle grigio (serranda); sul lato lungo nord una **fila di ~6 finestre** rettangolari con cornice bianca nella parte alta | [F] (scala: porta h ~2,1 m) |
| **Piano superiore** | **terrazza** aperta con **ringhiera bianca** h ~1,0 m fasciata da un **telo bianco** (PVC) e una **copertura leggera bianca** a falde basse (~1,5-2 m sopra il piano della terrazza); unità esterne del condizionatore, asta con bandiera, antenna. Sul lato nord parte della terrazza è chiusa da vetrate (veranda) | [F] |
| Altezza totale | scafo ~1 m + giallo ~3,2 m + parapetto 1 m + copertura ~1,5-2 m ≈ **6,5-7 m sull'acqua**: confermata la stima | [F] |
| **Accessi dal molo** | **due**, ~6 m l'uno dall'altro: (1) **rampa piatta blu** ~2,5 × 2 m con corrimano in legno verso la porta (a nord, è la passerella OSM a Y −48,0); (2) **passerella coperta** da una tettoia ad arco in tubolare bianco e telo, con una scala che sale alla terrazza (a sud, Y ≈ −54) [S] | [F]; OSM ne mappa una sola [V] |
| Sul molo davanti | transenne zincate mobili lungo lo scafo, cavalletto con il menu, striscione con il nome (da non riprodurre), bidoni della differenziata; a sud, **lance di salvataggio arancioni** ormeggiate | [F] |
| Cancello in legno | OSM lo mappa (node 7939085847): **non si vede** nella foto | [S] |
| Nel gioco | interni non modellati: vetri con un fondo semplice. Il giallo e il blu bastano a riconoscerlo | proposta |

## 4. Il faro rosso

| Voce | Valore | Stato |
|---|---|---|
| Posizione | **(678,6; −327,1)**, sulla testata del ramo 2, sul **lato sud** (marciapiede), a ~3 m dal bordo esterno | [V] OSM node 1327347929; [F] `faro_2` |
| Tipo | **torretta tonda in lamiera d'acciaio** con **ballatoio** e **lanterna** | [V] ibiblio; [F] |
| Luce | `Fl R 4s` (1+3): **un lampo rosso ogni 4 s**; portata 8 miglia; piano focale 8 m | [V] OSM + ibiblio |
| Riferimenti | Admiralty E1290, ARLHS ITA-294, NGA 7764 | [V] |
| Colori | **tutto rosso vivo** (fusto, ballatoio, ringhiera, tamburo, cupola), simile a RAL 3000; porta dello stesso rosso, **targa nera** rettangolare sul fusto; vetri della lanterna chiari | [V] ibiblio; [F] |
| **Altezza totale** | **~8 m** dal piano del molo alla punta del parafulmine (misura su una persona in piedi accanto, `faro_2`) | [F] ±1 m; concorda con [V] |

**Proporzioni [F]** (da `faro_2` e `faro_3`, scala persona 1,75 m; quote dal piano del molo):

| Parte | Quote | Diametro | Note |
|---|---|---|---|
| **Zoccolo svasato** | 0 → 0,6 m | **Ø ~3,4 m** alla base, raccordato al fusto con una curva (forma a campana) | poggia su una piccola piattaforma di cemento |
| **Fusto tronco-conico** | 0,6 → 5,3 m | **Ø 2,4 → 2,0 m** | porta in lamiera ~0,8 × 1,9 m rivolta verso **ovest** (verso il molo); targa nera ~0,4 × 0,5 m a ~2,5 m; una piccola finestrella in alto |
| **Cornice / piano del ballatoio** | 5,3 → 5,8 m | **Ø ~2,6 m**, sporge come un anello | |
| **Ringhiera del ballatoio** | 5,8 → 6,8 m | Ø ~2,6 m | 2 correnti + montanti, rossa |
| **Tamburo** sopra il ballatoio | 5,8 → 6,9 m | Ø ~1,6 m | rosso, con una piccola apertura |
| **Lanterna** | 6,9 → 7,5 m | Ø ~1,4 m | vetri su telaio rosso; un **corrimano ad arco** sul fianco per salire |
| **Cupola + pomolo + parafulmine** | 7,5 → ~8,1 m | Ø ~1,5 m alla gronda | cupoletta rossa, pomolo di sfiato |

Nel gioco: **secondo faro visivo** (CLAUDE.md §2.3), MI emissiva rossa con lampo a 4 s (Fl 1+3).

## 5. Intorno al molo

| Elemento | Posizione | Dimensioni / aspetto | Fonte | Stato |
|---|---|---|---|---|
| **Capitaneria di Porto / Guardia Costiera** (edificio a L) | X 592,3-617,0, Y 45,2-81,5: fronte lungo **ovest** (X 592,5, 36 m) sul parcheggio, fronte **nord** (Y 81,5, 25 m) su Largo Fiorillo | **2 piani** alti (~4,5 m l'uno) → **h ~9,5-10 m** [S]; **mattoni rossi a vista**, fasce marcapiano chiare, finestre alte con infissi **verde acqua**, tetto piano con cornicione chiaro; scritta in lettere sul parapetto e porta "Capitaneria di Porto" sul fronte ovest; antenne | OSM 205843153; [F] `guardia_costiera_molo_italia`, `_2`, `info_point_*` | pianta [V]; aspetto [F]; h [S] |
| **Edificio a 4 piani** della radice | X 578,8-593,2, Y 20,3-41,6 (subito a sud della Capitaneria, sul fianco del ramo 1) | **4 piani** (piano terra con grate alle finestre + 3) → **h ~14-15 m** [S]; stesso stile: mattoni, marcapiani chiari, **tapparelle verdi**, pluviali a vista; **due antenne a traliccio** alte sul tetto | OSM 205839145; [F] `molo_italia_1`, `guardia_costiera_molo_italia` | pianta [V]; piani [F]; h [S] |
| Edificio est della radice | X 615-630, Y 20,6-42,1 | non inquadrato | OSM 205839033 | [V] pianta; aspetto [S] (stesso mattone) |
| **Parcheggio della Capitaneria** | fra Largo Fiorillo e il fronte ovest, X ~570-592, Y ~45-80 | asfalto chiaro, **stalli a pettine con strisce gialle**, ~20-25 auto; davanti all'edificio un **giardino** dietro un muretto con recinzione verde: **palme Phoenix** (5-6), un pino domestico, oleandri bianchi | [F] `guardia_costiera_*` | [F]; numero stalli [S] |
| **Chioschetti dell'info point / taxi** (×3) | X ≈ 584,6, 603,2, 620,6, **Y ≈ 108** | **casette prefabbricate a facce piane**, ~3,5 × 3,5 m, h ~3 m: pareti **bianche**, grandi finestre con telai **blu**, tetto piano con una fascia insegna (una **blu**, una **rossa**). OSM li disegna tondi Ø 3,5 m: dalle foto **non sono cilindrici** | OSM 352041386/88/87; [F] `info_point_*`, I2 | posizione [V]; forma [F] |
| **Parcheggio taxi sotto i pini** | X 582-625, Y 90-103 | **pini domestici** grandi (h ~12-15 m, chioma a ombrello) in **aiuole rialzate in mattoni** rossi con bordo in pietra bianca (h ~0,5 m) e **panche in legno**; cartello "eccetto taxi"; dissuasori bassi lungo il bordo; palo alto di illuminazione | OSM 1111180853/54; [F] `info_point_*`, I2 | [F] |
| Posteggio taxi | X 582-625, Y 89-103 | 10 + 10 posti | OSM | [V] |
| Fontana "del Palio del Golfo" | rotatoria di Largo Fiorillo, X 640-649, Y 85-94 | Ø ~9 m | OSM 1198056663 | [V]; non inquadrata |
| **Terminal crociere** | X 677-725, Y 64-96 | edificio basso **bianco**, 1 piano, tetto piano, scritta in facciata (da non riprodurre); davanti una **scultura in metallo** a lame/ali (~4-5 m) | OSM 175935400; [F] `info_point_*`, `guardia_costiera_molo_italia_2` | [V] / [F] |
| Imbarco battelli Cinque Terre | radice del dito D1, node (567,1; −111,2) `amenity=ferry_terminal` | — | OSM 9981146925 | [V] |
| **Battelli turistici** | moli a dito D1/D2 | nella vista dall'alto: un battello a scafo **rosso** e altri bianchi a D2 | [F] solo `Molo_Italia_dall_alto` (Google, solo riferimento) | presenza [F]; nessuna foto ravvicinata → integrazione 6 |
| **Attacco del dito D1** | X ~572-580, Y ~−105 … −115 | **casetta a lamelle** metalliche bianche ~6 × 4 × 3,5 m con cancello estensibile; accanto un **pontile** con **ringhiera tubolare** zincata, gommoni e una motobarca rossa di servizio | [F] `molo_italia_4`, `molo_italia_3` (casetta bianca sul ciglio) | [F]; posizione [S] ±10 m |
| **Rimorchiatori** | ciglio est del ramo 1 (Y ~−160 … −200) e nord del ramo 2 | rimorchiatori portuali **scafo nero e rosso**, sovrastruttura bianca, alberi a traliccio, **parabordi di pneumatici** a prua; 4-6 unità. Nel gioco: nomi inventati | [F] `molo_italia_3/4/5/6` | [F] |
| Pilotine | ciglio est del ramo 1, Y ~−70 … −100 | motoscafi bianchi e neri con la scritta "PILOTI" (da non riprodurre) | [F] `molo_italia_3` | [F] |
| Motovedette | bacino della radice, lato Capitaneria | scafi bianchi con banda diagonale rossa (livrea istituzionale: nel gioco **livrea generica**) | [F] `ristorante_giallo_blu_gallegiante` | [F] |
| **Navi da crociera e gru** | porto commerciale a **est/nord-est** del ramo 2 (Molo Garibaldi e oltre) | 1-2 navi da crociera bianche (~250-300 m) e **5-6 gru portuali** a cavalletto bianco-rosse: dominano la vista dal ramo 2 e dal faro | [F] `molo_italia_5/6/7`, `faro_2/3`, ristorante | [F]; posizioni [S] → solo fondale |
| Circoli nautici (canottieri, vela) | X 681-711, Y 6-53, pontili X 677-714 | — | OSM | [V] |
| Area portuale di Calata Paita (recintata) | da X 748 verso est | — | OSM | [V]: solo fondale |
| Distributore di carburante | (605,8; 139,6), lato città | — | OSM 228154573 | [V]: fondale, senza marchio |
| "Monumento degli Alpini ai Marinai caduti" | etichetta della mappa Google sul **ramo 2**, a ~1/3 dalla testata | **non mappato in OSM e non visibile nelle foto** del ramo 2 | Google (solo riferimento) | [S] → integrazione 5 |

Il **monumento con busto** e le **3 aste portabandiera** stanno alla radice, sullo smusso: sono descritti in `blocco2.md` §4.5.

## 6. Raccordi

| Raccordo | Dove | Cosa fare |
|---|---|---|
| Con il Blocco 2 | X 548,7-570, Y 41,9-100 | `SM_Banchina_Angolo_MoloItalia` (scheda `blocco2.md` §4.5) chiude il ciglio della passeggiata fino a ~Y 47; poi la lunetta del monumento e la scogliera. Il piazzale e il percorso lungo l'acqua (X 555-570, Y 45-85) sono **cubetti**; la carreggiata di Largo Fiorillo e del molo è **asfalto**. Pavimento a Z 0, senza gradini (tranne il gradino basso del marciapiede del molo) |
| Strada d'accesso | Largo Fiorillo X 565-580, Y 40-130 | `M_Molo_Asfalto`; strisce pedonali verso il parcheggio taxi. **Auto parcheggiate** (kit `SM_Morin_Auto_*`) alla radice e lungo il lato est del ramo 1: sono nelle foto, quindi vanno messe come arredo statico. Nessuna auto in movimento sul molo |
| Barriere | — | La barriera di fine blocco va spostata a est della radice (X ≈ 575 per Y > 4), più una barriera sull'accesso a Largo Fiorillo. L'acqua Acqua V2 va estesa fino a X ~720, Y −350 |
| Linea di vista | dalla fine della passeggiata il faro è a ~420 m in diagonale | nessun asset alto sul ramo 1 deve coprirlo; le aste (11-12 m) sono sottili e non lo coprono [S], da verificare con il render |

## 7. Tabella degli elementi per la produzione

Priorità: **A** = identifica il posto · **B** = contorno visibile · **C** = dettaglio o fondale.

| # | Elemento | Posizione (X, Y) | Dimensioni | Fonte | Stato | Asset proposto | Texture nuove | Priorità |
|---|---|---|---|---|---|---|---|---|
| 1 | Suolo del molo (radice + 2 rami + 2 dita) | §2 | 17 × 285 m + 15,4 × 161 m | OSM + [F] | [V] pianta, [F] sezione | **nuovo** `SM_MoloItalia_Suolo` (pezzo unico, UCX a box) con le fasce del §2.2: carreggiata `M_Molo_Asfalto`, marciapiede in cemento (MI nuovo da `M_Molo_Asfalto` più chiaro o lastre `M_Pav_Lastre` ritinte), striscia gialla e mezzeria come decal o fascia di geometria | 0 | A |
| 2 | Ciglio d'ormeggio | **solo** est del ramo 1, nord del ramo 2, dita, testata | ~520 m di bordo | OSM + [F] | [V] | **kit** `SM_Banchina_Mod4m_v2` (~130 moduli) + testate su misura; coronamento con striscia gialla (variante MI) | 0 | A |
| 2b | **Scogliera** | ovest del ramo 1 (Y 45 → −204), sud del ramo 2, gomito, angolo della testata | ~450 m × 4-6 m | [F] | [F] | **kit nuovo** `SM_MoloItalia_Masso_A/B/C` (3 massi ≤ 1k tri, istanziati a scarpata) oppure moduli di scogliera da 8 m ≤ 2k tri; collisione a box inclinato | **1024 D+N+ORM ≈ 2,7 MiB** (roccia CC0 Poly Haven) oppure 0 con `MI_Banchina_Blocchi` ritinta e normal forte | A |
| 3 | Faro rosso | (678,6; −327,1) | h ~8 m, Ø 3,4/2,4/2,0 m | OSM + ibiblio + [F] | [V]/[F] | **nuovo, pezzo unico** `SM_MoloItalia_Faro` (≤ 8k tri) con le proporzioni del §4: lamiera rossa (`T_Ponte_Acciaio` + MI rossa), ringhiera, lanterna `M_Morin_Master_Vetro`, luce emissiva | 0 | A |
| 4 | Ristorante galleggiante | (583,9; −51,5) | 19,5 × 10,3 × ~7 m | OSM + [F] | [V]/[F] | **nuovo, pezzo unico** `SM_MoloItalia_RistoranteGalleggiante` (≤ 20k tri, UCX) + 2 accessi (rampa blu, passerella ad arco) | **0**: giallo e blu sono tinte piatte su `MI` con normal leggera di lamiera; vetri `M_Morin_Master_Vetro`; telo bianco in tinta. In alternativa [SV] dalla foto (≈ 2,7 MiB) | A |
| 5 | Bitte | ciglio d'ormeggio | passo ~12-15 m | [F] | tipo [F], passo [S] | **kit** `SM_Banchina_Bitta_v2` | 0 | B |
| 6 | Lampioni a pastorale | bordo esterno del marciapiede, ~16 in tutto | h ~5-5,5 m, passo ~25-30 m | [F] | tipo [F], passo [S] | **nuovo** `SM_MoloItalia_LampionePastorale` (≤ 3k tri, LOD) con la ghisa `MI_Banchina_Ghisa` e il globo del master emissivo esistente. Servirà anche al raccordo del Blocco 2 | 0 | A |
| 7 | Panchine (2 tipi), cestini, bidoni | marciapiede; davanti al ristorante | ~2,0 × 0,5 × 0,45 m | OSM + [F] | [S] numero | **kit** `SM_Morin_Panchina` (variante monolite pietra rosata e lastra su appoggi via MI), `SM_Morin_Cestino`; bidoni **nuovi** semplici (≤ 500 tri) | 0 | C |
| 7b | New Jersey, ringhiere della testata | ramo 2, testata | moduli 2 m | [F] | [F] | **nuovo** `SM_MoloItalia_NewJersey` (≤ 300 tri, strisce in tinta/UV) e `SM_MoloItalia_RinghieraModulo` (tubolare, ≤ 500 tri) | 0 | B |
| 8 | Battelli ai moli a dito, rimorchiatori, pilotine | D1, D2, ciglio est e nord | 25-35 m | [F] | [F]/[S] | **kit** `SM_Morin_Battello` (1-2 istanze); **nuovo** `SM_MoloItalia_Rimorchiatore` (≤ 15k tri, 2-3 istanze con yaw diverso), parabordi a pneumatici in geometria semplice | 0 | B |
| 9 | Capitaneria (2 piani) + edificio a 4 piani + edificio est | §5 | h ~10 m e ~14,5 m | OSM + [F] | pianta [V], aspetto [F] | **nuovo** low-poly (≤ 5k tri ciascuno), mattoni: `T_Fondale_Palazzo_*` ritinto oppure **[SV]** dalla facciata di `guardia_costiera_molo_italia.png`. Nessuna scritta istituzionale reale | 0 (o 1024 D+N ≈ 2 MiB [SV]) | B |
| 10 | Chioschetti ×3 | Y ≈ 108 | 3,5 × 3,5 × 3 m | OSM + [F] | [V]/[F] | **nuovo** `SM_Morin_ChioschettoInfo` (scatola, 1 mesh, 3 istanze con fascia blu/rossa via MI) | 0 | C |
| 10b | Pini domestici, aiuole in mattoni, panche in legno | parcheggio taxi | pini h 12-15 m | [F] | [F] | **kit** pino esistente (CLAUDE.md: max 2 varianti) + aiuola nuova semplice | 0 | C |
| 11 | Fontana del Palio + rotatoria | (644,5; 89,5) | Ø 9 m | OSM | [V] | **nuovo** semplice | 0 | C |
| 12 | Terminal crociere (+ scultura), circoli nautici, Calata Paita | §5 | — | OSM + [F] | [V] | **kit** sagome di fondale | 0 | C |
| 13 | Barche dei circoli, yacht | pontili X 677-714 | — | OSM | [V] | **kit** `SM_Mirabello_YachtA`, `YachtB_v2` | 0 | C |
| 14 | Navi da crociera + gru portuali | E/NE, oltre X 720 | ~250-300 m; gru ~60-80 m | [F] | posizioni [S] | **nuovo** sagome di fondale (nave ≤ 5k tri, gru ≤ 1k tri ×5), tinta senza texture. Ora **priorità B**: si vedono in ogni foto del ramo 2 | 0 | B |

## 8. Stima della memoria texture

| Voce | Set | MiB (con mip) |
|---|---|---|
| Scogliera (se non si riusa `MI_Banchina_Blocchi`) | 1024 D + N + ORM | ≈ **2,7** |
| Facciata in mattoni [SV] (facoltativa) | 1024 D + N | ≈ **2,0** |
| Ristorante, faro, molo, bitte, lampioni, battelli, rimorchiatori | tinte e riuso | 0 |
| **Totale Blocco 3** | | **≈ 0-4,7 MiB** (obiettivo ≤ 10 MiB) |

Il limite reale è il budget di pubblicazione di 300 MiB (nota del 2026-11-20 in PLAN.md, Blocco 3): c'è margine.

## 9. Foto disponibili

### 9.1 Elenco, punto di presa e cosa confermano

Tutte in `ref/foto/vista/`, aggiunte il 2026-11-20. Punti di presa stimati ±10 m.

| File | Punto di presa (X, Y) → direzione | Cosa mostra | Conferma (✓) / corregge (✗) / nuovo (+) |
|---|---|---|---|
| `Molo_Italia_dall_alto.png` | vista zenitale **Google Maps**, nord in alto, X ~250-720 | tutto il molo, ristorante, dita con battelli, rimorchiatori, testata, scogliera | ✓ pianta OSM, testata dritta; + **scogliera** su tutto il lato esterno; + battelli a D2. **Solo riferimento visivo**, mai geometrie (§9.2) |
| `molo_italia_1.png` | ~(568; 45) → −Y lungo il ramo 1 | edificio a 4 piani in mattoni a sinistra, auto in fila, carreggiata, marciapiede con lampioni a pastorale, scogliera; ristorante giallo in fondo | + sezione, + lampioni, + scogliera, + auto; ✗ asfalto già alla radice |
| `molo_italia_2.png` | ~(566; −25) → −Y | ristorante giallo-blu di fianco (lato nord), bitta, carreggiata, marciapiede con panchine in pietra, scogliera | ✓ chiatta perpendicolare al molo; + colori, finestre, terrazza |
| `molo_italia_3.png` | ~(566; −75) → −Y | pilotine, rimorchiatori, casetta bianca, cartello area pedonale, catene sul ciglio | + arredi del ciglio d'ormeggio, cartelli |
| `molo_italia_4.png` | ~(573; −100), ciglio est → SE | casetta a lamelle, pontile con ringhiera e gommoni, rimorchiatori, lampioni e panchine | + attacco di D1 (in parte M3) |
| `molo_italia_5.png` | ~(566; −195), gomito → E (ramo 2) | carreggiata in curva, rimorchiatore con parabordi a pneumatici, pescatori sulla scogliera | ✓ gomito senza gradini (M9) |
| `molo_italia_6.png` | ~(585; −225), ramo 2 → E | faro rosso in fondo, rimorchiatori al ciglio nord, linea gialla, navi da crociera e gru | + sezione del ramo 2 |
| `molo_italia_7.png` | ~(640; −285), ramo 2 → E | faro più vicino, New Jersey e panchina sul marciapiede, ringhiera vicino al faro, bitte al ciglio nord | + New Jersey, ringhiere |
| `faro_2.png` | ~(668; −318) → E | faro intero con persone accanto, testata dritta, ringhiere a moduli | ✓ altezza ~8 m, testata dritta (M7, M8) |
| `faro_3.png` | ~(673; −323) → E, ravvicinata | faro di fronte: porta, targa, zoccolo svasato, ballatoio, lanterna | ✓ proporzioni del §4 (M7) |
| `ristorante_giallo_blu_gallegiante.png` | ~(568; −50), ciglio est → +X | fronte corto del ristorante: scafo blu, piano giallo, terrazza bianca, 2 accessi; Capitaneria e motovedette sullo sfondo | ✓ 2 livelli, h ~7 m (M5); ✗ 2 accessi invece di 1 |
| `guardia_costiera_molo_italia.png` | ~(572; 75), parcheggio → SE | fronte ovest della Capitaneria (2 piani) e l'edificio a 4 piani; giardino con palme; auto | + aspetto e piani degli edifici |
| `guardia_costiera_molo_italia_2.png` | ~(566; 100), Largo Fiorillo → −Y | Capitaneria di scorcio, terminal crociere, percorso in cubetti con lampioni verso il molo, fioriere, cartello 10 km/h | + raccordo (M10) |
| `info_point_e_parcheggio_guardia_costiera.png` | ~(575; 95) → +X | chioschetti info point, pini, aiuole in mattoni, parcheggio, fianco nord della Capitaneria, terminal crociere | ✗ chioschetti non tondi; + pini e aiuole |
| `3_aste_bandiere_molo.png`, `monumento_molo.png`, `incrocio_*` (2), `chiosco_2_fine_passegiata_morin.png` | radice e fine passeggiata | vedi `blocco2.md` §9 | + aste, monumento, piazzale (M10) |

Coperte: **M1, M5, M7, M8, M9, M10**. In parte: **M2** (ciglio d'ormeggio sì, quota no), **M3** (solo l'attacco di D1), **M4** (tipo sì, misura no),
**M6** (solo dall'alto, Google).

### 9.2 Licenze delle foto

- **16 catture Street View** (filigrana "© 2025/2026 Google", logo Google Maps, bussola, zoom, riquadro della mappa, etichette 3D delle vie):
  per la **deroga dell'utente** (CLAUDE.md §5) si possono usare **anche per le texture**, segnate **[SV]** in `docs/CREDITS.md`, senza filigrane,
  interfaccia, etichette, persone né targhe (nelle foto ci sono molte persone e auto con targa). Prima di pubblicare l'utente le ricontrolla.
  Candidati utili: facciata in mattoni (`guardia_costiera_molo_italia.png`, parte alta), giallo del ristorante, rosso del faro (`faro_3`),
  massi della scogliera (`molo_italia_6`), cubetti con fasce bianche (`chiosco_2_*`).
- **`Molo_Italia_dall_alto.png` è una vista satellitare Google Maps**, non Street View: la deroga parla di catture Street View, quindi la tratto
  come **solo riferimento visivo**, mai texture e mai geometria ricalcata. Se l'utente vuole estendere la deroga, deve dirlo.
- Nessuna foto ha l'aspetto di una foto stock (niente filigrane di agenzie).
- Marchi e nomi reali visibili: nome del ristorante, "Guardia Costiera" e livrea delle motovedette, "PILOTI", nomi dei rimorchiatori,
  "Cruise Terminal", insegne dei chioschetti, compagnia dei battelli. **Nel gioco tutto inventato o neutro.**
  Per la scritta istituzionale sulla Capitaneria: proposta di toglierla (decisione dell'utente).

## 10. Integrazioni da chiedere all'utente (Blocchi 2 e 3)

Le foto M1, M5, M7-M10 e F8 (in parte), F9 non servono più. Restano queste richieste, in ordine di importanza:

1. **Chiosco ottagonale dal lato del viale** (B2.4, in lavorazione): una foto da Largo Fiorillo o dal vialetto (~X 560, Y 115) verso SO, con il tetto
   intero. Domanda: il tetto è a 8 falde (ottagonale) o a 4? Le tende ci sono su tutti i lati?
2. **Sezione del ramo 1 misurata a passi**, all'altezza del ristorante: quanti passi dal ciglio est all'inizio del marciapiede, quanti passi
   è largo il marciapiede, e com'è alto il gradino fra carreggiata e marciapiede (foto con una scarpa accanto al gradino).
3. **Lampioni e panchine del molo:** quanti lampioni ci sono sul ramo 1 (dalla radice al gomito) e quanti sul ramo 2? Una foto di un lampione
   con una persona accanto per l'altezza.
4. **La scogliera vista dal marciapiede**: una foto verso il basso dal bordo esterno del ramo 1 (anche a metà del ramo): c'è un cordolo o un
   muretto fra marciapiede e massi? A che quota sotto il marciapiede iniziano i massi?
5. **Monumenti:** (a) la stele con il busto alla radice, di fronte da ~5 m, per leggere la targa e capire a chi è dedicata;
   (b) esiste un monumento sul ramo 2 (la mappa Google indica un "Monumento degli Alpini ai Marinai caduti")? Se sì, una foto con una persona accanto.
6. **Moli a dito e battelli**: una foto dall'attacco di D2 (~Y −155) verso est. D1 e D2 sono moli in cemento o pontili galleggianti?
   Quali battelli ci sono di solito (forma e colori, senza i nomi)?
7. **Passo delle palme della passeggiata** (F7 di `blocco2.md`): blocca ancora B2.2. Basta contare le palme di un filare fra l'ancora 2 (X 280)
   e la scritta "PASSEGGIATA MORIN".
8. **Ristorante dal lato nord, ravvicinato** (facoltativa): le finestre del lato lungo e la terrazza, per il dettaglio dell'asset.

## 11. Ordine di lavoro proposto (Blocco 3)

Da iniziare dopo il Blocco 2, oppure insieme al punto 1 del Blocco 2 per il raccordo.
1. **(blender-artist) Suolo con la sezione del §2.2, ciglio d'ormeggio (kit) e scogliera** (elementi 1, 2, 2b): blockout prima.
   (uefn-builder) Acqua V2 estesa, barriere spostate.
2. **Faro rosso** (3): pezzo unico con le proporzioni del §4, luce lampeggiante.
3. **Ristorante galleggiante + 2 accessi** (4): le foto bastano.
4. **Lampione a pastorale** (6), che serve anche al raccordo del Blocco 2; poi panchine, bitte, New Jersey, ringhiere, bidoni (5, 7, 7b).
5. **Rimorchiatori, battelli, navi da crociera e gru** (8, 14).
6. **Radice e fondale:** Capitaneria ed edificio a 4 piani, chioschetti, pini, fontana, terminal, circoli (9-13).
7. (qa-tester) Sessione: percorso radice → faro senza fessure, cadute dalla scogliera e dal ciglio, faro visibile dalla passeggiata, memoria.
