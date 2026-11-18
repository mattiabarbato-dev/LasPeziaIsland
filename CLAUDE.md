# Progetto: Passeggiata Morin — isola Fortnite (UEFN)

Ricostruzione giocabile della **Passeggiata Costantino Morin**, il lungomare di La Spezia.
Non è una copia fotografica: è una versione **stilizzata e riconoscibile**, in cui uno spezzino
dice "è la Morin" al primo sguardo e un giocatore qualsiasi trova un livello leggibile e divertente.

Pipeline: OpenStreetMap -> Blender (Blosm + MCP `blender`) -> FBX -> UEFN (MCP `unreal-mcp`) -> Verse.
Stato e task: vedi `PLAN.md`. Lingua di lavoro: italiano.

---

## 1. Visione di gioco

**Titolo di lavoro:** *Morin Rush*
**Fantasia del giocatore:** una corsa al tramonto sul lungomare, tra palme, traghetti e il ponte bianco.
**Modalità (MVP):** corsa a tempo con collezionabili, 1-8 giocatori.
Si parte dal lato città, si raccolgono le *ancore dorate* sparse lungo la passeggiata e si taglia
il traguardo in fondo al Ponte Thaon di Revel. Vince chi arriva prima con tutte le ancore.
La modalità è una proposta: l'utente può cambiarla in Fase 2 senza rifare il livello.

### Pilastri di design (in caso di dubbio, decidono loro)
1. **Riconoscibilità prima del realismo.** Contano la sagoma del ponte, il filare di palme,
   il bordo banchina sull'acqua. Un dettaglio che nessuno nota non vale i suoi poligoni.
2. **Leggibilità del percorso.** Il giocatore deve sempre capire dove andare: il ponte è il faro
   visivo, visibile da ogni punto del tracciato.
3. **Flusso senza intoppi.** Niente spigoli che incastrano, niente collisioni invisibili sorprendenti,
   nessun punto senza uscita. Se si cade in acqua si rientra subito in gioco.
4. **Leggero.** Deve girare su mobile e Switch. Pochi asset riusati molte volte.

---

## 2. Il paesaggio

Legenda: **[V]** verificato da fonte · **[S]** stima o ricordo da confermare con geo-scout e foto in `ref/`.
Nessun agente deve trattare un dato [S] come certo: prima si verifica, poi si modella.

### 2.1 Quadro generale
- [V] Lungomare pedonale che costeggia il golfo, delimitato da palme, pini e oleandri.
- [V] All'estremità sud-ovest il **Ponte Thaon di Revel**, pedonale, ~160 m tra le spalle (176 m totali),
  inaugurato nel 2013, collega la passeggiata a **Porto Mirabello**. Non prosegue la passeggiata in linea:
  parte ad angolo retto (~92°) e va verso sud-est, preceduto da un molo d'accesso di ~86 m. Dettagli in `ref/ponte.md`.
- [V] All'estremità opposta (nord-est) il **Molo Italia**, percorribile fino a un piccolo **faro rosso**.
  Il molo ha due rami: il primo ortogonale alla banchina (284 m), il secondo ad angolo di ~136°.
- [V] Sul lato città corrono i **Giardini a Mare**, estensione dei giardini pubblici storici.
- [V] Dalla banchina partono i battelli per le Cinque Terre. Tra il ponte e l'imbarco (X ~89-290 m)
  l'acqua è occupata da pontili con yacht di un porticciolo turistico.
- [V] Viale Italia corre tra Giardini a Mare e Giardini pubblici; la cortina di edifici è 120-210 m dietro la banchina.
- [V] Passeggiata lunga 551 m, asse con azimut 41,3° (sud-ovest → nord-est), mare a sud-est. Fonte: OSM, `ref/area.md`.

