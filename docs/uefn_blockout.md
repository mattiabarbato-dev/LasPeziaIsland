# Blockout del Blocco 1 in UEFN

Data: 2026-11-18 · Agente: uefn-builder · Livello: `/705655d7-c848-4957-8e94-8a1c399ddeea/LasPezia_Island` (salvato)
Coordinate in XYZ nativo Unreal (X avanti, Y destra, Z su). L'editor mostra LUF: Left = −Y, Up = Z, Forward = X.
Regola Blender → UE: UE = (B_X·100, −B_Y·100, B_Z·100), yaw UE = −rotZ Blender (vedi `docs/scala.md`).

## Asset importati

Cartella `/705655d7-c848-4957-8e94-8a1c399ddeea/LaSpezia/Blockout` (Esplora contenuti: `LaSpezia/Blockout`).
Import con `StaticMeshToolset.ImportFile`, `bCombineMeshes=true`, `bImportMaterials=true`, `bImportTextures=false`.

| Asset | Bbox locale misurata (uu) | Tri LOD0 | Collisione (convessi) | UCX nell'FBX |
|---|---|---|---|---|
| `SM_Blockout_Passeggiata` | X −1230..25000 · Y −11800..8980 · Z −300..150 | 121 | 13 | 13 |
| `SM_Blockout_Ponte` | X −820..300 · Y 0..17900 · Z −300..3350 | 408 | 34 | 34 |
| `SM_Blockout_Mirabello` | X −2020..980 · Y 16800..21740 · Z −300..239,7 | 58 | 5 | 5 |
| `SM_Blockout_Fondale` | X −16388,3..33000 · Y −30000..30341,2 · Z −300..2130,9 | 517 | 53 | 53 |
| `SM_Blockout_PalmaSegnaposto` | X ±300 · Y ±300 · Z 0..1000 | 38 | 1 | 1 |

- Tutte le bbox coincidono con quelle attese entro 1 uu. Con più mesh per FBX **tutti** gli UCX diventano primitive
  convesse dell'asset combinato. Nessuna mesh UCX visibile.
- Materiali importati dall'FBX: `M_Blockout_Pietra`, `M_Blockout_Verde`, `M_Blockout_Ponte`, `M_Blockout_Fondale`.
  Su `M_Blockout_Pietra` e `M_Blockout_Verde` è stato attivato *Used with Instanced Static Meshes*, che serve per le palme in HISM.
- Nanite: l'import lo lascia **disattivato** su tutti e 5 gli asset, al contrario dei test di scala. Va bene così per il mobile.
- LOD: l'import generava 3 LOD automatici, con LOD1/LOD2 dimezzati (Passeggiata 121→63, Ponte 408→102). Gli override MinLOD = 2
  su Low e Medium (mobile e Switch) avrebbero mostrato quelle versioni rovinate. Le LOD sono state **rimosse** (resta solo LOD0)
  e gli override MinLOD sono stati azzerati.
- Collisione: Project Default (`CTF_UseDefault`), profilo `FortStaticMesh` sugli attori.

## Attori nel livello (cartelle Outliner)

| Cartella | Label | Tipo | Trasformazione |
|---|---|---|---|
| `Blockout` | `Blockout_Passeggiata`, `Blockout_Ponte`, `Blockout_Mirabello`, `Blockout_Fondale` | FortStaticMeshActor | (0,0,0), rot 0, scala 1 |
| `Blockout/Sostituiti` (era `Blockout`) | `Blockout_Palme_HISM` | Actor + HierarchicalInstancedStaticMeshComponent (53 istanze di `SM_Blockout_PalmaSegnaposto`, Static, profilo `FortStaticMesh`) | dal 2026-11-19 a (0,0,−10000), nascosto in gioco, collisione off: sostituito da `Arte_Palme_PalmaA` (`docs/uefn_arte.md`) |
| `Acqua` | `Acqua_Golfo_Device` | Device Acqua V2 (`PID_CP_Devices_Water_V2`) | (8500, 9550, **−484**) dal 2026-11-19 (prima −534) |
| `Device/Spawn` | `Player 1 Spawn Pad`, `Player 2 Spawn Pad` (con i PlayerStart figli) | Device del template | vedi sotto |
| `Device/Barriere` | 6 × `Barriera_*` | Barrier device (`PID_Device_Barrier`) | vedi sotto |
| `Luci` | `Luce_OraDelGiorno` | Device Sequenza giorno (`PID_DaySequence_Device`), ora fissa 18,0 | (24000, −10500, 0) |
| `Template_Spostati` | `GridPlane1-4` | GridPlane del template | spostati a Z −10000 |

