# Arte v2 in UEFN (banchina, palme, pavimentazione)

Data: 2026-11-19 · Agente: uefn-builder · Livello: `/705655d7-c848-4957-8e94-8a1c399ddeea/LasPezia_Island` (salvato)
Coordinate in XYZ nativo Unreal (X avanti, Y destra, Z su). L'editor mostra LUF: Left = −Y, Up = Z, Forward = X.
Regola Blender → UE: UE = (B_X·100, −B_Y·100, B_Z·100), yaw UE = −rotZ Blender (`docs/scala.md`).
Stato del blockout, dell'acqua e dei device: `docs/uefn_blockout.md`.

## 1. Asset importati

Radice contenuti: `/705655d7-c848-4957-8e94-8a1c399ddeea/LaSpezia/Arte/` (Esplora contenuti: `LaSpezia/Arte`).
Import con `StaticMeshToolset.ImportFile` (`bCombineMeshes=true`, materiali e texture embedded attivi).

| Asset | Cartella | Tri LOD0 / LOD1 / LOD2 | Bbox locale (uu) | Convessi (= UCX) | Slot materiali |
|---|---|---|---|---|---|
| `SM_Banchina_Mod4m` | `Arte/Banchina` | 276 / 138 / 40 | X 0..400 · Y −55..0 · Z −300..0,19 → **400 × 55 × 300** | 1 (1 UCX) | `MI_Banchina_Ciglio`, `MI_Banchina_Paramento` |
| `SM_Banchina_Bitta` | `Arte/Banchina` | 970 / 484 / 144 | X ±20 · Y ±20 · Z −1,2..45,4 → **40 × 40 × 46,6** | 1 (1 UCX) | `MI_Banchina_Ghisa` |
| `SM_Banchina_Scaletta` | `Arte/Banchina` | 736 / 368 / 110 | X ±27,5 · Y −34,5..16 · Z −285..48,7 → **55 × 50,5 × 333,7** | 3 (3 UCX) | `MI_Banchina_Ghisa` |
| `SM_Morin_PalmaA` | `Arte/Palme` | 8.480 / 3.588 / 1.000 | X −458..544 · Y −490..520 · Z 0..1200 → **1002 × 1010 × 1200** | 1 (1 UCX, solo tronco) | `MI_Morin_PalmaA_Tronco`, `MI_Morin_PalmaA_Fronde` |

- Tutti i valori coincidono con quelli attesi entro 1 uu. Triangoli identici al report di blender-artist.
- Lato città del modulo = UE −Y (Blender +Y → UE −Y): verificato, il modulo va da Y origine a Y origine −55.
- La scaletta sporge 16 uu verso il mare (UE +Y) e ha i maniglioni 34,5 uu verso la città.
- Collisione: **Use Simple Collision As Complex** sui 4 asset (prima era Project Default). Così anche le query complesse
  (telecamera, proiettili) usano solo gli UCX: niente collisione per-poligono, chioma della palma senza collisione.
  Trace semplice e complessa danno risultati identici (vedi §4).
- Soglie LOD (screen size) 1,0 / 0,2 / 0,08, quelle di default dell'import. MinLOD 2 su Low e Medium (default UEFN), lasciato:
  sui preset bassi si vede il LOD2.
- **Nanite: spento su tutti e 4.** Motivi: banchina, bitta e scaletta hanno meno di 1k tri, quindi Nanite non porta vantaggi
  e i LOD scritti a mano funzionano meglio. La palma ha fronde masked su card, che con Nanite passano dal raster programmabile
  (overdraw costoso) e perderebbero i LOD fatti da blender-artist. Si rivaluta solo per il ponte (fino a 120k tri).

### LOD: problema di `import_lod` e soluzione
`StaticMeshEditorSubsystem.import_lod` (unico modo per importare un FBX come LOD di una mesh esistente) **non applica la Lcl Rotation −90°**
che `morin_export.py` scrive nei nodi. LOD1 e LOD2 arrivavano ruotati di 90° (LOD2 del modulo X 0..56 · Y 0..400 invece di
X 0..400 · Y −55..0): da lontano il ciglio appariva "a trattini" trasversali.
Soluzione applicata: ogni file `_LOD1`/`_LOD2` importato con `ImportFile` (che applica la rotazione) come asset temporaneo,
poi `set_lod_from_static_mesh(dest, lod, tmp, 0)`, rimappatura delle sezioni sugli slot originali (la copia aggiungeva slot
duplicati con WorldGridMaterial) e rimozione degli slot in più. Gli 8 asset temporanei (`LaSpezia/Arte/_TmpLOD`, creati in questo
task, nessun referencer) sono stati eliminati. Verificato: bbox di LOD0/1/2 coincidenti, sezioni dei LOD sugli slot giusti.
Il LOD2 del modulo sborda di 3 cm verso il mare e 4 cm verso la città (Y −59,4..+3,2): artefatto della decimazione, invisibile a distanza.

## 2. Texture

24 texture 2048 × 2048 (verificato con `GetSize`).

| Gruppo | Cartella | Origine | Impostazioni |
|---|---|---|---|
| `T_Banchina_{Ciglio,Paramento,Ghisa}_D`, `T_Morin_PalmaA_{Tronco,Fronde}_D` | Arte/Banchina, Arte/Palme | embedded negli FBX | sRGB, Default |
| `..._N` (stessi 5) | idem | `blender/textures/` (gli FBX contengono solo le diffuse) | **Normalmap**, sRGB off, nessun flip del verde (DirectX) |
| `..._ORM` (stessi 5) | idem | `blender/textures/` | **Masks**, sRGB off |
| `T_Pav_{Lastre,Cubetti,Fascia}_{D,N,ORM}` | Arte/Pavimentazione | `blender/textures/` | D sRGB; N Normalmap; ORM Masks |

`T_Morin_PalmaA_Fronde_D` è RGBA (alfa delle fronde, PNG color type 6): usato come opacity mask.

## 3. Materiali

Cartella `Arte/Materiali`: tre master con parametri, tutti con *Used with Instanced Static Meshes* e *Used with Nanite*.

| Master | Tipo | Grafo |
|---|---|---|
| `M_Morin_Master_PBR` | Opaco | UV0 × `UV_Tiling` → BaseColor × `Tinta`; Normal (tangente); ORM: R → AO, G × `Roughness_Mult` → Roughness, B → Metallic |
| `M_Morin_Master_PBR_Masked` | **Masked, Two Sided**, clip 0,33 | come sopra + alfa della BaseColor → Opacity Mask |
| `M_Morin_Master_Pav` | Opaco, normale in spazio mondo | UV in **coordinate mondo** / (`Tile_m` × 100): XY sulle facce orizzontali, (X+Y, Z) su quelle verticali; normal map applicata solo sulle facce orizzontali (sulle verticali la normale del vertice). Non dipende dalle UV della mesh |

