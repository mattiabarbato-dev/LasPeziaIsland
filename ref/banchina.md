# Scheda — Banchina, bordo sull'acqua e pavimentazione (Blocco 1)

Legenda: **[V]** verificato (fonte citata) · **[S]** stima motivata, da confermare.
Scopo: riferimento per blender-artist per il kit `SM_Banchina_Mod4m`, testata, bitta, scaletta e per la pavimentazione
(CLAUDE.md §4: modulo banchina <= 2k tri, prop <= 4k, texture 2048 PBR con ORM).
Integra `sezione.md` (fasce, quota) ed `elementi.md` §2 (bitte, parapetti), che rimandano qui.
Fonti consultate il 2026-11-19. Google solo come riferimento visivo, niente salvato.
**Avviso:** in rete non ho trovato rilievi o capitolati della banchina. Quasi tutto il dettaglio costruttivo resta [S]
finché non arrivano le foto del §6.

## 0. Aggiornamento dalle foto dell'utente (2026-11-19, `ref/foto/banchina/`, `ref/foto/pavimentazione/`) — prevale sui §2-4

| Dato | Valore | Stato |
|---|---|---|
| Ciglio | blocchi lunghi di pietra **grigio chiaro**, lisci, faccia superiore **leggermente inclinata verso l'acqua**, spigolo arrotondato | [V foto utente] |
| Formato del blocco | ~1 m × ~0,5 m in pianta | [S] a occhio |
| Quota ciglio-acqua | **~0,6-1,0 m** (non 1,5 m) | [S] a occhio dalle foto. Il modulo usa 1,0 m; l'acqua UEFN oggi è a −1,5 m (vedi `docs/decisioni.md`) |
| Parapetto | **assente** | [V foto utente] |
| Bitta | piccola, scura, sul ciglio | presenza [V foto utente]; misure [S] |
| Paramento | muro in blocchi più scuro del ciglio | [S] (poco visibile nelle foto) |
| Camminamento lato mare | grandi **lastre rettangolari** di pietra (~40 × 60-80 cm), posa a correre, grigio-beige caldo | aspetto [V foto utente]; misure [S] |
| Fascia delle palme | **cubetti grigi** (porfido/sampietrini) posati ad archi ("coda di pavone"), riquadri divisi da fasce di pietra chiara larghe ~20-30 cm; panchine a lastra in pietra chiara | aspetto [V foto utente]; misure [S] |
| Lampioni | pali in ghisa scura decorati con globo bianco, ~4-5 m | aspetto [V foto utente]; altezza [S] |

## 1. Cosa è verificato

