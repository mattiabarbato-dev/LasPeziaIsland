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
- [x] (blender-artist) Script di export `blender/scripts/morin_export.py` (preset giro 3: FBX_SCALE_NONE + bake_space_transform,
      −Y/Z, Rz(−90°) solo in export con ripristino try/finally; modi `asset`/`scene`, UCX automatici, controlli, report tri/budget/bbox).
      Verifica 2026-11-18 su `blender/test_assi.blend` (non salvato): `exports/test/SM_Test_Assi_Script.fbx` (13 772 byte, 36 tri + UCX 12)
      uguale a `SM_Test_Assi_RotZm90.fbx` per header, UnitScaleFactor=1, vertici (diff 0,0) e Lcl Rotation (−89,999989° vs −90,000009°).
      Matrici, selezione e attivo ripristinati; is_dirty False/False. Rifiuta l'asset con origine spostata senza toccare nulla. Uso in `docs/scala.md`
- [x] (uefn-builder) Pulizia UEFN 2026-11-18 (confermata dall'utente): rimossi i 4 attori della cartella Outliner `Test`
      e i 5 asset `SM_Test_*` + cartella `LaSpezia/Test` (referencer verificati: solo gli attori di test). Livello salvato,
      24 attori restanti invariati (template: GridPlane 1-4, spawn pad, PlayerStart, IslandSettings, DaySequence...), log senza errori.
      FBX in `exports/test/` non toccati.
- [x] (blender-artist) Import OSM con Blosm del bounding box; fissare l'origine come da CLAUDE.md §3
      2026-11-18, `blender/blockout_blocco1.blend` (Metric, scale 1.0). Bbox esteso lat 44.09906-44.10539, lon 9.82159-9.83045,
      .osm scaricato da Overpass (online access di Blender disattivato, non toccato) e importato con Blosm da file, 3Dsimple, singleObject off.
      Proiezione TM centrata sul node 10249190464 (scene lat/lon impostati prima dell'import), quindi traslazione 0; Empty `OSM_Root`
      con rotZ −48,7°, genitore dei 13 empty di layer; tutto in collezione `OSM_Riferimento` (way_profiles nascosta).
      393 oggetti (139 edifici, 1 coastline, 5 vegetazione, 3 aree pedonali, 245 curve strade/percorsi), ~5,3k tri valutati. SOLO riferimento, non esportare.
      Verifiche: way ponte (0,0)→(−5,2; −178,9), pennoni (−2,3; −80,2) e (−3,8; −128,5); ciglio coastline Y 80,5→79,1 da X 19 a 549
      (−0,15°), bordo area pedonale Y 80,0 da X 0 a 561, footway Morin (9,0; 85,9)→(560,6; 85,4); radice molo NE e punta molo entro 0,5 m.
      Nota: nell'import non ci sono pontili (man_made=pier) né filari/alberi; i 5 poligoni di vegetazione sono anonimi. Le curve stanno a Z +0,3 (offset Blosm).
      La coastline è una sola mesh a soli spigoli, estesa ~5 km (way intera).
- [x] (blender-artist) Blockout: piano banchina, bordo, camminamento, fascia verde, volume del ponte
      (impalcato + antenna come scatole), testata Mirabello, edifici di fondale come blocchi
      2026-11-18, `blender/blockout_blocco1.blend`, collezione `Blockout` (sotto-collezioni Passeggiata, Ponte, Mirabello, Fondale,
      Asset, Palme_Istanze). Camminamento a Z 0, lastre fino a Z −3, cordolo 0,2 m a Y 89, Giardini a Mare con aiuole 0,3-0,4 m,
      vialetto da 4 m e 4 varchi da 4 m, siepe limite 1,5 m a Y 116-118. Ponte: impalcato 6 m (8 m agli anelli), rampa Y 0→−70 al 6,1 %,
      calpestio Z 4,3 da Y −70 a −136,1, discesa al 7 % fino a Z 1,30 a Y −179, parapetti 1,1 m, 2 antenne fino a Z 33,5.
      Mirabello: rampa al 7 % al posto della scala (Z 0 a Y −197,5), testata 30 × 49,4 m a Z 0. Quote [S] e scelte in `docs/decisioni.md`.
      Linea di vista da (240, 84, 1,8): entrambe le antenne libere da Z 10 a 33 (raycast + camera `CAM_Partenza`).
      Da verificare in UEFN: con bCombineMeshes gli UCX_ di più mesh nello stesso FBX devono diventare tutti collisione.
- [x] (blender-artist) Segnaposto cilindrici per le palme al passo reale
      `SM_Blockout_PalmaSegnaposto` (Ø 0,5 × 9 m + chioma 6 m a Z 8-10, 38 tri, UCX tronco). 53 istanze collegate (passo 9 m [S],
      filari sfalsati) in `Blockout_Palme_Istanze`, non esportate; posizioni UE in `exports/blockout/palme_posizioni.csv`
- [x] (blender-artist) Export del blockout in 3-4 FBX per zona -> `exports/blockout/`
      Con `morin_export.py`: Passeggiata 121 tri, Ponte 408, Mirabello 58, Fondale 517 (mode scene), PalmaSegnaposto 38 (mode asset).
      Primo uso del mode scene verificato leggendo gli FBX: bbox in uu ricostruita dal file = bbox prevista per tutti e 5 (UnitScaleFactor 1,
      Lcl Rotation Z −90, Translation 0)
- [x] (uefn-builder) Import e posa; Water Body del golfo alla quota corretta; spawn alla partenza
      2026-11-18, dettagli in `docs/uefn_blockout.md`. 5 asset in `LaSpezia/Blockout`, bbox = attese (±1 uu), tri 121/408/58/517/38,
      convessi 13/34/5/53/1 = numero di UCX (con più mesh per FBX li prende tutti). Nanite già off; LOD auto rimosse (solo LOD0,
      altrimenti su mobile si vedeva LOD2 dimezzata). 4 attori in `Blockout` a (0,0,0); palme = 1 attore HISM con 53 istanze
      (campioni 0/26/52 = CSV). Acqua: **device Acqua V2** (superficie Z −150, X −17100..34100, Y −11954..31054, niente onde):
      il WaterBodyLake nativo dava errori del validatore UEFN (riferimenti illegali a /Water) ed è stato rimosso.
      Spawn pad a (24000, −8250/−8650, 0), yaw 30 → PlayerStart yaw 180 (verso il ponte), su pavimento Z 0. GridPlane spostati
      a Z −10000 (`Template_Spostati`, non cancellati). Antenne visibili dalla partenza (trace + render `docs/qa/uefn_blockout_*.png`).
      Da confermare in sessione (qa-tester): HISM palme in gioco, nuoto e risalita sul ciglio
- [x] (uefn-builder) Barriere invisibili sul lato città e ai limiti del blocco
      6 Barrier device (Invisibile, Sempre, alte 3840 uu da Z −700): lato città Y −11930 (X −3510..27210), fine blocco X 25130
      (Y −12110..−6990), molo/area militare X −1360 (Y −12020..3340), testata Mirabello su 3 lati. Lato mare aperto.
      Aperto: chi nuota può raggiungere la riva del fondale (area militare, Mirabello) a Z 0 → serve il rientro dall'acqua (Verse)
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
| 2026-11-18 | Blockout: scala di Mirabello sostituita da rampa al 7 %, quote ponte [S], varchi nei giardini | Pilastro 3; dettagli in `docs/decisioni.md` |