Material instance (prefisso `MI_`, standard UE per le istanze; i master hanno `M_`):

| Istanza | Master | Texture | Parametri |
|---|---|---|---|
| `MI_Banchina_Ciglio` / `_Paramento` / `_Ghisa` | PBR | T_Banchina_*_D/N/ORM | — |
| `MI_Morin_PalmaA_Tronco` | PBR | T_Morin_PalmaA_Tronco_* | — |
| `MI_Morin_PalmaA_Fronde` | PBR_Masked | T_Morin_PalmaA_Fronde_* | — |
| `MI_Pav_Lastre` / `MI_Pav_Cubetti` | Pav | T_Pav_*_* | `Tile_m` 3,2 |
| `MI_Pav_Fascia` | Pav | T_Pav_Fascia_* | `Tile_m` 1,0 |

I materiali creati dall'import FBX (`M_Banchina_Ciglio`, `M_Banchina_Paramento`, `M_Banchina_Ghisa`, `M_Morin_PalmaA_Tronco`,
`M_Morin_PalmaA_Fronde`: solo diffusa) non sono più usati dalle mesh. Restano nel progetto: si possono eliminare con conferma.

**Costo.** `MaterialCostToolset.GetCost` non misura: manca il percorso del Mali Offline Compiler
(*Editor Preferences > Material Editor > Offline Shader Compilers*), azione dell'utente. Lo skill `MaterialCostOptimizationSkill`
restituisce istruzioni vuote. Ripiego: `MaterialToolset.GetStatistics` (piattaforma di valutazione ES3.1):

| Materiale | Istr. pixel | Istr. vertex | Campionatori | Campioni pixel |
|---|---|---|---|---|
| `M_Morin_Master_PBR` (e MI) | 213 | 289 | 3 | 3 |
| `M_Morin_Master_PBR_Masked` (e MI fronde) | 219 | 289 | 3 | 3 |
| `M_Morin_Master_Pav` (e MI) | 213 | 284 | 3 | 6 (conteggio del percorso mobile) |
| confronto: `M_Blockout_Pietra` | 186 | 284 | 0 | 3 |
| confronto: `M_Banchina_Ciglio` (dall'FBX, sola diffusa) | 189 | 289 | 1 | 1 |

Circa +15 % di istruzioni rispetto al blockout, per un PBR completo con 3 texture: costo contenuto. Una sola permutazione
per master, perché non ci sono static switch.

## 4. Attori posati (cartelle Outliner `Arte/Banchina`, `Arte/Palme`)

Ogni gruppo è un `Actor` con un `HierarchicalInstancedStaticMeshComponent` (Static, profilo `FortStaticMesh`), come le palme
segnaposto del blockout. Attori in (0,0,0).

**Retta del ciglio.** Il ciglio del blockout non è a Y −8000 fisso: segue la coastline OSM (Y 80,5 → 79,1 m).
Misurata con 30 line trace a Z −50: **Y = −8044,16 + 0,0021664·X** (yaw 0,1241°, residuo < 0,05 uu) da X ≈ 1920 a 25000.
Prima di X 1920 c'è lo smusso a 45° verso il molo del ponte. I moduli seguono questa retta **8 uu più verso il mare**
(Y = −8036,16 + 0,0021664·X): il paramento del modulo rientra di 6 cm sotto il ciglio, quindi così copre la faccia verticale grigia
del blockout (2 cm di margine). In questo tratto il ciglio sta tra Y −8032 e −7983, a non più di 3,6 cm dalla quota OSM.

**Quota.** La faccia superiore del modulo è inclinata e ha piccoli dislivelli fra i blocchi (da −2,7 a +0,2 cm). Per non
compenetrare il pavimento del blockout (Z 0) né fare z-fighting, i moduli stanno a **Z +2,5**. La collisione del ciglio è a Z 2,0,
quindi il gradino col pavimento è di 2 cm. Quando arriverà la mesh di pavimentazione l'offset va tolto.
**Aggiornamento 2026-11-19 (kit pavimentazione, §11):** offset tolto. Moduli a Z 0, bitte a Z −1,2, scalette a Z −1,3; collisione del ciglio a Z −0,5.

| Attore | Mesh | Istanze | Posizioni chiave |
|---|---|---|---|
| `Arte_Banchina_Moduli` | SM_Banchina_Mod4m | **58** | origine prima istanza (1920, −8032,0, 2,5), ultima (24720, −7982,6, 2,5), passo 400 lungo la retta, yaw 0,1241°. Copertura X 1920..25120 (l'ultimo modulo sporge 1,2 m oltre la fine del pavimento, dentro `Barriera_FineBlocco`, non raggiungibile) |
| `Arte_Banchina_Bitte` | SM_Banchina_Bitta | **18** | X 2600..23000 ogni 1200 (12 m), centro 30 uu dal ciglio verso la città (Y = retta − 30), Z 1,3, yaw 0,1241°. L'ultima bitta è a 7,5 m dagli spawn pad (X 23751) |
| `Arte_Banchina_Scalette` | SM_Banchina_Scaletta | **4** | X 4400, 9200, 14000, 18800 (passo 48 m, sempre a metà fra due bitte); Y −8026,6 / −8016,2 / −8005,8 / −7995,4; Z 1,2. La più vicina agli spawn pad è a 49,5 m |
| `Arte_Palme_PalmaA` | SM_Morin_PalmaA | **53** | posizioni di `exports/blockout/palme_posizioni.csv` (filari a Y −9260 e −9960), yaw casuale 0-360°, scala uniforme 0,9-1,1 (seme 20261119) |

Palme segnaposto: `Blockout_Palme_HISM` **non cancellato**. Spostato a Z −10000, *nascosto in gioco*, collisione disattivata,
cartella Outliner `Blockout/Sostituiti`.

### Verifiche con line trace (semplice e complessa identiche)
- Modulo: top a Z 2,0 (X 10000, Y −8030 e −8060); faccia lato mare a Z −50 su Y −8014,5 (X 10000), −7982,4 (X 24800), −8031,8 (X 2000),
  cioè sul ciglio.
- Bitta (X 5000): fianco a 16,8 uu dal centro, sommità Z 47,1. È alta 0,47 m, oltre il gradino massimo di 0,40 m:
  si salta, non si scavalca camminando (come previsto in `ref/banchina.md` §5).
- Scaletta (X 9200): pioli colpiti a Y −8000,2 da mare (Z −50), maniglione colpito a Z 30.
- Palma 0 (1200, −9260): tronco colpito a Z 100 (raggio 39 uu) e a Z 700; **nessun impatto a Z 1000 e 1100 nella chioma**.

## 5. Pavimentazione sul blockout

Le UV di `SM_Blockout_Passeggiata` sono tutte (0,0) (lette dalla mesh description): un materiale basato su UV non si può applicare.
Il master `M_Morin_Master_Pav` proietta invece in coordinate mondo. Provato a vista: sulle facce orizzontali nessuna deformazione,
con le lastre a scala corretta (lati lunghi trasversali alla passeggiata); sulle facce verticali (molo, cordolo) la proiezione
(X+Y, Z) evita le strisce stirate.

**Come è applicato (dal 2026-11-19, 06:14 UTC).** `MI_Pav_Lastre` è assegnato allo slot `M_Blockout_Pietra` (indice 1) di una **copia
dell'asset**, `LaSpezia/Blockout/SM_Blockout_Passeggiata_Arte` (duplicata da `SM_Blockout_Passeggiata`: stessa geometria, 121 tri,
bbox X −1230..25000 · Y −11800..8980 · Z −300..150, stessa collisione). L'attore `Blockout_Passeggiata` punta alla copia e **non ha più
override**. L'asset originale non è stato toccato: per tornare indietro basta ripuntare l'attore a `SM_Blockout_Passeggiata`.
Line trace semplici e complesse su corsia, fascia palme e molo: impatto a Z 0 su `Blockout_Passeggiata`, come prima.
Render: `docs/qa/uefn_arte_v2_lastre_asset.png`.
Limite noto: lo slot Pietra copre anche la fascia delle palme (Y −8900..−10200), che oggi mostra lastre invece dei cubetti.

### Problema risolto: lastre invisibili in sessione (grigio del blockout)
- **Sintomo** (prova dell'utente, sessione `@3` delle 06:04 UTC): in gioco il pavimento era il grigio di `M_Blockout_Pietra`; in editor si vedevano le lastre.
- **Causa:** l'override era **solo in memoria**. Il pacchetto OFPA dell'attore
  (`__ExternalActors__/LasPezia_Island/4/ZR/QVW7OHB54ZLHC2SCCL2SYW.uasset`) su disco era fermo al **18-11 22:19 UTC** e non conteneva
  né `MI_Pav_Lastre` né `OverrideMaterials`, mentre l'editor non lo segnava come modificato: il materiale era stato impostato con una
  chiamata che non marca il pacchetto come "dirty", quindi `save_dirty_packages` lo ha saltato. Sessioni e push cuociono i pacchetti
  salvati, quindi il client ha ricevuto l'attore senza override. Tutti gli altri attori toccati (moduli, bitte, scalette, palme, acqua,
  segnaposto) erano salvati alle 05:55: per questo in gioco funzionavano.
- **Escluso il materiale:** nel log del client delle sessioni `@3` e `@4` nessun errore o avviso `LogMaterial` sui contenuti del progetto
  (solo avvisi Nanite su materiali di Epic) e nessun materiale di default al loro posto. La libreria shader del progetto è passata da
  **47 shader** (`@3`, master Pav non referenziato da nessun pacchetto salvato, quindi non cotto) a **51** (`@4`, dopo la correzione).
- **Verifica del salvataggio:** dopo la correzione il pacchetto dell'attore è stato riscritto (06:13:59 UTC) e contiene il riferimento
  a `SM_Blockout_Passeggiata_Arte`; l'asset copia (06:13:38 UTC) contiene `MI_Pav_Lastre`. Nessun pacchetto rimasto da salvare.
- **Push:** `PushChanges` sulla sessione già aperta (nessuna nuova sessione). Cottura `@4` server e client "a success" alle 06:15 UTC.
- **Regola per il futuro:** dopo ogni modifica via Python a un attore fare `actor.modify()`/`component.modify()` (o una
  `ScopedEditorTransaction`) prima di cambiare proprietà, e controllare che il file `.uasset` del pacchetto OFPA abbia la data nuova.
`MI_Pav_Cubetti` e `MI_Pav_Fascia` sono pronti per le mesh di pavimentazione di blender-artist.

## 6. Acqua

Il device `Acqua_Golfo_Device` è stato spostato da Z −534 a **Z −484**; il `BP_FortWaterBodyCubeVolume_C` figlio lo segue.
- Superficie (`WaterSpline`) a **Z −100** (prima −150); fondo a Z −484; profondità invariata 384 uu (Altezza 1 unità). Pianta invariata
  (X −17100..34100, Y −11954..31054).
- Il ciglio è a 1,0 m sull'acqua (1,025 m con l'offset): coincide col modulo, che ha la fascia bagnata/alghe fra Z −1,6 e −0,7.
- Le barriere (base Z −700) restano sotto il fondo dell'acqua (Z −484). Paramenti del modulo e del blockout scendono fino a Z −300,
  sotto la superficie.