Palme: verifica a campione contro `exports/blockout/palme_posizioni.csv`. Istanze 0, 26 e 52 (`Palma_F1_01` (1200, −9260, 0),
`Palma_F1_27` (24600, −9260, 0), `Palma_F2_26` (24150, −9960, 0)) identiche alla CSV, yaw 0. Una line trace orizzontale a Z 100
colpisce il tronco a 23 uu dal centro, cioè la collisione UCX del tronco (Ø 50, sezione poligonale).

## Spawn (partenza)

| Pad | Posizione pad | Yaw pad | PlayerStart (world) | Yaw PlayerStart |
|---|---|---|---|---|
| Player 1 | (24000, −8250, 0) | 30 | (23998, −8255, 116) | **180** (verso il ponte, −X) |
| Player 2 | (24000, −8650, 0) | 30 | (23998, −8655, 116) | **180** |

- In LUF: Player 1 Left 8250 · Up 0 · Forward 24000.
- Il PlayerStart e la freccia ForwardDirection del pad sono ruotati di +150° rispetto al pad. Per avere i giocatori rivolti a −X
  il pad va quindi a **yaw 30**, non 180.
- Ingombro dei pad: X 23751..24128, Y −8378..−8122 e −8778..−8522. Restano sul camminamento (ciglio Y −8000, cordolo Y −8900).
- Line trace verso il basso sotto i PlayerStart e ai bordi dei pad: pavimento a Z 0.

## Acqua

