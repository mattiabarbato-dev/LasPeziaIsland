# Zona parcheggio iniziale, chiosco e prato (X ≈ 9-140)

Scheda dalle foto aggiunte dall'utente il 2026-11-19 sera (tutte catture Google: **[SV]**, usabili anche per texture
secondo la deroga di CLAUDE.md §5, senza UI, persone, targhe né insegne reali).
Coordinate di progetto: X lungo la passeggiata verso NE, Y verso la città. [V] = OSM/schede esistenti, [F] = letto dalle foto, [S] = stima.

## Foto
| File | Cosa mostra |
|---|---|
| `ref/foto/vista/vista_dall_alto_2.png` | Vista aerea annotata dall'utente: ristoranti (SO) → parcheggio iniziale → chiosco → prato con alberelli; tra viale e mare: Viale Italia, passeggiata fra palme, banchina, pontili |
| `ref/foto/vista/parcheggio_iniziale.png` | Strada di servizio del parcheggio vista verso NE, con auto ai due lati, pini a sinistra e passeggiata con palme a destra |
| `ref/foto/vista/chiosco_con_ombrelloni_e_tavolini.png` | Chiosco-bar sotto le palme; scritta "Passeggiata Morin" sul pavimento |
| `ref/foto/vista/chiosco_con_ombrelloni_e_tavolini_2.png` | Dehors del chiosco: ombrelloni quadrati, fioriere |
| `ref/foto/vista/prato con alberelli.png` | Giardini a Mare verso Viale Italia: prato, oleandri ad alberello, panchina lunga, palazzi del viale |

## Struttura della zona (da SO a NE)
1. **Parcheggio iniziale** (X ≈ 9-90 [S], tra la passeggiata e Viale Italia, Y ≈ 102-120 [S])
   - Strada di servizio in asfalto scuro e consumato, con crepe e rattoppi [F]: continua il "ramo verso il parcheggio"
     di `ref/radice_molo.md` (Y ≈ 109). Strisce pedonali bianche all'imbocco [F].
   - Auto parcheggiate in linea ai due lati [F]. Nel gioco basta qualche auto generica, senza marchi né targhe.
   - Lato città: filare di **pini domestici** (Pinus pinea), chioma a ombrello e tronco inclinato, come in foto e in OSM
     (Y 113, X 18-85). Deciso dall'utente il 2026-11-20, che corregge l'indicazione "latifoglie" del 2026-11-19.
     Si usa `SM_Morin_PinoDomestico`, già importato.
   - Lato mare: cordolo in pietra chiara, poi la passeggiata [F].
   - Arredi: cartelli blu "P" e divieto di sosta su palo [F], new jersey in cemento sulla banchina [F],
     lampione con **due globi affiancati su bracci ricurvi** [F]. È un modello diverso da `SM_Molo_Lampione2Globi`,
     che ha i globi in verticale: da verificare.
2. **Passeggiata fra palme** (fascia larga tra il parcheggio e la banchina)
   - **Sempre e solo due filari di palme** (Phoenix canariensis) lungo tutta la passeggiata [V-utente 2026-11-19],
     come in `ref/sezione.md`. L'impressione di 3-4 file nella vista aerea è un effetto delle chiome.
   - Ogni palma sta in un'aiuola quadrata di terra (~2 m) bordata di pietra bianca [F].
   - Pavimento in **cubetti grigi posati ad archi** (coda di pavone), diviso in riquadri da fasce di pietra bianca [F].
   - Scritta **"Passeggiata Morin"** in grandi lettere bianche nel pavimento, vicino al chiosco
     [F; anche `ref/foto/pavimentazione/scritta_pavimento_*`].
   - Luci decorative (fili di lampadine) tra le palme [F]: dettaglio facoltativo.
3. **Chiosco-bar** (X ≈ 100, Y ≈ 106 [V], `ref/elementi.md`)
   - Pianta ~4 × 4 m [S]: corpo color crema, bancone vetrato con sgabelli.
   - Tettoia bianca sporgente su tutti i lati, con mantovana; insegna in rilievo sul tetto [F].
     Nel gioco va un **nome inventato** (CLAUDE.md §5).
   - Dehors ~10 × 8 m [S], verso NE: 3-4 **ombrelloni quadrati bianchi** (~4-5 m di lato), tavolini e sedie,
     **fioriere quadrate grigio scuro** con arbusti a delimitare il perimetro [F]. Lampioncino da giardino a lato [F].
4. **Prato con alberelli: Giardini a Mare** (da X ≈ 118 [V])
   - Prato verde con aiuole geometriche bordate di siepi basse (bosso) [F].
   - Lungo Viale Italia, **oleandri ad alberello** (fusto unico e chioma sferica) alternati **bianchi e rosa** [F],
     ogni ~5-6 m [S]. È il filare di oleandri di Y 119,5 [V].
   - Lungo il bordo del pavimento, verso il prato: **panchina lunga continua** in pietra bianca, con la seduta
     su piccoli pilastrini [F], lunga decine di metri [S].
   - Pennoni con bandiere [F]: facoltativi.
   - Fondale: palazzi d'epoca di Viale Italia, 5-6 piani, gialli, rosa e ocra, con persiane verdi [F], e colline dietro.
5. **Banchina e acqua**: banchina larga in pietra chiara; traghetti/battelli turistici bianchi e blu ormeggiati
   davanti al parcheggio [F]; pontili con barche [V].

## Nuovi asset candidati (priorità arte)
| Asset | Tipo | Note |
|---|---|---|
| `SM_Morin_Chiosco` + `SM_Morin_Ombrellone`, `SM_Morin_Fioriera`, tavolino/sedia | pezzo unico + prop istanziati | texture dal chiosco [SV] |
| `SM_Morin_OleandroAlberello` (2 varianti di colore) | vegetazione, card | rientra nei 2 cespugli ammessi |
| `SM_Morin_PanchinaLunga_Mod` | modulo ripetuto | pietra bianca |
| `SM_Parcheggio_Asfalto` + strisce + cartelli + auto generiche | suolo + prop | asfalto consumato [SV] |
| `T_Pav_CubettiArchi` | texture | cubetti a coda di pavone con fasce bianche |
| Palazzi di Viale Italia | fondale ≤ 5k tri | facciate gialle e rosa [SV] |

## Da verificare
- Larghezza della strada del parcheggio e posizione delle file di auto.
- Lampione a due globi affiancati: è lo stesso modello della passeggiata?