- Sotto il ponte e davanti alla testata di Mirabello l'acqua è continua: la pianta del volume non cambia e il render
  `uefn_arte_v2_acqua_mirabello.png` non mostra buchi.

## 7. Linea di vista e render

- Trace dalla partenza (24000, −8450, 180) alle due antenne a Z 1000/2000/3000: tutte colpiscono `Blockout_Ponte` a 18-65 uu
  dal bersaglio. Le fronde non hanno collisione, quindi è stato fatto anche un controllo geometrico: sfera di chioma
  r 5,2 m × scala a Z 10 m × scala per ognuna delle 53 palme. La chioma più vicina resta a **6,7 m** dalle linee di vista,
  perché la vista verso il ponte va verso il mare (+Y) mentre i filari sono dal lato città.
- Render 1024 px con ombre (`docs/qa/`):
  - `uefn_arte_v2_partenza.png`: dalla partenza verso il ponte (yaw 148), antenne visibili, bitte sul ciglio, lastre.
  - `uefn_arte_v2_ciglio.png`: dettaglio dal mare di ciglio, paramento, bitta e scaletta (X ≈ 9200) con le palme dietro.
  - `uefn_arte_v2_filare.png`: altezza occhi lungo la corsia verso il ponte, filare a destra.
  - `uefn_arte_v2_filare_alto.png`: vista alta dal mare sul filare e sul ciglio continuo (dopo la correzione dei LOD).
  - `uefn_arte_v2_ponte.png`: dalla corsia (X 9000) verso il ponte, bitta in primo piano.
  - `uefn_arte_v2_molo.png`: molo e facce verticali con la pavimentazione proiettata.
  - `uefn_arte_v2_acqua_mirabello.png`: acqua a −1 m sotto il ponte e davanti alla testata.

## 8. Memoria e dimensioni

