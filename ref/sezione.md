# Scheda — Sezione trasversale della Passeggiata Morin (Blocco 1)

Legenda: **[V]** verificato (fonte citata) · **[S]** stima motivata, da confermare.
Metodo: 8 transetti perpendicolari all'asse (azimut 41,3°) a 20, 60, 100, 150, 200, 250, 300 e 400 m dall'angolo
del ponte. Per ogni transetto ho calcolato l'intersezione con le way OSM: coastline 137121074, footway 238848819
e 1198056664, filari 378875629/378875631/850396605/850406862, area pedonale 850396604, parco 850396610,
Viale Italia, Giardini pubblici 107277712, kerb 850396603.
Le misure sono **stabili entro ±0,5 m su tutti i transetti**. La geometria OSM è molto regolare: è stata
disegnata a mano, probabilmente su ortofoto. © OpenStreetMap contributors.
Y = coordinata progetto (vedi `area.md`), misurata dalla perpendicolare alla passeggiata passante per l'origine.

## 1. Fasce dal mare verso la città

| # | Fascia | Da Y | A Y | Larghezza | Contenuto | Stato |
|---|---|---|---|---|---|---|
| 1 | Acqua del golfo | — | 80,0 | — | Specchio portuale. Davanti a X 89-290 c'è il porto turistico Assonautica, con pontili | [V] OSM |
| 2 | Bordo banchina | 80,0 | 80,0 | ciglio | Ciglio rettilineo (coastline + bordo area pedonale coincidono) | [V] OSM |
| 3 | Fascia d'ormeggio | (nell'acqua) | < 80 | — | Pontile galleggiante d'imbarco a X ≈ 71 (lungo 28,9 m), pontili della marina da X ≈ 89 | [V] OSM, vedi `elementi.md` |
| 4 | **Camminamento principale** | 80,0 | 89,0 | **≈ 9,0 m** | Asse della footway "Passeggiata Costantino Morin" a Y ≈ 86, lit=yes, surface=paving_stones | [V] OSM |
| 4a | Cordolo | 89,0 | 89,0 | — | **kerb alto 0,20 m**, con pavimentazione tattile, da X 12 a X 558 | [V] OSM way 850396603 (height=0.2) |
| 5 | **Fascia delle palme** | 89,0 | 102,0 | **≈ 13,0 m** | **Due filari di palme**: fila 1 a Y ≈ 92,6, fila 2 a Y ≈ 99,6, distanti 7,0 m. Tra le file corre una seconda footway (Y ≈ 96, da X ≈ 190). Ci sono anche panchine, rastrelliere e pensilina | [V] OSM |
| 6 | **Giardini a Mare** (fascia verde) | 102,0 | 116,0 | **≈ 14,0 m** | Aiuola "leisure=park" da X ≈ 118. Per X < 118: pini (filare Pinus pinea a Y 113, X 18-85), bagni, chiosco, parcheggio | [V] OSM |
| 6a | Filare di oleandri | 119,5 | 119,5 | — | Oleandri lungo il bordo del viale, da X 131 a X 556 | [V] OSM way 850406862 |
| 7 | **Viale Italia** | ~121 | ~139 | ~18 m | 4 corsie su due carreggiate a senso unico (assi a Y ≈ 128 e ≈ 135) | assi [V] OSM; bordi [S] |
| 7a | Pista ciclabile "Linea 5 - Italia" | ~140 | ~142,5 | 2,5 m | lato città del viale | [V] OSM (width=2.5) |
| 8 | Giardini pubblici (fondale) | 145 | 194-294 | 50-150 m | Parco storico: monumento a Garibaldi, Palco della Musica, giostra | [V] OSM |
| 9 | Cortina edilizia (fondale) | ~206 | — | — | Edifici lungo Viale Mazzini (Y 206-242, X 178-308) | [V] OSM |

Totale **banchina pedonale** (fasce 4+5) dal ciglio al giardino: **22 m** [V].
La corsia libera di gara (fascia 4, ~9 m) rispetta il minimo di 8 m di CLAUDE.md §3 **senza allargamenti**.

### Tratto iniziale (X 9 → ~20) e molo del ponte
- Il molo d'accesso al ponte è largo **~21 m** (X da -11 a +10) e lungo ~162 m (Y da +72 a -90) [V OSM].
  Sul molo corre la strada di servizio "Banchina Thaon di Revel" (way 183535303, surface=sett, accesso con permesso), in pavé.