### 2.2 Sezione trasversale (dal mare verso la città)
È la "ricetta" del livello: ogni tratto della passeggiata ripete queste fasce.
1. **Acqua del golfo** — calma, portuale, niente onde. Water Body nativo di UEFN.
Misure da `ref/sezione.md` (Y dall'origine verso la città, ±0,5 m).
1. **Acqua del golfo** — calma, portuale, niente onde. Water Body nativo di UEFN.
2. **Bordo banchina** (Y 80) — ciglio rettilineo in pietra, salto di ~1,5 m sull'acqua [S],
   bitte in ghisa ~0,45 m ogni ~12 m [S], scalette [S], parapetto presunto assente [S].
3. **Fascia di ormeggio** — battelli turistici (~30-35 × 7 m [S]) e yacht ai pontili [V]: nel gioco
   piattaforme opzionali su cui saltare (scorciatoie rischiose).
4. **Camminamento principale** (Y 80-89, ~9 m [V]) — lastre di pietra chiara [V], pianeggiante.
   È la corsia di gara: deve restare sgombra per almeno 8 m di larghezza. Cordolo 0,20 m a Y 89.
5. **Filare di palme** (Y 89-102, 13 m [V]) — due filari a Y 92,6 e 99,6 [V], passo ~9 m [S].
6. **Fascia verde / Giardini a Mare** (Y 102-116, 14 m [V]) — aiuole, oleandri (Y ~119,5), panchine,
   lampioni (~ogni 20-25 m, 4-5 m [S]). Nel gioco: percorso alternativo più lento ma con più collezionabili.
7. **Limite lato città** — Viale Italia (Y ~121-139 [S]), ciclabile, Giardini pubblici da Y 145 [V],
   edifici a 120-210 m: solo fondale, non giocabile.

### 2.3 Punti di riferimento (landmark)
| Landmark | Ruolo nel gioco | Priorità | Note |
|---|---|---|---|
| Ponte Thaon di Revel | Traguardo e faro visivo | **Massima** | [V] strallato, **due antenne** bianche alte 35 m s.l.m., acciaio bianco, calpestio in legno, impalcato 3,6 m, tratto apribile 18 m. [S] inclinazione antenne, n. stralli: vedi `ref/ponte.md` |
| Filare di palme | Ritmo del percorso, identità | Alta | Un solo asset palma + 2 varianti, istanziato |
| Bordo banchina + bitte | Limite leggibile mare/terra | Alta | Modulare, pezzi da 4 m |
| Battello Cinque Terre | Piattaforma / scorciatoia | Media | Sagoma semplice, 1-2 esemplari |
| Porto Mirabello | Zona d'arrivo oltre il ponte | Media | Solo la testata d'arrivo; yacht come fondale |
| Molo Italia + faro rosso | Blocco 3, finale esteso | Bassa (dopo MVP) | Il faro è un ottimo secondo faro visivo |
| Giardini, monumento a Garibaldi | Fondale lato città | Bassa | [V] il monumento è nei giardini pubblici; posizione esatta da verificare |

### 2.4 Atmosfera e direzione artistica
- **Ora del giorno:** tardo pomeriggio, luce calda radente da ovest, ombre lunghe delle palme sul camminamento.
- **Palette:** blu-verde del golfo, bianco del ponte, verde scuro di palme e pini, pietra chiara
  della pavimentazione, accenti rossi (faro, salvagenti) e oro (collezionabili).
- **Stile:** quello di Fortnite. Forme pulite e un po' esagerate, texture semplici, niente
  fotogrammetria né texture fotografiche sporche. Le foto servono per proporzioni e colori.
- **Sfondo:** colline del golfo e profilo della città come sagome a bassa risoluzione [S].
- **Audio (Fase 3):** gabbiani, sciabordio, sartie che battono sugli alberi delle barche.

### 2.5 Suddivisione in blocchi
Si costruisce un blocco alla volta; un blocco si chiude solo quando è giocabile.
- **Blocco 1 (MVP):** Ponte Thaon di Revel + circa 250 m di passeggiata adiacente + testata Mirabello.
- **Blocco 2:** tratto centrale della passeggiata con l'imbarco dei battelli.
- **Blocco 3:** Molo Italia e faro rosso.
- **Fondale:** giardini, Viale Italia e cortina edilizia, sempre e solo come sagome.

---

## 3. Metriche di level design

- **Scala reale 1:1** come base: 1 m = 100 unità Unreal (uu). Blender lavora in metri.
- **Origine (0,0,0):** imbocco del ponte lato passeggiata, a quota camminamento. X lungo la passeggiata
  verso nord-est, Y verso la città, Z in alto. Stessa origine in Blender e in UEFN.
- **Griglia Fortnite:** cella 512 uu, parete 384 uu. Dove possibile allineare moduli di banchina
  e pavimentazione a multipli di 512 uu, così i giocatori possono costruire senza scalini strani.
- **Dimensioni giocabili:** corsia libera >= 8 m; passaggi secondari >= 3 m; nessun gradino
  superiore a 40 cm senza rampa; parapetti alti almeno 1 m dove non si deve cadere.
- **Larghezza del ponte:** se quella reale risulta sotto i 4 m, allargarla nel gioco fino a 5-6 m.
  È una deroga voluta alla scala reale (pilastro 3): annotarla nel log decisioni.
- **Durata obiettivo di una corsa:** 60-90 secondi per il Blocco 1. La misura qa-tester;
  se è troppo corta si aggiungono deviazioni, non si allunga la geometria.
- **Linea di vista:** dalla partenza si deve vedere l'antenna del ponte. Nessun asset la copre.
- **Acqua:** chi cade viene riportato all'ultimo checkpoint entro 3 secondi.

---

## 4. Regole tecniche

- **Server MCP:** `blender` (Blender), `unreal-mcp` (editor UEFN), `unreal-insights` (profilazione).
  Prima di usarli verifica che rispondano; se no, FERMATI e chiedi all'utente di aprire l'applicazione.
  Un solo agente alla volta per server.
- **Cartelle:** `ref/` riferimenti · `blender/` file .blend · `exports/` FBX finali ·
  `docs/` note, QA, `CREDITS.md` · `PLAN.md` stato.
- **Naming:** `SM_` mesh, `M_` materiali, `T_` texture, `UCX_<Mesh>_00` collisioni.
  Prefisso di zona: `SM_Morin_PalmaA`, `SM_Ponte_Antenna`, `SM_Banchina_Mod4m`.
- **Modularità:** banchina, pavimentazione, parapetti, lampioni e panchine sono moduli riusati.
  Pezzo unico solo per: ponte, battello, faro.
- **Budget triangoli:** ponte completo <= 30k · battello <= 8k · palma <= 1,5k · modulo banchina <= 500 ·
  prop <= 1k · edificio di fondale <= 2k. Riporta sempre il conteggio a fine task.
- **Vegetazione:** massimo 3 varianti di palma, 2 di pino, 2 di cespuglio; sempre istanziate.
- **Texture:** 2048 px per il ponte, 1024 px per il resto, 512 px per il fondale. PNG o JPG.
- **Collisioni:** solo box o convessi semplici (UCX_). Mai collisione per-poligono.
- **Acqua:** Water Body nativo di UEFN, a cura di uefn-builder. Niente mesh d'acqua da Blender.
- **Export FBX:** Selected Objects, Apply Scalings **"FBX Units Scale: None"** (`FBX_SCALE_NONE`),
  Scale 1.0, **Apply Transform attivo** (`bake_space_transform=True`), Apply Modifiers, Embed Textures,
  Path Mode Copy. Mai `FBX_SCALE_UNITS` né `FBX_SCALE_ALL`: lasciano i vertici in metri e in UEFN
  l'asset arriva 100 volte più piccolo. Assi: `axis_forward='-Y'`, `axis_up='Z'` **più rotazione −90° in Z
  applicata solo durante l'export** (poi ripristinata nel .blend). Risultato verificato: Blender +X → UE +X,
  Blender +Y → UE −Y (Left in LUF), Z → Z. Cambiare `axis_forward` non serve: UEFN riconverte dall'header.
  Dettagli e regola posizione/yaw in `docs/scala.md`.
  Un FBX per asset o per kit modulare in `exports/<zona>/`.
- **Test di scala obbligatorio** prima di ogni altra cosa: cubo da 1 m -> deve misurare 100 uu in UEFN.

---

## 5. Licenze

- OpenStreetMap (ODbL): ok, con "© OpenStreetMap contributors" in `docs/CREDITS.md`.
- Poly Haven (CC0): ok. Poly Pizza: verifica la licenza di ogni modello; se CC-BY, cita l'autore.
- Google Maps / Earth / Street View / 3D Tiles: **solo riferimento visivo**. Mai geometrie o texture
  Google in `blender/` o `exports/`.
- Foto scattate dall'utente in `ref/foto/`: libere, ma senza persone riconoscibili né targhe nelle texture.
- Niente loghi o marchi reali (compagnie di navigazione, bar, insegne): nomi e grafiche inventati.

---

## 6. Regole di sicurezza

- Non cancellare attori in UEFN né file in `blender/` o `exports/` senza conferma esplicita.
- Non pubblicare e non caricare versioni private dell'isola: lo fa solo l'utente.
- Salva il .blend prima di operazioni distruttive; chiedi un commit Git prima di modifiche estese in UEFN.
- Se un dato [S] è necessario per proseguire e non è verificabile, fermati e chiedi una foto o una misura.

---

## 7. Come lavora il team

L'orchestratore (sessione principale) legge `PLAN.md`, assegna un task alla volta ai subagent
in `.claude/agents/` e controlla il risultato prima di segnarlo come fatto.

| Agente | Fa | Non fa |
|---|---|---|
| geo-scout | Dati OSM, misure, verifica dei dati [S], schede in `ref/` | Non tocca Blender né UEFN |
| blender-artist | Modelli, kit modulari, collisioni, export FBX | Non modella senza scheda di riferimento |
| uefn-builder | Import, posa, acqua, luci, device | Non scrive Verse |
| verse-dev | Logica di gara, checkpoint, punteggio | Non sposta geometria |
| qa-tester | Sessioni di prova, misure, report in `docs/qa/` | Non corregge: segnala |

**Definizione di "fatto"** per ogni task: rispetta budget e naming, è verificato nell'applicazione
(non solo dichiarato), `PLAN.md` è aggiornato, eventuali deroghe sono nel log decisioni.
A fine task ogni agente riporta: cosa ha prodotto, numeri (dimensioni, triangoli), problemi aperti.