- **Project Size** (`ValkyrieProjectSize.fetch_project_size_stats`): riporta l'**ultima versione cotta e inviata**, cioè solo il blockout,
  531 KB in download e 518 KB in upload. L'arte nuova entra nel conteggio solo dopo una sessione o un push, che in questo task non si
  potevano avviare. Limiti letti (`fetch_project_limits`): memoria di pubblicazione 314.572.800 byte (300 MiB), download 400 MiB,
  upload 2 GiB, 20.480 file.
- Su disco: `Content/LaSpezia/Arte` = **103 MB** (non cotto, comprende i dati sorgente delle texture). Tutto `Content` ≈ 104 MB.
- Stima della memoria texture a piena risoluzione: 8 normal BC5 da ~5,3 MiB, 7 diffuse BC1 da ~2,7 MiB più le fronde BC3 da ~5,3 MiB,
  8 ORM BC1 da ~2,7 MiB, tutte con i mip. Totale **≈ 88 MiB**, di cui ≈ 67 MiB referenziati dal livello (Cubetti e Fascia
  non sono ancora usati). Le mesh pesano poco: 4 asset, meno di 11k tri al LOD0.
  Da rileggere con Project Size e Memory Calculation dopo la prossima sessione.

## 9. Salvataggio, validazione, log
- `save_dirty_packages`: nessun pacchetto rimasto da salvare.
- `ValidateAssets` su 44 asset di `LaSpezia/Arte` + mappa: 45 controllati, 45 validi, 0 errori, 0 avvisi. `EditorValidatorSubsystem`
  sui 7 attori toccati: tutti VALID.
- Log: gli errori `AssetReferenceRestrictions` ("riferimento a un pacchetto non salvato") delle 05:49-05:50 erano transitori
  (texture appena importate e non ancora salvate); dopo il salvataggio la validazione è pulita. Gli avvisi "missing usage flag Nanite"
  sulle MI venivano dal render delle anteprime (nessuna mesh è Nanite): flag attivato sui master. Restano avvisi di geometria
  su Bitta e Scaletta (vedi §10).

## 10. Problemi aperti
1. **(blender-artist)** `SM_Banchina_Bitta` e `SM_Banchina_Scaletta`: "normali e bi-normali quasi nulle", e sulla scaletta anche
   "basi tangenti degeneri" (MikkTSpace). Probabili triangoli degeneri o vertici duplicati: da pulire in Blender.
2. **(blender-artist)** Per i LOD conviene esportare i file `_LOD1/_LOD2` con la rotazione −90° **applicata ai vertici** (senza
   Lcl Rotation nel nodo), così un futuro `import_lod` diretto funziona. Oggi c'è il giro con gli asset temporanei (§1).
3. **(blender-artist)** Testata/angolo del ciglio: a X 1920 l'estremità del primo modulo resta a vista verso lo smusso a 45°
   del blockout; a X 25120 l'ultimo modulo finisce nel vuoto (dietro la barriera). Serve il pezzo d'angolo già in PLAN.
4. ~~**(blender-artist)** Mesh di pavimentazione~~ → kit v1 posato il 2026-11-19 (§11). Testo originale: la fascia delle palme oggi mostra lastre (slot Pietra unico del blockout, ora sulla copia
   `SM_Blockout_Passeggiata_Arte`). Con la mesh dedicata si ripunta l'attore e si toglie l'offset Z +2,5 dei moduli.
5. **(utente)** Impostare il percorso del Mali Offline Compiler per avere `GetCost`.
6. **(qa-tester, in sessione)** Palme e bitte HISM visibili e solide in gioco; risalita dalle scalette; nuoto con l'acqua a −1 m;
   rilettura di Project Size e memoria dopo la cottura.
7. I materiali `M_Banchina_*`/`M_Morin_PalmaA_*` creati dall'import FBX non sono usati: si possono eliminare (serve conferma).

## 11. Kit pavimentazione v1 (2026-11-19, 10:10-10:25 UTC)

Sorgenti: `exports/pavimentazione/*.fbx`, posizioni `exports/pavimentazione/pav_posizioni.csv`, blockout `exports/blockout/SM_Blockout_Passeggiata_Pav.fbx`.

### Import
`StaticMeshToolset.ImportFile` con **materiali e texture disattivati** (`bImportMaterials=false`): gli slot arrivano col nome del materiale
Blender e WorldGridMaterial; **nessuna texture né materiale duplicato creato** (le 2048 incorporate negli FBX non sono state importate).
L'import genera 3 LOD automatici su ogni mesh: rimossi con `RemoveLods` prima di mettere quelli manuali.
Nanite spento (`nanite_settings.enabled = False`; nota: `IsNaniteMesh` risponde True anche sugli asset banchina, noti come non Nanite: non è affidabile).
**Use Simple Collision As Complex** su tutti.

