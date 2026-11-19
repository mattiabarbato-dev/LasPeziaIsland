# UEFN: limiti di distanza per il fondale (1,5-15 km)

uefn-builder, 2026-11-19. Compito di sola lettura/verifica per `ref/fondale.md` §7.5.
Nessun attore, asset o impostazione salvata è stato modificato. Le prove (cubi temporanei, valori di nebbia) sono state fatte
solo in memoria e annullate nello stesso script; alla fine nessun pacchetto risulta da salvare (`get_dirty_map_packages` e
`get_dirty_content_packages` vuoti) e nessun attore `T_*` è rimasto nel livello.
Coordinate in uu native (X avanti, Y destra, Z su); azimut → yaw UE = azimut − 41,3°.

Legenda: **[V]** verificato in editor (lettura via MCP o render) · **[D]** da documentazione Epic (URL in fondo) · **[S]** stima.

---

## 1. Riepilogo

| Domanda | Risposta |
|---|---|
| Si può posizionare e disegnare geometria a 10-15 km? | **Sì** [V]. Cubi a 1,5 / 3 / 5 / 10 / 15 km dalla partenza disegnati in render dalla partenza. |
| Limite duro di distanza | La **cupola del cielo** (`SkyDome` della sequenza giorno) ha raggio **~36 km** (3 607 800 uu) centrata nell'origine [V]: oltre si nasconde dietro il cielo. Tenere tutto **entro ~30 km**. Il limite del mondo LWC (UE 5.1+) è di milioni di km: non conta. |
| Serve scalare l'anello lontano (omotetia)? | **No.** Anelli A-C a scala reale fino a 10 km, tenda dell'anello D a 12-15 km come proposto. |
| Cull/draw distance | Tutti i componenti del livello hanno `LDMaxDrawDistance` = 0 (mai) [V]; nessun Cull Distance Volume; far clipping plane infinito (`r.FarClippingPlane` 0) [V]. Lasciare 0 sui settori del fondale. |
| Streaming World Partition | Oggi **disattivato** (tag `LevelHasStreamingDisabled = 1` del .umap) [V]: tutto è sempre caricato. Se un giorno si attiva, griglia principale cella 128 m con **raggio di caricamento 256 m** [V]: i settori del fondale vanno messi a **Is Spatially Loaded = NO**. |
| Nebbia | Quella attuale (sequenza del template) satura presto ed è limitata al 70 %: le colline a 1,5 km sono già velate, quelle a 15 km non spariscono mai del tutto. Proposta con *Override nebbia* del device: densità ~0,003, diminuzione 0,01, opacità max 1,0 (§4). |
| Acqua fino all'orizzonte | Un device Acqua V2 arriva al massimo a 512 × 512 m [V]: non si può allungare a 6,5 km. Oltre i ~400 m il "mare" è già la mesh di terra del cielo (`SkyCubeGroundMesh`, blu scuro); con la nebbia proposta la giunzione sparisce (§5). |

---

## 2. Mondo, coordinate e precisione

**Letto in editor [V]** (`FortWorldSettings` del livello `LasPezia_Island`):
- `enable_world_bounds_checks` = True, `kill_z` = −1 048 575 uu (−10,5 km, solo verticale: irrilevante per il fondale).
- `enable_large_worlds`: proprietà deprecata con il messaggio "As of UE 5.1 all worlds are large" → **LWC attivo**.
  Il vecchio limite UE4 `WORLD_MAX` = 2 097 152 uu (±10,5 km), che rendeva rischiosi 10-15 km, **non vale più**.
- `enable_world_origin_rebasing` = False (non serve con LWC).
- `net_cull_distance_squared` = 2,25e8 → 150 m: riguarda solo gli attori **replicati**; le static mesh del fondale non lo sono.
- Bounds attuali World Partition (editor e runtime): X −17 100..59 725 · Y −34 993..45 525 · Z −26 454..25 438 uu.

**Prova pratica [V]:** cubi `/Engine/BasicShapes/Cube` posati in memoria a 5, 10, 15 km verso la bocca del golfo
(fino a (−407 041, 1 428 284) uu) e a 3, 6, 10, 15 km verso le colline SO (fino a (−1 223 931, −840 717) uu),
poi muri da 1,5 a 15 km. Tutti disegnati nel render dalla partenza (24000, −8450, 180) e nella vista dall'alto, senza sfarfallii
né buchi. Render: `docs/qa/uefn_fondale_cubi_5-15km_mare.png`, `docs/qa/uefn_fondale_muri_1.5-15km_dallalto.png`.