| Dato | Valore | Fonte |
|---|---|---|
| Ciglio | rettilineo a Y 80, la coastline coincide con il bordo dell'area pedonale | [V] OSM coastline 137121074, area 850396604 (`sezione.md`) |
| Superficie del camminamento | `surface=paving_stones`, **`smoothness=intermediate`** (fondo a elementi, non perfettamente liscio) | [V] OSM footway 238848819 |
| Cordolo lato palme | Y 89, h 0,20 m, con **pavimentazione tattile** | [V] OSM 850396603 |
| Banchina Thaon di Revel (radice del molo del ponte, nel Blocco 1) | cedimento della pavimentazione "in corrispondenza del dente di attracco"; la zona depressa **si allaga a ogni mareggiata**. Progetto AdSP: rialzo alle quote circostanti, nuova fondazione in **calcestruzzo armato su micropali** | [V] Città della Spezia, 15-05-2026 ([link](https://www.cittadellaspezia.com/2026/05/15/stop-agli-allagamenti-in-occasione-delle-mareggiate-la-banchina-tra-morin-e-revel-sara-consolidata-e-rialzata-654349/)) |
| Imbarcadero dei battelli (X ≈ 71) | pontile su **tubi d'acciaio infissi e riempiti di calcestruzzo**, impalcato su **travi d'acciaio con tavolato** in legno; 5 tratti da ~6 m (~30 m, coerente con i 28,9 m di OSM). Ristrutturazione da ~1 M€ prevista dopo la stagione turistica | [V] La Nazione, 11-01-2026 ([link](https://www.lanazione.it/la-spezia/cronaca/manutenzione-imbarcadero-b6s3sluw)). **Conflitto:** OSM lo tagga `floating=yes`, l'articolo descrive un pontile fisso su pali. Vale l'articolo |
| Bitte, anelli, scalette, parabordi | **non mappati** in OSM | [V] assenza nel dato OSM |

Conseguenza per la quota: una banchina che si allaga con le mareggiate è **bassa**. Il ciglio a ~1,0-1,5 m sul medio mare
è plausibile; la proposta di gioco (acqua a Z -1,5 m) resta valida [S].

## 2. Ciglio e paramento (faccia verso l'acqua)

| Elemento | Proposta | Stato |
|---|---|---|
| Quota del ciglio sul mare | **1,2-1,5 m** (gioco: 1,5 m) | [S] vedi §1 |
| Ciglio (cimasa) | blocchi di **pietra grigia** (granito o arenaria locale) o **cemento prefabbricato**, a correre | [S] |
| Dimensioni del blocco di ciglio | **~1,0-1,5 m** lungo × 0,5-0,6 m in pianta × 0,3-0,4 m di spessore; spigolo verso il mare smussato o arrotondato (r ~5 cm) | [S] valori tipici delle banchine storiche. Per il kit: blocco da **1,0 m** → 4 blocchi per modulo da 4 m |
| Aggetto del ciglio sul paramento | 5-10 cm | [S] |
| Paramento | muro verticale in blocchi di calcestruzzo o muratura di pietra, grigio, **scurito e con alghe/verde nella fascia di 30-40 cm sopra l'acqua** | [S] |
| Colore | ciglio grigio chiaro (valore ~0,55-0,65), paramento grigio medio, fascia di bagnasciuga verde-bruna | [S] |
| Parapetto sul ciglio | nessuno mappato: probabilmente ciglio libero | [S] **decide le cadute in acqua** |

## 3. Arredi d'ormeggio

| Elemento | Forma | Materiale e colore | Dimensioni | Passo | Stato |
|---|---|---|---|---|---|
| **Bitta** | "a fungo" (fusto cilindrico rastremato con testa più larga) o "a T" | ghisa, verniciata **nera** o grigio scuro, testa spesso consumata e lucida [S] | h **0,40-0,50 m**, Ø testa 0,30-0,40 m, piastra di base ~0,5 × 0,5 m incassata nel ciglio | **~10-15 m** sui tratti d'ormeggio (imbarco, X ≈ 50-90); forse assenti dove ci sono i pontili della marina | [S] |
| Anello d'ormeggio | anello in ferro Ø 15-20 cm su perno, nel ciglio o sul paramento | ferro arrugginito / nero | — | tra le bitte, ~5 m | [S] |
| Scaletta alla marinara | pioli in ferro incassati nel paramento, con maniglioni sul ciglio | acciaio zincato o verniciato | larghezza 0,4-0,5 m, dal ciglio fino a sotto il livello del mare | ~1 ogni 50 m [S]. **Nel gioco servono:** sono la risalita dall'acqua (CLAUDE.md §1, pilastro 3) | [S] |
| Parabordi | gomma nera (profili a D o cilindri) sul paramento, solo dove attraccano i battelli | gomma nera | profilo ~25-30 cm | solo X ≈ 55-90 | [S] |
| Colonnine acqua/luce | per le barche della marina, alla radice dei pontili | acciaio/plastica grigia | h ~1 m | ai pontili X 89-290 | [S] |

## 4. Pavimentazione del camminamento (Y 80-89) e della fascia palme

| Dato | Proposta | Stato |
|---|---|---|
| Tipo | elementi in pietra o masselli di cemento (`paving_stones`, smoothness intermediate) | tipo [V] OSM; materiale preciso [S] |
| Formato | **lastre rettangolari ~60 × 40 cm** (in alternativa masselli 20 × 10) | [S] |
| Posa | a correre, con i giunti lunghi **paralleli all'asse della passeggiata** | [S] |
| Colore | grigio chiaro-beige (pietra chiara), giunti scuri sottili | [S] (in `CLAUDE.md` §2.2 la "pietra chiara" è [V] dal livello di sezione) |
| Fascia lungo il ciglio | probabile corso di lastre più grandi o del ciglio stesso, larghezza 0,5-0,6 m | [S] |
| Lungo il cordolo Y 89 | striscia di **pavimentazione tattile** (rilievi a righe/bolle, grigia o gialla) | presenza [V] OSM; aspetto [S] |
| Strada sul molo (Banchina Thaon di Revel) | **pavé / cubetti** (`surface=sett`) | [V] OSM 183535303 |
| Griglia Fortnite | modulo 4 m (non multiplo di 5,12 m): lastre da 0,6 × 0,4 → 4 m = 6,67 lastre. Meglio texture che "chiude" su 4 m o su 2 m | nota di progetto |

## 5. Note per blender-artist
- Modulo dritto da 4 m: ciglio (4 blocchi da 1 m), paramento fino a Z -3 (sotto il pelo dell'acqua a -1,5),
  fascia di bagnasciuga come secondo materiale o vertex color, piastre delle bitte come decal o geometria minima.
- Bitta e scaletta come prop separati, istanziati: la bitta va bene a ~300-600 tri, la scaletta a ~500-1k.
- Collisione: UCX box per il blocco di ciglio e il muro; UCX cilindro basso per la bitta (si deve poter scavalcare: h 0,45 m
  supera il gradino massimo di 0,40 m di CLAUDE.md §3 → **segnalarlo a uefn-builder**, si salta, non si scavalca camminando).
- Texture e fonti: `ref/asset_fonti.md`.

## 6. Foto che servono all'utente (`ref/foto/`) — i dati restano [S] senza
1. **Bordo banchina di profilo**, dal camminamento, con una persona accanto e l'acqua visibile: quota del ciglio, parapetto sì/no.
2. **Ciglio dall'alto**, a piombo, con un piede o un oggetto noto: materiale, dimensione dei blocchi, smusso.
3. **Paramento verso l'acqua**, dal pontile d'imbarco (X ≈ 71) guardando la banchina: materiale del muro, fascia di alghe, parabordi.
4. **Una bitta da vicino**, con una scarpa accanto, più una foto di 2-3 bitte d'infilata (per il passo).
5. **Una scaletta** in acqua, se c'è; annotare dove (vicino a quale elemento: ancora, cannone, pontile).
6. **Pavimentazione in pianta**, a piombo, con un piede: formato, posa, colore delle lastre; e una foto della striscia tattile al cordolo.
7. Il **dente di attracco** alla radice del molo del ponte (zona che si allaga): forma e quota rispetto al camminamento.