- **Device Acqua V2** (`Acqua_Golfo_Device`), tipo "Predefinito", attivo in fase **Sempre**.
  Volume X −17100..34100 · Y −11954..31054 · Z −484..**−100** (superficie a −100, profondità 384 uu). Nessuna onda.
  **2026-11-19 (decisione dell'utente):** superficie alzata da −150 a −100 spostando il device da Z −534 a −484. Ciglio a 1,0 m
  sull'acqua, come il modulo `SM_Banchina_Mod4m`. Barriere (base −700) ancora sotto il fondo. Dettagli in `docs/uefn_arte.md` §6.
  Le righe sotto che citano −150 o −534 descrivono lo stato del 2026-11-18.
  Larghezza 100 unità, profondità 84 unità, altezza 1 unità (1 unità = 512 uu in pianta e 384 uu in altezza).
- Copre il mare davanti alla passeggiata, il molo, il tratto sotto il ponte, Mirabello e anche la tasca senza geometria
  oltre la fine del blocco (X 25000..33000, Y −11800..−8200). Sotto le terre emerse è nascosta, perché camminamento e
  fondale hanno la faccia superiore a Z ≥ 0 e la base a Z −300.
- Il device crea da sé un `BP_FortWaterBodyCubeVolume` (water body Fortnite, materiale `/FortWater/.../M_Water_Pool_01_Inst`).
- **Perché non un Water Body Lake/Ocean nativo:** è stato provato un `WaterBodyLake` (spline rettangolare a Z −150, senza onde,
  WaterZone automatica). Si vedeva bene, ma il validatore UEFN (`AssetValidator_AssetReferenceRestrictions`) segnala riferimenti
  illegali a `/Water/...` (materiale, curve, post-process, DrawWaterInfo) e a `/FortWater/.../HLODWater`. Con quegli errori
  l'isola non si può caricare. L'attore e la sua WaterZone (creati in questo task) sono stati rimossi. Il device è la soluzione
  supportata, più leggera (un volume a scatola) e stabile.
- Da verificare in sessione (qa-tester): galleggiamento e nuoto, e risalita dal mare sul ciglio a Z 0 (1,5 m sopra l'acqua).

## Barriere invisibili

Barrier device, forma Scatola, materiale **Invisibile**, attive in fase **Sempre**, *Collisione con visuale* = NO,
altezza 10 unità (3840 uu). Base a Z −700, sotto il fondo dell'acqua, quindi non si passa a nuoto sotto la barriera.
La sommità è a Z 3140. Rotazione 0. Il lato mare resta aperto.

| Label | Centro (X, Y, Z) | Larg. × Prof. (unità) | Ingombro X | Ingombro Y |
|---|---|---|---|---|
| `Barriera_LatoCitta` | (11850, −11930, −700) | 60 × 0,5 | −3510..27210 | −12058..−11802 (subito oltre la siepe, Y −11600..−11800) |
| `Barriera_FineBlocco` | (25130, 10930, −700) | 0,5 × 90 | 25002..25258 | −12110..33970 (dalla siepe attraverso tutto il mare; modificata il 2026-11-19, prima era Y −12110..−6990) |
| `Barriera_Molo_AreaMilitare` | (−1360, −4340, −700) | 0,5 × 30 | −1488..−1232 | −12020..3340 (dal lato città fino oltre la riva dell'area militare, Y ≈ 2300) |
| `Barriera_Mirabello_LatoPiuX` | (1110, 18875, −700) | 0,5 × 12 | 982..1238 | 15803..21947 |
| `Barriera_Mirabello_LatoMenoX` | (−2150, 18875, −700) | 0,5 × 12 | −2278..−2022 | 15803..21947 |
| `Barriera_Mirabello_Fondo` | (−520, 21880, −700) | 7 × 0,5 | −2312..1272 | 21752..22008 |

**Chiusura della fine blocco (2026-11-19).** Prima si poteva aggirare `Barriera_FineBlocco` a nuoto (finiva a Y −6990),
passare oltre X 25258 e risalire sul fondale cittadino a Z 0, che continua fino a X 33000 mentre `Barriera_LatoCitta`
finisce a X 27210. Ora `Barriera_FineBlocco` ha profondità 90 unità (46080 uu) e attraversa tutto il volume d'acqua
(acqua Y −11954..31054, barriera Y −12110..33970). Verifica dai componenti `BarrierBounds`, scala (0,5, 90, 10) e (60, 0,5, 10):
- le due barriere si sovrappongono in X 25002..25258 · Y −12058..−11802, quindi all'angolo non c'è varco;
- oltre X 25258 non si arriva più né da terra né dall'acqua; la base a Z −700 resta sotto il fondo dell'acqua (Z −534);
- trace verticali a X 25130: fondale (Z 0) solo per Y ≤ −12000, altrove solo acqua. La barriera comincia subito dopo la fine
  del camminamento (X 25000) e 8,7 m oltre il bordo degli spawn pad (X 24128), quindi non tocca la corsia.

Sulle due barriere lunghe (`Barriera_LatoCitta`, `Barriera_FineBlocco`) *Influenza della distanza dissolvenza* è ora **NO**.
Il centro di `Barriera_FineBlocco` è a ~190 m dalla partenza: con SÌ la barriera rischierebbe di disattivarsi
oltre la distanza di dissolvenza. Le barriere non hanno collisione in modalità Crea, quindi le line trace in editor non le vedono.
Che blocchino davvero va confermato in sessione (qa-tester).

Le tre barriere di Mirabello chiudono la testata (X −2020..980, Y 16800..21740) su tre lati. Il lato verso il ponte resta aperto.
I due lati partono 10 m in acqua (Y 15800).

## Island Settings

Attore `IslandSettings0` (`Device_ExperienceSettings_V2_UEFN`). Valori scritti con `DeviceToolset.SetClassicDeviceOption`
e riletti con `ListClassicDeviceOptions` il 2026-11-19 (decisione dell'utente):

| Opzione | Valore letto | Note |
|---|---|---|
| Consenti costruzione (`AllowBuilding`) | `None` (NESSUNO) | prima era TUTTI |
| Preset locomozione (`LocomotionPreset`) | `Current BR` (BR ATTUALE) | invariato |
| Consenti scatto (`bAllowSprinting`) | `True` (SÌ) | non modificabile finché il preset non è PERSONALIZZATO; lo scatto lo dà il preset BR |
| Moltiplicatore velocità scatto | 1,4× | dal preset |

## Ora del giorno e luce (2026-11-19)

Problema dalla QA del 2026-11-19: il ciclo giorno/notte del template era attivo e in sessione era notte.

**Soluzione:** device **Sequenza giorno** (`PID_DaySequence_Device`, classe `BP_DaySequenceModifier_Device_C`), label
`Luce_OraDelGiorno`, cartella `Luci`, a (24000, −10500, 0) nella fascia verde (in LUF: Left 10500 · Up 0 · Forward 24000).
Valori scritti con `DeviceToolset.SetClassicDeviceOption` e riletti con `ListClassicDeviceOptions`:

| Opzione | Valore letto |
|---|---|
| Abilita durante la fase (`EnableDuringPhase`) | `Always` (TUTTO) |
| Modalità ciclo giorno-notte (`DayNightCycleMode`) | `FixedTime` (ORARIO FISSO) |
| Tempo ciclo giorno-notte (`DayNightCycleTime`) | `18.000000` |
| Priorità | 2000 (predefinita) |
| Usa volume | NO, quindi vale su tutta l'isola |
| Override luce sole / nebbia / luce cielo / cielo / nuvole | tutti NO: sole, colore e cielo restano quelli della sequenza del template (`DSA_UEFN_Ch5S1`) |

- Island Settings "Orario" (`TimeOfDayOverride`): provato a 17:00, poi rimesso a `NoOverride` (PREDEFINITO). Offre solo ore
  intere, in editor non si vede l'effetto e due fonti per l'ora potrebbero entrare in conflitto. L'ora la decide solo il device.
- **Sole letto in editor** (componente `Sun` dell'attore di sequenza, che il device pilota anche nell'anteprima): l'ora del device
  passa per una curva della sequenza (18,0 → tempo interno 16,13). Direzione della luce (0,66, 0,59, −0,46): **elevazione 27,2°**,
  il sole sta verso −X/−Y (lato ponte e lato città). Intensità 12,96, colore (255, 219, 168), quindi leggermente caldo.
  Confronto: 17,0 → 35,7° · 17,5 → 31,6° · 18,0 → 27,2°. Scelto 18,0 per le ombre più lunghe: è ancora giorno pieno.
- **Orientamento:** il sole reale da ovest, nel sistema del progetto (asse X ad azimut 41,3°), sta verso −X e −Y, cioè dal ponte
  e dal lato città, **non** dal mare. La sequenza del template alle 18 lo mette già lì: la luce arriva con azimut 42° in UE, contro
  i ~34-44° del sole reale tra le 17 e le 18 d'estate. Non è stato necessario ruotarlo.
- **Ombre:** cadono verso +X/+Y, cioè verso il mare. Le palme (Y −9260 e −9960) proiettano sul camminamento (Y −8000..−8900)
  ombre lunghe circa 19 m (13 m in Y), che lo attraversano tutto. Render con ombre attive (768 px):
  `docs/qa/uefn_ora18_partenza.png` (dalla partenza (24000, −8450, 180), yaw 145, verso il ponte, con le 2 antenne visibili) e
  `docs/qa/uefn_ora18_palme.png` (da (17000, −3000, 1500) verso la città: le ombre dei filari attraversano la corsia).
- Per ruotare il sole a mano servirebbe *Override luce sole* = SÌ (`SunlightRotationZ`/`SunlightRotationX`), che però sostituisce anche
  intensità (10) e colore (bianco) della sequenza. Per ora non serve.
- Il device non ha mesh visibile in gioco. Attori salvati (`Luce_OraDelGiorno`, `IslandSettings0`, cartella `Luci`), nessun pacchetto
  rimasto da salvare. Validazione del livello: 0 errori, 0 avvisi. Nel log non ci sono errori legati a DaySequence.
- **Da verificare in sessione** (prova manuale): che sia giorno e che l'ora non avanzi (nel log client la `DaySequence` dovrebbe
  restare ferma).

## Linea di vista e render

- Line trace dagli occhi alla partenza (24000, −8450, 180) verso le due antenne ((−230, 8020) e (−380, 12850)) a Z 1000, 2000 e 3000.
  Tutte le tracce arrivano sull'antenna (impatto a 20-65 uu dal bersaglio): niente le copre, né palme né barriere.
- Render (1024 px, ombre attive) in `docs/qa/`:
  - `uefn_blockout_dallalto.png`: zenitale da Z 42000 centrata su (9000, 5000). In alto c'è +X, a destra +Y.
  - `uefn_blockout_partenza.png`: altezza occhi dalla partenza verso il ponte (yaw 148, pitch 3). Le due antenne sono visibili.
  - `uefn_blockout_obliqua.png`: vista d'insieme da (30000, −20000, 9000).
  - `uefn_blockout_mirabello.png`: ponte e testata di Mirabello.

## Template

- `GridPlane1-4` erano a Z 0 (faccia superiore) e coprivano X/Y ±12800, cioè anche il mare sotto il ponte e davanti al molo.
  Sono stati **spostati a Z −10000**, cartella `Template_Spostati`, e non cancellati: decide l'utente.
- Gli spawn pad del template sono stati spostati alla partenza (vedi sopra). Nessun attore del template è stato cancellato.

## Problemi aperti

1. **Attore palme HISM:** è un `Actor` generico con un HISM aggiunto da Python. Nell'editor funziona (collisione e istanze OK)
   e il validatore non segnala nulla. Va però confermato in una sessione di gioco (qa-tester) che le palme compaiano e collidano.
   Se non funziona, il ripiego sono 53 StaticMeshActor in `Blockout/Palme`.
2. **Fondale calpestabile:** l'area militare (X < −1300, Y < 2300) e il terreno attorno a Mirabello sono a Z ≈ 0, cioè 1,5 m sopra
   l'acqua. Chi cade in mare può nuotare fin lì e forse risalire. Le barriere chiudono gli accessi da terra, ma non tutta la riva.
   È previsto che il rientro dall'acqua entro 3 s (Verse, Fase 2) risolva il problema. In alternativa servono altre barriere
   sulla riva o un bordo più alto nel fondale (blender-artist).
3. **Tasca senza geometria** oltre X 25000 tra il fondale (Y < −11800) e il mare: ora è coperta dall'acqua e chiusa dalla barriera
   di fine blocco, che dal 2026-11-19 attraversa tutto il mare. Se in futuro serve un bordo pulito, il fondale va esteso in Blender.
4. I materiali `M_Blockout_*` sono quelli dell'FBX (colori piatti). La pavimentazione è quasi bianca e sotto il sole radente
   abbaglia un po' nei render. Va bene per il blockout.
   Dal 2026-11-19 l'attore `Blockout_Passeggiata` ha un **override** dello slot `M_Blockout_Pietra` con `MI_Pav_Lastre`
   (proiezione in coordinate mondo, perché le UV del blockout sono nulle). L'asset non è stato modificato. Vedi `docs/uefn_arte.md` §5.