**Precisione:**
- Posizioni degli attori in double (LWC): nessun problema a 1-1,5 milioni di uu.
- Vertici delle mesh in float32 relativi al pivot: a 1,5e6 uu il passo è ~0,125 uu (1,25 mm) → nessun tremolio visibile.
  Consiglio comunque **pivot di ogni settore vicino al suo baricentro** (non nell'origine): riduce l'errore e rende i bounds più stretti.
- Materiali: evitare rumore/texture proiettati in **coordinate mondo** a 10 km (possibili bande con funzioni in float). Usare UV
  dell'atlas (come previsto in `ref/fondale.md` §7.6). Se serve world position, usare i nodi LWC.
- Ombre: oltre la distanza delle ombre dinamiche le colline non ricevono ombre proprie; la luce radente va dipinta nell'albedo
  o affidata alle normali. [S] da vedere in sessione.
- Non verificato in sessione: comportamento del client Fortnite (lo fa qa-tester, §7).

## 3. Distanze di rendering e streaming

**Draw/cull distance [V]:**
- Tutti i componenti `Blockout_*` e `Arte_*` (StaticMesh e HISM): `LDMaxDrawDistance` 0, `CachedMaxDrawDistance` 0,
  `InstanceStart/EndCullDistance` 0 → mai tagliati per distanza. Nel livello non c'è nessun `CullDistanceVolume`.
- CVar in editor: `r.ViewDistanceScale` 2,0, `sg.ViewDistanceQuality` 2, `r.StaticMeshLODDistanceScale` 1,
  `r.FarClippingPlane` 0 (piano lontano infinito), `r.HLOD.DistanceOverride` 40000.
  `r.ViewDistanceScale` e la scalabilità *View Distance* scalano solo le distanze di cull **non nulle**: con 0 non hanno effetto
  su PC né su console.
- **LOD:** un settore largo 3-4 km visto da 3 km ha una dimensione a schermo > 1 → resta sempre al LOD0. I LOD dei settori
  B e C non scattano quasi mai: il budget va pensato **tutto al LOD0** (la densità decrescente con la distanza va già nella mesh,
  come in §7.2 della scheda). I 2 LOD restano utili solo per pezzi piccoli (edifici di fondale).

**World Partition [V]:**
- Hash runtime: `WorldPartitionRuntimeHashSet`, partizione `MainPartition`:
  - griglia principale `RuntimePartitionLHGrid_0`: **cella 12 800 uu (128 m), raggio di caricamento 25 600 uu (256 m)**, 2D;
  - griglia HLOD `RuntimePartitionLHGrid_1`: cella 25 600 uu, raggio 51 200 uu (512 m), solo client.
- **Streaming disattivato**: tag del registro asset `LevelHasStreamingDisabled = 1` e `LevelIsPartitioned = 1` sul .umap
  (salvato il 2026-11-18). Con lo streaming spento ogni attore è sempre caricato e il raggio di 256 m non conta.
- **Attenzione:** la documentazione [D1] dice che UEFN propone di attivare lo streaming con un popup quando un attore è a più di
  **1 km dall'origine** o l'isola supera 1 km. Il fondale lo farà comparire (`bHideEnableStreamingWarning` = False).
  - Se si risponde NO, nulla cambia. È la scelta consigliata: l'isola è piccola e il fondale (≤ 55k tri, 8 texture 1024) pesa poco.
  - Se si attiva lo streaming, con i valori attuali un settore del fondale (bounds a ≥ 1,5 km dal giocatore) **non verrebbe mai
    caricato**. Va messo **Is Spatially Loaded = NO** su ogni attore del fondale, come la documentazione raccomanda per "mountains"
    [D1], e **Include Actor in HLODs = NO** (le colline non hanno bisogno di HLOD [D1]).
  - In ogni caso conviene mettere Is Spatially Loaded = NO già alla posa: non costa nulla con lo streaming spento e mette al riparo.

## 4. Nebbia e atmosfera

Gli attori di cielo, sole e nebbia non sono nel livello: li crea la sequenza del template `DSA_UEFN_Ch5S1` (attore
`DSA_UEFN_Ch5S1_C_0` di proprietà di `FortWorldSettings`, `worldTimeOfDayManager`). Valori letti in editor con l'anteprima del device
alle 18,0 [V]:

| Componente | Valori |
|---|---|
| ExponentialHeightFog (Z 0) | densità **0,025**, diminuzione altezza **0,15**, opacità max **0,7**, distanza d'inizio **0**, cutoff 0; inscattering (0,068, 0,152, 0,427); direzionale (0,45, 0,34, 0,18), esponente 50, inizio 10 000; seconda nebbia densità 0,01, diminuzione 0,8, offset −10 000; nebbia volumetrica attiva, distanza 14 000 |
| SkyAtmosphere | raggio terra 6360 km, altezza 61 km, Rayleigh ×0,0435, Mie ×0,003 (anisotropia 0,8), prospettiva aerea ×1, contributo della nebbia 1 |
| SkyDome | `S_SkyDome01_Round_newUV` × 300, raggio ~36 km, senza collisione |
| SkyCubeGroundMesh | `SM_SkyboxGroundmesh` × 500 000 a Z −1000, materiale `M_GroundMeshInSky`: è la "terra/mare" blu scuro sotto l'orizzonte oltre l'acqua di gioco |
| VolumetricCloud | invisibile |

**Prova in memoria [V]** (muri di materiale `M_Blockout_Verde` a 1,5 / 3 / 5 / 10 / 15 km verso il mare, render dalla partenza,
valori scritti sul componente dell'attore di sequenza e ripristinati subito dopo):

| Variante | Densità / diminuzione / opacità max | Risultato | Render |
|---|---|---|---|
| Attuale | 0,025 / 0,15 / 0,7 | già velato a 1,5 km, quasi uniforme fino a 15 km: le colline perdono profondità e quelle lontane restano al 70 % | `uefn_fondale_nebbia_attuale.png` |
| Zero | 0 | resta solo la prospettiva aerea dell'atmosfera, debole: verdi saturi anche a 15 km | `uefn_fondale_nebbia_zero.png` |
| A | 0,0015 / 0,01 / 1,0 | 1,5 km quasi pulito, 5 km leggero, 10 km ~50 %, 15 km ~70 % [S a occhio] | `uefn_fondale_nebbia_A.png` |
| **C (consigliata)** | **0,004 / 0,01 / 1,0** | 1,5 km ~15 %, 5 km ~40 %, 10 km ~70 %, 15 km quasi color cielo: è la curva chiesta da `ref/fondale.md` §7.5 [S a occhio] | `uefn_fondale_nebbia_C.png` |

Con la diminuzione bassa (0,01) la foschia sale con le colline (quota 500-700 m) invece di restare schiacciata al livello del mare,
come succede con 0,15. Con opacità max 1,0 la tenda dell'Appennino (anello D) può arrivare all'85-90 %.

**Come applicarla senza rompere la Sequenza giorno:**
- Il device `Luce_OraDelGiorno` ha già *Override nebbia* (`OverrideFog`, oggi NO) con i campi `FogDensity`, `FogHeightFalloff`,
  `FogMaxOpacity`, `FogColor`, `FogDirectionalInscatteringColor`, `SecondaryFogDensity/Falloff/Offset`, `SunlightVolumetricScattering` [V].
  Gli override sono separati per sole, nebbia, luce cielo, cielo e nuvole: attivando solo la nebbia, sole e cielo restano quelli della
  sequenza alle 18 e l'ora fissa non cambia.
- Valori di partenza proposti: `OverrideFog` SÌ, `FogDensity` **0,003-0,004**, `FogHeightFalloff` **0,01**, `FogMaxOpacity` **1,0**,
  `FogColor` vicino all'inscattering attuale ma più chiaro e caldo verso l'orizzonte del tramonto (es. (0,45, 0,52, 0,66)),
  `SecondaryFogDensity` 0 (o molto bassa).
- Il device **non espone la distanza d'inizio** (`StartDistance`): la foschia parte da 0. Con densità 0,003-0,004 l'effetto
  entro 300 m (passeggiata, ponte) è trascurabile (pochi %), quindi non serve.
- **Da verificare** prima di applicare (non fatto: è una modifica salvata): che i campi del device corrispondano 1:1 a quelli del
  componente (stessi nomi e intervalli: densità 0-10, diminuzione 0-2) e che il blend dell'override non mescoli i valori con la
  sequenza. Prova: attivare l'override, rileggere il componente `ExponentialHeightFog` dell'attore di sequenza, render dalla partenza.
- Antenna bianca davanti al Monte Castellana (4,1 km): con la variante C la cresta a 4 km è velata ~35-40 % e il contrasto con
  l'antenna resta buono [S, da confermare con il fondale vero].

## 5. Acqua V2 fino all'orizzonte

- Opzioni del device `Acqua_Golfo_Device` [V]: `Zone Width` 100 (massimo 100), `Zone Depth` 84 (massimo 100), `Zone Height` 1;
  1 unità = 512 uu. **Un device copre al massimo 512 × 512 m.** La larghezza (X) è già al massimo; in Y si possono aggiungere
  16 unità (82 m).
- Dalla partenza l'acqua di gioco finisce a ~395 m verso il mare (Y 31 054). Oltre si vede la `SkyCubeGroundMesh` della sequenza
  (blu scuro uniforme, piatta, senza riflessi) fino all'orizzonte: nel render `uefn_fondale_cubi_5-15km_mare.png` è la fascia scura
  di ~7 px sotto l'orizzonte. Con la nebbia C la fascia si schiarisce e la giunzione quasi sparisce (`uefn_fondale_nebbia_C.png`).
- **Proposta (non applicata), in ordine di preferenza:**
  1. **Non allungare il device.** Tenere l'acqua di gioco com'è (+ eventualmente `Zone Depth` 100 se serve più mare vicino),
     usare la nebbia C e lasciare alla mesh del cielo il mare lontano. La costa del fondale (Varignano, Le Grazie, Lerici) va
     chiusa con la gonna verticale prevista in §7.3 della scheda, che scende sotto Z −100: così la riva "entra" nel blu.
  2. Se la differenza di colore tra l'acqua del device (chiara, con riflessi) e il blu della mesh del cielo si nota in sessione:
     un **anello di mare solo visivo** (mesh piatta senza collisione a Z −100, da ~350 m a ~7 km, materiale unlit/semplice con
     gradiente verso il colore della nebbia). È una **deroga** a CLAUDE.md §4 ("niente mesh d'acqua da Blender"): decide l'utente.
  3. Più device Acqua V2 affiancati: servirebbero ~40 device da 512 m per il settore 124°-154° fino a 6,5 km. Sconsigliato
     (costo, memoria, nuoto in tutto il golfo).
- Il nuoto resta limitato all'acqua attuale e alle barriere esistenti.

## 6. Raccomandazioni per blender-artist e per la posa

1. **Distanza:** scala reale fino a 15 km; nessuna omotetia. Tetto pratico 30 km (cupola del cielo a 36 km).
2. **Attori:** un `FortStaticMeshActor` per settore, pivot al baricentro del settore, cartella Outliner `Fondale/Colline`.
   `LDMaxDrawDistance` 0 (predefinito), **Is Spatially Loaded = NO**, **Include Actor in HLODs = NO**, collisione **NoCollision**
   (`ref/fondale.md` §7.5), *Cast Shadow* da provare (vedi §2).
3. **Budget:** contare tutti i 55k tri come sempre al LOD0 (§3). LOD solo per gli edifici di fondale.
4. **Materiale:** albedo dall'atlas con UV; niente proiezioni in coordinate mondo; roughness alta costante.
5. **Nebbia:** variante C con *Override nebbia* sul device esistente, da tarare con il fondale vero.
6. **Popup streaming:** quando compare (primo attore oltre 1 km), rispondere NO finché la memoria non lo richiede.

## 7. Da verificare in sessione (qa-tester / utente)

- Fondale visibile nel client Fortnite su PC (e console, se disponibile) a tutte le distanze, senza pop-in.
- Comparsa del popup di streaming dopo la posa del fondale e scelta dell'utente.
- *Override nebbia*: corrispondenza dei valori col componente e aspetto in gioco alle 18.
- Giunzione acqua di gioco / mare della mesh del cielo con la nebbia scelta.
- Memoria dopo l'import del fondale (pannello Memoria; limite di pubblicazione 300 MiB [D2]).

## Fonti

- [D1] Epic, *Streaming and HLODs in UEFN*: https://dev.epicgames.com/documentation/en-us/uefn/streaming-and-hlods-in-unreal-editor-for-fortnite
  (popup oltre 1 km; Is Spatially Loaded = NO per "skyscrapers or mountains"; griglie in World Partition Setup > Runtime Settings > Grids).
- [D2] Epic, *Memory Management in UEFN*: https://dev.epicgames.com/documentation/fortnite/memory-management-in-unreal-editor-for-fortnite
  (budget di pubblicazione 300 MiB; attori non spatially loaded sempre caricati).
- [D3] Epic, *World Partition in Unreal Engine*: https://dev.epicgames.com/documentation/unreal-engine/world-partition-in-unreal-engine
  (loading range per griglia).
- Letture dirette via MCP (`unreal-mcp`): `FortWorldSettings`, `WorldPartition_0.WorldPartitionRuntimeHashSet_0`, componenti
  dell'attore `DSA_UEFN_Ch5S1_C_0`, opzioni dei device `Luce_OraDelGiorno` e `Acqua_Golfo_Device`, tag del registro asset del .umap.

---

## 8. Fondale v1 in UEFN: import, posa, nebbia, barriere (uefn-builder, 2026-11-19, 12:40-13:01 UTC)

Sorgenti: `exports/fondale/` (21 asset × LOD0/1/2), posizioni `exports/fondale/fondale_posizioni.csv`, texture `blender/textures/fondale/`.
Nessun asset, attore o cartella cancellato. Nessuna finestra modale aperta. Il popup di attivazione dello streaming non è stato
accettato (durante la posa non è comparso nulla di bloccante).

### 8.1 Asset (`LaSpezia/Arte/Fondale`)
| Asset | Tri LOD0 / 1 / 2 | Bbox locale (uu) |
|---|---|---|
| `SM_Fondale_Colline_E / N / NE / NO / O / S / SE / SO` | 7118 / 6543 / 6939 / 5319 / 7656 / 6342 / 1389 / 6581 (solo LOD0) | = CSV (scarto ≤ 0,4 uu) |
| `SM_Fondale_Tenda` | **410** (CSV 412: 2 triangoli degeneri scartati dall'import), solo LOD0 | X −713730..1299982 · Y −1300432..1289013 · Z −3000..102809. Il CSV riporta l'ingombro di tutti i 720 vertici (anche quelli del settore mare, senza triangoli); verificato: vertici a passo 1° su 360° |
| `SM_Fondale_Citta_*` (12) | 33 728 / 16 947 / 6 143 (ogni blocco = CSV) | = CSV; bbox di LOD1/LOD2 contenute in quella del LOD0 (nessuna rotazione) |

Totale LOD0 **82 025 tri** (terreno + tenda 48 297, città 33 728).
- **LOD**: solo i blocchi città hanno LOD1/LOD2 (soglie 1,0 / 0,2 / 0,08, MinLOD Low/Medium 2 come gli altri asset). Settori di
  collina e tenda **solo LOD0**: con raggi di 2,5-13 km a 0,1-10 km dalla corsia la dimensione a schermo resta > 1, i LOD non
  scatterebbero mai (§3) e occuperebbero solo memoria; con MinLOD 2 sulle qualità Low/Medium la silhouette perderebbe fino all'85 %
  dei triangoli. MinLOD Low/Medium portato a **0** su questi 9 asset (con 2 il validatore segnalava "fuori intervallo").
  Avviso residuo del validatore sugli 8 settori: "mesh complessa con un solo LOD", accettato per la ragione sopra.
- **Nanite off**, **nessuna collisione** (rimossi i convessi generati dall'import; `Use Simple Collision As Complex` con forma semplice
  vuota, quindi nemmeno collisione complessa), nessun LOD automatico (i 3 LOD identici creati dall'import sono stati rimossi).
- **Colore vertice della città.** `ImportFile` scarta il colore vertice degli FBX (tutto bianco). Per i 12 blocchi i LOD0/1/2 sono stati
  reimportati in `_Temp` con `AssetImportTask` + **`FbxFactory` esplicita**, `automated=True`, `replace_existing=False`, nome nuovo,
  `FbxImportUI.static_mesh_import_data.vertex_color_import_option = REPLACE` (nessun modale, bbox identica a quella di `ImportFile`), poi
  copiati negli asset finali con `remove_lods` + `set_lod_from_static_mesh` (§12 di `docs/uefn_arte.md`). Colori verificati per LOD
  (es. NE_01 (0,98; 0,86; 0,58), NO_02 (0,96; 0,80; 0,66)). Nota: queste reimportazioni in `_Temp` hanno Nanite on (non referenziate).

### 8.2 Materiali
- Nuovo master **`Arte/Materiali/M_Morin_Master_Fondale`** (opaco, lit): `Albedo` (Texture2D, UV0) × `Tinta` × lerp(1, VertexColor.RGB,
  `UsaVertexColor`) → BaseColor; `Roughness` 0,92; `Specular` 0,3. Nessuna coordinata mondo.
- MI in `Arte/Fondale`: `MI_Fondale_Colline_<S>` (8) con `T_Fondale_Colline_<S>_D`, `MI_Fondale_Tenda` con `T_Fondale_Tenda_D`
  (UsaVertexColor 0); `MI_Fondale_Facciate` con `T_Fondale_Facciata_D` (UsaVertexColor 1, texture ripetuta).
- Texture importate da `blender/textures/fondale/` in `Arte/Fondale/Texture` (10; 1024 × 1024, tenda 1024 × 256; sRGB). Colline e tenda in
  **Clamp** (UV polari 0..1, niente sbavature ai bordi), facciata in Wrap. Le texture incorporate negli FBX non sono state estratte.

### 8.3 Attori (Outliner `Arte/Fondale`, 21 `FortStaticMeshActor` `Arte_Fondale_<nome>`)
Posizione = CSV (yaw 0, scala 1, Z 0). Su tutti: mobilità Static, `LDMaxDrawDistance` 0, profilo **NoCollision**, `CanCharacterStepUpOn` No,
**Is Spatially Loaded = NO**, **Include Actor in HLODs = NO**. *Cast Shadow*: **SÌ sui 12 blocchi città** (0,25-1,5 km: le ombre fra
edifici danno volume, costo trascurabile), **NO su colline e tenda** (oltre la distanza delle ombre dinamiche non servono; la luce è già
dipinta nell'albedo; evita che la tenda proietti ombre lunghe chilometri).

### 8.4 Nebbia (`Luce_OraDelGiorno`, solo *Override nebbia*)
Valori scritti con `SetClassicDeviceOption` e riletti sul componente `ExponentialHeightFog` della sequenza (corrispondenza 1:1):
`OverrideFog` SÌ · `FogDensity` **0,004** · `FogHeightFalloff` **0,02** · `FogMaxOpacity` **1,0** · `SecondaryFogDensity` **0** ·
`FogColor` **(0,30; 0,38; 0,52)** · inscattering direzionale invariato. Sole, cielo, luce cielo, nuvole, ora fissa 18 e priorità non toccati.
- Taratura (render dalla partenza a 189° e 135°, FOV 45): densità 0 / 0,002 / 0,003 / 0,004 / 0,008 / 0,01 con diminuzione 0,01 / 0,02 / 0,04 / 0,08
  e due colori. Con **diminuzione 0,01** la nebbia sale fino al cielo e lo ingrigisce tutto (le foto `ref/foto/vista/` hanno cielo blu);
  con 0,04 le colline tornano quasi nitide. **0,02** è il compromesso: foschia che cresce con la distanza (1-2 km leggera, Castellana a
  4 km velato, tenda a 13 km quasi color cielo), cielo azzurro in alto. Il colore più scuro (0,30; 0,38; 0,52) evita il velo latteo del
  (0,45; 0,52; 0,66) proposto in §4. Deroga voluta dalla proposta C (diminuzione 0,01).
- Antenne contro il Monte Castellana (az 189°): antenne bianche nettamente più chiare della cresta velata, leggibili
  (`uefn_fondale_v1_zoom_antenne_189.png`). Prima/dopo: `uefn_fondale_v1_nebbiaPrima_*.png` (nebbia del template 0,025/0,15/0,7) e `uefn_fondale_v1_*.png`.

### 8.5 Barriere sui bordi dell'acqua (`Device/Barriere`)
Volume `Acqua_Golfo_Device`: X −17100..34100 · Y −11954..31054 · Z −484..−100. Lati già chiusi: +X (`Barriera_FineBlocco`, X 25130) e
città (terra + `Barriera_LatoCitta`). Aperti: lato mare (Y 31054) e lato −X (X −17100). Aggiunte due barriere **duplicando
`Barriera_FineBlocco`** (stesse impostazioni: Scatola, materiale invisibile, sempre attiva, altezza 10, collisione visuale NO,
*Influenza distanza dissolvenza* NO, blocca proiettili); larghezza/profondità con `SetClassicDeviceOption` (valori ammessi: 0,5 e 90).

| Label | Centro | Unità (L × P × A) | Ingombro (letto da `BarrierBounds`) |
|---|---|---|---|
| `Barriera_Acqua_LatoMare` | (5440, 30928, −700) | 90 × 0,5 × 10 | X −17600..28480 · Y 30800..31056 · Z −700..3140 |
| `Barriera_Acqua_LatoMenoX` | (−16978, 9473, −700) | 0,5 × 90 × 10 | X −17106..−16850 · Y −13567..32513 · Z −700..3140 |

Gli angoli si sovrappongono fra loro e con `Barriera_FineBlocco` (X 25002..25258, Y fino a 33970): nessun varco. Base sotto il fondo
dell'acqua. Distanza dalla passeggiata, dal ponte e da Mirabello > 90 m. Da confermare in sessione (in modalità Crea le barriere non hanno collisione).

### 8.6 Verifiche
- Render 1024 px con ombre (`docs/qa/`): `uefn_fondale_v1_partenza_{SO_221, antenna_Castellana_189, O_265, NO_citta_320, SE_bocca_135, NE_40}.png`,
  `uefn_fondale_v1_ponte_verso_passeggiata_311.png`, `uefn_fondale_v1_zoom_antenne_189.png`, `uefn_fondale_v1_zoom_NE_40.png` (FOV 25).
  Sagome coerenti con `arte_fondale_v1_*` e con le foto `ref/foto/vista/` (colline più chiare e meno sature delle foto: vedi problemi).
- **Giunzione acqua / mare del cielo** (135°, bocca del golfo): con la nebbia nuova nessuna fascia scura visibile a 1024 px; l'acqua di
  gioco si fonde con l'orizzonte e la costa del fondale entra nel mare senza bordo. L'anello di mare visivo **dai render non serve**;
  decisione finale dell'utente dopo la prova in sessione.
- **Linea di vista sulle antenne invariata**: il fondale non ha collisione, quindi verifica geometrica. Nessun asset del fondale ha vertici
  fra la partenza e le antenne (le AABB di `Colline_S` e `Tenda` intersecano i segmenti, ma i loro vertici più vicini sono a 425 m e 13 km,
  oltre le antenne a ~290 m).
- Popping: i LOD della città hanno soglie 1,0/0,2/0,08 e dalla passeggiata restano al LOD0; colline e tenda non hanno LOD; cull 0. Non
  verificabile nei fermi immagine: da confermare in sessione (qa-tester).
- Validazione (`LaSpezia/Arte/Fondale`, `Arte/Materiali`, mappa): 47 asset, 47 validi, 0 errori, 8 avvisi (§8.1). I 24 attori nuovi/modificati: VALID.
  Log: nessun errore nuovo (solo avvisi `LogSpatialMetrics` di una sessione di profilazione già aperta).
- Salvataggio `save_dirty_packages` alle 12:58:16 UTC (+ MinLOD alle ~12:59); date OFPA su disco controllate (21 attori, 2 barriere, device
  luce); 0 pacchetti sporchi.
- `PushChanges` sulla sessione aperta: **Completed** (cottura v7). **Project Size v7: download 22.432.052 byte (21,4 MiB)** (v6: 13,0 MiB),
  upload 133,9 MB; in download mesh 8,8 MB e texture 12,6 MB. Mesh del fondale ≈ 7,9 MB, texture del fondale ≈ 1,2 MB.
  Calcolo memoria dell'editor dopo la cottura (`LogValkyrieMemoryCalculation`): `peak=5 809 329 threshold=314 572 800` (5,5 MiB su
  300 MiB, `sampled=1`). È la stima del campionatore dell'editor; il riferimento resta il pannello Memoria (utente).

### 8.7 Temporanei in `LaSpezia/_Temp` (non cancellati, nessun referencer)
`TMP_SM_Fondale_Citta_<blocco>_LOD1/_LOD2` (24, da `ImportFile`, senza colore vertice) e `TMPVC_SM_Fondale_Citta_<blocco>` (+`_LOD1`, `_LOD2`)
(36, con colore vertice, Nanite on). Totale 60 nuovi; con i 33 precedenti, 93 asset in `_Temp`. Eliminabili quando l'utente conferma.

### 8.8 Problemi aperti
1. (qa-tester) Sessione: fondale visibile e senza pop-in nel client, barriere d'acqua che bloccano davvero, nebbia alle 18, giunzione col mare.
2. (utente) Anello di mare visivo: dai render non serve; decidere dopo la sessione.
3. (utente / blender-artist) Colline più chiare e di un verde più giallo delle foto (verde scuro): eventualmente scurire `Tinta` delle MI
   delle colline (es. 0,8) o l'albedo in Blender. Facciate molto chiare: i colori vertice vanno dal crema all'ocra chiaro.
4. (blender-artist, minore) CSV della tenda: bbox calcolata su tutti i vertici, non sui triangoli; 2 triangoli degeneri.
5. Blockout fondale (scatole bianche vicino al ponte e all'area militare) ancora visibile davanti alla città nuova: serve un task dedicato.

## 9. Tinta v2 (uefn-builder, 2026-11-19)

Correzione del problema §8.8 punto 3 solo tramite il parametro vettoriale `Tinta` delle MI esistenti (master
`M_Morin_Master_Fondale`: `Tinta` è già un **LinearColor**, nessuna modifica al master). Nessun import, nessun nuovo asset,
nulla cancellato, nebbia e luce non toccate.

### 9.1 Valori
| MI | `Tinta` prima | `Tinta` dopo |
|---|---|---|
| `MI_Fondale_Colline_<N, NE, E, SE, S, SO, O, NO>` (8) | (1; 1; 1), ereditato dal master, nessun override | **(0,34; 0,52; 0,38)** |
| `MI_Fondale_Tenda` | (1; 1; 1), ereditato | **(0,34; 0,52; 0,38)** |
| `MI_Fondale_Facciate` | (1; 1; 1), ereditato | **(0,40; 0,40; 0,40)** (neutro: tonalità dai colori vertice) |

Il valore suggerito (0,72; 0,80; 0,74) e Facciate 0,72 sono stati provati per primi: differenza quasi invisibile nei render
(cresta della Castellana da (176; 189; 197) a (172; 186; 195) sRGB). Tappe: (0,72; 0,80; 0,74) → (0,30; 0,36; 0,30)
(colline grigio-beige, verde perso) → (0,42; 0,60; 0,46) → **(0,34; 0,52; 0,38)**: rapporto verde/rosso 1,5 per compensare il
grigio della nebbia. Facciate: 0,72 → 0,30 (ocra/rosa leggibili ma sporche) → 0,50 (ancora chiare) → **0,40**.

### 9.2 Render (1024 px, ombre, FOV 60, pitch −2)
Punto di vista: **partenza (24000, −8450, 180)**, la stessa di §8.6 (non l'origine: dall'origine la vista a 189° guarda dentro
il ponte). Yaw = azimut − 41,3°. Nomi `docs/qa/uefn_fondale_v2_prima_<vista>.png` e `docs/qa/uefn_fondale_v2_tinta_<vista>.png`,
con `<vista>` = `SO_221`, `Castellana_189`, `O_265`, `NO_citta_320`, `NE_40`. I "prima" sono nuovi (pitch e inquadratura diversi da v1).

Medie sRGB delle zone (stesse finestre di pixel prima/dopo):
| Zona | Prima | Dopo | Foto `ponte_verso_passegiata.png` |
|---|---|---|---|
| Cresta Castellana (189°, ~4 km) | (176; 189; 197) | (165; 180; 193) | collina lontana (94; 118; 146) |
| Colline vicine SO (221°, 1-2 km) | (166; 180; 188) | (155; 171; 185) | |
| Colline NE (40°) | (170; 185; 198) | (163; 179; 196) | |
| Facciate NE (40°, ~0,5-1 km) | (232; 221; 218) | (217; 197; 188) | case al sole (125; 111; 103) |
| Facciate NO (320°, tra le palme) | (201; 200; 204) | (161; 158; 165) | |
| Cielo (riferimento) | (186; 204; 221) | invariato | (93; 135; 193) |

### 9.3 Esito
- **Facciate: corrette in buona parte.** Da bianco-crema abbagliante a crema/ocra/rosa distinguibili, non grigie.
- **Colline: miglioramento piccolo.** Meno giallo, un po' più scure e più verde-grigie, ma restano molto più chiare delle foto.
  **Causa: la nebbia, non l'albedo.** Con `Tinta` 0,30 la cresta a 4 km cambia solo da 176 a 163 di rosso: oltre ~1 km quasi
  tutto il colore viene dall'inscattering di `ExponentialHeightFog` (densità 0,004, diminuzione 0,02, §8.4), non dalla superficie.
  A 265° (controluce, sole delle 18) le colline restano beige-rosate per l'inscattering direzionale.
- Per avvicinarsi alle foto serve un task sulla nebbia (non fatto qui, fuori mandato): densità più bassa (0,002-0,003) o
  diminuzione più alta (0,03), colore più blu e scuro, eventualmente inscattering direzionale ridotto. Le tinte di §9.1 restano
  valide anche dopo: con meno nebbia diventeranno più visibili, quindi vanno ricontrollate (rischio colline troppo scure vicino).
- Validazione delle 10 MI: 10 valide, 0 errori, 0 avvisi. Salvate (0 pacchetti sporchi dopo il salvataggio).
- **PushChanges non eseguito: nessuna sessione aperta** (`GetSessionStatus` = Disconnected). Le modifiche arriveranno al
  prossimo avvio di sessione.

## 10. Colle cittadino v2 in UEFN (uefn-builder, 2026-11-19, ~15:05-15:25 UTC)

Sorgenti: `exports/fondale/` (9 asset × LOD0/1/2), posizioni `exports/fondale/fondale_posizioni_v2.csv` (righe `nuovo_v2`),
texture `blender/textures/fondale/T_Fondale_Colle_Suolo_D.png`. Scheda: `ref/fondale.md` §10.
Nessun asset, attore o cartella cancellato; nessuna finestra modale; solo import da zero (nessun reimport/sostituzione).
Blockout del fondale, nebbia, luce e `PLAN.md` non toccati.

### 10.1 Metodo di import
- **Città e alberi (8 asset)**: `AssetImportTask` + `FbxFactory` esplicita (`automated`, `replace_existing=False`, `FbxImportUI`
  static mesh, `combine_meshes`, `vertex_color_import_option = REPLACE`, niente materiali/texture, `auto_generate_collision=False`).
  LOD0 importato direttamente col nome finale in `LaSpezia/Arte/Fondale` (nome nuovo, quindi nessuna sostituzione);
  `_LOD1`/`_LOD2` in `_Temp` come `TMPVC2_<asset>_LOD1/2`.
- **Suolo**: `StaticMeshToolset.ImportFile` (LOD0 col nome finale, LOD1/2 in `_Temp` come `TMP2_SM_Fondale_Colle_Suolo_01_LOD1/2`).
- Entrambi gli import creano **3 LOD automatici** (riduzione dell'importatore): rimossi con `remove_lods`, poi
  `set_lod_from_static_mesh(dest, 1|2, tmp, 0, True)` (§12 di `docs/uefn_arte.md`).
- Poi: MI sugli slot con `SetMaterial` (il `set_editor_property('static_materials')` fatto prima di `remove_lods` non resta),
  `SetNaniteEnabled` false, `SetLodThresholds` 1,0 / 0,2 / 0,08, `RemoveCollisions` + `CTF_UseSimpleAsComplex` (nessuna forma:
  nemmeno collisione complessa), `SetQualityLevelMinLod` Low/Medium = 2 (come i blocchi città v1; default 0).
- Nota strumenti: `IsNaniteMesh` e `has_valid_nanite_data()` rispondono *vero* per **tutte** le mesh del fondale, anche le v1 con
  Nanite off (UEFN costruisce comunque i dati Nanite); l'impostazione `nanite_settings.enabled` è **False** su tutte.

### 10.2 Asset (`LaSpezia/Arte/Fondale`, verificati in editor per LOD con GeometryScript sul source model)
| Asset | Tri LOD0 / 1 / 2 (= CSV) | Bbox LOD0 (uu) = CSV | Colore vertice medio | Slot → MI |
|---|---|---|---|---|
| `SM_Fondale_Citta_Colle_01` | 4784 / 2031 / 682 | X −37605..37515 · Y −26217..26078 · Z −22..9163 | (0,76; 0,62; 0,51) | `M_Fondale_Facciate` → `MI_Fondale_Facciate` |
| `SM_Fondale_Citta_Colle_02` | 292 / 122 / 57 | X −15162..14684 · Y −10795..10586 · Z −79..2087 | (0,76; 0,62; 0,48) | idem |
| `SM_Fondale_Citta_Colle_03` | 4761 / 2455 / 800 | X −46060..46351 · Y −20929..21225 · Z 459..9254 | (0,76; 0,62; 0,51) | idem |
| `SM_Fondale_Citta_Colle_04` | 1509 / 727 / 267 | X −21611..22577 · Y −27232..27054 · Z −22..3468 | (0,75; 0,61; 0,50) | idem |
| `SM_Fondale_Citta_Colle_05` | 4785 / 2355 / 801 | X −40660..40078 · Y −28062..27634 · Z 518..10186 | (0,76; 0,62; 0,51) | idem |
| `SM_Fondale_Citta_Colle_06` | 4773 / 2120 / 658 | X −51508..50769 · Y −43581..44566 · Z 406..12142 | (0,76; 0,62; 0,50) | idem |
| `SM_Fondale_Citta_Colle_07` | 420 / 175 / 56 | X −17109..16575 · Y −18680..19590 · Z 113..3603 | (0,75; 0,61; 0,50) | idem |
| `SM_Fondale_Colle_Alberi_01` | 4800 / 1920 / 720 | X −57287..56981 · Y −54260..55180 · Z 749..10761 | (0,21; 0,30; 0,18) | idem (UV tutte in un punto: colore solo dal vertice) |
| `SM_Fondale_Colle_Suolo_01` | 3668 / 1862 / 600 | X −58250..58750 · Y −58750..58250 · Z 104..9499 | bianco (non usato) | `M_Fondale_Colle_Suolo` → `MI_Fondale_Colle_Suolo` |

Totale nuovo: LOD0 **29 792 tri**, LOD1 13 767, LOD2 4 641. I 5 blocchi v1 nascosti valgono 19 720 tri LOD0: a schermo +10 072 tri.
Bbox di LOD1/LOD2 contenute in quella del LOD0 (nessuna rotazione), **tranne il suolo**: LOD1 X/Y fino a ±59 195, LOD2 fino a
±61 850 (fino a 31 m oltre il LOD0, sui bordi del quadrato; Z 78..9717). Effetto della decimazione in Blender, a 260+ m e coperto
da case e colline v1: segnalato a blender-artist come minore.

### 10.3 Texture e materiale
- `Arte/Fondale/Texture/T_Fondale_Colle_Suolo_D`: 1024 × 1024, sRGB, gruppo World, compressione Default. UV del suolo planari
  0,02..0,97 (LOD2 −0,01..1,01) → **Clamp** su X e Y, come le colline (niente ripetizione ai bordi).
- **`MI_Fondale_Colle_Suolo`** (nuova, master `M_Morin_Master_Fondale`): `Albedo` = `T_Fondale_Colle_Suolo_D`, `UsaVertexColor` 0,
  `Roughness` 0,92 e `Specular` 0,3 ereditati, **`Tinta` (0,40; 0,50; 0,40)**. Prove: (0,5; 0,5; 0,5) neutra e (0,62; 0,66; 0,60)
  chiara contro (0,40; 0,50; 0,40): differenza piccola (oltre 300 m domina la nebbia, §9.3). Scelta (0,40; 0,50; 0,40): meno scura
  in rosso delle colline (0,34) perché la texture contiene già case e strade, appena più verde per avvicinarsi alla foto dal ponte.
- Città e alberi: `MI_Fondale_Facciate` esistente (UsaVertexColor 1, Tinta 0,40), non modificata.

### 10.4 Attori (Outliner `Arte/Fondale`, `FortStaticMeshActor`, duplicati da `Arte_Fondale_Citta_NO_01`)
| Attore | Posizione (yaw 0, scala 1) | Cast Shadow |
|---|---|---|
| `Arte_Fondale_Citta_Colle_01` | (43000, −48000, 0) | sì |
| `Arte_Fondale_Citta_Colle_02` | (68000, −31000, 0) | sì |
| `Arte_Fondale_Citta_Colle_03` | (40000, −89000, 0) | sì |
| `Arte_Fondale_Citta_Colle_04` | (93000, −58000, 0) | sì |
| `Arte_Fondale_Citta_Colle_05` | (17000, −131000, 0) | sì |
| `Arte_Fondale_Citta_Colle_06` | (100000, −110000, 0) | sì |
| `Arte_Fondale_Citta_Colle_07` | (136000, −58000, 0) | sì |
| `Arte_Fondale_Colle_Alberi_01` | (55000, −96000, 0) | **no** (chiome a 360-1400 m, oltre le ombre dinamiche) |
| `Arte_Fondale_Colle_Suolo_01` | (53000, −89000, 0) | **no** (come colline e tenda) |

Su tutti (riletti): mobilità Static, `NoCollision`, `CanCharacterStepUpOn` No, `LDMaxDrawDistance` 0, **Is Spatially Loaded NO**,
**Include Actor in HLODs NO**. `EditorValidatorSubsystem`: VALID.

**Nascosti (non cancellati)**: `Arte_Fondale_Citta_NO_01`, `_NO_02`, `_NO_03`, `_N_01`, `_N_02`:
- *Actor Hidden In Game* = sì;
- componente mesh **`Visible` = falso** (persistente: nascosto in editor e in gioco). `bHiddenEd` non è esposto a Python; in più
  è attivo l'occhio dell'Outliner (temporaneo, si perde alla riapertura: resta comunque invisibile per `Visible` = falso).
- Per ripristinarli: `Visible` = vero sul componente e *Actor Hidden In Game* = no. Le mesh v1 restano referenziate dagli attori
  nascosti, quindi **restano nella cottura e nella memoria** finché l'utente non conferma la cancellazione.

### 10.5 Render (1024 px, ombre, `docs/qa/`)
| File | Camera (UE) | Note |
|---|---|---|
| `uefn_fondale_v2_colle_partenza_320.png` | (24000, −8450, 180), yaw 278,7, pitch −2, FOV 60 | stesso punto di §9.2 |
| `uefn_fondale_v2_colle_partenza_zoom_320.png` | idem, pitch 3, FOV 25 | |
| `uefn_fondale_v2_colle_ponte_313.png` | (−460, 16500, 430) sull'impalcato lato Mirabello (Z impalcato 263), yaw 271,7, pitch −2, FOV 60 | confronto con `ref/foto/ponte/ponte_verso_passegiata.png` e `arte_fondale_v2_colle_ponte_313.png` |
| `uefn_fondale_v2_colle_ponte_zoom_330.png` | idem, yaw 288,7, pitch 1, FOV 25 | confronto con `arte_fondale_v2_colle_ponte_zoom_325.png` |
| `uefn_fondale_v2_colle_obliqua_alto.png` | (50000, −15000, 4000), yaw 270, pitch −6, FOV 50 | vista di controllo del suolo fra le case |

Esito:
- **Dal ponte**: il colle sale a destra dell'antenna con case a gradoni e tetti in coppo, come nella foto (fascia 307°-345°, quota a
  schermo simile). Coerente con il render Blender. Il suolo si vede fra le case come terreno grigio-verde; nessun bordo del quadrato visibile.
- **Dalla partenza**: il colle è quasi tutto coperto dalle scatole bianche del blockout del fondale (come nel render Blender
  `arte_fondale_v2_colle_partenza_320.png`); si vedono solo le case più alte fra le scatole. Atteso: task blockout separato.
- **Differenze dalla foto**: nella foto il colle è punteggiato di alberi verde scuro; in UEFN le chiome sono poche e **grigio-salvia
  chiare** (colore vertice (0,21; 0,30; 0,18) × `Tinta` 0,40 di `MI_Fondale_Facciate` × texel della facciata, più la nebbia), molto
  più chiare che nel render Blender. Le facciate restano più chiare e rosate della foto (stessa causa nebbia di §9.3).

### 10.6 Validazione, salvataggio, sessione
- `ValidateAssets` su `Arte/Fondale` (ricorsivo, con texture) + `Arte/Materiali`: **57 controllati, 57 validi, 0 errori**, 8 avvisi
  (solo i settori di collina con un solo LOD, già accettati in §8.1).
- `save_dirty_packages` alle **15:18:57 UTC**, 0 pacchetti sporchi dopo. Su disco: 9 mesh, MI nuova, texture, 19 temporanei e
  **14 file OFPA** (9 attori nuovi + 5 nascosti) con data di questo salvataggio. `MI_Fondale_Facciate` risalvata senza modifiche ai parametri.
- **PushChanges non eseguito: nessuna sessione aperta** (`GetSessionStatus` = Disconnected). Project Size e memoria da
  rileggere al prossimo avvio di sessione.
- Log: nessun errore dell'import. Avviso già presente prima di questo task (15:03, `MI_Fondale_Facciate` e `MI_Fondale_Tenda`) e ora
  anche su `MI_Fondale_Colle_Suolo`: *"missing usage flag Nanite! Default Material will be used in game"*: vedi problemi.

### 10.7 Temporanei nuovi in `LaSpezia/_Temp` (non cancellati, nessun referencer)
`TMPTEST_SM_Fondale_Citta_Colle_02` (prova dell'import con colore vertice), `TMPVC2_SM_Fondale_Citta_Colle_0<1..7>_LOD1/_LOD2` (14),
`TMPVC2_SM_Fondale_Colle_Alberi_01_LOD1/_LOD2` (2), `TMP2_SM_Fondale_Colle_Suolo_01_LOD1/_LOD2` (2). Totale **19**; in `_Temp` ora 112 asset.

### 10.8 Problemi aperti
1. **(qa-tester / uefn-builder)** Avviso *missing usage flag Nanite* sul master `M_Morin_Master_Fondale` (tocca tutte le MI del
   fondale, anche v1). Le mesh hanno Nanite off, quindi in gioco non dovrebbe scattare; se in sessione il fondale appare col
   materiale grigio di default, attivare *Used with Nanite* sul master (come `M_Morin_Master_Emissivo`).
2. **(utente / blender-artist)** Alberi del colle troppo chiari e radi rispetto alla foto: proposta una MI dedicata
   `MI_Fondale_Colle_Alberi` (Tinta ~1,0 o più scura in R) oppure colore vertice più scuro in Blender. Non fatto: fuori mandato.
3. **(utente)** Cancellazione dei 5 attori v1 nascosti e delle loro mesh (risparmio di memoria e cottura): serve conferma.
4. **(blender-artist, minore)** Bbox di LOD1/LOD2 del suolo più larghe del LOD0 (fino a 31 m).
5. **(task separato)** Scatole bianche del blockout davanti al colle dalla partenza.
6. **(qa-tester)** Sessione: colle visibile senza pop-in (LOD 1,0/0,2/0,08, MinLOD 2 su Low/Medium), attori nascosti assenti nel client.