| Asset | Cartella | Tri LOD0/1/2 | Bbox locale (uu) | Convessi | Slot → MI |
|---|---|---|---|---|---|
| `SM_Pav_Camminamento_4m` | Arte/Pavimentazione | 2 (nessun LOD, deroga) | X 0..400 · Y −870..−54 · Z 0 | 1 (Z −30..0) | Lastre → `MI_Pav_Lastre` |
| `SM_Pav_FasciaPalme_9m` | Arte/Pavimentazione | 50 (nessun LOD, deroga) | X 0..900 · Y −10200..−8915 · Z 0 | 1 (Z −30..0) | Cubetti → `MI_Pav_Cubetti`, Fascia → `MI_Pav_Fascia` |
| `SM_Pav_Cordolo_9m` | Arte/Pavimentazione | 76 / 26 / 18 | X 0..900 · Y −8915..−8845 · Z −15..3 | 2 (striscia Y −8885..−8845 top 1,2; cordolo Y −8915..−8885 top 3,0) | Fascia → `MI_Pav_Fascia` |
| `SM_Pav_Aiuola` | Arte/Pavimentazione | 64 / 26 / 18 | X ±110 · Y ±110 · Z −3..6 | 1 (top 4,5) | Fascia → `MI_Pav_Fascia`, Terra → `MI_Pav_Terra` |
| `SM_Morin_Panchina` | Arte/Pavimentazione | 240 / 104 / 32 | X ±110 · Y ±25 · Z 0..45 | 1 (top 45) | Fascia → `MI_Pav_Fascia` |
| `SM_Blockout_Passeggiata_Pav` | Blockout | 128 | X −1230..25000 · Y −11800..8980 · Z −300..150 | **13** (= 13 oggetti UCX nell'FBX) | Pietra → `MI_Pav_Lastre`, Verde → `M_Blockout_Verde` |

Triangoli e bbox coincidono col report di blender-artist. Soglie LOD 1,0 / 0,2 / 0,08 (come la banchina). MinLOD Low/Medium:
2 sui tre asset con LOD (default UEFN), **0** su camminamento, fascia e blockout (con un solo LOD il valore 2 dava un avviso di validazione).

**LOD.** `import_lod` diretto (file `_LOD1/_LOD2` con rotazione applicata ai vertici) ha dato LOD **ruotati di +90°**
(cordolo LOD1 X 8845..8915 · Y 0..900; panchina LOD1 X ±25 · Y ±110). La rotazione nei vertici non basta: `import_lod` non applica
la conversione d'assi di `ImportFile`. Corretto col metodo del §1: `ImportFile` in `Arte/_TmpLOD` + `set_lod_from_static_mesh(..., reuse_existing_material_slots=True)`
dopo aver messo sugli slot dei temporanei le stesse MI. Verificato: bbox dei LOD1/LOD2 identici al LOD0, vertici dei LOD contenuti
in quelli del LOD0 (cordolo LOD1 100 %), sezioni sugli slot giusti, nessuno slot in più. I 6 temporanei (creati in questo task,
nessun referencer) e la cartella `_TmpLOD` sono stati eliminati.

**Blockout, UCX.** Nell'FBX ci sono 13 oggetti `UCX_SM_Blockout_PassPav_*` (Aiuole 6, Lastra 4, Molo 2, SiepeLimite 1), non 17: in UEFN 13 convessi.
Il convesso del tratto X 1020..1920 resta con la faccia a **Z 0** anche dove la mesh è ribassata a −15 (X 975..1920, Y −8845..−10200):
innocuo, perché lì sopra ci sono fascia e cordolo con collisione a Z 0 / +1,2 / +3, ma è un'incoerenza da segnalare a blender-artist.
Avvisi di import su `SM_Blockout_Passeggiata_Pav`: "basi tangenti degeneri" e "normali/bi-normali quasi nulle" (MikkTSpace).

### Texture e materiali
- `T_Pav_Terra_D` (sRGB), `_N` (Normalmap, sRGB off, nessun flip), `_ORM` (Masks, sRGB off), 2048 × 2048, da `blender/textures/`.
- `MI_Pav_Terra` su `M_Morin_Master_Pav`, `Tile_m` 2,0.
- **Tinta lastre.** Il master ha già il parametro vettoriale `Tinta` (moltiplica la BaseColor): nessuna modifica al master.
  Misure (media sRGB, lette con Blender in background): texture `T_Pav_Lastre_D` 191/189/180 (albedo lineare 0,52/0,49/0,43);
  `passegiata_1.png` (zona del pavimento, cielo coperto) 194/189/182; `pav_1.png` (sera, ombra) 143/143/144.
  L'albedo era troppo alto per una pietra grigia e con la luce delle 18 virava al rosa/malva. `MI_Pav_Lastre.Tinta` = **(0,60; 0,56; 0,48)**:
  albedo medio ≈ 0,31/0,28/0,20 lineare, grigio-bruno. Provata prima (0,60; 0,60; 0,63): più scura ma ancora fredda/violacea.
  Confronto: `docs/qa/uefn_pav_v1_lastre_prima.png` / `uefn_pav_v1_lastre_dopo.png` (stessa camera, X 100 m).
  La tinta vale anche per il blockout (`SM_Blockout_Passeggiata_Pav`, slot Pietra), quindi per molo e tratto X < 9,75 m.

### Posa (cartella Outliner `Arte/Pavimentazione`)
Attori ottenuti duplicando `Arte_Banchina_Moduli` (stessa struttura: `Actor` + `HierarchicalInstancedStaticMeshComponent`, Static,
profilo `FortStaticMesh`), in (0,0,0), istanze dal CSV.

| Attore | Mesh | Istanze | Note |
|---|---|---|---|
| `Arte_Pav_Camminamento` | SM_Pav_Camminamento_4m | **58** | X 1920..24720, Y −8032,0..−7982,61, Z 0, yaw 0,1241° (come i moduli banchina) |
| `Arte_Pav_FasciaPalme` | SM_Pav_FasciaPalme_9m | **27** | X 975 + 900·k (ultima 24375, copre fino a 25275), Y 0, yaw 0 |
| `Arte_Pav_Cordolo` | SM_Pav_Cordolo_9m | **27** | come la fascia |
| `Arte_Pav_Aiuole` | SM_Pav_Aiuola | **53** | ai piedi delle 53 palme (Y −9260 e −9960) |
| `Arte_Pav_Panchine` | SM_Morin_Panchina | **4** | X 34,5 / 43,5 / 52,5 / 61,5 m, Y −9340 |

Contemporaneamente: `Arte_Banchina_Moduli` Z 2,5 → **0**, `Arte_Banchina_Bitte` 1,3 → **−1,2**, `Arte_Banchina_Scalette` 1,2 → **−1,3** (tutte le istanze).
`Blockout_Passeggiata` (FortStaticMeshActor) ora usa **`SM_Blockout_Passeggiata_Pav`**, nessun override; `SM_Blockout_Passeggiata` e `_Arte` restano nel progetto.
Ogni modifica preceduta da `modify()` su attore e componente dentro `ScopedEditorTransaction`. Nota: `unreal.Rotator(a, b, c)` è (roll, pitch, yaw):
la prima posa del camminamento aveva lo yaw finito nel pitch, corretta subito con argomenti nominati (verificato: roll 0, pitch 0, yaw 0,1241).

**Salvataggio.** 20 pacchetti salvati (6 mesh, MI e 3 texture, 9 pacchetti OFPA, 1 external object); tutti i `.uasset` OFPA degli attori toccati
hanno data 10:17:26-27 UTC; quello di `Blockout_Passeggiata` (`4/ZR/QVW7OHB54ZLHC2SCCL2SYW.uasset`) contiene il riferimento a
`SM_Blockout_Passeggiata_Pav`, quello del camminamento a `SM_Pav_Camminamento_4m`. Poi salvati `MI_Pav_Lastre` (tinta) e i MinLOD. Nessun pacchetto sporco.

### Verifiche
Line trace (semplice e complessa identiche):

| Punto | Impatto |
|---|---|
| Camminamento (X 100/200 m, Y −84/−85 m) | Z 0, `Arte_Pav_Camminamento` |
| Raccordo ciglio/lastre: retta−54,5 e retta−56 | Z 0, camminamento; ciglio (retta−30/−50) Z −0,5, `Arte_Banchina_Moduli` |
| Striscia tattile (Y −88,55) | Z +1,2; cordolo (Y −88,85/−89,05) **Z +3,0**, uguale da X 9,8 a 108 m |
| Fascia palme (Y −96/−101,5 e sul filare) | Z 0, `Arte_Pav_FasciaPalme` (anche a X 15 m e 251 m) |
| Aiuola (terra e bordo) | Z +4,5 (un solo UCX: la terra visiva è a +2,5/+4, il bordo a +6) |
| Panchina | Z +45 |
| Oltre Y 102 | Z +40, siepe del blockout (invariata) |

Scansione a griglia 100 × 25 uu da X 9,8 a 250 m, dal ciglio a Y −101,95 m (circa 21.000 trace): **nessun buco**, nessun impatto sotto Z −1,
il blockout ribassato a −15 non è mai il primo impatto; il blockout a Z 0 è colpito solo nel tratto previsto X < 19,2 m, Y > −88,45 m.
Z-fighting: al raccordo X 9,75 m il blockout passa da Z 0 a −15 esattamente a X 975 (vertici letti dalla mesh), dove iniziano fascia e cordolo;
a Y 102 fascia (Z 0) e giardino del blockout si toccano solo lungo lo spigolo, senza facce sovrapposte. Nei render nessuno sfarfallio.
Linea di vista dalla partenza (24000, −8450, 180) alle antenne (−220, 8040) e (−370, 12860) a Z 10/20/30 m: tutte su `Blockout_Ponte`
a 25-52 uu dal bersaglio, **invariata**.

Render 1024 px con ombre (`docs/qa/`): `uefn_pav_v1_partenza.png` (partenza verso il ponte), `uefn_pav_v1_aiuole_alto.png` (vista alta su aiuole,
fasce e panchina), `uefn_pav_v1_ciglio.png` (ciglio dal mare con bitta, lastre, cordolo), `uefn_pav_v1_cordolo.png` (striscia tattile e cordolo),
`uefn_pav_v1_lastre_prima.png` / `_dopo.png` (tinta).

Validazione: `ValidateAssets` su 55 asset (`LaSpezia/Arte` + blockout nuovo + mappa): 55 validi, 0 errori, 0 avvisi (dopo la correzione dei MinLOD).
`EditorValidatorSubsystem` sui 10 attori Arte_* e `Blockout_Passeggiata`: VALID. Log dell'editor: nessun errore nuovo legato al progetto
(solo avvisi di import su tangenti del blockout e "LOD pattern mismatch" di Interchange sui nomi `_LOD1/_LOD2`, innocuo).

### Sessione e memoria
Sessione avviata (`StartSession`, Connected, cottura 10:21 UTC, lasciata aperta). Libreria shader del progetto: **51 shader** (come prima: nessun master nuovo).
Client: nessun avviso `LogMaterial` sui materiali del progetto.
**Project Size** (ultima versione cotta, v5 del 10:21:24): download **12.688.568 byte (12,1 MiB)**, upload 122.023.684 byte (116 MiB),
di cui texture 10,8 MB in download. Pavimentazione in download: texture circa 4,9 MB, mesh 44 KB, blockout nuovo 28 KB.
Limiti: memoria di pubblicazione 300 MiB, download 400 MiB. Project Size non dà la memoria; stima texture a piena risoluzione
con i mip: circa 99 MiB (88 + 10,7 delle 3 Terra), ora tutte referenziate dal livello. Il calcolo di memoria esatto resta da fare dal pannello dell'utente.

### Problemi aperti (pavimentazione)
1. **(blender-artist)** `import_lod` continua a ruotare i LOD di +90° anche con `bake_rotation`: o si accetta il metodo dei temporanei
   (funziona, documentato), o va provato un export dei LOD senza la rotazione −90°. Non bloccante.
2. **(blender-artist)** `SM_Blockout_Passeggiata_Pav`: UCX del tratto X 10,2-19,2 m non ribassato (vedi sopra); tangenti degeneri e normali quasi nulle.
   Nel brief si parlava di 17 UCX, nell'FBX sono 13.
3. **(blender-artist/utente)** Fascia e cordolo arrivano a X 252,75 m, 2,75 m oltre la fine del blockout (X 250): come l'ultimo modulo banchina,
   finiscono nella zona della `Barriera_FineBlocco`.
4. **(utente)** `MI_Pav_Cubetti` nei render appare violaceo/rosato come le lastre prima della correzione: da confrontare con le foto
   (stesso parametro `Tinta`). Non toccato perché fuori dal task.
5. Cordolo a +3 cm lasciato come richiesto ([S], in attesa di conferma dell'utente).
6. **(qa-tester)** Prova in sessione: percorrenza su cordolo, aiuole (+4,5) e panchine; nessun inciampo al raccordo ciglio (−0,5 cm).

## 12. Pavimentazione v2/v3 e arredi (2026-11-19, 11:27-11:45 UTC)

Sorgenti: `exports/pavimentazione/` (cordolo, fascia, aiuola, panchina), `exports/arredi/` (lampione, tombino),
**`exports/arredi/gazebo_v3/`** (gazebo; quello in `exports/arredi/` è la v2 superata). Posizioni `pav_posizioni_v3.csv` e `palme_posizioni_v3.csv`.
Ripresa del tentativo interrotto alle 11:16 UTC (finestra modale): nessun asset né attore cancellato.

### Metodo di import che funziona (sostituire il contenuto di un asset esistente)
1. **Import da zero con nome nuovo** in `LaSpezia/_Temp` con `StaticMeshToolset.ImportFile` (`bImportMaterials/bImportTextures=false`,
   `bCombineMeshes=true`): passa da `FbxFactory`, applica la conversione d'assi e porta gli UCX. Un file per LOD0, `_LOD1`, `_LOD2`.
   Controllo bbox e convessi su ogni temporaneo prima di usarlo.
2. Sugli slot dei temporanei e dell'asset di destinazione si mettono **le stesse MI** (stesso nome di slot).
3. Sull'asset esistente (stesso percorso, quindi HISM e riferimenti restano validi): `StaticMeshEditorSubsystem.remove_lods`, poi
   `set_lod_from_static_mesh(dest, i, tmp_i, 0, reuse_existing_material_slots=True)` per i = 0, 1, 2 (funziona anche sul LOD0).
4. Collisione: `dest.body_setup.set_editor_property('agg_geom', tmp.body_setup.agg_geom)` + `collision_trace_flag = CTF_USE_SIMPLE_AS_COMPLEX`.
   Verificato con `export_text()` (identico al temporaneo) e con line trace in editor.
5. `nanite_settings.enabled = False`, `set_lod_screen_sizes([1.0, 0.2, 0.08])`. Tutto dentro `ScopedEditorTransaction` con `modify()`.

**Da NON usare:** `AssetImportTask` senza factory esplicita (passa da Interchange: ignora `FbxImportUI`, ruota di 90°, perde gli UCX, ha messo
Nanite on sulla panchina); reimport/sostituzione con `FbxFactory` o `replace_existing` (può aprire la finestra modale che blocca l'editor e
lascia comunque la mesh ruotata); `import_lod` (ruota i LOD di +90°). `ImportFile` rifiuta nomi esistenti: per questo il giro dei temporanei.
`StaticMesh.post_edit_change()` non esiste in Python: non serve, `set_editor_property` notifica da solo.

### Asset (verificati in editor; bbox per LOD letta con GeometryScript dalla mesh sorgente di ogni LOD)
| Asset | Cartella | Tri LOD0/1/2 | Bbox (uu) | Convessi = UCX | Slot → MI |
|---|---|---|---|---|---|
| `SM_Pav_Cordolo_9m` | Arte/Pavimentazione | 74 / 24 / 20 | X 0..900 · Y −8915..−8845 · Z −15..15 (tutti i LOD) | 2 | Fascia → `MI_Pav_Fascia` |
| `SM_Pav_FasciaPalme_9m` | Arte/Pavimentazione | 36 (nessun LOD) | X 0..900 · Y −10200..−8915 · Z −15..15 | 1 | Cubetti → `MI_Pav_Cubetti`, Fascia → `MI_Pav_Fascia` |
| `SM_Pav_Aiuola` | Arte/Pavimentazione | 64 / 26 / 18 | X ±180 · Y ±150 · Z −3..2 (tutti) | 1 | Fascia, Terra → `MI_Pav_Fascia`, `MI_Pav_Terra` |
| `SM_Morin_Panchina` | Arte/Pavimentazione | 306 / 134 / 42 | X ±140 · Y ±25 · Z 0..45 (tutti) | 1 | Fascia → `MI_Pav_Fascia` |
| `SM_Morin_Lampione` | Arte/Arredi | 2.400 / 1.078 / 294 | X ±74 · Y ±19 · Z 0..482 (LOD1 Y ±18,1, LOD2 Y ±16,5: globi decimati) | 2 (base + fusto) | Ghisa → `MI_Morin_Ghisa`, Globo → `MI_Morin_Globo` |
| `SM_Morin_Tombino` | Arte/Arredi | 20 / 4 / 4 | X ±88,2 · Y ±30,2 · Z −1..0,4 (LOD1/2: due quad a Z 0,4, X ±87 · Y ±29) | 1 (Z −5..0) | Tombino → `MI_Morin_Tombino` |
| `SM_Morin_Gazebo` (v3) | Arte/Arredi | 2.570 / 1.392 / 432 | X ±200 · Y ±173,2 · Z 0..512 (tutti) | 16 | Ghisa, Fregio, Fascia → `MI_Morin_Ghisa`, `MI_Morin_Gazebo_Fregio`, `MI_Pav_Fascia` |

Tutti: Nanite off, Use Simple Collision As Complex, soglie LOD 1,0 / 0,2 / 0,08 (fascia: solo 1,0), MinLOD Low/Medium 2 (fascia 0),
sezioni di ogni LOD sugli slot giusti, numero di slot invariato.

### Texture e materiali
- `T_Morin_Tombino_D/N/ORM` 1024 × 1024 e `T_Morin_Gazebo_Fregio_D/N/ORM` 2048 × 512 (alfa nella D) in `Arte/Arredi`, da `blender/textures/`;
  N = Normalmap senza flip, ORM = Masks, sRGB off.
- `MI_Morin_Ghisa`: `M_Morin_Master_PBR` con `T_Banchina_Ghisa_*`, Tinta (0,42; 0,50; 0,60).
- `MI_Morin_Tombino`: `M_Morin_Master_PBR` con `T_Morin_Tombino_*`.
- `MI_Morin_Gazebo_Fregio`: `M_Morin_Master_PBR_Masked` (two-sided, clip 0,33) con `T_Morin_Gazebo_Fregio_*`.
- `MI_Morin_Globo`: **nuovo master `Arte/Materiali/M_Morin_Master_Emissivo`** (opaco; `Colore` → BaseColor, `Roughness`, `Colore × Emissivo` → Emissive;
  usage ISM e Nanite), perché i master PBR non hanno emissivo. MI: Colore (0,85; 0,85; 0,82), Emissivo 0,5, Roughness 0,3.
  Libreria shader del progetto in sessione: 51 → **55 shader**.
- **`MI_Pav_Cubetti.Tinta`** (1; 1; 1) → **(0,62; 0,58; 0,52)**. Misure (Blender in background, valori sRGB): `pav_palme.png` cubetti al sole
  181/166/157 e 190/178/171 (grigio-bruno caldo, R > G > B), texture `T_Pav_Cubetti_D` 92/93/95 (neutra, appena fredda): con la luce
  delle 18 il render virava al malva. Provata (0,80; 0,74; 0,58): troppo beige-arancio. Render `uefn_pav_v3_cubetti_prima.png` / `_dopo.png` (stessa camera).

### Posa (Outliner: `Arte/Pavimentazione`, `Arte/Palme`, nuova `Arte/Arredi`)
| Attore | Mesh | Istanze | Note |
|---|---|---|---|
| `Arte_Pav_Cordolo`, `Arte_Pav_FasciaPalme` | cordolo, fascia | 27 + 27 | posizioni invariate (X 975 + 900·k) |
| `Arte_Pav_Aiuole` | SM_Pav_Aiuola | **54** | dal CSV v3, Z 15 |
| `Arte_Pav_Panchine` | SM_Morin_Panchina | **13** | X 1650 + 1800·k, Y −9210, Z 15 |
| `Arte_Palme_PalmaA` | SM_Morin_PalmaA | **54** | `palme_posizioni_v3.csv`, Z 15; yaw/scala con `random.Random(20261119)` in ordine di CSV (`uniform(0,360)`, poi `uniform(0.9,1.1)`): stesso generatore di prima (prima palma −74,13° / 1,041) |
| `Arte_Arredi_Lampioni` (nuovo HISM) | SM_Morin_Lampione | **7** | X 1680 + 3600·k, Y −9285, Z 15 |
| `Arte_Arredi_Tombini` (nuovo HISM) | SM_Morin_Tombino | **8** | dal CSV, yaw 0 / −180 |
| `Arte_Arredi_Gazebo` (FortStaticMeshActor) | SM_Morin_Gazebo | 1 | (2550, −9300, 15), yaw 0 |

Nuovi HISM ottenuti duplicando `Arte_Banchina_Moduli` (Actor + HISM, profilo `FortStaticMesh`, attore in 0,0,0). Mobilità dei componenti di
aiuole e panchine portata da **Movable a Static** (come palme, moduli e arredi nuovi). Camminamento e banchina non toccati.

### Verifiche (line trace e sweep in editor, semplice = complessa)
- Cordolo a X 10/20/50/120/200/249 m: lastre Z 0 → striscia tattile +1,2 → cordolo **+15** → fascia +15: gradino 15 cm ovunque (< 40 cm).
- Inizio fascia: X 9,70 m blockout Z 0; X 9,80 m fascia +15 e striscia +1,2 (testata a X 9,75).
- Bordo Y 102: fascia +15 fino a Y −101,9; oltre, siepe del blockout a +40 (gradino 25 cm) o varchi dei giardini a Z 0 (gradino 15 cm in discesa).
- Aiuola: bordo e terra +17 (UCX top +2), fuori impronta fascia +15. Panchine +60 (top 45 + 15), larghezza ±25 verificata.
- Lampioni: fusto colpito a Z 100, 353 e 393 (UCX del fusto fino in cima); trace verticali a ±55 cm dal fusto (bracci e globi) colpiscono la fascia:
  **globi e bracci senza collisione**.
- Tombini a raso: UCX Z −5..0 locale, cioè a filo della fascia (+15); il trace vede la fascia.
- Gazebo: 6 colonne colpite a Z 150 (r ≈ 1,73 m) e plinti a Z 40 (r ≈ 1,80 m); 3 panchine interne +60; tetto da sopra Z 487 (convesso unico, Z mondo 303..487).
  Sweep di capsula r 32 / hh 75: giro attorno a r 2,3 / 2,6 / 3,0 m **nessun impatto** (la gronda è sopra la capsula); a r 3,3 m tocca le aiuole vicine
  (distanza netta 0,7 m, come da Blender). Entrata verso il centro **libera dai tre varchi a 30°, 150°, 270°**; dagli altri tre lati le panchine
  fermano la capsula a r 1,62 m, verso le colonne a r 2,12 m. Uscita dal centro libera dagli stessi tre varchi. Nessuna sovrapposizione iniziale
  in 6 punti interni; salto al centro fermato dal tetto con la testa a Z 303, nessun incastro.
- Palme: tronco colpito a Z 100, 400 e 700 su **54 / 54** (ventaglio di trace su ±3 m); chioma senza collisione (Z 1050 nessun impatto).
- Linea di vista dalla partenza (24000, −8450, 180) alle antenne a Z 10/20/30 m: `Blockout_Ponte` a 25-52 uu dal bersaglio, **invariata**.
  Distanza minima delle linee da lampioni e gazebo 11 m; margine minimo delle chiome (sfere r 5,2 m × scala) 6,85 m.
- Z-fighting: nessuna faccia complanare a vista (aiuole +0,8/+2 cm, tombino +0,4 cm; i 72 vertici del gazebo a Z 0 sono fondi di plinti e panchine,
  facce rivolte in basso). Nei render nessuno sfarfallio.

### Render (1024 px, ombre, `docs/qa/`)
`uefn_pav_v3_occhi.png` (altezza occhi dalle lastre verso panchina e lampione, confronto con `113500`), `uefn_pav_v3_alto.png` (vista alta della fascia),
`uefn_pav_v3_gazebo.png` (confronto `gazzebo2.png`), `uefn_pav_v3_dalponte.png` (dal molo del ponte: prime palme e gazebo), `uefn_pav_v3_partenza.png`
(antenne visibili), `uefn_pav_v3_cubetti_prima.png` / `_dopo.png`.

### Salvataggio, validazione, sessione
- Alle 11:35:50 UTC un `InternalPromptForCheckoutAndSave` non lanciato da questo agente (probabilmente "Salva tutto" dall'editor) ha salvato i pacchetti
  sporchi di quel momento (mesh già corrette, MI, texture, temporanei). Il resto (tinta cubetti, 7 pacchetti OFPA, 1 external object) è stato salvato con
  `save_dirty_packages` alle 11:40:49 UTC. Date dei `.uasset` controllate su disco; **nessun pacchetto sporco** rimasto.
- `ValidateAssets` su `LaSpezia/Arte` + mappa: 68 controllati, 68 validi, 0 errori, 0 avvisi. `EditorValidatorSubsystem` sui 9 attori Arte_Pav/Arredi/Palme: VALID.
  Log: nessun errore o avviso nuovo sul progetto (solo deprecazioni Python e avvisi di rete/EOS).
- `PushChanges` sulla sessione aperta: cottura v6 server e client completata (11:43:32 UTC). **Project Size v6**: download **13.647.813 byte (13,0 MiB)**,
  upload 124.950.798 byte (119 MiB); texture 11,4 MB in download, mesh 1,45 MB. I temporanei di `_Temp` non sono referenziati e non entrano nella cottura.

### Temporanei in `LaSpezia/_Temp` (non cancellati, per regola dell'utente; nessun referencer)
- Di questo task (19): `TMP3_SM_Pav_Cordolo_9m` (+`_LOD1`, `_LOD2`), `TMP3_SM_Pav_FasciaPalme_9m`, `TMP3_SM_Pav_Aiuola` (+2), `TMP3_SM_Morin_Panchina` (+2),
  `TMP3_SM_Morin_Lampione` (+2), `TMP3_SM_Morin_Tombino` (+2), `TMP3_SM_Morin_Gazebo` (+2, da `gazebo_v3`).
- Del tentativo interrotto (14): `TMP_SM_Pav_Cordolo_9m_LOD1/2`, `TMP_SM_Pav_Aiuola_LOD1/2`, `TMP_SM_Morin_Panchina_LOD1/2`, `TMP_SM_Morin_Lampione_LOD1/2`,
  `TMP_SM_Morin_Tombino_LOD1/2`, `TMP_SM_Morin_Gazebo_LOD1/2` (gazebo v2), `TMP_Test_Panchina_FFX_0`, `TMP_Test_Panchina_FFX_1`.
Si possono eliminare in blocco quando l'utente lo conferma.

### Problemi aperti
1. **(qa-tester)** Prova in sessione: gradino del cordolo, ingresso nel gazebo dai tre varchi, panchine, lampioni, palme alle posizioni nuove.
2. **(utente)** Tinta dei cubetti (0,62; 0,58; 0,52) da confermare a occhio; idem `MI_Morin_Globo` (emissivo 0,5, all'ora 18 quasi invisibile).
3. **(utente)** Pulizia di `_Temp` (33 asset) e dei vecchi `M_Banchina_*`/`M_Morin_PalmaA_*` non usati: serve conferma.
4. Siepe del blockout a +40 dietro la fascia (+15): gradino di 25 cm, salibile; da sostituire con la fascia verde vera.
