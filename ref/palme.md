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
