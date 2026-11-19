# Scheda — Radice del molo del ponte (incrocio Banchina Thaon di Revel) e molo fino al ponte

Legenda: **[V]** verificato (fonte citata) · **[S]** stima motivata, da confermare · **[V-utente]** confermato dall'utente.
Coordinate locali del progetto (`area.md`): X lungo la passeggiata verso NE, Y verso la città, origine all'imbocco del ponte.
In UE: (X·100, −Y·100). Dati OSM: `ref/osm/morin_bbox.osm` (2026-11-18) più una verifica live con Overpass API (2026-11-19),
© OpenStreetMap contributors. Nella zona Overpass non ha dato nulla di nuovo: nessun `natural=tree`/`wood`, nessun lampione.
Geo-scout, 2026-11-19 (sessione 3).

**Foto usate** (catture Street View dell'utente; per le texture vale la deroga [SV] di CLAUDE.md §5, vedi §8):
- **F1** `ref/foto/vista/inizio_passegiata_ristoranti_che_vanno_verso_il_ponte.png` (1886 × 811, 2023): incrocio, vista verso il ponte.
- **F2** `ref/foto/vista/ristoranti_visti_da_di_fronte.png` (1030 × 667): facciate dei ristoranti, vista frontale.
- **F3** `ref/foto/vista/strada_cheProsegue_verso_il_ponte.png` (975 × 895): il molo verso il ponte.
- **F4** `ref/foto/pavimentazione/pavimento verso il ponte.png` (390 × 200): masselli del molo in primo piano.

**Attenzione, elementi della UI di Street View, da NON modellare:** il **cerchio bianco con freccia** sulle lastre (F1 e F3)
e la scritta "Banchina Thaon di Revel" sul pavimento (F3) sono sovrimpressioni di navigazione. Lo è quasi certamente anche
la freccia bianca in basso in F1 [S]. La **croce bianca** sull'asfalto di F1 potrebbe essere UI oppure segnaletica: è la domanda D2.
Le auto parcheggiate sul molo vanno ignorate, per indicazione dell'utente.

---

## 1. Punto di presa e direzione di F1

| Voce | Valore | Stato |
|---|---|---|
| Luogo | radice del molo del ponte, all'incrocio con Viale Italia; vista verso il ponte (bacino a sinistra, ristoranti a destra) | [V-utente] |
| Punto di presa | **X ≈ 12,5 · Y ≈ 117 (±4 m)**, sull'asfalto all'imbocco della strada di servizio, a ~4 m dal bordo di Viale Italia | [S] calcolo |
| Altezza della camera | ~2,5-3,0 m (auto Street View) | [S] |
| Direzione | **azimut ≈ 150-156°**, cioè −Y ruotato di ~20° verso −X (verso i ristoranti). FOV orizzontale ≈ 100° | [S] calcolo |

**Metodo.** Ho calcolato la camera con i minimi quadrati, con l'orizzonte a y 365 px, usando tre corrispondenze: il piede
della palma d'angolo con il primo albero OSM del filare 1 (20,4; 92,9), lo spigolo arrotondato dell'edificio d'angolo con il
nodo OSM (0,6; 102,6), e le **antenne del ponte**. Le antenne sono le due "aste" bianche con gli stralli al centro di F1
(x ≈ 680 px), allineate con il pennone 1 (−2,3; −80,1). Con camera alta 2,8 m il residuo è 8 px, con 2,5 m 16 px.
La geometria ricavata torna con OSM: il cordolo della strada riproiettato cade a X ≈ 9,3-10,4 lungo tutto Y 90-108, cioè
parallelo all'asse OSM della strada (X ≈ 9). Anche l'ordine delle insegne torna con i nodi OSM: Pescheria (0,6; 98,4) e
"Dai Pescatori" (−3,4; 105,1).
**Esito:** l'ipotesi dell'orchestratore è **confermata**, con una precisazione. La camera non è a Y 100-120 sulla strada
già nel molo: è più indietro, quasi sul bordo di Viale Italia, e guarda giù lungo la strada di servizio.

## 2. Planimetria dell'incrocio e del molo

### 2.1 Strada di servizio "Banchina Thaon di Revel"
| Tratto | Tracciato (X, Y) | Superficie | Larghezza | Stato |
|---|---|---|---|---|
| Ramo da Viale Italia | asse (9,2; 129,2) → (9,3; 120,9) → (8,9; 109,6) → (8,8; 101,9) → (8,9; 96,0) → (9,0; 85,8). Via `highway=unclassified`, `lane_markings=no` | **asfalto scuro** | asse [V] OSM 238848818. Carreggiata **~3,5-4,5 m** [S] da F1: bordo est (cordolo) a X ≈ 10, bordo ovest a X ≈ 6-7,5 | asse e asfalto [V] OSM e F1; larghezza [S] |
| Molo verso il ponte | (9,0; 85,8) → (6,9; 78,0) → (4,7; 66,1) → (0; 0), poi il ponte | in OSM `sett`; nelle foto **masselli rettangolari grigio chiaro** (F3, F4), non cubetti. Non c'è una carreggiata distinta: tutto il molo è pavimentato allo stesso modo | tutto il molo, ~13-21 m (X −12/−6 → +10) | tracciato [V] OSM 183535303; materiale [V-foto] F3/F4 |
| Ramo verso est (accesso al parcheggio) | dall'incrocio (8,9; 109,6) verso +X lungo Y ≈ 109 (`parking_aisle` 378872040, asfalto) | asfalto | ~4-5 m [S] | [V] OSM; in F1 è l'asfalto in basso a sinistra |
| Nodo `access=permit` | (4,7; 66,1): ingresso riservato ai veicoli autorizzati | — | — | [V] OSM 10249190465 |
| Attraversamenti | pedonale non segnato in (8,9; 96,0), cioè la passeggiata attraversa la strada; strisce su Viale Italia in (9,3; 120,9) | — | — | [V] OSM |

**Fine dell'asfalto:** nel reale l'asfalto prosegue fino a **Y ≈ 86-90** affiancato all'angolo in cubetti (F1). Più avanti si
vedono solo masselli (F3). Il punto preciso del cambio è [S] (domanda D3).

### 2.2 Superfici pedonali
| Area | Posizione | Materiale | Stato |
|---|---|---|---|
| **Angolo in cubetti** (lato mare della strada) | da X ≈ 10 (cordolo) a X ≈ 20, da Y ≈ 108 fino al camminamento (Y ≈ 89); prosegue nella fascia palme | cubetti di porfido/sampietrini **a coda di pavone** con fasce chiare, come la fascia palme. Spigolo dell'angolo **smussato/arrotondato** verso l'incrocio | materiale [V-foto] F1; contorno [S] da F1 (spigolo a ≈ (10,3; 108), lato nord lungo Y ≈ 107-109 verso +X) |
| Cordolo della strada | lungo X ≈ 10, da Y ≈ 108 a ≈ 89; lungo Y ≈ 108 verso +X | pietra chiara, h ~12-15 cm [S] | [V-foto] F1; altezza [S] |
| **Fascia davanti ai ristoranti** (lato ovest della strada) | X ≈ 1 → 7, Y ≈ 62 → 112 | **masselli/lastre grigi** rettangolari, uguali al molo | [V-foto] F1, F2; area pedonale [V] OSM 850396604 |
| Molo (Y 86 → 0) | tutta la larghezza del molo, X ≈ −12 → +10 | masselli rettangolari grigio chiaro ~25-30 × 12-15 cm [S], posati a correre, giunti con erba (F4). I corsi sembrano trasversali all'asse del molo [S] | [V-foto] F3, F4; misure [S] |
| Camminamento (Y 80-89) | dall'angolo X ≈ 10-19 | lastre grandi (come il resto della passeggiata) | [V] OSM, `sezione.md` |

### 2.3 Segnaletica e arredi dell'incrocio (forme generiche, niente marchi)
| Elemento | Posizione | Note | Stato |
|---|---|---|---|
| Linea gialla trasversale sottile | da (≈ 8; 110) verso i ristoranti, sulle lastre | probabile limite di sosta o di dehors | [S] F1 |
| Croce bianca sull'asfalto | ≈ (10,7; 109,5) | da confermare: UI o vernice (D2) | [S] |
| Cartello rotondo di divieto d'accesso su palo | ≈ (13-15; 80-83), all'ingresso del molo lato bacino | h ~2,5 m. Nel gioco solo un disco rosso-bianco generico | [S] F1 |
| Secondo cartello rotondo (ZTL/divieto) | sul molo, ≈ (8; 65) | | [S] F1 |
| Barriera tipo new jersey (bianco-nera) | sul ciglio dell'angolo, ≈ (18; 81-90) | ~1,5 × 0,5 × 0,6 m | [S] F1 |
| Cestino cilindrico scuro | accanto al new jersey | h ~0,8 m | [S] F1 |
| Blocco grigio basso (plinto o fioriera) | ≈ (11; 93) | ~0,8 × 0,8 × 0,5 m. Vicino alla posizione OSM della Sirena (13,8; 91,9): nel 2023 la statua **non si vede** (D1) | [S] F1 |
| Bordo del molo dipinto di blu | ciglio est del molo, Y ≈ 60-80 | fascia blu sul ciglio [S] | [S] F1 |
| Telecamera su palo, semafori | (12,3; 125,5); semafori a (15,3; 129,2) e (15,3; 135,0) su Viale Italia | fuori dal molo, fondale | [V] OSM |

### 2.4 Elementi lungo il molo (F3)
| Elemento | Posizione | Dimensioni | Stato |
|---|---|---|---|
| **Fioriere bianche tonde con palme nane** (Chamaerops/Phoenix giovani) | fila lungo il lato est del molo, X ≈ 7-9, Y ≈ 30-75 | vaso Ø ~1,0 m, h ~0,9 m; pianta h ~1,5-2,5 m | [V-foto] F3; posizioni e numero [S] (D6) |
| **Palme alte** | lato ovest, dietro il dehors a righe, X ≈ −8…−12, Y ≈ 20-60 | 4-5 esemplari, h ~10-12 m; sembrano Phoenix come quelle della passeggiata | [S] F3 |
| **Lampioni alti del molo** | lungo il molo, X ≈ 2-5, passo ~20-25 m | palo liscio grigio, **h ~8-9 m**, piccola armatura in cima. Diversi da quelli della passeggiata | [V-foto] F1, F3; misure [S] |
| Ingresso del ponte | Y ≈ 0 | rampa con ringhiera bianca; cancello/recinzione bianca a montanti ai lati | [V-foto] F3; dettagli in `ponte.md` |
| Auto parcheggiate | lato est | **da ignorare** (indicazione dell'utente) | — |

## 3. Edifici bassi (lato ovest del molo)
Nomi reali solo come riferimento: nel gioco nomi inventati e niente loghi o insegne vere (CLAUDE.md §5).

### 3.1 Piante OSM (vertici X, Y in m)
| Id | Cosa | Vertici | Ingombro | Stato |
|---|---|---|---|---|
| **A** 352041383 | fila principale dei ristoranti: gastronomia d'angolo (nord), pescheria, sezioni bianche/gialle, blocco sud | (−5,7; 102,6) (−7,9; 102,7) (−7,9; 106,7) (−4,1; 106,9) **(0,6; 102,6)** (0,3; 79,9) (1,4; 79,9) (1,2; 68,0) (0,2; 68,1) (0,1; 62,1) (−6,3; 62,0) | ~45 m in Y × 6-8,5 m. Facciata a X ≈ 0,1-1,4; retro a X ≈ −6/−8 (confine dell'area militare). Lo spigolo NE fra (0,6; 102,6) e (−4,1; 106,9) è lo **spigolo arrotondato** di F1/F2 | pianta [V] OSM (Regione Liguria) |
| **B** 1383525363 | probabile tendone/pergola scura a nord del ristorante d'angolo ("tendone sulla destra" di F2) | (−8,1; 111,4) (0,5; 111,5) (0,5; 116,7) (−8,1; 116,6) | 8,6 × 5,3 m | pianta [V] OSM (Microsoft footprints); natura [S] |
| **C** 205840540 | casa/ristorante sul molo (ristorante con dehors, nodo (−11,5; 30,2)) | (−12,1; 42,1) (−7,7; 42,2) (−7,5; 24,8) (−11,9; 24,8) | 4,5 × 17,4 m | [V] OSM |
| D 205841992 | edificio lungo dentro l'area militare, dietro A | (−14,2; 87,0) (−14,8; 29,6) (−19,5; 29,6) (−19,2; 55,3) (−20,8; 55,3) (−20,0; 87,1) | 5-6,5 × 57 m | [V] OSM; fondale |
| D2 205839287, D3 175935410 | edifici nell'area militare | (−15,8; 25,6)(−15,7; 1,5)(−20,9; 1,5)(−21,0; 25,6) · (−20,5; 30,2)(−20,5; 37,0)(−28,2; 36,9)(−28,1; 30,1) | | [V] OSM; fondale |
| E 205842871, 205843780 | edifici tra il ristorante d'angolo e il distributore, area militare | vedi OSM; X −50…−17, Y 87…115 | | [V] OSM; fondale |
| F 1444664603 | distributore di carburante (pensilina) | X −60…−9, Y 102…122 | | [V] OSM; fondale. In F1/F2 forse la copertura blu in alto a destra [S] |

### 3.2 Sezioni della fila A (da nord a sud) — aspetto da F1/F2/F3
| Sezione | Tratto Y [S] | Facciata | Altezza | Tetto | Dehors | Stato |
|---|---|---|---|---|---|---|
| **A1 ristorante d'angolo** | ~94 → 107, con lo spigolo NE arrotondato (raggio ~4-5 m) | intonaco **giallo caldo**; porte-finestre in legno scuro con vetri (2 ante, h ~2,5 m); tenda avvolgibile **crema** sopra la vetrina; stemma/insegna rosso da sostituire con un'insegna inventata | **~3,8 m** al cornicione [S] (calcolo da F1: 3,7-4,1 m) | piano, con **cornicione rosso-bruno** (fascia h ~0,35 m) sopra una sottile cornice bianca; macchine del clima sul tetto | tavolini quadrati bianchi, sedie scure in polipropilene, 2-3 ombrelloni chiusi bianchi, fioriere rettangolari antracite con arbusti (pittosporo/lauro) | [V-foto]; misure [S] |
| **A2 pescheria (rosa)** | ~88 → 94 | intonaco **rosa salmone**, finestra con fiori, insegna rettangolare bianca | ~3,8 m | come A1, cornicione rosso-bruno | fioriere, tavolini | [V-foto] F1, F2 |
| **A3 sezione bianca e gialla** | ~68 → 88 | parte bassa **bianca**, fascia **gialla** in alto, vetrate a porta-finestra con telaio legno, insegna blu "pescheria" (nel gioco: generica); bracci metallici delle tende | **~3,3-3,6 m** (più bassa di A1) | piano, bordo bianco | fila di fioriere antracite (~1,0 × 0,4 × 0,4 m) a ~1,5 m dalla facciata, tavolini, ombrelloni | [V-foto] F2 |
| **A4 blocco sud** | ~62 → 68 (e verso nord) | **bianco** con fasce gialle/ocra, porte e scuri **rosso scuro**; zoccolo grigio | **~4,5-5,5 m** con il parapetto [S] | piano, **terrazza con ringhiera** rosso-bruna; insegna verde piccola | fioriere | [V-foto] F2 (a sinistra) |
| **A5 lato sud verso il ponte** (F3) | facciata est del blocco sud e poi verso Y ~40 | **bianco** liscio, finestra con grata bianca, applique; sul tetto verde che ricade (vegetazione dell'area militare dietro) | ~3,8-4 m | piano | **dehors lungo con tende a righe blu-bianche** (tettoia a falda, h gronda ~2,4 m, profondità ~3 m), tende laterali bianche, ombrelloni bianchi aperti con palo in legno, tavoli in legno e sedie, lavagna a cavalletto (testo da non riprodurre) | [V-foto] F3; tratto Y e misure [S] |

**Altezze:** sostituiscono la stima di `elementi.md` §3 ("1-2 piani, 4-7 m"): **un solo piano, 3,3-4 m**, più parapetti.
L'unica eccezione è il blocco sud con la terrazza (~5 m) [S].

## 4. Alberi dietro gli edifici e confine dell'area militare
| Voce | Dato | Stato |
|---|---|---|
| Alberi in OSM | **nessuno** nell'area militare (né nel file né su Overpass live). Unico dato vicino: filare `tree_row` 378875630 (latifoglie semi-sempreverdi) lungo Viale Italia, Y 137, X −108 → −4 | [V] OSM (assenza) |
| Massa arborea in F1/F2 | chiome larghe e dense a foglia larga, verde chiaro-medio, subito dietro la fila A (X ≈ −8 → −35, Y ≈ 40 → 112), dentro il Circolo Ufficiali | [V-foto] |
| Specie probabile | **platano** (Platanus × hispanica) o bagolaro/olmo, per la chioma chiara e il portamento; a destra di F2, dietro il tendone, un **pino domestico** (chioma scura a ombrello) | [S] |
| Altezza | **15-20 m** (le chiome superano di 4-5 volte il cornicione da 3,8 m e sono più lontane) | [S] calcolo da F1/F2 |
| Numero e posizioni proposte | 5-6 grandi latifoglie a (−14; 105), (−22; 96), (−18; 80), (−25; 66), (−20; 50), (−28; 38); pino a (−12; 118) | [S] da F2, senza dati OSM |
| Confine militare | recinzione a rete (`chain_link`) 224920368 lungo **Y ≈ 102,7 da X −49,8 a −7,9**, cioè dietro il ristorante d'angolo; poi il confine segue i **muri posteriori** degli edifici A e C (X ≈ −6 → −12), fino a (−13,2; −4,1). Altezza ~2 m [S] | percorso [V] OSM 224920367/224920368; altezza [S] |
| Barriera di gioco esistente | `Barriera_Molo_AreaMilitare` a X ≈ −13,6 (Y −120 → +33): sta oltre il retro di A e C, quindi gli edifici restano nella zona giocabile | [V] `docs/uefn_blockout.md` |

## 5. Lampione a due globi dell'angolo
| Voce | Dato | Stato |
|---|---|---|
| Posizione | **(12,5; 106) ± 2 m**, sull'angolo in cubetti accanto al cordolo, su una lastra quadrata di base (~0,9 m) | [S] calcolo da F1 |
| Forma | palo in ghisa scura con base scanalata svasata (~1,2 m); **due globi bianchi sovrapposti sull'asse del palo**, il superiore più grande; pinnacolo in cima. **Niente bracci** | [V-foto] F1 |
| Misure | h totale **~7-7,5 m**; globo inferiore a ~5,5 m, superiore a ~6,2 m; globi Ø ~0,6-0,8 m | [S] calcolo (camera 2,8 m) |
| Confronto con `SM_Morin_Lampione` | **È diverso.** Quello della passeggiata (`ref/foto/arredi/lampione.png`, `docs/uefn_arte.md` §12) è alto 4,82 m, ha **due bracci a ricciolo** e i globi appesi ai lati, alla stessa quota. Questo è un **candelabro a globi sovrapposti**, più alto: serve un asset nuovo | [V-foto] |
| Lampioni del molo | diversi da entrambi: pali lisci alti ~8-9 m (§2.4) | [V-foto] |

## 6. Confronto con lo stato attuale del progetto (zona X −15 → 25, Y 0 → 120)
| Elemento | Oggi nel progetto | Realtà | Cosa cambiare |
|---|---|---|---|
| Superficie del molo | `SM_Blockout_Passeggiata_Pav`: molo piatto a Z 0 con `MI_Pav_Lastre` (lastre grandi della passeggiata), anche nel tratto X < 9,75 | masselli piccoli grigio chiaro, giunti erbosi | nuova mesh/materiale `MI_Molo_Masselli`; il molo resta a Z 0 |
| Strada di servizio | assente (lastre) | asfalto scuro X ≈ 6-10, Y ≈ 86 → 121, cordolo a X ≈ 10; ramo d'asfalto verso +X a Y ≈ 109 | aggiungere la striscia d'asfalto (a raso o −2 cm) e il cordolo da 12-15 cm |
| Angolo in cubetti | la fascia palme parte a X 9,75 tra Y 89 e 102; oltre Y 102 c'è il blockout dei giardini, con siepe a Y 116-118 alta 1,5 m | cubetti dall'angolo X ≈ 10 fino a Y ≈ 108, con spigolo smussato verso l'incrocio | pezzo d'angolo `SM_Pav_AngoloMolo` (X 10-20, Y 89-109) che raccorda fascia palme e cordolo della strada; siepe e giardino del blockout da arretrare dietro X ≈ 16-20 |
| **Prime palme** | `Palma_F1_01` e `F2_01` a **X 12** (filari X 12 + 9k, decisione del 2026-11-19) | in F1 **non c'è nessuna palma fra la strada e X ≈ 18**: una palma in (12; 92,6) o (12; 99,6) si vedrebbe sopra il lampione, dove c'è solo cielo. I filari OSM partono da X 20,4 | proposta: togliere F1_01/F2_01 (o spostare i filari a X 20,4 + 9k). **Decide l'utente (D4):** cambia una posa già verificata |
| Lampione dell'angolo | il primo `SM_Morin_Lampione` è a (16,8; 92,85) | candelabro a 2 globi in (12,5; 106) | nuovo asset `SM_Molo_Lampione2Globi`; controllare che non si sovrapponga alla panchina (16,5; 92,1) |
| Edifici A, B, C | scatole bianche del blockout di fondale (`SM_Blockout_Fondale`, un box per edificio OSM, **h 6 m**) | un piano, 3,3-4 m (blocco sud ~5 m), facciate colorate, dehors | sostituire con modelli veri (§9); B diventa un tendone |
| Alberi dietro | nessuno (solo il fondale) | grandi latifoglie da 15-20 m e un pino | 2 varianti di latifoglia e 1 pino domestico, istanziati |
| Arredi del molo | nessuno | fioriere bianche con palme nane, palme alte, lampioni alti, dehors | asset §9 |
| Sirena | nessun asset | OSM la mette in (13,8; 91,9); nel 2023 non si vede | dipende da D1 |

## 7. Domande per l'utente (bloccano o cambiano la modellazione)
- **D1. Sirena:** oggi la statua c'è? Dove sta rispetto al lampione a due globi e al blocco grigio in (≈ 11; 93)? Una foto con una persona accanto.
- **D2.** La croce bianca sull'asfalto di F1 è vera (vernice) o è il cursore di Street View? E la linea gialla sulle lastre?
- **D3.** Dove finisce l'asfalto e cominciano i masselli: all'altezza della passeggiata (Y ≈ 86) o prima? Una foto della strada vista da Viale Italia (incrocio, semaforo, strisce).
- **D4. Prime palme:** confermi che all'angolo, vicino alla strada, non ci sono palme e che la prima palma è ~8 m più verso la passeggiata? Se sì, si tolgono `Palma_F1_01`/`F2_01` (X 12) o si spostano i filari.
- **D5.** Foto del lato nord del ristorante d'angolo e del tendone (verso Viale Italia) e del retro (recinzione militare, alberi).
- **D6.** Foto del molo lato bacino: fioriere bianche con palme nane (quante, ogni quanti metri) e un lampione alto da vicino.
- **D7.** Foto dell'ultimo tratto, Y 0-40: ristorante con dehors a righe, imbocco del ponte con cancello bianco, palme alte.
- **D8.** I dehors (tavolini, ombrelloni, tende a righe) li vogliamo nel gioco come nel 2023, o solo fioriere e tende fisse? Cambiano anche gli spazi in cui si corre.

### 7.1 Risposte dell'utente (2026-11-19, sessione 3) [V-utente]
- **D1:** la Sirena **c'è** → modellarla stilizzata (opera d'autore, non copia fedele) sul basamento, posizione OSM (≈ 14; 92). Misure [S].
- **D2:** nessuna segnaletica a terra (né croce bianca né linea gialla).
- **D3:** non risposta → usare la stima della scheda (asfalto fino a Y ≈ 86-90), da confermare in sessione.
- **D4:** **spostare i filari** in modo che partano da X 20,4 come in OSM e in foto (niente palme all'angolo).
  Il **gazebo va fra la 2ª e la 3ª palma** (X ≈ 33,9 con passo 9 m: palme a 20,4 / 29,4 / 38,4) [V-utente].
  Con i filari si spostano di conseguenza aiuole, strisce trasversali, panchine, lampioni e tombini (layout v4).
- **D5-D7:** foto non ancora fornite; procedere con le stime.
- **D8:** dehors **completi come in foto** (tavolini, sedie, ombrelloni aperti/chiusi, tende, fioriere).
- Auto sul molo: **ignorarle** (non modellare).

## 8. Texture: quali foto e quali porzioni (deroga [SV], CLAUDE.md §5)
Regole: niente UI di Street View (frecce, cerchi, etichette, "© 2023 Google" in F1 a x 1700-1880 / y 375-400,
"Immagini soggette a copyright" in alto a sinistra in F2), niente persone, targhe, loghi, insegne, poster ("Jurassic Show" in F1)
né testo della lavagna (F3). Pixel in coordinate dell'immagine originale (x, y). Ogni texture va annotata in `docs/CREDITS.md` con [SV].

| Texture proposta | Foto e porzione | Note |
|---|---|---|
| `T_Molo_Masselli_D/N/ORM` (2048) | **F4 intera** (primo piano, la fonte migliore); scala e colore da **F3** x 0-380, y 700-895 (sotto l'etichetta, che sta a x 195-290 / y 500-680: esclusa) | rendere tileable; giunti con erba come secondo strato |
| `T_Molo_Asfalto_D` (1024-2048) | F1 x 950-1250, y 690-800 (lontano dalla croce, che sta a x 750-890) | asfalto scuro con rattoppi |
| `T_Molo_Intonaco_Giallo_D` | F2 x 800-835 e 900-935, y 430-500 (fra le porte, senza lo stemma a x 730-790); in alternativa F1 x 1640-1700, y 300-360 | de-lighting: luce radente |
| `T_Molo_Intonaco_Rosa_D` | F2 x 690-728, y 395-500 (sotto l'insegna) | |
| `T_Molo_Intonaco_Bianco_D` | F3 x 860-975, y 330-420 (parete del blocco sud, senza applique e finestra) | |
| `T_Molo_Cornicione_D` (striscia) | F2 x 600-990, y 376-392 (fascia rosso-bruna) e la cornice bianca sotto | atlante di trim |
| Porte-finestre in legno e vetro | F2 x 838-905, y 435-525 (porta di A1), senza riflessi di persone | per una texture di trim delle aperture |
| `T_Molo_TendaRighe_D` | F3 x 440-700, y 350-400 (righe blu-bianche della tettoia) | raddrizzare, poi ricostruire il modulo a righe |
| Tenda crema avvolgibile | F2 x 820-950, y 403-422 | |
| Fioriera antracite | F2 x 455-500, y 528-548 | |
| Fogliame latifoglie (card) | F2 x 330-900, y 130-330, bordo con il cielo per l'alfa | solo colori e tessitura: le card vanno ricostruite (il cielo dietro non dà un'alfa pulita) |
| Arbusti delle fioriere | F2 x 600-660, y 490-545 | card |
| Cubetti dell'angolo | già coperti da `T_Pav_Cubetti` (`CREDITS.md`) | controllare la tinta con F1 x 50-500, y 520-700 |

## 9. Proposta di asset per blender-artist (budget LOD0; LOD1 ~50 %, LOD2 ~15 % sui ripetuti)
| Asset | Contenuto | Budget tri | Texture | Priorità |
|---|---|---|---|---|
| `SM_Molo_Pav_Strada` + `SM_Molo_Pav_Masselli` | striscia d'asfalto Y 86-121 con cordolo X ≈ 10 e ramo a Y 109; superficie del molo in moduli che seguono la pianta OSM | ≤ 2k per modulo | asfalto 2048, masselli 2048 | Alta |
| `SM_Pav_AngoloMolo` | angolo in cubetti X 10-20, Y 89-109, spigolo smussato, cordoli, raccordo con fascia palme e giardini | ≤ 2k | riusa `MI_Pav_Cubetti`/`Fascia` | Alta |
| `SM_Molo_Edificio_A1A2` | ristorante d'angolo con spigolo arrotondato + sezione rosa, cornicione, tenda crema, clima sul tetto | ≤ 5k | atlante facciate 2048 | Alta |
| `SM_Molo_Edificio_A3` | sezione bianca e gialla con vetrate (modulare: campata da ~3 m ripetibile) | ≤ 4k | stesso atlante | Alta |
| `SM_Molo_Edificio_A4A5` | blocco sud con terrazza e ringhiera, facciata bianca verso il ponte | ≤ 5k | stesso atlante | Media |
| `SM_Molo_Edificio_C` | casa/ristorante sul molo, Y 25-42 | ≤ 4k | stesso atlante | Media |
| `SM_Molo_Tendone` | pergola metallica con telo scuro (B) | ≤ 1,5k | — | Media |
| `SM_Molo_TettoiaRighe_3m` | modulo di tettoia a righe blu-bianche con montanti e tende laterali | ≤ 1k | tenda a righe 1024 | Media |
| `SM_Molo_Ombrellone` (aperto/chiuso) | palo in legno, telo bianco | ≤ 1,2k ciascuno | 1024 | Bassa |
| `SM_Molo_Fioriera_Antracite` | vaso rettangolare + arbusto su card | ≤ 2k | 1024 | Media |
| `SM_Molo_Fioriera_PalmaNana` | vaso tondo bianco Ø 1 m + palma nana su card | ≤ 3k | 1024 | Media |
| `SM_Molo_Tavolino` + `SM_Molo_Sedia` | dehors | ≤ 400 + ≤ 600 | 1024 condivisa | Bassa (dipende da D8) |
| `SM_Molo_Lampione2Globi` | candelabro in ghisa ~7,2 m, due globi sovrapposti | ≤ 3k | riusa `MI_Morin_Ghisa`, `MI_Morin_Globo` | Alta (1 esemplare) |
| `SM_Molo_LampioneAlto` | palo liscio ~8,5 m del molo | ≤ 800 | — | Media |
| `SM_Albero_LatifogliaA/B` | grandi latifoglie da 15-20 m (platano), chioma a card | ≤ 10k ciascuna | 2048 | Alta (fanno lo sfondo della foto) |
| `SM_Morin_PinoDomestico` | pino a ombrello (1ª delle 2 varianti di pino ammesse) | ≤ 10k | 2048 | Media |
| Piccoli prop | new jersey, cestino, cartello rotondo generico, recinzione a rete da 2,5 m (masked) | ≤ 500 ciascuno | atlante 1024 | Bassa |
| Palme alte del molo | riuso `SM_Morin_PalmaA` (4-5 istanze) | — | — | Media |

Note: con questi budget gli edifici rientrano nel limite "edificio di fondale ≤ 5k", anche se sono vicini alla corsia.
Collisioni UCX a scatola su edifici, fioriere e tettoie; i dehors senza collisione oppure a box bassi (D8).
Le latifoglie non rientrano nelle categorie di vegetazione di CLAUDE.md §4 (palme, pini, cespugli): servono 2 varianti nuove,
da annotare nel log decisioni.