- Sul lato SW del molo (X -12 … -21, Y 1 … 87) c'è una fila di edifici bassi: ristorante, pescheria,
  gastronomia, bagni. Oltre la recinzione c'è l'area militare [V OSM].

## 2. Altezza della banchina sull'acqua

| Voce | Valore | Stato |
|---|---|---|
| Quota del ciglio sul livello medio del mare | **~1,5 m** (intervallo plausibile 1,2-1,8 m) | [S] Valore tipico delle banchine portuali liguri; l'escursione di marea nel Golfo è di soli ~30 cm. Nessun dato in OSM |
| Nel gioco | ciglio a Z = 0, Water Body a **Z = -1,5 m** (-150 uu) | [S] proposta |

## 3. Passo delle palme

| Voce | Valore | Stato |
|---|---|---|
| Specie | Phoenix dactylifera ("palma da datteri") secondo i tag OSM | [V] OSM species. **Possibile errore di mappatura**: sui lungomari liguri è molto diffusa anche *Phoenix canariensis* (tronco più grosso, chioma più piena). Verificare in foto |
| Numero di filari | **2**, paralleli, distanti **7,0 m** | [V] OSM |
| Lunghezza dei filari | 536 m e 535 m (da X ≈ 20 a X ≈ 557) | [V] OSM |
| **Passo lungo il filare** | **~9 m** (proposta), quindi ~60 palme per fila e ~27 per fila nel Blocco 1 (X 20 → 260) | **[S]** OSM non mappa gli alberi singoli (natural=tree assente), quindi il passo non si può calcolare. 8-10 m è l'interasse tipico dei filari di Phoenix adulte |
| Disposizione tra le file | allineata o sfalsata: **non nota** | [S] |
| Altezza palma | 8-12 m di stipite, chioma di ~6-8 m di diametro | [S] |

## 4. Pavimentazione

| Superficie | Materiale | Stato |
|---|---|---|
| Camminamento e banchina pedonale | **masselli / lastre** (surface=paving_stones) | [V] OSM ways 238848819, 850396604 |
| Strada sul molo (Banchina Thaon di Revel) | **pavé / cubetti** (surface=sett) | [V] OSM way 183535303 |
| Ponte | legno | [V] OSM |
| Colore e formato delle lastre | pietra chiara, lastre rettangolari posate a correre | [S] da verificare con foto in pianta |

## 5. Lampioni e panchine

| Voce | Valore | Stato |
|---|---|---|
| Illuminazione | footway principale lit=yes | [V] OSM |
| Lampioni singoli | **non mappati** in OSM nel Blocco 1 | — |
| Passo dei lampioni (proposta) | 1 ogni ~20-25 m, sul lato giardino della corsia (Y ≈ 89-90) | [S] |
| Altezza / tipo | palo da ~4-5 m, testa singola | [S] **foto di un lampione** |
| Panchine pensilina (X 32-64, Y 92-94) | **7 panchine in pietra**, con e senza schienale, attorno alla pensilina | [V] OSM nodes 5913662680…5913663088, material=stone |
| Panchine fascia palme (X 256-288, Y 92-93) | 4 panchine senza schienale | [V] OSM |
| Dimensioni panchina | ~2,0 × 0,6 m, seduta a 0,45 m | [S] |
| Cestini | X 18 e X 42, Y ≈ 91-92 | [V] OSM |
| Rastrelliere bici | 7 rastrelliere da 8-10 posti, a Y ≈ 89-93, X 59-185 | [V] OSM |

## Da verificare con foto o misura dell'utente
1. **Passo delle palme** e disposizione tra le due file (allineata o sfalsata): foto d'insieme del filare. Basta contare le palme tra due riferimenti noti.
2. **Specie della palma** (dactylifera o canariensis): foto di una palma intera.
3. **Altezza del ciglio sull'acqua**: foto del bordo banchina con un riferimento, come una persona o una bitta.
4. Cosa separa il camminamento dalla fascia delle palme oltre al cordolo da 20 cm (aiuole, griglie, sedute): foto in pianta.
5. Tipo, altezza e passo dei lampioni: foto di un lampione.
6. Formato e colore della pavimentazione: foto in pianta.
