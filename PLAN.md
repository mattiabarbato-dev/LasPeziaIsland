# PLAN — Morin Rush (Passeggiata Costantino Morin)

Stato: `[ ]` da fare · `[~]` in corso · `[x]` fatto · `[!]` bloccato
Ogni fase ha un **cancello**: non si passa alla successiva finché non è superato.
Regole, paesaggio e metriche: vedi `CLAUDE.md`.

---

## Fase 0 — Riferimenti e verifica dei dati
Obiettivo: trasformare i dati [S] di CLAUDE.md in dati verificati per il Blocco 1.

- [x] (orchestratore) Creare `docs/CREDITS.md` e `docs/decisioni.md`
- [x] (geo-scout) Bounding box del Blocco 1 in lat/lon: ponte + ~250 m di passeggiata + testata Mirabello -> `ref/area.md`
      (bbox lat 44.09993-44.10433, lon 9.82337-9.82953; origine node OSM 10249190464; asse X a 41,3°)
- [x] (geo-scout) Orientamento e lunghezza reale della passeggiata; correggere i dati [S] del quadro generale
      (sezione "Quadro generale verificato" in `ref/area.md`; CLAUDE.md da aggiornare a cura dell'orchestratore)
- [~] (geo-scout) Scheda `ref/ponte.md`: lunghezza, larghezza impalcato, altezza e inclinazione dell'antenna,
      numero di stralli, eventuale parte mobile, materiali e colori. Ogni dato marcato V o S
      Nota: le antenne sono DUE da 35 m. Restano [S] l'inclinazione, il numero esatto di stralli e i parapetti: serve una foto laterale
- [~] (geo-scout) Scheda `ref/sezione.md`: larghezza di ogni fascia della sezione trasversale,
      altezza banchina sull'acqua, passo delle palme, tipo di pavimentazione, lampioni e panchine
      Nota: fasce [V] da OSM. Restano [S] il passo delle palme (proposta 9 m), la quota del ciglio (1,5 m) e i lampioni (non mappati)
- [~] (geo-scout) Scheda `ref/elementi.md`: battelli, bitte, parapetti, chioschi, monumenti nel Blocco 1
      Nota: posizioni [V]. Restano [S] le dimensioni del battello, le bitte e la presenza del parapetto sul ciglio
- [ ] (utente) Foto in `ref/foto/`: ponte (dall'imbocco, di lato, da sotto), pavimentazione in pianta,
      una palma intera, bordo banchina, un lampione, una panchina, vista d'insieme verso il ponte
- [x] (orchestratore) Aggiornare la sezione 2 di CLAUDE.md con i dati verificati (2.1, 2.2, riga ponte in 2.3)

**Cancello 0:** le tre schede esistono e nessun dato necessario al blockout è ancora [S] senza una stima motivata.

---

## Fase 1 — Scala e blockout (solo forme grigie)
Obiettivo: percorrere il Blocco 1 dall'inizio alla fine con volumi semplici, in scala.

- [x] (blender-artist) Cubo di test 1 m -> `exports/test/SM_Test_Cubo1m.fbx`
      (1×1×1 m, 12 tri, origine alla base, UCX incluso; sorgente `blender/test_scala.blend`)
- [x] (uefn-builder) Import del cubo, verifica 100 uu, preset annotato in `docs/scala.md`
      Giro 2 OK: `SM_Test_AssiCm` (FBX_SCALE_NONE + bake_space_transform=True) misura 100 uu, 36 tri, 1 collisione convessa
      100×100×100, nessuna mesh UCX. `SM_Test_Assi` (FBX_SCALE_ALL) misura di nuovo 1 uu: preset scartato.
      Attore `Test_AssiCm` in (2560, −2048, 0), cartella `Test`. Mappatura assi misurata: Blender +X → UE −Y, Blender +Y → UE −X
      (nessuno specchio). Regola: UE_X = −B_Y·100, UE_Y = −B_X·100, UE_Z = B_Z·100; yaw UE = −rotZ Blender.
- [x] (orchestratore) Decidere gli assi — DECISO 2026-11-18: preset giro 2 + rotazione −90° Z solo in export (giro 3 verificato in UEFN). Regola: UE_X = B_X·100, UE_Y = −B_Y·100, UE_Z = B_Z·100, yaw UE = −rotZ Blender. Prossimo: script di export (blender-artist).
  Storico: tenere la regola sopra oppure giro 3 con `axis_forward='X'` (ipotesi: Blender +X → UE +X,
      Blender +Y → UE −Y). Vedi "Decisione aperta" in `docs/scala.md`. Da chiudere prima dell'export del blockout
      Nota blender-artist (giro 3, sorgente `blender/test_assi.blend` non modificato, 36 tri + UCX 12 tri, 1,4 × 1,2 × 1 m):
      - `exports/test/SM_Test_AssiX.fbx` (preset con axis_forward='X', axis_up='Z'): vertici X −50..70 · Y −90..50 · Z 0..100 cm
        (= B_Y, −B_X), header Front=−X, Coord=−Y, Up=+Z, nessuna Lcl Rotation. Blender cambia insieme vertici e header, in modo coerente:
        l'importer UEFN converte dall'header (modello che riproduce il giro 2: target Z-up/front +X, poi Y negata), quindi la PREVISIONE è
        la stessa mappatura del giro 2 (B+X → UE −Y, B+Y → UE −X). L'ipotesi 'X' probabilmente NON funziona: da confermare in UEFN.
      - `exports/test/SM_Test_Assi_RotZm90.fbx` (CANDIDATO): preset del giro 2 (axis_forward='-Y') con mesh e UCX ruotati di −90° in Z
        solo durante l'export (Lcl Rotation Z = −90 nel file, vertici come AssiCm, .blend ripristinato). Previsione: B+X → UE +X,
        B+Y → UE −Y (obiettivo), sia col modello "header" sia col modello "scambio grezzo". Da importare e misurare in UEFN.
      Esito uefn-builder (giro 3, misurato in UEFN, dettagli in `docs/scala.md`):
      - `SM_Test_AssiX`: bounds X −70..50 · Y −90..50 · Z 0..100, 36 tri, 1 convesso ±50/0..100. Mappatura IDENTICA al giro 2
        (B+X → UE −Y, B+Y → UE −X): modello "header" confermato, `axis_forward='X'` non serve. Attore `Test_AssiX` (3072, −2048, 0).
      - `SM_Test_Assi_RotZm90`: bounds X −50..90 · Y −70..50 · Z 0..100, 36 tri, 1 convesso ±50/0..100. **B+X → UE +X, B+Y → UE −Y**
        (come previsto). Attore `Test_Assi_RotZm90` (3584, −2048, 0). Regola: UE = (B_X·100, −B_Y·100, B_Z·100), yaw UE = −rotZ Blender.
      - Preset raccomandato: preset giro 2 + rotazione −90° Z applicata solo in export, da automatizzare con uno script di export.
        In attesa della decisione dell'orchestratore.
      Storico giro 1 — KO: il cubo misura 1 uu (fattore 0,01). L'FBX ha UnitScaleFactor=100 con geometria in metri
      (FBX_SCALE_UNITS) e l'import MCP non converte le unità. Riesportare con FBX_SCALE_ALL e ripetere.
      Pivot, 12 tri e collisione UCX: OK. Da verificare anche una Lcl Rotation Z=180° negli oggetti. Dettagli in `docs/scala.md`
      Nota blender-artist (giro 2, sorgente `blender/test_assi.blend`, cubo asimmetrico `SM_Test_Assi`, 36 tri + UCX 12 tri):
      - `exports/test/SM_Test_Assi.fbx` (FBX_SCALE_ALL, come richiesto): letto dall'FBX è IDENTICO al giro 1
        (UnitScaleFactor=100, vertici in metri, Lcl Rotation 0,0,180). Con global_scale=1 FBX_SCALE_ALL = FBX_SCALE_UNITS: atteso di nuovo 1 uu.
      - `exports/test/SM_Test_AssiCm.fbx` (FBX_SCALE_NONE + bake_space_transform=True): UnitScaleFactor=1, vertici in cm
        (X -90..50, Y -70..50, Z 0..100), nessuna Lcl Rotation/Scaling. Candidato da importare per primo.
      - La rotazione 180° nasce dalla conversione assi axis_forward='-Y' (gli oggetti in Blender hanno rot 0 / scale 1);
        con bake_space_transform finisce nei vertici (X e Y negati). Da misurare in UEFN dove arrivano i marcatori +X (lungo) e +Y (corto).
- [ ] (blender-artist) Import OSM con Blosm del bounding box; fissare l'origine come da CLAUDE.md §3
- [ ] (blender-artist) Blockout: piano banchina, bordo, camminamento, fascia verde, volume del ponte
      (impalcato + antenna come scatole), testata Mirabello, edifici di fondale come blocchi
- [ ] (blender-artist) Segnaposto cilindrici per le palme al passo reale
- [ ] (blender-artist) Export del blockout in 3-4 FBX per zona -> `exports/blockout/`
- [ ] (uefn-builder) Import e posa; Water Body del golfo alla quota corretta; spawn alla partenza
- [ ] (uefn-builder) Barriere invisibili sul lato città e ai limiti del blocco
- [ ] (qa-tester) Prova di percorrenza: tempo partenza -> fine ponte, punti d'incastro, linea di vista
      sull'antenna, caduta in acqua. Report in `docs/qa/`

**Cancello 1:** si corre dalla partenza al fondo del ponte senza incastri; tempo misurato e annotato;
la scala "sembra giusta" con un personaggio accanto a parapetti e palme.

---

## Fase 2 — Prototipo di gioco (ancora su blockout)
Obiettivo: la corsa è divertente prima di essere bella.

- [ ] (utente) Confermare o cambiare la modalità proposta (corsa a tempo con ancore dorate)
- [ ] (verse-dev) Documento breve `docs/gameplay.md`: regole, condizioni di vittoria, device usati
- [ ] (uefn-builder) Partenza con conto alla rovescia, 3-4 checkpoint, traguardo a fine ponte
- [ ] (uefn-builder) 10-15 collezionabili: facili sulla corsia, difficili su battelli e fascia verde
- [ ] (verse-dev) Logica: timer, conteggio ancore, rientro da caduta in acqua entro 3 s, classifica finale
- [ ] (uefn-builder) Almeno una scorciatoia rischiosa (salto sui battelli) e una deviazione sicura
- [ ] (qa-tester) 5 corse complete: durata, punti morti, chiarezza del percorso. Report con proposte

**Cancello 2:** una corsa dura 60-90 s, il percorso si capisce senza spiegazioni, l'utente dice che è divertente.

---

## Fase 3 — Arte del Blocco 1
Obiettivo: sostituire il grigio con asset definitivi, uno alla volta, senza rompere il gioco.
Ordine per impatto visivo:

- [ ] (blender-artist) **Ponte Thaon di Revel** da `ref/ponte.md`: impalcato, antenna, stralli, parapetti
- [ ] (blender-artist) Kit banchina: modulo dritto 4 m, testata, bitta, scaletta
- [ ] (blender-artist) Palma A + 2 varianti (prima cercare su Poly Haven / Poly Pizza, poi modellare)
- [ ] (blender-artist) Kit pavimentazione e cordoli; materiali da Poly Haven
- [ ] (blender-artist) Arredi: lampione, panchina, cestino, parapetto
- [ ] (blender-artist) Battello turistico stilizzato, senza marchi reali
- [ ] (blender-artist) Pini, oleandri, aiuole della fascia verde
- [ ] (blender-artist) Fondale: sagome di edifici e colline
- [ ] (uefn-builder) Sostituzione progressiva del blockout; palme e arredi come istanze
- [ ] (uefn-builder) Luce del tardo pomeriggio, cielo, nebbia leggera sul golfo
- [ ] (uefn-builder) Audio ambientale: gabbiani, acqua, sartie
- [ ] (qa-tester) Dopo ogni sostituzione importante: collisioni e percorrenza invariati

**Cancello 3:** nessun volume grigio visibile nel Blocco 1; il ponte è riconoscibile dalla partenza.

---

## Fase 4 — Ottimizzazione
- [ ] (blender-artist) Collisioni UCX_ su tutti gli asset; verifica budget triangoli
- [ ] (uefn-builder) Controllo "Dimensioni del progetto" e calcolo della memoria
- [ ] (qa-tester) Profilazione con unreal-insights; elenco dei 5 asset più pesanti
- [ ] (blender-artist) Riduzione degli asset segnalati

**Cancello 4:** memoria dentro i limiti di UEFN con margine per i blocchi 2 e 3.

---

## Fase 5 — Rilascio del Blocco 1
- [ ] (orchestratore) `docs/CREDITS.md` completo (OSM, Poly Haven, autori CC-BY)
- [ ] (orchestratore) Controllo finale: nessun dato Google, nessun marchio reale, nessun volto nelle texture
- [ ] (utente) Caricamento in versione privata e prova con amici
- [ ] (utente) Decisione: pubblicare o proseguire con i blocchi successivi

---

## Dopo l'MVP
- [ ] Blocco 2: tratto centrale e imbarco battelli (ripetere Fasi 0-4 sul nuovo blocco)
- [ ] Blocco 3: Molo Italia e faro rosso come finale esteso
- [ ] Modalità aggiuntive: nascondino tra i giardini, gara a squadre

---

## Log decisioni
| Data | Decisione | Motivo |
|---|---|---|
| 2026-11-18 | Soggetto: Passeggiata Morin invece di Piazza Verdi | Scelta dell'utente |
| 2026-11-18 | Primo blocco: ponte + ~250 m | Tratto più riconoscibile, dimensione gestibile |
| 2026-11-18 | Stile Fortnite stilizzato, niente fotogrammetria | Licenze, prestazioni, coerenza visiva |
| 2026-11-18 | Export FBX con `FBX_SCALE_NONE` + `bake_space_transform=True` | Unico preset che dà 1 m = 100 uu con l'import MCP (test di scala, giro 2) |
