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

## 13. Radice del molo v2 (2026-11-19, 18:05-18:15 ora locale)

Sorgenti: `exports/molo/` (32 FBX), posizioni `exports/molo/molo_posizioni_v1.csv`, texture `blender/textures/molo/`.
Controllo iniziale: nessun asset né attore con questi nomi in UEFN. Nessun attore esistente spostato, nascosto o cancellato.

### Metodo (variante del §12 per asset nuovi)
- LOD0 importati **direttamente con il nome finale** (`StaticMeshToolset.ImportFile`, materiali/texture off, combine on): il nome non esiste,
  quindi niente temporaneo per il LOD0. LOD1/LOD2 come `LaSpezia/_Temp/TMPM_<asset>_LOD1/2`, poi `set_lod_from_static_mesh`.
- **Nuova insidia:** ogni mesh importata con `ImportFile` arriva con **3 LOD generati automaticamente** e **MinLOD Low/Medium = 2**.
  Sempre `remove_lods` (anche sui pezzi unici), poi `set_lod_from_static_mesh` per LOD1/2, e reimpostare il MinLOD: su una mesh a 1 LOD
  il MinLOD 2 fa scattare l'avviso del validatore "valore minimo di LOD di 2 per Low non rientra nell'intervallo 0..0".
- Gli UCX arrivano con `ImportFile` anche sugli asset nuovi (convessi presenti subito, nessuna copia di `agg_geom` necessaria).
- Texture con `TextureToolset.ImportFile`: subito dopo l'import `blueprint_get_size_x()` di N/ORM restituisce 32 (segnaposto durante la
  ricompressione), poi 2048/1024 corretti. Le texture risultano già salvate all'import; per sicurezza ri-salvate con `save_asset(..., False)`.
- Nessuna mesh del kit usa il colore vertice (`morin_molo.py`): `ImportFile` va bene ovunque.
- Attori singoli duplicando `Arte_Arredi_Gazebo` (FortStaticMeshActor, profilo `FortStaticMesh`, Static), HISM duplicando
  `Arte_Arredi_Tombini` + `clear_instances()`; tutto in `ScopedEditorTransaction` con `modify()`.
- `line_trace_multi` si ferma al primo impatto bloccante: per vedere cosa c'è sotto un blockout usare `line_trace_single` con
  `actors_to_ignore` (il primo giro di verifica sembrava "edifici senza collisione": erano solo coperti dal blockout).
- Camera Blender → UE (`morin_molo.cameras()`: `fwd = (sin az, cos az)`): **yaw UE = atan2(cos az, −sin az)**; F1 az 199,7° → yaw **109,7°**,
  F3 az 213,4° → yaw 123,4°. `RenderLevelPOVs` fa solo immagini quadrate con FOV orizzontale: si usa lo stesso FOV della camera Blender.

### Asset (verificati in editor)
| Asset | Cartella | Tri LOD0/1/2 | Bbox (uu) | Convessi | Slot → MI |
|---|---|---|---|---|---|
| `SM_Molo_Pav_Strada` | Arte/Molo | 32 | X 650..2400 · Y −12100..−8600 · Z −15..15 | 3 | Asfalto, Fascia → `MI_Molo_Asfalto`, `MI_Pav_Fascia` |
| `SM_Molo_Pav_Masselli_01` | Arte/Molo | 29 | X −810..1020 · Y −12100..−6200 · Z 1 | 10 | `MI_Molo_Masselli_Grigio` |
| `SM_Molo_Pav_Masselli_02` | Arte/Molo | 4 | X −1210..999 · Y −6200..−3100 · Z 1 | 2 | `MI_Molo_Masselli` |
| `SM_Molo_Pav_Masselli_03` | Arte/Molo | 4 | X −1216..929 · Y −3100..0 · Z 1 | 2 | `MI_Molo_Masselli` |
| `SM_Pav_AngoloMolo` | Arte/Molo | 92 | X 955..2000 · Y −10925..−8915 · Z −15..15 | 3 | Cubetti, Fascia → `MI_Pav_Cubetti`, `MI_Pav_Fascia` |
| `SM_Molo_Edificio_A1A2` | Arte/Molo | 412 / 220 / 52 | X −808..99 · Y −10782..−9862 · Z 0..465 | 3 | `MI_Molo_Facciate` |
| `SM_Molo_Edificio_A3` | Arte/Molo | 466 / 244 / 26 | X −627..146 · Y −9886..−6794 · Z 0..415 | 2 | `MI_Molo_Facciate` |
| `SM_Molo_Edificio_A4A5` | Arte/Molo | 2.558 / 1.458 / 334 | X −636..26 · Y −6806..−6194 · Z 0..497 | 1 | `MI_Molo_Facciate` |
| `SM_Molo_Edificio_C` | Arte/Molo | 430 / 236 / 90 | X −1218..−742 · Y −4228..−2472 · Z 0..462 | 1 | `MI_Molo_Facciate` |
| `SM_Molo_Tendone` | Arte/Molo | 128 / 108 / 84 | X −835..75 · Y −11696..−11115 · Z 0..314 | 7 | `MI_Molo_Facciate` |
| `SM_Molo_Lampione2Globi` | Arte/Molo | 1.880 / 988 / 268 | X ±45 · Y ±45 · Z −1..728 | 2 | Ghisa, Globo, Fascia → `MI_Morin_Ghisa`, `MI_Morin_Globo`, `MI_Pav_Fascia` |
| `SM_Albero_LatifogliaA` | Arte/Alberi | 7.540 / 3.701 / 1.179 | X −1101..990 · Y −958..859 · Z −1..2120 | 1 | `MI_Albero_Platano_Corteccia`, `MI_Albero_Latifoglia_Chioma` |
| `SM_Albero_LatifogliaB` | Arte/Alberi | 7.427 / 3.641 / 1.145 | X −846..807 · Y −904..871 · Z −3..1806 | 1 | idem |
| `SM_Morin_PinoDomestico` | Arte/Alberi | 3.388 / 1.659 / 673 | X −961..928 · Y −876..806 · Z −5..1754 | 1 | `MI_Morin_PinoDomestico_Corteccia`, `_Chioma` |

Bbox coerenti con la scheda (`ref/radice_molo.md` §10: asfalto Y 86-121, masselli 01/02/03 Y 62-121 / 31-62 / 0-31 a Z +0,01, angolo +0,15,
A3 Y 68-98,8, lampione 7,28 m): scala 1:1, nessuna rotazione di 90°. Bbox di LOD1/LOD2 uguali al LOD0 (temporanei controllati prima della copia).
Tutti: Nanite off, Use Simple Collision As Complex, soglie LOD 1,0 / 0,2 / 0,08 sui 9 asset con LOD; MinLOD Low/Medium 0 su suolo ed edifici,
2 su lampione e alberi (log decisioni).

Texture (21, da `blender/textures/molo/`): `Arte/Molo/T_Molo_{Masselli,Asfalto,Facciate}_{D,N,ORM}` 2048;
`Arte/Alberi/T_Albero_Latifoglia_Chioma_*`, `T_Morin_PinoDomestico_Chioma_*` 2048 (alfa nella D), `T_Albero_Platano_Corteccia_*`,
`T_Morin_PinoDomestico_Corteccia_*` 1024. N = Normalmap senza flip, ORM = Masks, sRGB off.
MI: `MI_Molo_Asfalto`, `MI_Molo_Masselli`, `MI_Molo_Masselli_Grigio` (Tinta 0,36/0,37/0,40), `MI_Molo_Facciate`, `MI_Albero_Platano_Corteccia`,
`MI_Morin_PinoDomestico_Corteccia` su `M_Morin_Master_PBR`; `MI_Albero_Latifoglia_Chioma`, `MI_Morin_PinoDomestico_Chioma` su
`M_Morin_Master_PBR_Masked` (two-sided, clip 0,33). Nessun master nuovo: libreria shader invariata.
Stima memoria delle texture nuove a piena risoluzione con i mip: circa 65 MiB (prima circa 99 MiB), totale stimato circa 165 MiB su 300.
Project Size non letto (nessuna sessione avviata in questo task).

### Posa (Outliner `Arte/Molo`, `Arte/Alberi`)
| Attore | Mesh | Trasformazione |
|---|---|---|
| `Arte_Molo_Pav_Strada`, `_Pav_Masselli_01/02/03`, `Arte_Pav_AngoloMolo`, `Arte_Molo_Edificio_A1A2/A3/A4A5/C`, `Arte_Molo_Tendone` | omonime | (0,0,0), yaw 0 (vertici in posizione mondo) |
| `Arte_Molo_Lampione2Globi_00` | SM_Molo_Lampione2Globi | (1300, −10600, 15), yaw 0 |
| `Arte_Alberi_PinoDomestico_00` | SM_Morin_PinoDomestico | (−1200, −11800, 0), yaw −40 |
| `Arte_Alberi_LatifogliaA` (HISM) | SM_Albero_LatifogliaA | 4 istanze dal CSV (Latifoglia_00/02/04/06) |
| `Arte_Alberi_LatifogliaB` (HISM) | SM_Albero_LatifogliaB | 3 istanze dal CSV (01/03/05) |

### Verifiche (line trace in editor)
- Griglia 100 × 200 uu su X −13..24 m, Y 0..122 m: suolo colpito sempre sulla nostra arte o sul blockout atteso; masselli a Z +1, angolo a +15.
- Collisioni: convessi letti da `agg_geom.export_text()` (es. A1A2 3 blocchi X −790..60, Z 0..380; A3 2 blocchi Z 0..340; C Z 0..387).
- Lampione: fusto colpito (r 24 uu), poggia sull'angolo a +15. Alberi: tronco colpito su 9/9 (r 40-52 uu); suolo Z 0 sul blockout del fondale.
- Mappa a caratteri della griglia (−30..24 m × 0..122 m): **gli edifici sono interamente dentro le scatole di `Blockout_Fondale`**
  (tetti delle scatole a Z 400/449/600/800), vedi problemi.

### Render (`docs/qa/`)
`uefn_molo_v2_F1.png` (camera F1, 1400 px quadrata, FOV 87°, ombre), da confrontare con `arte_molo_v2_F1.png`: lampione a 2 globi, angolo in cubetti,
asfalto e chiome delle latifoglie nella stessa posizione dell'inquadratura Blender; **i ristoranti non si vedono**, coperti dalla scatola bianca
del blockout; in primo piano la siepe verde del blockout del giardino (la camera a Y 118,4 sta dentro la fascia Y 116-118).
`uefn_molo_v2_F3.png` (camera F3): masselli chiari, edificio C con finestre e la scatola del blockout che sporge sopra il tetto.
`uefn_molo_v2_alto.png`: vista alta dal mare; masselli 01 grigi e 02/03 chiari, chiome dietro la scatola dei ristoranti.

### Salvataggio e validazione
`save_dirty_packages` alle 18:12:41 (40 pacchetti di contenuto + 16 della mappa/OFPA), date dei `.uasset` in `__ExternalActors__` controllate
(18:12:40); MinLOD corretti e risalvati, poi nessun pacchetto sporco. `validate_assets_with_settings` su `Arte/Molo` + `Arte/Alberi`:
**43 controllati, 43 validi, 0 avvisi**.

### Temporanei in `LaSpezia/_Temp` (non cancellati)
18 `TMPM_<asset>_LOD1/_LOD2` (edifici ×4, tendone, lampione, latifoglie A/B, pino). Nessun referencer; eliminabili con conferma dell'utente.

### Problemi aperti
1. **(utente/blender-artist)** `Blockout_Fondale` copre A1A2, A3, A4A5, C, tendone (scatole Z 4-8 m) e i tronchi di Latifoglia_02, _05, _06;
   `Blockout_Passeggiata` (siepe Y 116-118 a +40 e aiuole) copre asfalto e ramo verso il parcheggio (Y 112-121) e taglia la vista F1.
   Sono mesh uniche insieme al resto del blockout: o nuove versioni senza quelle scatole/siepe, o si nascondono gli attori interi. Serve conferma.
2. **(qa-tester)** Confronto F1 completo possibile solo dopo il punto 1; prova in sessione di cordolo dell'angolo (+15), lampione, tendone.
3. **(utente)** `MI_Molo_Masselli_Grigio` molto più scura dei masselli 02/03 nella vista alta: da confermare a occhio con F1/F2 dopo il punto 1.
4. Il primo `SM_Morin_Lampione` della pavimentazione a (16,8; 92,85) resta (scheda §10.4: in F1 non c'è); da togliere solo col layout palme v4.

## 14. Blockout ritagliati v2 (2026-11-19, 18:20-18:35 ora locale)

Sorgenti: `exports/blockout/SM_Blockout_Fondale_v2.fbx`, `exports/blockout/SM_Blockout_Passeggiata_Pav_v2.fbx` (blender-artist, PLAN.md voce 0).
Decisione dell'utente: **nessuna cancellazione**; attori nuovi accanto agli originali, originali nascosti in modo reversibile.

### Asset (`LaSpezia/Blockout`, import con `StaticMeshToolset.ImportFile`, nome nuovo, materiali/texture off, combine on)
| Asset | Tri | Bbox (uu) | Convessi | Slot → materiale |
|---|---|---|---|---|
| `SM_Blockout_Fondale_v2` | 557 (prima 517) | X −16388,3..33000 · Y −30000..30341,2 · Z −300..2130,9 | 57 (prima 53) | `M_Blockout_Fondale`, `M_Blockout_Verde` (come l'originale) |
| `SM_Blockout_Passeggiata_Pav_v2` | 128 | X −1230..25000 · Y −11800..8980 · Z −300..150 | 13 | Verde → `M_Blockout_Verde`, Pietra → `MI_Pav_Lastre` (come `_Pav`) |

- `ImportFile` ha aggiunto 3 LOD automatici e MinLOD Low/Medium 2: `RemoveLods` → **solo LOD0**, MinLOD Low/Medium **0**.
- Nanite off; collisione **Use Simple Collision As Complex** su entrambi (l'originale del fondale era "Project Default": portato al semplice
  come richiede CLAUDE.md §4, nessun per-poligono).
- Gli slot sono stati riconosciuti per nome dai materiali esistenti già all'import; sul Pav_v2 lo slot Pietra puntava a `M_Blockout_Pietra`
  ed è stato portato a `MI_Pav_Lastre`.
- Differenze dei convessi rispetto agli originali (lette da `agg_geom.export_text()`): tolte le scatole sopra C (X −1215..−752), A1A2/A3/A4A5
  (X −803..200, Y −10717..−6192) e tendone (X −809..53, Y −11681..−11157); scatole D/D3 spezzate con tacche ai tronchi; siepe (Y −11800..−11600,
  Z 0..150) da X 100 → **2000**, aiuola (Y −11600..−11100) da X 2000 → **2400**. Le lastre di suolo (Z 0) sono **identiche**: nessun buco.

### Attori (Outliner `Blockout`)
- `Blockout_Fondale_v2` → `SM_Blockout_Fondale_v2`, `Blockout_Passeggiata_v2` → `SM_Blockout_Passeggiata_Pav_v2`: duplicati degli originali
  (FortStaticMeshActor, profilo `FortStaticMesh`, Static, Query Only come gli originali), posa (0,0,0), yaw 0, scala 1, nessun override di materiale.
- **Originali nascosti, non cancellati né spostati**: `Blockout_Fondale`, `Blockout_Passeggiata` (mesh e materiali invariati, `.uasset` degli asset
  originali non toccati):
  - *Actor Hidden In Game* = sì;
  - componente mesh **Visible = falso** (nascosto in editor e in gioco, persistente);
  - componente **Collision Enabled = No Collision** e attore **Actor Enable Collision = no**.
- **Per riattivarli** (Details dell'attore, oppure Python in una transazione con `modify()`): `Visible` = vero sul componente
  `StaticMeshComponent0`, *Actor Hidden In Game* = no, *Collision Enabled* del componente = **Query Only** (com'era), *Actor Enable Collision* = sì.
  In quel caso nascondere allo stesso modo i due `_v2`, altrimenti le due versioni si sovrappongono.
- Le mesh originali restano referenziate dagli attori nascosti: restano nella cottura e nella memoria finché l'utente non conferma la cancellazione.

### Verifiche
- Line trace verticali (griglia 100 × 200 uu, X −30..24 m, Y 0..122 m): **0 impatti** sugli originali; gli edifici ora vengono colpiti
  sui loro tetti (A3 340, C 387, A1A2 380, A4A5 497, tendone 313); masselli +1, asfalto +1, angolo +15. I punti senza impatto sono solo
  mare (X > 9 m, Y 0..72 m), come prima (coperture del suolo identiche nei convessi).
- Trace ignorando edifici, tendone, alberi e lampione (X −12..3 m, Y 20..120 m, passo 1 m): **nessun buco**, suolo a Z 0 (`Blockout_Fondale_v2`,
  `Blockout_Passeggiata_v2`) o masselli a +1.
- Siepe residua (Z 150) solo da X 20 m e Y 116-118 m, fuori dall'asfalto (il ramo d'asfalto finisce a Y 113,75 + cordolo a 113,95).
- Primo piano di F1 (X 10-20 m, Y 114-118 m): è il poligono di suolo dello slot **Pietra** del Pav_v2 (Z 0, gruppo 1) con `MI_Pav_Lastre`:
  materiale e scala identici al camminamento (render zenitali di confronto senza ombre); l'ocra saturo della cattura F1 è la luce radente.
  Cosa ci sia davvero lì resta da decidere (PLAN.md).

### Render (`docs/qa/`, 1024 px, ombre)
- `uefn_molo_v2b_F1.png` (UE 1365, −11843, 284; pitch −2,92; yaw 109,7; FOV 87): ristoranti colorati visibili, niente scatola bianca né siepe.
- `uefn_molo_v2b_F3.png` (UE 445, −4640, 230; pitch −6,7; yaw 123,4; FOV 92,5): edificio C libero; la chioma della latifoglia in alto a destra
  poggia sul tetto della scatola D dietro.
- `uefn_molo_v2b_alto.png` (UE 1500, −4500, 1900; pitch −38; yaw −130; FOV 90): ristoranti, tendone e masselli liberi; **le chiome delle
  latifoglie entrano nei tetti delle scatole D/E** (Z 600-800) a sinistra. In F1 non si nota.

### Salvataggio e validazione
`save_dirty_packages` alle 18:34:29: 2 asset nuovi + 4 OFPA (`Blockout_Fondale`, `Blockout_Passeggiata`, i due `_v2`), date controllate su disco;
nessun pacchetto sporco. `validate_assets_with_settings` sui due v2: 2 controllati, 2 validi, **1 avviso atteso** (`ValkyrieValidator_StaticMesh`:
"mesh complessa con un solo LOD" su `SM_Blockout_Fondale_v2`, voluto: i blockout hanno solo LOD0). `EditorValidatorSubsystem` sui 4 attori: VALID.
Nessun `TMPM_*` toccato.

### Problemi aperti
1. **(utente)** Chiome basse delle latifoglie nei tetti delle scatole D/E del fondale (visibile in alto e F3).
2. **(utente/geo-scout)** Lastre del blockout in primo piano in F1 (Y 114-118 m): sostituirle con il suolo vero.
3. ~~**(utente)** Conferma per cancellare gli originali nascosti e le loro mesh.~~ Fatto, vedi §15.
4. **(qa-tester)** Prova in sessione: nessuna collisione invisibile nella zona ristoranti (gli originali ora non esistono più).

## 15. Pulizia di attori e asset superati (2026-11-19, ~20:05-20:10 ora locale, autorizzata dall'utente)

Metodo: per ogni asset, referencer letti subito prima della cancellazione (asset registry con riferimenti hard/soft/management e
`find_package_referencers_for_asset` con caricamento); cancellato solo se senza referencer o referenziato solo da altro in lista.
Cancellazione con `AssetToolset.Delete` (nessun force delete né replace references). Ricerca testuale nei `.uasset` del progetto
(281 file, OFPA inclusi) di `/_Temp/` e dei nomi v1: nessun riferimento esterno. Nessun file Verse nel progetto.

- **Attori:** `Blockout_Fondale` (OFPA `9/9Y/ZCPL2X6ABMHD8JEH00BQ5F`) e `Blockout_Passeggiata` (OFPA `4/ZR/QVW7OHB54ZLHC2SCCL2SYW`);
  nessun figlio né genitore, unico referencer la mappa. File OFPA rimossi dal disco al salvataggio. Attori nel livello: 84.
- **Mesh `LaSpezia/Blockout`:** `SM_Blockout_Fondale`, `SM_Blockout_Passeggiata_Pav` (referencer: solo i due attori sopra),
  `SM_Blockout_Passeggiata`, `SM_Blockout_Passeggiata_Arte` (nessun referencer). ~180 KB su disco.
- **`LaSpezia/_Temp`:** tutti i 130 asset (StaticMesh `TMP_*`, `TMP2_*`, `TMP3_*`, `TMPVC_*`, `TMPVC2_*`, `TMPTEST_*`, `TMP_Test_*`,
  18 `TMPM_*`), nessun referencer. 7,3 MB su disco. La cartella vuota resta per i prossimi import.
- **Materiali orfani:** `Arte/Banchina/M_Banchina_Ciglio`, `_Ghisa`, `_Paramento`, `Arte/Palme/M_Morin_PalmaA_Fronde`, `_Tronco`
  (dall'import FBX, sola diffusa, nessun referencer). Le loro texture `T_*_D` restano: le usano gli MI.
- **Tenuti:** `M_Blockout_Pietra` (usato da `SM_Blockout_Mirabello`, `SM_Blockout_PalmaSegnaposto`), `M_Blockout_Verde` e
  `M_Blockout_Fondale` (usati dai v2), `M_Blockout_Ponte`; attore `Blockout_Palme_HISM` e la sua mesh (non in lista).

Verifica: `save_dirty_packages`, nessun pacchetto sporco. Validazione di tutto `LaSpezia/`: 167 controllati, 167 validi, 0 errori,
10 avvisi già noti ("un solo LOD" su colline, `SM_Blockout_Fondale_v2`, `SM_Blockout_Ponte`). Log dalle 20:00: nessun
"Failed to load"/"missing" né errori legati agli asset cancellati. Render dall'alto della zona molo (ortografico, centro X 456,
Y −4380, larghezza 200 m): `docs/qa/uefn_pulizia_alto.png`, scena invariata (blockout v2, molo, alberi, palme presenti).

## 16. Chiosco-bar v2 e blockout passeggiata v3 (2026-11-19, 22:00-22:10 ora locale)

Sorgenti: `exports/chiosco/` (28 FBX), `exports/chiosco/chiosco_posizioni_v1.csv` (42 righe), texture `blender/textures/chiosco/`,
`exports/blockout/SM_Blockout_Passeggiata_Pav_v3.fbx`. Controllo iniziale: nessun asset né attore con questi nomi.
Metodo del §13 (LOD0 con il nome finale, LOD1/2 come `_Temp/TMPC_<asset>_LOD1/2` + `set_lod_from_static_mesh`, `remove_lods`, MinLOD,
Nanite off, Use Simple Collision As Complex, soglie 1,0 / 0,2 / 0,08). Nessun colore vertice nel kit (`morin_chiosco.py`).

### Asset (`LaSpezia/Arte/Chiosco`, salvo il blockout)
| Asset | Tri LOD0/1/2 | Bbox LOD0 (uu) | Convessi | Slot → MI | MinLOD Low/Med |
|---|---|---|---|---|---|
| `SM_Morin_Chiosco` | 2.776 / 1.288 / 100 | X ±270 · Y −270..295 · Z 0..368,1 (5,40 × 5,65 × 3,68 m) | 3 | `MI_Morin_Chiosco` | 2 |
| `SM_Morin_Ombrellone` | 910 / 304 / 126 | X ±250 · Y ±200 · Z 0..306 | 3 | `MI_Morin_Dehors` | 2 |
| `SM_Morin_Fioriera` | 222 / 116 / 50 | X −59..53 · Y −49..67 · Z 0..178 | 1 | Dehors, `MI_Albero_Latifoglia_Chioma`, `MI_Morin_PinoDomestico_Chioma` | 2 |
| `SM_Morin_FiorieraB` | 182 / 96 / 46 | X −67..62 · Y −67..61 · Z 0..162 | 1 | idem | 2 |
| `SM_Morin_FiorieraC` | 206 / 106 / 48 | X −57..65 · Y −42..58 · Z 0..180 | 1 | idem | 2 |
| `SM_Morin_TavoloSet` | 672 / 450 / 324 | X ±91 · Y ±91 · Z 0..88 | 1 | `MI_Morin_Dehors` | 2 |
| `SM_Morin_Tavolino` | 184 / 106 / 76 | X ±35 · Y ±35 · Z 0..75 | 1 | `MI_Morin_Dehors` | 2 |
| `SM_Morin_Sedia` | 122 / 86 / 62 | X ±21,5 · Y −27,7..22 · Z 0..88 | 1 | `MI_Morin_Dehors` | 2 |
| `SM_Morin_Sgabello` | 168 / 144 / 68 | X ±19 · Y ±19 · Z 0..76 | 1 | `MI_Morin_Dehors` | 2 |
| `SM_Pav_Chiosco` | 8 | X 9500..11700 · Y −11350..−10200 · Z −15..15 | 1 | `MI_Pav_Cubetti` | 0 |
| `Blockout/SM_Blockout_Passeggiata_Pav_v3` | 138 | X −1230..25000 · Y −11800..8980 · Z −300..150 (= v2) | 14 | Verde → `M_Blockout_Verde`, Pietra → `MI_Pav_Lastre` | 0 |

- Bbox dei LOD1/2 uguali al LOD0 per chiosco, ombrellone e arredi; nelle fioriere variano di qualche cm (card degli arbusti decimate).
- Texture `T_Morin_Chiosco_D/N/ORM`, `T_Morin_Dehors_D/N/ORM` 2048 (N = Normalmap senza flip, ORM = Masks, sRGB off).
  `MI_Morin_Chiosco`, `MI_Morin_Dehors` su `M_Morin_Master_PBR` (nessun master nuovo). Riusate `MI_Pav_Cubetti` e le chiome del molo.
- Insidie: lo slot Pietra del blockout v3 arriva su `M_Blockout_Pietra` (va riportato a `MI_Pav_Lastre`, come la v2);
  `set_material_instance_texture_parameter_value` restituisce False anche quando imposta il parametro (verificare con `texture_parameter_values`);
  `BodySetup.agg_geom` in Python solo con `get_editor_property('agg_geom')`. Avvisi d'import sul blockout v3: tangenti degeneri (blockout, innocuo).
- `SM_Morin_Tavolino` e `SM_Morin_Sedia` sono importati ma **non posati** (il CSV usa solo `SM_Morin_TavoloSet`).

### Posa (Outliner `Arte/Chiosco`, Static, profilo `FortStaticMesh`)
| Attore | Tipo | Mesh | Istanze / trasformazione |
|---|---|---|---|
| `Arte_Pav_Chiosco` | FortStaticMeshActor (dup. del gazebo) | SM_Pav_Chiosco | (0,0,0) |
| `Arte_Chiosco_Chiosco` | idem | SM_Morin_Chiosco | (10000, −10600, 15), yaw 0 |
| `Arte_Chiosco_Ombrelloni` | HISM (dup. dei tombini) | SM_Morin_Ombrellone | 4 |
| `Arte_Chiosco_TavoliSet` | HISM | SM_Morin_TavoloSet | 9 |
| `Arte_Chiosco_Sgabelli` | HISM | SM_Morin_Sgabello | 5 |
| `Arte_Chiosco_FiorieraA/B/C` | HISM | SM_Morin_Fioriera/B/C | 8 / 7 / 7 |
| `Blockout_Passeggiata_v3` (cartella `Blockout`) | FortStaticMeshActor (dup. della v2) | SM_Blockout_Passeggiata_Pav_v3 | (0,0,0) |

Tutte le posizioni e gli yaw dal CSV (Z 15). **`Blockout_Passeggiata_v2` nascosto, non cancellato** (stesso metodo del §14: Actor Hidden In Game,
componente Visible falso, No Collision, Actor Enable Collision no): la richiesta di cancellazione è arrivata dall'orchestratore, non direttamente
dall'utente, e CLAUDE.md §6 chiede una conferma esplicita. L'asset `SM_Blockout_Passeggiata_Pav_v2` resta referenziato dall'attore nascosto.
Attori nel livello: 93.

### Verifiche
- Line trace verticali (passo 50 uu, X 9500..11700, Y −11650..−10200), ignorando gli arredi: tassello `Arte_Pav_Chiosco` a +15 (1.012 punti),
  blockout v3 a Z 0 fuori dal tassello, fascia palme +15 a Y −10200; **nessuna superficie del blockout sopra Z 5 nel tassello**, nessun buco.
  Unica quota 150: la siepe esistente a Y −11650 (fuori dal tassello, come nella v2). Gradino tassello/lastre 15 cm.
- Primo impatto: chiosco, ombrelloni (le tele hanno collisione), tavoli e fioriere colpiti: collisioni semplici attive.
- Salvataggio `save_dirty_packages` 22:03:23 (38 asset + 10 OFPA + 1 external object), date su disco controllate, nessun pacchetto sporco.
- Validazione `LaSpezia/`: 204 controllati, 204 validi, 0 errori, 10 avvisi già noti ("un solo LOD" su colline, fondale v2, ponte).
  Log: nessun "Failed to load"/missing (solo gli avvisi EOS/libcurl ricorrenti).

### Render (`docs/qa/`, 1024 px, FOV 90, ombre)
`uefn_chiosco_v2.png` (UE 8850, −10050, 180; yaw −14; pitch −4): chiosco con insegna, sgabelli, aiuola verde del blockout in primo piano.
`uefn_chiosco_v2_b.png` (UE 8700, −9450, 180; yaw −24; pitch −5): inquadratura simile a `ref/foto/vista/chiosco_con_ombrelloni_e_tavolini.png`,
chiosco, ombrelloni e fioriere dietro il filare di palme.

### Temporanei
18 `LaSpezia/_Temp/TMPC_<asset>_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente.

## 17. Giardini a Mare v2 e blockout passeggiata v4 (2026-11-19, 22:40-22:47 ora locale)

Sorgenti: `exports/giardini/` (9 FBX), posizioni **solo** `giardini_posizioni_v1.csv` (51 righe; il CSV `_blocco2` non è posato: oltre X 250 m
non c'è suolo), texture `blender/textures/giardini/`, `exports/blockout/SM_Blockout_Passeggiata_Pav_v4.fbx`.
Controllo iniziale: nessun asset né attore con questi nomi. Metodo del §13 (LOD0 col nome finale, LOD1/2 come `_Temp/TMPG_<asset>_LOD1/2`
+ `set_lod_from_static_mesh` dopo `remove_lods`; ImportFile aveva di nuovo messo 3 LOD automatici).

### Asset
| Asset | Cartella | Tri LOD0/1/2 | Bbox LOD0 (uu) | Convessi | Slot → MI | MinLOD Low/Med |
|---|---|---|---|---|---|---|
| `SM_Morin_OleandroAlberello_Bianco` | Arte/Giardini | 2.694 / 1.309 / 427 | X −190..182 · Y −191..146 · Z 0..413 | 1 (fusto) | Fusto, Chioma → `MI_Morin_Oleandro_Fusto`, `_Chioma` | 2 |
| `SM_Morin_OleandroAlberello_Rosa` | Arte/Giardini | 2.734 / 1.335 / 427 | X −173..148 · Y −166..169 · Z 0..404 | 1 (fusto) | idem | 2 |
| `SM_Morin_PanchinaLunga_Mod` | Arte/Giardini | 372 / 164 / 52 | X ±200 · Y ±22,5 · Z 0..45 | 1 (box) | `MI_Pav_Fascia` | 2 |
| `Blockout/SM_Blockout_Passeggiata_Pav_v4` | Blockout | 128 (solo LOD0) | X −1230..25000 · Y −11800..8980 · Z −300..40 | 13 | Verde → `M_Blockout_Verde`, Pietra → `MI_Pav_Lastre` (arrivava su `M_Blockout_Pietra`) | 0 |

Tutti: Nanite off, Use Simple Collision As Complex, soglie 1,0 / 0,2 / 0,08 (oleandri, panchina). Sezioni di ogni LOD sugli slot giusti.
Texture `T_Morin_Oleandro_{Chioma,Fusto}_{D,N,ORM}` in `Arte/Giardini` (N = Normalmap senza flip, ORM = Masks, sRGB off).
`MI_Morin_Oleandro_Chioma` su `M_Morin_Master_PBR_Masked` (come `MI_Albero_Latifoglia_Chioma`), `MI_Morin_Oleandro_Fusto` su `M_Morin_Master_PBR`.
Nessun master nuovo. Insidia: in Python `static_materials[i].material_interface = ...` non ha effetto (copia della struct): usare `mesh.set_material(i, mi)`.

### Posa
| Attore (Outliner) | Tipo | Mesh | Istanze |
|---|---|---|---|
| `Arte_Giardini_OleandriBianco` (`Arte/Giardini`) | HISM (dup. di `Arte_Chiosco_FiorieraA` + `clear_instances`) | Bianco | 11 (Y −11950, Z 0, yaw dal CSV) |
| `Arte_Giardini_OleandriRosa` | HISM | Rosa | 11 |
| `Arte_Giardini_Panchine` | HISM | PanchinaLunga_Mod | 29 (Y −10170, Z 15, yaw 0; tratti X 122-178 / 183-227 / 233-249 m) |
| `Blockout_Passeggiata_v4` (`Blockout`) | FortStaticMeshActor (dup. della v3) | Pav_v4 | (0,0,0), Query Only |

**`Blockout_Passeggiata_v3` nascosto, non cancellato** (metodo §14: Actor Hidden In Game, componente Visible falso, No Collision,
Actor Enable Collision no). Anche la v2 resta nascosta. Attori nel livello: 97.

### Verifiche (line trace in editor)
- Griglia 100 uu su X 11700..25000, Y −12000..−10100 ignorando oleandri e panchine: blockout v4 a +5 (prato provvisorio, 1.259 punti) e a 0,
  `Blockout_Fondale_v2` a 0 (fascia oleandri Y ≥ 118 m), fascia palme +15, aiuole +17. **Nessuna superficie sopra +20** (siepe sparita),
  unica eccezione il device `Luce_OraDelGiorno` a (24000, −10500), già esistente. Nessun buco: 16 punti senza impatto solo sul bordo X = 25000.
- Panchine: 174/174 trace sotto le impronte → fascia +15 (appoggiano); piano di seduta colpito a +60 su 29/29. Trace orizzontale a Z 35 lungo
  Y −10150/−10170/−10190: nessun ostacolo che le attraversi.
- Oleandri: suolo `Blockout_Fondale_v2` Z 0 sotto 22/22; fusto colpito a Z 100 su 22/22; chioma a Z 300 senza collisione (voluto).

### Salvataggio, validazione, render
`save_dirty_packages` 22:46:22 (18 asset + 5 OFPA + 1 external object), date `.uasset` controllate; nessun pacchetto sporco.
Validazione `LaSpezia/`: 222 controllati, 222 validi, 0 errori, 10 avvisi già noti. Log: solo tangenti degeneri del blockout v4 (innocuo),
EOS/audio e deprecazioni Python. Render 1024 px, FOV 90, ombre: `docs/qa/uefn_giardini_v2.png` (UE 15300, −9650, 180; yaw −90; pitch −3;
confronto con `ref/foto/vista/prato con alberelli.png`), `docs/qa/uefn_giardini_v2_b.png` (UE 13000, −9700, 180; yaw −72).

### Temporanei e problemi aperti
- 6 `LaSpezia/_Temp/TMPG_<asset>_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente.
- Il prato provvisorio (`M_Blockout_Verde`) è verde menta chiarissimo: nel render stacca molto dagli oleandri; serve un materiale prato vero.
- Oltre il prato (Y > 121 m) non c'è ancora Viale Italia con auto: si vedono le scatole del fondale.

## 18. Vista città v1: prato, Viale Italia, palazzi, Giardini pubblici; blockout fondale v3 (2026-11-19, 23:14-23:22 ora locale)

Sorgenti: `exports/viale/` (25 FBX), `exports/viale/viale_posizioni_v1.csv` (107 righe), texture `blender/textures/viale/`,
`exports/blockout/SM_Blockout_Fondale_v3.fbx`. Controllo iniziale: nessun asset né attore con questi nomi. Metodo del §13
(LOD0 col nome finale, LOD1/2 come `_Temp/TMPV_<asset>_LOD1/2` + `set_lod_from_static_mesh` dopo `remove_lods`).

### Asset
| Asset | Cartella | Tri LOD0/1/2 | Bbox LOD0 (uu) | Convessi | Slot → MI | MinLOD L/M |
|---|---|---|---|---|---|---|
| `SM_Morin_Prato_Giardini` | Arte/Viale | 48 | X 0..13250 · Y −1895..0 · Z −5..8 | 1 (UCX) | `MI_Morin_Prato` | 0 |
| `SM_Morin_Aiuola_Bosso` | Arte/Viale | 76 / 40 / 28 | X ±600 · Y ±150 · Z −3..36 | 1 (UCX) | `MI_Morin_Bosso` | 2 |
| `SM_Viale_Italia_Strada` | Arte/Viale | 88 / 80 / 32 | X 0..1900 · Y −2415..0 · Z −5..15,5 | **0** | `MI_Molo_Asfalto`, `MI_Pav_Fascia`, `MI_Viale_Segnaletica` | 2 |
| `SM_Morin_Auto_A/B/C` | Arte/Viale | 324 / 204 / 124 | A X ±197,5 · Y ±88 · Z 0..150; B ±217,5 · ±92 · 0..164; C ±222,5 · ±89 · 0..145 | **0** | `MI_Morin_Auto` | 2 |
| `SM_Fondale_Palazzo_A` | Arte/Fondale/Palazzi | 2.264 / 878 / 22 | X ±1062 · Y −1862..62 · Z 0..2686 | **0** | `MI_Fondale_Palazzo_A` | 2 |
| `SM_Fondale_Palazzo_B` | Arte/Fondale/Palazzi | 2.740 / 1.186 / 22 | X ±1287 · Y −1862..95 · Z 0..2679 | **0** | `MI_Fondale_Palazzo_B` | 2 |
| `SM_Fondale_Palazzo_C` | Arte/Fondale/Palazzi | 1.940 / 754 / 22 | X ±1062 · Y −1662..62 · Z 0..2279 | **0** | `MI_Fondale_Palazzo_C` | 2 |
| `SM_Blockout_Fondale_v3` | Blockout | 417 (solo LOD0) | X −16388..33000 · Y −30000..30341 · Z −300..1949 | 43 | `M_Blockout_Fondale`, Verde → **`MI_Morin_Prato_Mondo`** | 0 |

- Tutti: Nanite off, Use Simple Collision As Complex, soglie 1,0 / 0,2 / 0,08 sugli asset con LOD; sezioni di ogni LOD sugli slot giusti.
- **Nuova insidia:** `ImportFile` genera **un convesso automatico** anche sugli FBX senza UCX (strada, auto, palazzi ne avevano 1):
  tolto con `remove_collisions`. Inoltre i componenti HISM di strada, auto, palazzi e alberi dei Giardini pubblici sono **No Collision**.
- Il bosso non è su card: master opaco `M_Morin_Master_PBR`. Nessun master nuovo.
- Texture (21): `Arte/Viale/T_Morin_Prato_*` 2048, `T_Morin_Bosso_*`, `T_Morin_Auto_*` 1024, `T_Viale_Segnaletica_*` 512;
  `Arte/Fondale/Palazzi/T_Fondale_Palazzo_{A,B,C}_*` 1024. N = Normalmap senza flip, ORM = Masks, sRGB off.
- MI su `M_Morin_Master_PBR`: `MI_Morin_Prato`, `MI_Morin_Bosso`, `MI_Viale_Segnaletica`, `MI_Morin_Auto`, `MI_Fondale_Palazzo_A/B/C`.
- **Prato sul blockout.** Le UV di `SM_Blockout_Fondale_v3` sono tutte (0,0) (area UV 0, letta con GeometryScript): `MI_Morin_Prato`
  lì darebbe un solo texel. Creato `Arte/Viale/MI_Morin_Prato_Mondo` su `M_Morin_Master_Pav` (proiezione in coordinate mondo, `Tile_m` 4,
  stesse texture del prato) e assegnato allo slot Verde **del solo asset** `SM_Blockout_Fondale_v3`. `M_Blockout_Verde` non toccato
  (resta su `SM_Blockout_Fondale_v2` e sul blockout della passeggiata). Nella vista alta (25 m) il tiling a 4 m non si nota: tenuto.

### Posa (Outliner `Arte/Viale`; HISM duplicati da `Arte_Arredi_Tombini` + `clear_instances`, attore singolo dal gazebo)
| Attore | Mesh | Istanze | Collisione componente |
|---|---|---|---|
| `Arte_Viale_Prato` (FortStaticMeshActor) | SM_Morin_Prato_Giardini | (11750, −10190, 0) | Query Only (come il template) |
| `Arte_Viale_AiuoleBosso` | SM_Morin_Aiuola_Bosso | 8 (Y −11000, Z 8) | Query Only |
| `Arte_Viale_Strada` | SM_Viale_Italia_Strada | 7 (X 11700..23100, Y −12085) | No Collision |
| `Arte_Viale_AutoA/B/C` | SM_Morin_Auto_A/B/C | 13 / 13 / 15 (Y −12207 e −13752, Z 2) | No Collision |
| `Arte_Viale_PalazzoA/B/C` | SM_Fondale_Palazzo_A/B/C | 5 / 4 / 4 (Y −20600..−26600) | No Collision |
| `Arte_Viale_GP_LatifogliaA/B` | `Arte/Alberi/SM_Albero_LatifogliaA/B` (esistenti) | 11 / 8 | No Collision |
| `Arte_Viale_GP_PinoDomestico` | `Arte/Alberi/SM_Morin_PinoDomestico` (esistente) | 5 | No Collision |
| `Arte_Viale_GP_PalmaA` | `Arte/Palme/SM_Morin_PalmaA` (esistente) | 13 | No Collision |
| `Blockout_Fondale_v3` (`Blockout`) | SM_Blockout_Fondale_v3 | (0,0,0), dup. della v2, Query Only | — |

Posizioni e yaw dal CSV, scala 1. **`Blockout_Fondale_v2` nascosto, non cancellato** (metodo §14). `Barriera_LatoCitta` occupa Y −118,0..−120,6 m:
tutto ciò che sta oltre è senza collisione.

### Verifiche (line trace in editor, semplice = complessa)
- Griglia 100 × 50 uu su X 11750..25000, Y −10200..−11800 (4.389 punti), ignorando oleandri, panchine, aiuole e `Luce_OraDelGiorno`:
  **prato +8** su 4.256 punti, fascia palme +15 a Y −10200; nessun buco, il blockout v4 (+5) non è mai il primo impatto.
- Trace verticali sui centri delle 41 auto, dei 7 moduli di strada, davanti ai 13 palazzi e su alberi/palme: primo impatto sempre
  `Blockout_Fondale_v3` a Z 0 (mai auto, strada, palazzi né alberi). Trace orizzontali a Z 80 lungo le due file di auto (X 115-250 m): nessun impatto.
- Oltre la barriera (X 118-250 m, Y −118,5..−146 m) suolo continuo `Blockout_Fondale_v3` a Z 0.
- **Senza suolo del blockout sotto:** Palazzo A a X 330 m, Palazzo B a X 357,5 m e una latifoglia a X 333 m (il Fondale_v3 finisce a X 330 m).

### Salvataggio, validazione, render
`save_dirty_packages` 23:20:16 (71 pacchetti), date dei 15 `.uasset` OFPA controllate (contengono i riferimenti nuovi; v2 risalvato nascosto),
`SM_Blockout_Fondale_v3` contiene `MI_Morin_Prato_Mondo`; nessun pacchetto sporco. Validazione `LaSpezia/` + mappa: 278 controllati,
278 validi, 0 errori, 11 avvisi (10 noti + "un solo LOD" su `SM_Blockout_Fondale_v3`, voluto). Log: solo tangenti degeneri su palazzi e
Fondale_v3 (import) ed EOS. Render `docs/qa/uefn_viale_v1.png` (UE 22180, −9340, 205; yaw −90; pitch −3; FOV 100, 1024 px, ombre):
stessa camera di `CAM_Viale_F1` (Z = cubetti +15 + 1,9 m).

### Memoria
Project Size non riletto (nessuna sessione). Stima delle texture nuove a piena risoluzione con i mip: prato 2048 ≈ 11-13 MiB,
cinque set 1024 ≈ 13-17 MiB, segnaletica ≈ 0,8 MiB: **≈ 25-31 MiB** in più. Mesh: < 20k tri complessivi.

### Temporanei
16 `LaSpezia/_Temp/TMPV_<asset>_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente.

## 19. Parcheggio iniziale v1, viale v2, blockout fondale v4 e passeggiata v5 (2026-11-20, 04:28-04:40 ora locale)

Sorgenti: `exports/parcheggio/` (19 FBX), `exports/parcheggio/parcheggio_posizioni_v1.csv` (54 righe, coordinate UE), texture
`blender/textures/parcheggio/`, `exports/viale/viale_posizioni_v2.csv` (167 righe), `exports/blockout/SM_Blockout_Fondale_v4.fbx`,
`SM_Blockout_Passeggiata_Pav_v5.fbx`. Controllo iniziale: nessun asset né attore con questi nomi. Metodo del §13 (LOD0 col nome finale,
LOD1/2 come `_Temp/TMPP_<asset>_LOD1/2` + `set_lod_from_static_mesh` dopo `remove_lods`). Tutti gli FBX hanno UCX: niente `remove_collisions`.

### Asset
| Asset | Cartella | Tri LOD0/1/2 | Bbox LOD0 (uu) | Convessi | Slot → materiale | MinLOD L/M |
|---|---|---|---|---|---|---|
| `SM_Parcheggio_Asfalto` | Arte/Parcheggio | 153 | X 2000..10600 · Y −12085..−10200 · Z 2..15 | 6 | Asfalto, Segnaletica, Fascia, Terra → `MI_Parcheggio_Asfalto`, `MI_Viale_Segnaletica`, `MI_Pav_Fascia`, `MI_Pav_Terra` | 0 |
| `SM_Morin_CartelloP` | Arte/Parcheggio | 78 / 50 / 20 | X −5,5..3,6 · Y ±30 · Z 0..270 | 1 | `MI_Morin_Cartelli` | 2 |
| `SM_Morin_CartelloDivieto` | Arte/Parcheggio | 154 / 94 / 48 | idem | 1 | `MI_Morin_Cartelli` | 2 |
| `SM_Morin_NewJersey` | Arte/Parcheggio | 54 / 26 / 18 | X ±100 · Y ±30,5 · Z 0..81 | 1 | `MI_Morin_NewJersey` | 2 |
| `SM_Morin_Auto_A/B/C_Col` | Arte/Parcheggio | 324 / 204 / 124 | come `SM_Morin_Auto_A/B/C` | 2 | `MI_Morin_Auto` | 2 |
| `SM_Blockout_Fondale_v4` | Blockout | 397 (solo LOD0) | X −16388..33000 · Y −30000..30341 · Z −300..1948,5 | 41 | `M_Blockout_Fondale`, Verde → `MI_Morin_Prato_Mondo` (come v3) | 0 |
| `SM_Blockout_Passeggiata_Pav_v5` | Blockout | 98 (solo LOD0) | X −1230..25000 · Y −11800..8980 · Z −300..5 | 10 | Verde → `M_Blockout_Verde`, Pietra → `MI_Pav_Lastre` (arrivava su `M_Blockout_Pietra`) | 0 |

Tutti: Nanite off, Use Simple Collision As Complex, soglie 1,0 / 0,2 / 0,08 sugli asset con LOD. Texture (9, `Arte/Parcheggio`):
`T_Parcheggio_Asfalto_*` 2048 [SV], `T_Morin_Cartelli_*` 512, `T_Morin_NewJersey_*` 1024 (N = Normalmap senza flip, ORM = Masks, sRGB off).
MI nuove su `M_Morin_Master_PBR`: `MI_Parcheggio_Asfalto`, `MI_Morin_Cartelli`, `MI_Morin_NewJersey`. Nessun master nuovo.
Avvisi d'import: tangenti degeneri / bi-normali nulle su NewJersey, CartelloDivieto e sui due blockout (innocui).

### Posa (Outliner `Arte/Parcheggio`; HISM duplicati da `Arte_Arredi_Tombini` + `clear_instances`, attore singolo dal gazebo)
| Attore | Mesh | Istanze | Collisione |
|---|---|---|---|
| `Arte_Parcheggio_Asfalto` (FortStaticMeshActor) | SM_Parcheggio_Asfalto | (0,0,0) | Query Only |
| `Arte_Parcheggio_AutoA/B/C_Col` | SM_Morin_Auto_A/B/C_Col | 11 / 18 / 11 | Query Only (`FortStaticMesh`) |
| `Arte_Parcheggio_CartelliP` / `_CartelliDivieto` | CartelloP / CartelloDivieto | 2 / 2 | Query Only |
| `Arte_Parcheggio_NewJersey` | SM_Morin_NewJersey | 3 | Query Only |
| `Arte_Parcheggio_LatifogliaA/B` | `Arte/Alberi/SM_Albero_LatifogliaA/B` (esistenti) | 3 / 3 | Query Only (area giocabile) |

**Viale v2** (`Arte/Viale`, stessi HISM, confronto per posizione X/Y con tolleranza 1 uu): `Arte_Viale_Strada` +10 (17), `AutoA` +13 (26),
`AutoB` +21 (34), `AutoC` +16 (31), restano senza collisione; `Arte_Viale_PalazzoB` istanza Palazzo_06 Z 0 → **115,4**. Tutti gli altri HISM
del viale già uguali al CSV v2; nessuna istanza in più o duplicata.

**Blockout:** `Blockout_Fondale_v4` (dup. della v3) e `Blockout_Passeggiata_v5` (dup. della v4), posa (0,0,0), Query Only.
**`Blockout_Fondale_v3` e `Blockout_Passeggiata_v4` nascosti, non cancellati** (metodo §14). Attori nel livello: 122.

### Verifiche (line trace in editor)
- Griglia 50 uu su X 2000..9500, Y −11800..−10000 (5.587 punti), ignorando auto, cartelli, new jersey, alberi, palme, arredi:
  asfalto **+2** (3.925), aiuola degli alberi +14 (Y −11350..−11650), fascia palme +15 e aiuole +17 a Y > −10200, ramo del molo +1
  (X ≤ 2350), tassello del chiosco +15 a X 9500. **Nessun buco, nessuna superficie del blockout sopra il suolo, salto massimo 16 cm.**
- Trace dall'alto su tutte le 53 istanze: colpite **53/53** (auto, cartelli, new jersey, tronchi). Sotto le 21 auto a pettine (Y ≈ −11925..−11945)
  il suolo di collisione è `Blockout_Fondale_v4` a Z 0: gli UCX dell'asfalto finiscono a Y −11800 (voluto, barriera); la mesh visibile resta a +2.

### Salvataggio, validazione, render
`save_dirty_packages` 04:36:40 (21 asset + 19 pacchetti mappa/OFPA; 18 OFPA con data 04:36:40-41 su disco), nessun pacchetto sporco.
Validazione `LaSpezia/`: 310 controllati, 310 validi, 0 errori, 12 avvisi (11 noti + "un solo LOD" su `SM_Blockout_Fondale_v4`, voluto).
Log: solo tangenti degeneri, EOS, deprecazioni Python. Render `docs/qa/uefn_parcheggio_v1.png` (camera `CAM_Park_F1` di
`morin_parcheggio.py`: Blender (21,5; 106,6; 2,12) az 82°, pitch −6°, FOV 78° → UE (2150, −10660, 212), yaw **−8**, pitch −6, FOV 78, 1024 px, ombre).
Nota sulla conversione: per una camera Blender (rotX ~90°) la direzione di vista è (−sin rotZ, cos rotZ), quindi yaw UE = **−(rotZ + 90°)**
(rotZ = −82° → −8°); la regola "yaw = −rotZ" darebbe +82°, cioè la camera girata verso il mare.

### Temporanei e problemi aperti
- 12 `LaSpezia/_Temp/TMPP_<asset>_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente.
- **Fila a pettine dentro la barriera:** `Barriera_LatoCitta` (volume Y −12058..−11802, X −35..272 m) copre le 21 auto a pettine
  (centri Y −11923..−11945) e l'asfalto oltre Y 118 m: in gioco la fila a pettine non è raggiungibile. Da decidere: spostare la barriera
  (es. a Y ≥ 121 m solo davanti al parcheggio) o accettarlo.
- **`NewJersey_00`** (6200, −8060) è sopra la bitta 3 di `Arte_Banchina_Bitte` (6200, −8052,7; alta 45 cm): la bitta sta dentro il new jersey.
  Da correggere nel CSV in Blender (spostare il new jersey di ~0,5-1 m lungo X) o togliere la bitta.

## 20. Auto v2, pini del parcheggio, new jersey, barriera lato città (2026-11-20, ~04:50-05:05 ora locale)

Sorgenti: `exports/auto/` (54 FBX), texture `blender/textures/auto/T_Morin_Auto_v2_D/N/ORM.png`, `exports/parcheggio/parcheggio_posizioni_v2.csv`
(55 righe, colonne `pitch,roll`), `exports/viale/viale_posizioni_v3.csv` (167 righe). Controllo iniziale: nessun asset né attore con questi nomi.
Metodo del §13: LOD0 col nome finale in `LaSpezia/Arte/Auto`, LOD1/2 come `_Temp/TMPA2_<asset>_LOD1/2`, `remove_lods` (ImportFile aveva messo
3 LOD automatici) + `set_lod_from_static_mesh(..., True)`; Nanite off, Use Simple Collision As Complex, soglie 1,0 / 0,2 / 0,08, MinLOD Low/Medium 2.

### Asset (`Arte/Auto`)
| Asset | Tri LOD0/1/2 | Bbox (uu) | Convessi |
|---|---|---|---|
| `SM_Morin_Auto_A_v2_{Bianco,Rosso,Azzurro}` / `_A_Col_v2_*` | 1.804 / 812 / 260 | X ±197,5 · Y ±106 · Z 0..150 | 0 / 2 |
| `SM_Morin_Auto_B_v2_{GrigioScuro,Argento,Arancio}` / `_B_Col_v2_*` | 1.844 / 840 / 260 | X ±217,5 · Y ±110 · Z 0..164 | 0 / 2 |
| `SM_Morin_Auto_C_v2_{Nero,BluScuro,BiancoPerla}` / `_C_Col_v2_*` | 1.844 / 840 / 276 | X ±222,5 · Y ±108 · Z 0..147 | 0 / 2 |

- Lunghezza e altezza come da brief. La larghezza della bbox (2,12 / 2,20 / 2,16 m) **include gli specchietti**: la scocca (UCX box) è ±87 uu = 1,74 m
  per la A, come da brief (PLAN: "2,12 con specchietti").
- `ImportFile` ha di nuovo creato **1 convesso automatico** sulle 9 mesh senza UCX: tolto con `remove_collisions` (0 convessi). Le `_Col` hanno i 2 UCX
  (scocca Z 12..94, abitacolo Z 94..147 per la A).
- **Texture una sola volta**: FBX importati con materiali e texture **off**; `T_Morin_Auto_v2_D/N/ORM` (2048, N = Normalmap senza flip, ORM = Masks,
  sRGB off) importate da `blender/textures/auto/`. `MI_Morin_Auto_v2` su `M_Morin_Master_PBR` (BaseColor/Normal/ORM), assegnata allo slot
  unico `M_Morin_Auto_v2` di tutte le 18 mesh e dei 36 temporanei. **Nessun duplicato** creato.

### Posa
| Attore (Outliner) | Mesh | Istanze | Collisione |
|---|---|---|---|
| `Arte_Parcheggio_Auto{A,B,C}_Col_v2_<Colore>` (9 HISM, `Arte/Parcheggio`, dup. di `Arte_Parcheggio_AutoA_Col`) | `_Col_v2` | 40 in tutto | Query Only (`FortStaticMesh`) |
| `Arte_Parcheggio_Pini` (HISM) | `Arte/Alberi/SM_Morin_PinoDomestico` | 7, `Rotator(roll, pitch, yaw)` dal CSV (pitch −3,8..−7,8°) | Query Only |
| `Arte_Viale_Auto{A,B,C}_v2_<Colore>` (9 HISM, `Arte/Viale`, dup. di `Arte_Viale_AutoA`) | `_v2` | 91 in tutto | No Collision |
| `Arte_Parcheggio_NewJersey` | invariato | istanza 0 → (6070, −8060, 0), yaw 0,37 | Query Only |

**Nascosti, non cancellati** (metodo §14): `Arte_Parcheggio_AutoA/B/C_Col`, `Arte_Parcheggio_LatifogliaA/B`, `Arte_Viale_AutoA/B/C`.
Il resto del CSV del parcheggio (asfalto, cartelli, new jersey 01/02) è uguale a quanto già posato. Attori nel livello: 144.

### Barriera lato città (`Device/Barriere`, device Barriera duplicati da `Barriera_LatoCitta`, stesse opzioni: Scatola, invisibile, sempre attiva,
altezza 10, blocca proiettili, collisione visuale NO, dissolvenza NO; larghezza/profondità con `SetClassicDeviceOption`, 1 unità = 512 uu)
Bordo dell'asfalto verificato: bbox di `SM_Parcheggio_Asfalto` Y min **−12085,0** (X 2000..10600). Fila a pettine: centri Y −11923..−11957, X 27,9-84,8 m.
| Label | Centro | Unità L × P | Ingombro (da `BarrierBounds`) |
|---|---|---|---|
| `Barriera_LatoCitta` (modificata) | (20864, −11930, −700) | 40 × 0,5 | X 10624..31104 · Y −12058..−11802 |
| `Barriera_LatoCitta_SO` (nuova) | (−950, −11930, −700) | 10 × 0,5 | X −3510..1610 · Y −12058..−11802 |
| `Barriera_LatoCitta_Parcheggio` (nuova) | (6144, −12313, −700) | 18 × 0,5 | X 1536..10752 · Y −12441..−12185 |
| `Barriera_LatoCitta_RaccordoSO` (nuova) | (1573, −12121, −700) | 0,5 × 1 | X 1445..1701 · Y −12377..−11865 |
| `Barriera_LatoCitta_RaccordoNE` (nuova) | (10688, −12121, −700) | 0,5 × 1 | X 10560..10816 · Y −12377..−11865 |

- Davanti al parcheggio la faccia lato terra è a **Y −12185** (1 m oltre l'asfalto); altrove resta a Y −11802 come prima. Il limite sinistro
  resta −3510 (sovrapposto a `Barriera_Molo_AreaMilitare`); il destro passa da 27210 a 31104 (fuori area, oltre `Barriera_FineBlocco`): innocuo.
- Il volume del segmento nuovo arriva a Y −12441, cioè ~1 m dentro la corsia di sosta/carreggiata del viale: è invisibile e non raggiungibile,
  il giocatore si ferma a −12185.
- **Verifica di continuità** sui bounds (passo 4 uu, X −3510..27210, con `Barriera_Molo_AreaMilitare` e `Barriera_FineBlocco`): ogni X è coperta e
  i tratti adiacenti si sovrappongono in Y di almeno 256 uu → **nessun varco**, neanche in diagonale ai raccordi.
- Line trace orizzontali a Z 100 (X −3500..27200 ogni 1 m, da Y −11700 a −12600): 249/308 senza impatto, il resto auto `_Col_v2` della fila
  a pettine, un pino, oleandri, collina a X −35 m. **Le barriere non hanno collisione in modalità Crea**: il trace non le vede, quindi la tenuta
  è verificata solo dai bounds. Da confermare in sessione (qa-tester).

### Verifiche (line trace in editor)
- Auto del parcheggio: trace dall'alto sulle 40 posizioni → **40/40** colpite (HISM `_Col_v2`), tetti a Z 146-163.
- Auto del viale: 91/91 trace verticali passano e colpiscono `Blockout_Fondale_v4` a Z 0 (**nessuna collisione**).
- Pini: tronco colpito a Z 112 su **7/7**; chioma a Z 1000 nessun impatto; suolo sotto = asfalto/aiuola del parcheggio.
- `NewJersey_00` colpito a Z 81 nella nuova posizione.

### Salvataggio, validazione, render
`save_dirty_packages` 05:03:12 (58 asset + 33 pacchetti mappa/OFPA; 91 `.uasset` con data successiva alle 05:02 su disco, 22 in `Arte/Auto`),
nessun pacchetto sporco. Validazione `LaSpezia/` (368 asset): 368 validi, 0 errori, 12 avvisi già noti (colline, blockout fondale/ponte "un solo LOD").
Log: nessun errore nuovo (solo audio/EOS). Render `docs/qa/uefn_parcheggio_v2.png` (UE 2150, −10660, 212; yaw −8; pitch −6; FOV 78; 1024 px; ombre).

### Temporanei e problemi aperti
- 36 `LaSpezia/_Temp/TMPA2_<asset>_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente.
- Alle auto del viale in sosta davanti al parcheggio (Y ≈ −12207..−12223, X 17-87 m, senza collisione) il giocatore arriva fino a Y −12185:
  entra di ~0,7-0,9 m nel fianco delle auto. Da decidere: accettare, oppure usare le `_Col_v2` per quelle 13 auto.
- Nel render le auto v2 hanno tetti e cofani lattiginosi e la texture appare morbida (la miniatura dell'asset è corretta): probabile riflesso
  del cielo con la luce delle 18 e/o streaming delle mip nel render; da guardare in sessione, eventualmente `Roughness_Mult` di `MI_Morin_Auto_v2`.
- I pini sono inclinati (pitch fino a −7,8°) tutti verso lo stesso lato: è il CSV, da confermare con la foto.
- **Correzione (05:15 circa):** auto sfocate/lattiginose per **LODBias 1** su `T_Morin_Auto_v2_D/N/ORM` (default dell'import; sRGB, compressione e
  canali della MI erano già giusti, identici a `MI_Morin_Chiosco`) e mip non residenti nel render: LODBias → **0**, mip forzati prima della cattura;
  `uefn_parcheggio_v2.png` rifatta (texture nitide, vetri scuri, `Roughness_Mult` non toccato). Le 13 auto del viale in sosta davanti al
  parcheggio (Y −12207..−12223, X 17-86 m) spostate dagli HISM `Arte_Viale_Auto*_v2_*` agli HISM `Arte_Parcheggio_Auto*_Col_v2_*` dello stesso
  modello e colore (parcheggio 53 istanze, viale 78): trace dall'alto 13/13 sulle `_Col_v2`. Salvato, nessun pacchetto sporco, validazione 368/368, 0 errori.

## 21. Banchina v2 e stima LODBias delle texture vicine (2026-11-20, ~05:10-05:25 ora locale)

Sorgenti: `exports/banchina_v2/` (21 FBX), `exports/banchina_v2/banchina_posizioni_v2.csv` (83 righe), texture
`blender/textures/banchina_v2/T_Banchina_Blocchi_*`. Controllo iniziale: nessun asset né attore con questi nomi. Metodo del §13:
LOD0 col nome finale in `LaSpezia/Arte/Banchina`, LOD1/2 come `_Temp/TMPB2_<asset>_LOD1/2`, `remove_lods` (ImportFile aveva messo 3 LOD
automatici) + `set_lod_from_static_mesh(..., True)`. Tutti i LOD0 hanno UCX (verificato nei file FBX): niente `remove_collisions`.

### Asset (`Arte/Banchina`; Nanite off, Use Simple Collision As Complex, soglie 1,0 / 0,2 / 0,08, MinLOD Low/Medium 2 come la v1)
| Asset | Tri LOD0/1/2 | Bbox locale (uu) | Convessi | Slot → MI |
|---|---|---|---|---|
| `SM_Banchina_Mod4m_v2` | 164 / 92 / 12 | X 0..400 · Y −55..0 · Z −300..0,1 | 1 (top Z −0,5) | Blocchi, Paramento |
| `SM_Banchina_Mod4m_Nicchia` | 234 / 146 / 58 | come sopra; nicchia X 40..120, profonda 24 | 1 (scatola piena) | Blocchi, Paramento |
| `SM_Banchina_Scaletta_v2` | 448 / 202 / 82 | X ±27 · Y −42,6..−1,4 · Z −285..50,6 | 3 | Ghisa |
| `SM_Banchina_Bitta_v2` | 970 / 484 / 144 | X ±20 · Y ±20 · Z −1,2..45,4 | 1 | Ghisa |
| `SM_Banchina_Testata` | 845 / 473 / 39 | X −970..0 · Y −55..1832 · Z −300..0 | 3 | Blocchi, Paramento |
| `SM_Banchina_Testata_Fine` | 67 / 39 / 19 | X 0..25 · Y −55..0 · Z −300..0 | 1 | Blocchi, Paramento |
| `SM_Morin_AncoraMonumento` | 1.506 / 662 / 258 | X −199,5..70,7 · Y −42,2..274,2 · Z 0..272,3 | 4 | Ghisa, Blocchi |

Texture nuove `T_Banchina_Blocchi_D/N/ORM` 2048 (N = Normalmap senza flip, ORM = Masks, sRGB off), **LODBias 0** subito.
`MI_Banchina_Blocchi` su `M_Morin_Master_PBR`; Paramento e Ghisa riusano `MI_Banchina_Paramento` e `MI_Banchina_Ghisa` (come bitte/scalette v1).

### Posa (Outliner `Arte/Banchina`; HISM duplicati da `Arte_Arredi_Tombini` + `clear_instances`, singoli dal gazebo; profilo `FortStaticMesh`, Static)
| Attore | Mesh | Istanze / posa |
|---|---|---|
| `Arte_Banchina_Moduli_v2` | Mod4m_v2 | 54 (CSV, Z 0, yaw 0,1241) |
| `Arte_Banchina_Nicchie` | Mod4m_Nicchia | 4 (Mod_06/18/30/42) |
| `Arte_Banchina_Scalette_v2` | Scaletta_v2 | 4 (X 44/92/140/188 m, Z 0) |
| `Arte_Banchina_Bitte_v2` | Bitta_v2 | **6** (Bitta_00..05, X 26-86 m, Z −1,2): decisione dell'utente, solo zona d'imbarco (X ≤ 90 m); Bitta_06..17 non posate |
| `Arte_Banchina_Testata` | Testata | (1920, −8032, 0), yaw 0,1241 |
| `Arte_Banchina_Testata_Fine` | Testata_Fine | (25120, −7981,74, 0), yaw 0,1241 |
| `Arte_Banchina_AncoraMonumento` | AncoraMonumento | (22660, −8450, 0), yaw 0 |

**Nascosti, non cancellati** (metodo §14: Actor Hidden In Game, componente Visible = falso, No Collision, Actor Enable Collision = no):
`Arte_Banchina_Moduli` (58), `Arte_Banchina_Bitte` (18), `Arte_Banchina_Scalette` (4). Attori nel livello: 151.

### Verifiche (line trace in editor)
- **Ciglio continuo:** trace verticali ogni 5 cm a 5/30/50 cm dal bordo, X 19,0-251,4 m: sempre banchina v2 (top collisione Z −0,5, 5 mm sotto
  le lastre), nessun buco. Trace orizzontali dal mare a Z −20/−150/−280: faccia sempre a ±1,5 cm dalla retta del ciglio
  (Y = −8032 + 0,002166·(X−1920)), 0 anomalie. Giunto testata/Mod_00: testata fino a X 1920, modulo da 1924; smusso a 45° (X 1900 → Y −8012).
- **Scalette:** 4/4 dentro la nicchia (nicchia X 40..120 locale, scaletta X ±27,5 attorno a 80); UCX della scaletta (Y −24..+3, Z −285..−2 e
  corrimani Z −2..50) colpiti dal mare a Z −100 e dall'alto a Z 50. La collisione della nicchia è una scatola piena (24 cm, ininfluente).
- **Ancora:** 208/224 trace verticali sulla bbox colpiscono l'ancora; colpita anche orizzontalmente a Z 100 e 200. Nessuna panchina, lampione,
  aiuola o palma entro 4,5 m. Occupa Y 81,8-84,9 m sul camminamento (Y 80-89): restano 1,8 m lato mare e 4,1 m lato palme (vedi problemi).
- **Bitte:** 6 istanze, X max 8600 uu. `Bitta_03` (6200) a 10 cm dal `NewJersey_00` (X 5970..6170): nessuna compenetrazione.

### Render
`docs/qa/uefn_banchina_v2.png` (UE 25200, −7930, 175; yaw 184; pitch −6; FOV 75; 1024 px; ombre), da confrontare con
`ref/foto/vista/banchina_vista_montagne_verso_ponte.jpg`: grandi blocchi bianchi del ciglio, ancora sul camminamento, filare di palme.

### LODBias delle texture "vicine": stima, NON applicato (soglie 220/245 MiB superate: vedi §30, limite reale 300 MiB)
Regola del task: fermarsi se il totale stimato delle texture del progetto supera 220 MiB. Stima = larghezza × altezza × byte/px × 4/3 (mip),
÷ 4 per ogni passo di LODBias; byte/px: BC5 normal 1, DXT1 0,5, DXT5 (D con alfa) 1. Due casi: solo le D "masked" con alfa (chiome, fronde,
fregio) oppure tutte le D salvate RGBA nei PNG sorgente (UE potrebbe trattarle come DXT5).
- **Totale texture progetto (113):** oggi **110-133 MiB**, dopo **273-325 MiB** → oltre la soglia, nessuna modifica fatta.
- 60 texture da 1 a 0 (tutte le altre "vicine" sono già a 0: Blocchi v2, tombino, oleandro fusto, bosso, cartelli, new jersey, cortecce,
  segnaletica). Aumento per gruppo (MiB, caso basso-alto): Pavimentazione `T_Pav_Lastre/Cubetti/Fascia/Terra` 32-40 · Banchina v1
  `Ciglio/Paramento/Ghisa` 24-30 · Palme `PalmaA_Fronde/Tronco` 18-20 · Chiosco `Chiosco/Dehors` 16-20 · Giardini `Oleandro_Chioma` 10 ·
  Prato `T_Morin_Prato` 8-10 · Arredi `Gazebo_Fregio` (2048×512) 2,5 · Molo `Asfalto/Facciate/Masselli` 24-30 · Parcheggio `Asfalto` 8-10 ·
  Alberi `Latifoglia_Chioma`, `PinoDomestico_Chioma` 20. Ogni set 2048 D+N+ORM passa da ~2,7-3,3 a ~10,7-13,3 MiB.
- Note per la scelta: `T_Banchina_Ciglio_*` ora serve solo ai moduli v1 nascosti (resta in cottura finché non si cancellano);
  con ~110 MiB di margine sotto i 220 ci stanno circa 10-13 set 2048 (es. pavimentazione + Ghisa/Paramento + palme + chiosco ≈ 90-110 MiB).

### Salvataggio, validazione, log
`save_dirty_packages` 05:22:05 (25 asset + 10 OFPA: 7 attori nuovi + 3 nascosti, date 05:22:04 su disco). I 14 `TMPB2_*` con 1 LOD avevano
MinLOD 2 (avviso "non rientra nell'intervallo 0..0"): portati a 0 e risalvati. Nessun pacchetto sporco. Validazione `LaSpezia/`: **393/393 validi,
0 errori, 13 avvisi** (12 noti "un solo LOD" + `TMPB2_SM_Morin_AncoraMonumento_LOD1`, temporaneo non referenziato). Log: solo EOS.

### Temporanei e problemi aperti
- 14 `LaSpezia/_Temp/TMPB2_<asset>_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente.
- ~~Ancora sul camminamento~~: **decisione dell'utente**, resta dov'è (deroga alla corsia di 8 m in `docs/decisioni.md`, gioco rimandato).
- Top della collisione dei moduli a Z −0,5 (UCX da Blender), visivo a 0..0,1: gradino di 5 mm, ininfluente.
- **(qa-tester)** In sessione: moduli e ancora solidi, nessun inciampo al giunto testata/modulo, bitte v1 davvero assenti.

### LODBias applicato: selezione dell'utente da ~100 MiB (05:25)
La stima "vicine" qui sopra era la prima proposta (non applicata). Applicata la selezione dell'utente:
- **A 0 (30 texture, D/N/ORM):** `T_Pav_Lastre/Cubetti/Fascia/Terra_*`, `T_Banchina_Ghisa_*`, `T_Banchina_Paramento_*`,
  `T_Morin_PalmaA_Fronde/Tronco_*`, `T_Morin_Chiosco_*`, `T_Morin_Dehors_*` (oltre a quelle già a 0).
- **Restano a 1 (30):** `T_Banchina_Ciglio_*` (solo moduli v1 nascosti), `T_Morin_Oleandro_Chioma_*`, `T_Morin_Prato_*`, `T_Morin_Gazebo_Fregio_*`,
  `T_Molo_Asfalto/Facciate/Masselli_*`, `T_Parcheggio_Asfalto_*`, `T_Albero_Latifoglia_Chioma_*`, `T_Morin_PinoDomestico_Chioma_*`.
- Stima ricalcolata prima di applicare: totale texture del progetto **192,3-232,7 MiB** (prima 110,3-132,7), sotto la soglia di 245 MiB.
- **Aggiornamento 2026-11-20 (§27):** dopo il ponte il totale era 313,7-391,5 MiB; con "Compress Without Alpha" su 47 D opache e LODBias 1 su Ponte_Acciaio, Auto_v2, Imbarco, Imbarco_Legno, Pav_Terra, Banchina_Paramento: **235,5-236,2 MiB**. Elenco nel §27.
- Transazione con `modify()`; `save_dirty_packages` 05:25:31 (30 texture), nessun pacchetto sporco; validazione `LaSpezia/` 393/393 validi,
  0 errori, 13 avvisi (gli stessi di sopra). Decisione in `docs/decisioni.md`.

## 22. Imbarco v1: battello, pontile, biglietteria, cestini, rastrelliere, parabordi (2026-11-20, ~09:20-09:35 ora locale)

Sorgenti: `exports/imbarco/` (18 FBX), texture `blender/textures/imbarco/`, `exports/imbarco/imbarco_posizioni_v1.csv` (22 righe).
Controllo iniziale: nessun asset né attore con questi nomi. Metodo del §13: LOD0 col nome finale in `LaSpezia/Arte/Imbarco` (`ImportFile`,
materiali/texture off), LOD1/2 come `_Temp/TMPI_<asset>_LOD1/2`, `remove_lods` (di nuovo 3 LOD automatici) + `set_lod_from_static_mesh(..., True)`.
Tutti i LOD0 hanno UCX e `ImportFile` non ha aggiunto convessi automatici: **niente `remove_collisions`**. Nanite off, Use Simple Collision As Complex,
soglie 1,0 / 0,2 / 0,08, MinLOD Low/Medium 2 (temporanei a 0).

### Asset (`Arte/Imbarco`)
| Asset | Tri LOD0/1/2 | Bbox locale (uu) | Convessi | Slot → MI |
|---|---|---|---|---|
| `SM_Morin_Battello` | 3.351 / 1.675 / 501 | X ±1600 · Y ±377 · Z −140..687 | 19 | `MI_Morin_Imbarco` |
| `SM_Morin_PontileImbarco` | 1.240 / 620 / 185 | X −160..550 · Y −12..2851 · Z −400..104 | 18 | `MI_Morin_Imbarco`, `MI_Morin_Imbarco_Legno` |
| `SM_Morin_Biglietteria` | 324 / 162 / 48 | X ±170 · Y −145..115 · Z 0..310 | 1 | `MI_Morin_Imbarco` |
| `SM_Morin_Cestino` | 252 / 126 / 37 | X ±22,5 · Y ±22,5 · Z 0..95 | 1 | `MI_Morin_Imbarco` |
| `SM_Morin_Rastrelliera` | 768 / 346 / 114 | X ±125 · Y ±27 · Z 0..82,5 | 2 | `MI_Morin_Imbarco` |
| `SM_Banchina_Parabordo` | 58 / 28 / 8 | X ±15 · Y 0..22,5 · Z −90..0 | 1 | `MI_Morin_Imbarco` |

- Battello 32,0 × 7,54 × 8,27 m (larghezza con i parabordi), pontile 7,1 × 28,6 m: come da brief.
- **Nuova insidia:** dopo `set_lod_from_static_mesh` le sezioni dei LOD1/2 del pontile puntavano entrambe allo slot 0 (legno perso):
  corretto con `StaticMeshEditorSubsystem.set_lod_material_slot(mesh, 1, lod, 1)`. Controllare sempre le sezioni dei LOD sulle mesh a più slot.
- Texture importate una volta sola (`AssetImportTask`): `T_Morin_Imbarco_D/N/ORM`, `T_Morin_Imbarco_Legno_D/N/ORM`, 2048, N = Normalmap senza flip,
  ORM = Masks sRGB off, **LODBias 0**. `MI_Morin_Imbarco` e `MI_Morin_Imbarco_Legno` su `M_Morin_Master_PBR` (BaseColor/Normal/ORM).

### Posa (Outliner `Arte/Imbarco`; singoli duplicati da `Arte_Arredi_Gazebo`, HISM da `Arte_Arredi_Tombini` + `clear_instances`; `Rotator(roll, pitch, yaw)`)
| Attore | Mesh | Posa |
|---|---|---|
| `Arte_Imbarco_Battello` | Battello | **(6656, −6200, −100)**, yaw 90 (CSV X 6670: vedi sotto) |
| `Arte_Imbarco_Pontile` | PontileImbarco | (7200, −8020,56, 0), yaw 0,1241 |
| `Arte_Imbarco_Biglietteria` | Biglietteria | (7580, −7760,56, 1), yaw 0,1241 (sulla piattaforma di radice) |
| `Arte_Imbarco_Cestini` (HISM) | Cestino | 9, Y −9210, Z 15 |
| `Arte_Imbarco_Rastrelliere` (HISM) | Rastrelliera | 3, Y −9260, Z 15 |
| `Arte_Imbarco_Parabordi` (HISM) | Parabordo | 7, Z −52, yaw 0,1241 |
Attori nel livello: 158. Nessun attore esistente spostato, nascosto o cancellato.

**Battello −14 cm in X.** Dai vertici: i parabordi del battello (scafo locale Y ±377, Z −75..0 mondo, Y −7213..−5687) arrivavano a X 7047, il bottazzo
del pontile (locale X −160, Z −79..−39) sta a X 7038..7035 per la rotazione 0,1241°: **compenetrazione 9-12 cm**. Con X 6656 la distanza visiva
minima è ~2 cm, quella fra le collisioni 34 cm. Il CSV/Blender (`BATT_POS` 66,7) va allineato a 66,56 (segnalato).

### Verifiche (line trace in editor)
- **Ponti calpestabili:** griglia 40 × 80 uu sul battello: 653/720 colpi sul battello; coperta di poppa Z 0..5, passavanti laterali Z 0, ponte di prua
  Z 35-42, ponte superiore Z 230 (Z 410 tetto timoniera). La tuga è un convesso pieno (non si entra in cabina). Scala di poppa: rampa continua
  Z 0 → 230 (X 6440 prima dello spostamento, Y −7780..−7460).
- **Varco di poppa:** trace orizzontali a Z 60 dal pontile: liberi da Y −7620 a −7440 (1,8 m), murata colpita fuori dal varco; a Z 150 nessun ostacolo.
  Pavimento a Y −7530: pontile Z −10 fino a X 7050, poi acqua, poi coperta Z +1..+4 da X 6996: **fessura ~54 cm** (40 cm prima dello spostamento),
  gradino +11..14 cm. Da provare in sessione.
- **Pontile dalla banchina:** camminamento Z 0 → ciglio −0,5 (collisione) → piattaforma Z +1 da Y −8025 (X 7100/7300/7700), rampa dal Y −7650
  (Z +1) a −7200 (Z −34), impalcato Z −34 fino a Y −5250: continuo.
- **Compenetrazioni** (AABB di ogni istanza contro tutti gli attori `Arte*`/`Blockout*` visibili, poi trace): nessuna con scalette, bitte, panchine,
  lampioni, aiuole. Cestini e rastrelliere: trace orizzontali a +20/50/80 cm sull'impronta (ignorando l'imbarco) senza impatti, poggiano su
  `Arte_Pav_FasciaPalme` a Z 15, palma più vicina a 2,5 m (cestini) e 4,5 m (rastrelliere). Sovrapposizioni **volute** da Blender, da confermare:
  parabordi incassati ~4-5 cm nel paramento (origine a ciglio + 4 cm), labbro della piattaforma del pontile 12 cm sopra il ciglio (Z −39..+1).
- **Battello/banchina:** distanza minima 2,03 m (poppa Y −7800, parabordo banchina Y −8003). **Battello/pontile:** vedi sopra.
- **Scalette X 44 e 92:** 1.050 trace verticali ciascuna su X ±2 m, Y −7990..−6000: nessun impatto. Battello da X 6279, pontile fino a ~7750.
- **Acqua V2** (`Acqua_Golfo_Device`): box X −16850..33850, Y −11744..30844, superficie Z −103 → copre tutto il battello. Fascia blu dello scafo
  Z −130..−45 (locale −0,3..0,55): la superficie la taglia ~27 cm sopra il bordo inferiore; nel render la fascia blu emerge come previsto.

### Salvataggio, validazione, log, memoria
`save_dirty_packages` 09:30:31: 6 OFPA (date 09:30:33 su disco) + 14 asset in `Arte/Imbarco` + 12 `TMPI_*`; nessun pacchetto sporco.
Validazione `LaSpezia/`: **419/419 validi, 0 errori, 17 avvisi** (13 di prima + 4 "un solo LOD" su `TMPI_SM_Morin_Battello/PontileImbarco_LOD1/2`,
temporanei non referenziati). Log: nessun errore nuovo.
Memoria texture (metodo §21): 2 set 2048 D+N+ORM a LODBias 0 = **+21,3-26,7 MiB** (PNG sorgenti RGBA: caso alto se UE tiene l'alfa nelle D);
totale progetto stimato **213,6-259,4 MiB** (prima 192,3-232,7). Il caso alto supera la soglia di 245 MiB del §21.

### Render
`docs/qa/uefn_imbarco_v1.png` (UE 5300, −8350, 170; yaw 42,2; pitch −3; FOV 75; 1024 px; ombre; mip forzati): camminamento, ciglio, poppa del
battello con scala, fascia blu sull'acqua, biglietteria sulla piattaforma del pontile.

### Temporanei e problemi aperti
- 12 `LaSpezia/_Temp/TMPI_<asset>_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente.
- **(blender-artist)** `BATT_POS` X 66,7 → 66,56 (o parabordi del battello/bottazzo più sottili) e rigenerare il CSV.
- **(qa-tester)** salita a bordo dal varco con la fessura di ~54 cm, scala di poppa, rampa del pontile, nessun incastro fra scafo e pontile.
- **(utente)** memoria: se il caso alto è reale, valutare LODBias 1 su `T_Morin_Imbarco_Legno_*` o sul set atlante.

## 23. Incrocio v1, viale v4, parcheggio v3 (2026-11-20, ~09:40-09:55 ora locale)

Sorgenti: `exports/incrocio/` (28 FBX), `exports/incrocio/incrocio_posizioni_v1.csv` (56 righe), `exports/parcheggio/SM_Parcheggio_Asfalto_v2.fbx`,
`parcheggio_posizioni_v3.csv` (64), `exports/viale/viale_posizioni_v4.csv` (167), texture `blender/textures/incrocio/`. Controllo iniziale: nessun
asset né attore con questi nomi. Metodo del §13: LOD0 col nome finale (`ImportFile`, materiali/texture off), LOD1/2 come `_Temp/TMPX_<asset>_LOD1/2`,
`remove_lods` + `set_lod_from_static_mesh(..., True)`, Nanite off, Use Simple Collision As Complex, soglie 1,0 / 0,2 / 0,08, MinLOD Low/Medium 2
(asset a 1 LOD e temporanei: 0). Sezioni dei LOD1/2 rimappate sugli slot giusti (insidia del §22) su spartitraffico e modulo del viale.

### Asset
| Asset | Cartella | Tri LOD0/1/2 | Bbox locale (uu) | Convessi | Slot → MI |
|---|---|---|---|---|---|
| `SM_Morin_Dissuasore` | Arte/Incrocio | 182 / 130 / 54 | X ±12,5 · Y ±12,2 · Z 0..65 | 1 | `MI_Incrocio_Props` |
| `SM_Morin_Semaforo` | Arte/Incrocio | 214 / 104 / 54 | X −48..10 · Y ±24 · Z 0..466 | 2 | `MI_Incrocio_Props` |
| `SM_Morin_CartelloPrecedenza` | Arte/Incrocio | 56 / 50 / 14 | X −5..3,2 · Y ±45 · Z 0..294 | 1 | `MI_Incrocio_Props` |
| `SM_Morin_CartelloObbligoDestra` | Arte/Incrocio | 100 / 70 / 28 | X −5..3,2 · Y ±30 · Z 0..229 | 1 | `MI_Incrocio_Props` |
| `SM_Morin_Scooter` | Arte/Incrocio | 440 / 276 / 180 | X −98..95 · Y ±36 · Z 0,7..134 | 2 | `MI_Incrocio_Props` |
| `SM_Viale_Spartitraffico_Fiori` | Arte/Incrocio | 82 / 58 / 46 | X 0..475 · Y ±50 · Z 15..73 | 0 (automatico tolto) | `MI_Pav_Fascia`, `MI_Pav_Terra`, `MI_Viale_Fiori` |
| `SM_Viale_Italia_Incrocio` | Arte/Incrocio | 256 / 254 / 128 | X 0..1900 · Y −2415..0 · Z −5..15,5 | 0 (automatico tolto) | `MI_Molo_Asfalto`, `MI_Pav_Fascia`, `MI_Viale_Segnaletica` |
| `SM_Molo_DehorsVetrato` | Arte/Incrocio | 2.496 / 1.579 / 246 | X −828..495 · Y −11744..−11122 · Z 0..293 | 7 | `MI_Incrocio_Props` |
| `SM_Fondale_EdificioVetrate` | Arte/Incrocio | 44 / 44 / 10 | X ±1610 · Y −1200..220 · Z 0..740 | 0 (automatico tolto) | `MI_Fondale_EdificioVetrate` |
| `SM_Viale_Incrocio_Marciapiede` | Arte/Incrocio | 27 | X 660..2000 · Y −12085..−11375 · Z 0..15 | 2 | `MI_Molo_Masselli_Grigio`, `MI_Pav_Fascia`, `MI_Viale_Segnaletica` |
| `SM_Parcheggio_Asfalto_v2` | Arte/Parcheggio | 173 | X 2000..10600 · Y −12085..−10200 · Z 2..15 | 6 | come v1 (`MI_Parcheggio_Asfalto`, Segnaletica, Fascia, Terra) |

Texture (9, `Arte/Incrocio`, 1024, **LODBias 0**): `T_Incrocio_Props_*`, `T_Viale_Fiori_*` (D RGBA), `T_Fondale_EdificioVetrate_*`;
N = Normalmap senza flip, ORM = Masks sRGB off. MI nuove: `MI_Incrocio_Props`, `MI_Fondale_EdificioVetrate` su `M_Morin_Master_PBR`,
`MI_Viale_Fiori` su `M_Morin_Master_PBR_Masked` (masked, two-sided: stesso master delle chiome). Nessun master nuovo.

### Posa (HISM duplicati da `Arte_Arredi_Tombini` + `clear_instances`, singoli dal gazebo; `Rotator(roll, pitch, yaw)`; profilo `FortStaticMesh`)
| Attore (Outliner) | Mesh | Istanze / posa | Collisione |
|---|---|---|---|
| `Arte_Incrocio_Marciapiede` (Arte/Incrocio) | Viale_Incrocio_Marciapiede | (0,0,0) | Query Only |
| `Arte_Incrocio_DehorsVetrato` | Molo_DehorsVetrato | (0,0,0) | Query Only |
| `Arte_Incrocio_EdificioVetrate` | Fondale_EdificioVetrate | (4600, −15100, 0) | No Collision |
| `Arte_Incrocio_Spartitraffico` (HISM) | Spartitraffico_Fiori | 22 (Y −13150) | No Collision |
| `Arte_Incrocio_Dissuasori` / `_Semafori` / `_Scooter` | Dissuasore / Semaforo / Scooter | 8 / 4 / 6 | Query Only |
| `Arte_Incrocio_CartelliPrecedenza` / `_CartelliObbligoDestra` / `_CartelliP` | idem / `SM_Morin_CartelloP` | 1 / 1 / 2 | Query Only |
| `Arte_Incrocio_PlataniA` / `_PlataniB` | `Arte/Alberi/SM_Albero_LatifogliaA/B` | 5 / 4 (Giardini pubblici) | Query Only |
| `Arte_Viale_Incrocio` (HISM, Arte/Viale) | Viale_Italia_Incrocio | 1: `Viale_Strada_SO_00` (300, −12085, 0) | No Collision |
| `Arte_Parcheggio_Asfalto_v2` (Arte/Parcheggio) | Parcheggio_Asfalto_v2 | (0,0,0) | Query Only |

- **Viale v4:** `Viale_Strada_SO_00` tolta da `Arte_Viale_Strada` e ricreata in `Arte_Viale_Incrocio`; `Viale_Strada_SO_m1` (−1600, −12085) aggiunta a
  `Arte_Viale_Strada` (17 istanze); `Auto_065` (1742,22, −12222,96) tolta da `Arte_Parcheggio_AutoB_Col_v2_GrigioScuro` (dove era finita col §20;
  la copia nell'HISM nascosto `Arte_Viale_AutoB` non è stata toccata). Confronto con il CSV v4 sulle istanze visibili: 166/166 righe HISM trovate
  (+ `Prato_Giardini`, attore singolo), **0 duplicati, 0 istanze in più**.
- **Parcheggio v3:** tolte le 9 `ParkAuto_010-018`, aggiunte le 18 `ParkAuto_Pettine_00-17` negli HISM `_Col_v2` del loro modello/colore, 7 pini
  e `Cartello_P_01` aggiornati (match per posizione v2). Confronto di tutti gli HISM con il CSV v3 (X/Y ±1 uu, Z ±0,5, yaw/pitch ±0,05°):
  0 mancanti, 0 errati; le 12 istanze in più sono le auto del viale in sosta a Y ≈ −122 m spostate negli HISM del parcheggio al §20 (sono nel CSV v4).
- **Nascosti, non cancellati** (metodo §14): `Arte_Molo_Tendone` (sostituito dal dehors vetrato), `Arte_Parcheggio_Asfalto`. Attori nel livello: 172.

### Verifiche (line trace in editor)
- **Suolo X 0..25 m, Y 110..122 m** (griglia 25 uu, 4.949 punti, prop ignorati): **nessun buco**, salto massimo fra punti vicini **15 cm**.
  Suolo: strada del molo +1/+15, masselli del molo +1, marciapiede dell'incrocio +15 (1.130 punti), asfalto v2 +2, blockout fondale 0.
- **Marciapiede sulle lastre:** nella sua impronta il primo impatto è il marciapiede (1.128 punti) o la strada del molo; il blockout compare solo
  in 20 punti verso l'angolo smussato (Y < −11965), dove manca la collisione del marciapiede (sotto).
- **Collisione sotto il modulo del viale e nella fascia raggiungibile** (X ≥ 1700 fino a `Barriera_LatoCitta_Parcheggio`, Y −12185): sempre presente,
  ma è `Blockout_Fondale_v4` a Z 0 in X 975..2000 / Y < −11965 (marciapiede visibile a Z 15: **piedi 15 cm dentro**), in X ≥ 2000 / Y < −11800
  (asfalto v2 visibile a Z 2: 2 cm) e sotto il modulo del viale (Y < −12085, nessuna collisione propria). Gli UCX di marciapiede e asfalto v2 non
  coprono tutta l'impronta visibile: **da estendere in Blender** fino a Y −12085.
- **Prop:** trace orizzontali sulle istanze: dissuasori 8/8, semafori 4/4, scooter 6/6, cartelli 4/4, platani 9/9 colpiti. Dehors: 303/495 trace
  verticali sulla bbox colpiscono pavimento Z 75 / tetto Z 250-293, 14/21 trace orizzontali a Z 100 dal lato mare (gli altri passano dalle aperture).
  Dissuasori `_00-_04` (Y −11860), scooter, cartelli P e `Semaforo_02` stanno dentro o oltre il volume di `Barriera_LatoCitta_SO` (Y −11802..−12058):
  non raggiungibili.
- **Parcheggio:** auto a pettine 18/18 colpite dall'alto (tetti Z > 120); collisioni a pettine Y −11095..−11558; fila in linea lato corsia Y −10460:
  **corsia libera 6,35 m** (nessun ostacolo fra le due file). Pini: base sull'aiuola (cordolo a Y ≈ −11575, suolo Z 14); tronco (Z 20-150, con
  l'inclinazione) fino a Y −11571..−11583, tranne `Pino_04` che a 1,5 m arriva a −11557 (~18 cm sopra lo stallo, a ~1 cm dalla collisione dell'auto).
- **Barriere (§20):** nessun device toccato; i nuovi attori non aprono varchi (nessuna geometria tolta lungo le barriere; il tendone nascosto stava
  all'interno dell'area giocabile).

### Salvataggio, validazione, log, memoria
`save_dirty_packages` 09:50:35 (29 asset + 25 pacchetti mappa/OFPA), nessun pacchetto sporco. Validazione `LaSpezia/`: **460/460 validi, 0 errori,
18 avvisi** (17 noti + "un solo LOD" su `TMPX_SM_Molo_DehorsVetrato_LOD1`, temporaneo non referenziato). Log: nessun errore (solo avvisi
"accesso CPU" delle letture dei vertici fatte per la verifica).
Memoria texture (metodo §21): 3 set 1024 a LODBias 0 = **+8,7-10,0 MiB**; totale progetto stimato **222,3-269,4 MiB** (prima 213,6-259,4):
il caso alto resta sopra la soglia di 245 MiB.

### Render
- `docs/qa/uefn_incrocio_v1.png`: camera `CAM_Incrocio_F1` Blender (8; 118; 2,7) az −32° → UE (800, −11800, 270), yaw **−122** (= atan2(−cos az, sin az)),
  pitch 0, **FOV 150** (accettato da `RenderLevelPOVs`), 1024 px, ombre, mip forzati. Inquadratura uguale a `arte_incrocio_v1_confronto.png`:
  dehors a sinistra, scooter e dissuasori sul marciapiede, strisce, semafori e spartitraffico, edificio a vetrate a destra.
- `docs/qa/uefn_parcheggio_v3.png`: (2150, −10660, 212), yaw −8, pitch −6, FOV 78.

### Temporanei e problemi aperti
- 18 `LaSpezia/_Temp/TMPX_<asset>_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente.
- **(blender-artist)** UCX di `SM_Viale_Incrocio_Marciapiede` e `SM_Parcheggio_Asfalto_v2` fino al bordo visibile (Y −12085); valutare `Pino_04` (inclinazione).
- **(qa-tester)** in sessione: marciapiede e dehors, corsia, auto a pettine, barriera davanti al parcheggio.

## 24. Marciapiede v2, asfalto v3, dehors vetrato v2, Pino_04 (2026-11-20, ~10:00-10:10 ora locale)

Sorgenti: `exports/incrocio/SM_Viale_Incrocio_Marciapiede_v2.fbx`, `exports/parcheggio/SM_Parcheggio_Asfalto_v3.fbx`,
`exports/incrocio/SM_Molo_DehorsVetrato_v2.fbx` (+`_LOD1/_LOD2`), `exports/parcheggio/parcheggio_posizioni_v4.csv`. Metodo del §13/§23:
LOD0 col nome finale (`ImportFile`, materiali/texture off), LOD1/2 del dehors come `_Temp/TMPX_SM_Molo_DehorsVetrato_v2_LOD1/2`, `RemoveLods`,
`set_lod_from_static_mesh(..., True)`, Nanite off, Use Simple Collision As Complex, soglie 1,0 / 0,2 / 0,08, MinLOD Low/Medium 2 sul dehors
(0 su marciapiede e asfalto, 1 LOD). Nessun convesso automatico (tutti con UCX).

| Asset | Tri LOD0/1/2 | Bbox (uu) | Convessi | Slot → MI |
|---|---|---|---|---|
| `Arte/Incrocio/SM_Viale_Incrocio_Marciapiede_v2` | 27 | come v1 | 1 (X 955..2000, Y −12085..−11375, Z −30..15) | come v1 |
| `Arte/Parcheggio/SM_Parcheggio_Asfalto_v3` | 173 | come v2 | 6 | come v2 |
| `Arte/Incrocio/SM_Molo_DehorsVetrato_v2` | 3.168 / 1.579 / 366 | come v1 | 7 (identici alla v1, confrontati da `agg_geom`) | `MI_Incrocio_Props`, `MI_Molo_Vetro` |

- **Insidia §22 confermata:** dopo `set_lod_from_static_mesh` le sezioni dei LOD1/2 puntavano entrambe allo slot 0; rimappate con
  `set_lod_material_slot(mesh, 1, lod, 1)` → sezioni [0,1] su tutti e 3 i LOD.
- **Vetro:** nessun master traslucido nel progetto → nuovo `Arte/Materiali/M_Morin_Master_Vetro` (Translucent, two-sided, parametri `Colore`
  0,10/0,16/0,20, `Opacita` 0,25, `Metallic` 0,05, `Specular` 0,8, `Roughness` 0,08; usage Nanite e ISM come `M_Morin_Master_PBR`) e
  `Arte/Incrocio/MI_Molo_Vetro`. `MaterialCostToolset.GetCost` non misura (manca il Mali Offline Compiler nelle preferenze): usate le
  statistiche del compilatore. Istruzioni PS per modalità di illuminazione: Surface 1.197, Surface per-pixel 1.743, **Volumetric Directional
  385** (scelta), Non Directional 360 (opaco PBR: 213). Superficie piccola: costo accettabile. Niente riflessi speculari della scena (volumetrico).

### Posa (duplicati dei vecchi attori, stessa cartella, profilo `FortStaticMesh`, Query Only, nessun override di materiale)
| Nuovo | Mesh | Vecchio, **nascosto** (metodo §14: Hidden In Game, Visible falso, No Collision, Actor Collision off) |
|---|---|---|
| `Arte_Incrocio_Marciapiede_v2` | Marciapiede_v2, (0,0,0) | `Arte_Incrocio_Marciapiede` |
| `Arte_Parcheggio_Asfalto_v3` | Asfalto_v3, (0,0,0) | `Arte_Parcheggio_Asfalto_v2` |
| `Arte_Incrocio_DehorsVetrato_v2` | DehorsVetrato_v2, (0,0,0) | `Arte_Incrocio_DehorsVetrato` |

`Arte_Parcheggio_Pini` istanza 4 (= `Parcheggio_Pino_04`, (6744,35; −11621,15; 12)): yaw 56,52 → **−10**, pitch −7,03 → **−4** (CSV v4).
Attori nel livello: 175. Nulla cancellato.

### Verifiche (line trace in editor)
- **Suolo X 975..10600, Y −12085..−11300** (griglia 25 uu, 12.352 punti, prop ignorati): **nessun buco**. Impronta visibile del marciapiede
  (triangoli LOD0): 1.179/1.179 punti sul marciapiede v2 a Z 15. Impronta dell'asfalto: 9.061 a Z 2 e 1.160 sull'aiuola a Z 14;
  sovrapposizioni attese con strada del molo (X 2000-2375, Y > −11385, sopra) e pavimento del chiosco (X 9500-10150, Y > −11335, Z 15).
  **Problema:** 392 punti (X 9525..10575) colpiscono `Blockout_Passeggiata_v5` / `Blockout_Fondale_v4` a Z 0: il convesso dello smusso NE va
  da (9500, −11350) a (10600, −12085), ma il triangolo visibile da (9500, −10225) a (10600, −12085) → fascia senza collisione propria,
  piedi 2 cm dentro l'asfalto. Da correggere in Blender (PLAN.md).
- **Dehors v2:** 7 convessi identici alla v1; 260/495 trace verticali sulla bbox colpiscono pavimento/tetto (aperture libere come la v1).
  Nel render il vetro è trasparente (tavoli e sedie visibili dentro).
- **Pino_04:** collisione del tronco a Z 20-200 fino a Y −11580..−11582 (cordolo −11575): non entra più negli stalli; auto più vicina a
  Y −11553 (27 cm).

### Salvataggio, validazione, log
`save_dirty_packages` 10:05 e dopo il cambio di usage del master: nessun pacchetto sporco. Validazione `LaSpezia/`: **467/467 validi,
0 errori, 20 avvisi** (18 noti + "un solo LOD" su `TMPX_SM_Molo_DehorsVetrato_v2_LOD1/2`, temporanei). Log: nessun errore; avvisi
dell'import di `SM_Parcheggio_Asfalto_v3` (tangenti degeneri, normali quasi nulle: come le versioni precedenti, superficie piana) e un
"MI_Molo_Vetro missing usage flag Nanite" risolto attivando l'usage sul master.

### Render
`docs/qa/uefn_incrocio_v2.png`: stessa camera del §23 (800, −11800, 270; yaw −122; pitch 0; FOV 150; 1024 px; ombre; mip forzati).

### Temporanei e problemi aperti
- 2 nuovi `LaSpezia/_Temp/TMPX_SM_Molo_DehorsVetrato_v2_LOD1/_LOD2`; i 3 attori nascosti e le loro mesh restano finché l'utente non conferma.
- **(blender-artist)** convesso dello smusso NE di `SM_Parcheggio_Asfalto_v3` (sopra).

## 25. Viale Italia senza sosta e traffico finto (2026-11-20, ~10:15-10:30 ora locale)

Decisione dell'utente (2026-11-20): in Viale Italia niente auto in sosta, solo auto che passano; le auto del parcheggio vicino alla passeggiata
restano. Nessun attore né asset cancellato.

### Auto in sosta tolte
- **Nascosti** (metodo §14: Hidden In Game, componente Visible falso, No Collision, Actor Collision off): i 9 HISM `Arte_Viale_Auto{A,B,C}_v2_<Colore>`
  (78 istanze, `Arte/Viale`). Le vecchie `Arte_Viale_AutoA/B/C` restano nascoste.
- **Istanze rimosse** dagli HISM del parcheggio: le auto del viale che non compaiono in `exports/parcheggio/parcheggio_posizioni_v4.csv` (match per
  asset e X/Y ±2 uu). Sono **12**: la 13a (`Auto_065`, 1742,22; −12222,96) era già stata tolta al §23. Dopo la rimozione gli HISM `_Col_v2`
  del parcheggio coincidono col CSV v4: **49/49**, 0 in più. Trasformazioni rimosse (UE, uu, world space, scala 1, pitch e roll 0; indice prima della rimozione):

| HISM | Indice | X | Y | Z | Yaw |
|---|---|---|---|---|---|
| `Arte_Parcheggio_AutoB_Col_v2_Argento` | 3 | 6518,11 | −12207,36 | 2,0 | 179,95 |
| `Arte_Parcheggio_AutoB_Col_v2_Argento` | 6 | 2288,02 | −12212,58 | 2,0 | 179,07 |
| `Arte_Parcheggio_AutoB_Col_v2_Argento` | 7 | 5422,19 | −12207,64 | 2,0 | −179,66 |
| `Arte_Parcheggio_AutoA_Col_v2_Azzurro` | 1 | 8625,17 | −12208,61 | 2,0 | −179,33 |
| `Arte_Parcheggio_AutoA_Col_v2_Azzurro` | 3 | 3862,15 | −12214,65 | 2,0 | −179,70 |
| `Arte_Parcheggio_AutoC_Col_v2_BiancoPerla` | 3 | 5947,79 | −12209,48 | 2,0 | −179,64 |
| `Arte_Parcheggio_AutoB_Col_v2_Arancio` | 2 | 7577,52 | −12216,41 | 2,0 | 179,52 |
| `Arte_Parcheggio_AutoA_Col_v2_Bianco` | 5 | 4364,12 | −12221,57 | 2,0 | −179,27 |
| `Arte_Parcheggio_AutoA_Col_v2_Bianco` | 6 | 4894,62 | −12214,52 | 2,0 | −179,71 |
| `Arte_Parcheggio_AutoA_Col_v2_Rosso` | 3 | 8094,05 | −12211,69 | 2,0 | 178,97 |
| `Arte_Parcheggio_AutoC_Col_v2_BluScuro` | 0 | 7041,51 | −12220,64 | 2,0 | 179,88 |
| `Arte_Parcheggio_AutoC_Col_v2_BluScuro` | 3 | 3361,11 | −12213,24 | 2,0 | 178,72 |

  Per ripristinarle: `add_instance` con queste trasformazioni (world space) nello stesso HISM.
- **Verifica:** nessuna istanza visibile di mesh auto tra Y −12100 e −14000; line trace verticali (X −1600..33000, Y −12100..−14000, passo
  50 × 25 uu): impatti su auto solo a Y −12100..−12175 = musi delle auto a pettine del parcheggio (CSV v4, fino a ~Y −12180). Il resto è
  `Blockout_Fondale_v4`, masselli, strada del molo, un semaforo.

### Corsie (dalla mesh `SM_Viale_Italia_Strada`, origine moduli Y −12085, carreggiata Z 2,5)
| Fascia | Y UE | Uso |
|---|---|---|
| Striscia con stalli lato giardini | −12100..−12330 | vuota (stalli ancora disegnati, vedi problemi) |
| Corsia mare 1 | −12330..−12700 (asse −12515) | traffico NE, 34 km/h |
| Corsia mare 2 | −12700..−13080 (asse −12890) | traffico NE, 42 km/h |
| Spartitraffico | −13100..−13200 | — |
| Striscia con stalli lato città | −13220..−13450 (asse −13335) | traffico SO, 31 km/h |
| Corsia città | −13450..−13840 (asse −13645) | traffico SO, 40 km/h |

Il modello ha 3 corsie di marcia + 2 strisce di sosta; `ref/sezione.md` dice 4 corsie su due carreggiate (assi Y 128 e 135 m): uso anche la
striscia lato città come quarta corsia. **Senso di marcia [S]:** carreggiata lato mare verso **NE** (+X), lato città verso **SO** (−X), come
vuole la circolazione a destra (vedi `decisioni.md`).

### Traffico (metodo senza Verse)
- **Attori:** `Arte_Viale_Traffico_00..13` (Outliner `Arte/Viale/Traffico`), `FortStaticMeshActor`, componente **Movable**, profilo `NoCollision`,
  Actor Collision off, mesh `SM_Morin_Auto_{A,B,C}_v2_<Colore>` (9 colori a rotazione), override slot 0 → `MI_Morin_Auto_v2_Luci`.
  Fari a +X locale nella mesh (verificato incrociando UV e texture E: bianchi a X +196..+221, rossi a −196..−220): yaw 0 verso NE, 180 verso SO.
- **Sequenza:** `LaSpezia/Arte/Viale/LS_Viale_Traffico`, 30 fps, frame 0-1800 (**60 s**), 14 binding possessable con traccia Transform.
  Ogni auto percorre X −15000 → 33000 (o il contrario) a velocità costante (chiavi lineari), poi salta a Z −3000 sotto il suolo (chiavi
  costanti) e aspetta lì il giro successivo. Corsa 480 m: 41,1 s a 42 km/h, 50,8 s a 34, 43,2 s a 40, 55,7 s a 31.
  Partenze (s): mare 2 → 0/14/31/45, mare 1 → 6/26/47, città → 3/18/33/48, striscia città → 10/30/52. Le auto con la corsa a cavallo della fine
  del giro hanno a frame 0 e 1800 la stessa posizione intermedia: loop continuo.
- **Verifica (scrub ogni 10 frame):** in media **7,8 auto** sul tratto visibile del viale (X −16..326 m, max 9); distanza minima fra auto della
  stessa corsia **155 m**; nessun salto di posizione con l'auto visibile; il salto avviene a X −150 m (oltre il modulo `Viale_Strada_SO_m1`,
  ~115 m oltre la barriera del molo) e a X +330 m (fine del fondale, dove finisce il suolo).
- **Device:** `Device_Cinematica_TrafficoViale` (Cinematic Sequence Device, `Device/Cinematiche`, (16000, −14300, 0)): Riproduzione automatica SÌ,
  Loop SÌ, Visibilità TUTTI, Si abilita nella fase SEMPRE, attore sempre connesso SÌ, HUD visibile, input non disattivato.
  **Insidia:** `SetClassicDeviceOption` rifiuta la sequenza ("Allowed values: ." vuoto anche dopo il salvataggio); assegnata con
  `set_editor_property('Sequence', ...)` in transazione: `ListClassicDeviceOptions` la mostra, validazione OK. Da confermare in sessione.
- **Costo:** 14 static mesh mobili (1.804-1.844 tri al LOD0, LOD1/2 attivi), nessuna luce dinamica, solo emissive.

### Fari
- `T_Morin_Auto_v2_E` importata in `Arte/Auto` (2048, sRGB, LODBias 0, compressione Default). Memoria stimata +2,7-5,3 MiB (BC1/BC3 con mip).
- Il master `M_Morin_Master_PBR` non ha emissive: duplicato in **`Arte/Materiali/M_Morin_Master_PBR_Emissive`** (stesso grafo + `Emissive`
  TextureSampleParameter2D sulla stessa UV × scalare `Emissive_Intensita`, default 0, → Emissive Color; usage ISM e Nanite come l'originale).
- **`Arte/Auto/MI_Morin_Auto_v2_Luci`**: stesse D/N/ORM di `MI_Morin_Auto_v2`, `Emissive` = E, **`Emissive_Intensita` 4** (Blender 6): nel render al
  tramonto fari bianchi e fanali rossi leggibili senza effetto neon (`docs/qa/uefn_viale_traffico_fari.png`). Usata solo dalle 14 auto in movimento.

### Audio
- **Nessun suono di traffico o clacson utilizzabile.** L'Audio Player accetta solo la sua lista interna (136 voci: stinger, Halloween, fiera,
  fantasy): niente traffico. In `/AmbientAudioContent` ci sono loop di città (`Ambience_CrimeTown_City_Evening_Loop_Ext_Cue` ecc.), ma al salvataggio
  `AssetValidator_AssetReferenceRestrictions` dà **errore** ("fa riferimento illegalmente a /AmbientAudioContent/..."); la validazione per oggetto
  con usecase Script diceva VALID: non basta. Nessun clacson nemmeno lì (solo treno, nave; il clacson del bus è in `/Game`, non utilizzabile).
- Attori lasciati **vuoti e inattivi** (non cancellati): `Device_Audio_TrafficoViale_SO` (Audio Player, `Device/Audio`, (8000, −13800, 300),
  audio NESSUNO, volume 0,3, Riproduci all'impatto NO, invisibile) e `Audio_Viale_BrusioTraffico` (AmbientSound, Outliner `Audio`,
  (16000, −13800, 300), suono None, auto-activate off, attenuazione box 180 × 9 × 6 m + falloff 40 m già impostata). Servono WAV importati
  nel progetto (PLAN.md).

### Salvataggio, validazione, log, render
`save_dirty_packages` dopo ogni passo, nessun pacchetto sporco. Validazione `LaSpezia/`: **471/471 validi, 0 errori, 20 avvisi** (gli stessi del §24,
"un solo LOD" sulle mesh statiche). Log: l'unico errore è quello dell'AmbientSound col cue di `/AmbientAudioContent`, risolto togliendo il cue
(il salvataggio successivo non lo ripete); il resto sono avvisi EOS/HTTP e di deprecazione Python. Attori nel livello: 192 (+17: 14 auto,
2 device, 1 AmbientSound). Render (sequenza a metà, frame 900, mip forzati, ombre, 1024 px, FOV 80): `docs/qa/uefn_viale_traffico.png`
(UE 24500, −12150, 450; yaw −160; pitch −7) e `docs/qa/uefn_viale_traffico_fari.png` (20900, −12750, 140; yaw −170; pitch −3).

### Problemi aperti
1. **(qa-tester/utente)** In sessione: la sequenza parte da sola, in loop, per tutti i giocatori; movimento fluido; salti non visibili.
2. **(utente)** File audio esterni (traffico lontano, clacson): vedi PLAN.md.
3. **(blender-artist)** Stalli di sosta ancora disegnati sulle strisce laterali del viale: ridisegnare la segnaletica a 4 corsie.

## 26. Viale a 4 corsie, incrocio senza marciapiede, asfalto parcheggio v4, audio del viale (2026-11-20, ~11:00-11:20 ora locale)

Sorgenti: `exports/viale/SM_Viale_Italia_Strada_v2{,_Varco}{,_LOD1,_LOD2}.fbx`, `exports/incrocio/SM_Viale_Italia_Incrocio_v3{,_LOD1,_LOD2}.fbx`,
`exports/incrocio/SM_Viale_Incrocio_Asfalto.fbx`, `exports/molo/SM_Molo_Pav_Strada_v2.fbx`, `exports/parcheggio/SM_Parcheggio_Asfalto_v4.fbx`,
`exports/audio/*.wav`. Metodo del §23/§24 (LOD0 col nome finale via `ImportFile`, materiali off; LOD1/2 come `_Temp/TMPX_<asset>_LOD1/2`,
`remove_lods` + `set_lod_from_static_mesh`, sezioni dei LOD1/2 rimappate sugli slot 0/1/2, Nanite off, Use Simple Collision As Complex,
soglie 1,0 / 0,2 / 0,08, MinLOD Low/Medium 2 sulle mesh a 3 LOD, 0 sulle altre e sui temporanei). Convesso automatico tolto dai moduli del viale
(come v1/v2). Materiali riassegnati alle MI esistenti, nessuna MI nuova.

| Asset | Tri LOD0/1/2 | Bbox (uu) | Convessi | Slot → MI |
|---|---|---|---|---|
| `Arte/Viale/SM_Viale_Italia_Strada_v2` | 80 / 80 / 32 | X 0..1900 · Y −2415..0 · Z −5..15,5 | 0 | `MI_Molo_Asfalto`, `MI_Pav_Fascia`, `MI_Viale_Segnaletica` |
| `Arte/Viale/SM_Viale_Italia_Strada_v2_Varco` | 132 / 132 / 46 | idem | 0 | idem |
| `Arte/Incrocio/SM_Viale_Italia_Incrocio_v3` | 244 / 244 / 130 | idem | 0 | idem |
| `Arte/Incrocio/SM_Viale_Incrocio_Asfalto` | 100 | X 660..2000 · Y −12085..−11375 · Z −15..15 | 2 | idem |
| `Arte/Molo/SM_Molo_Pav_Strada_v2` | 22 | X 650..2400 · Y −12100..−8600 · Z −15..1 | 3 | `MI_Molo_Asfalto` (unico slot: il `M_Pav_Fascia` della v1 era il cordolo tolto) |
| `Arte/Parcheggio/SM_Parcheggio_Asfalto_v4` | 173 | come v3 | 4 | come v3 |

### Posa
- `Arte_Viale_Strada` (HISM): mesh → `SM_Viale_Italia_Strada_v2` (pose invariate); **istanza X 2200 (`Viale_Strada_SO_01`) tolta** (era (2200, −12085, 0),
  yaw 0, scala 1) e ricreata come attore singolo `Arte_Viale_Strada_SO_01_Varco` (Arte/Viale, stessa posa, mesh `_Varco`, No Collision come l'HISM).
  Istanze HISM: 16.
- `Arte_Viale_Incrocio` (HISM, 1 istanza SO_00 a (300, −12085, 0)): mesh → `SM_Viale_Italia_Incrocio_v3`.
- Nuovi a (0,0,0), duplicati del vecchio attore (FortStaticMesh, Query Only): `Arte_Incrocio_Asfalto` (Arte/Incrocio), `Arte_Molo_Pav_Strada_v2` (Arte/Molo),
  `Arte_Parcheggio_Asfalto_v4` (Arte/Parcheggio).
- **Nascosti, non cancellati** (metodo §14): `Arte_Incrocio_Marciapiede_v2`, `Arte_Molo_Pav_Strada`, `Arte_Parcheggio_Asfalto_v3`
  (`Arte_Incrocio_Marciapiede` era già nascosto). `Semaforo_02` (1320, −12045, 15) non toccato: ora poggia sulla base tonda.

### Verifiche (line trace in editor, prop ignorati)
- **X 950..2600, Y −12100..−10900** (griglia 25 uu, 3.283 punti): **nessun buco**. Asfalto incrocio Z +2 (1.183 punti) + base del semaforo Z 15
  (6 punti, X 1300-1350 / Y −12075..−12025); strada molo v2 Z +1 (748); asfalto parcheggio v4 Z +2 (1.194) + aiuola Z 14 (6); lastre
  `Arte_Pav_AngoloMolo` Z 15 solo sulla fila Y −10900/−10925 (bordo della passeggiata, come prima); `Blockout_Fondale_v4` Z 0 solo sulla fila
  Y −12100 (oltre il bordo dell'asfalto −12085, sotto il viale: zona non giocabile). **Nessun cordolo residuo**, nessun gradino tra molo, ramo,
  parcheggio e incrocio (salti di 1 cm); l'unico salto di 15 cm è la base del semaforo.
- **Asfalto parcheggio v4:** smusso NE (triangolo visibile (9500, −10225)-(10600, −12085), griglia 20 uu) 2.618/2.618 punti su v4 a Z +2;
  tacca X 2000-2400 / Y −11400..−10925 (griglia 10 uu) 1.968/1.968 su v4 a Z +2. La v3 lasciava 392 punti sul blockout.

### Audio
- **Import** (`SoundWaveToolset.ImportFile`) in `LaSpezia/Audio/`: `A_Viale_TrafficoLontano_Loop` (60,0 s, **Looping** sì), `A_Viale_Clacson_01..06`
  (0,85 / 1,55 / 0,50 / 2,00 / 0,70 / 0,60 s). Nuovo `ATT_Viale_ClacsonLontano` (SoundAttenuation: sfera 15 m, falloff 120 m lineare,
  spazializzato), assegnato ai 6 clacson.
- **Brusio:** `Audio_Viale_BrusioTraffico` (AmbientSound, (16000, −13800, 300)) suono = loop, Auto Activate sì, volume 0,3, override attenuazione:
  box 180 × 9 × 6 m (estensioni 18000 × 900 × 600) + falloff **80 m lineare** (prima 40 m log): sulla passeggiata (Y ≈ −8500..−9000, ~40 m
  dal box) arriva a circa metà del volume 0,3.
- **Clacson:** l'Audio Player (`Device_Audio_TrafficoViale_SO`) accetta il SoundWave del progetto (impostato con `ObjectToolset.SetProperties`
  su `audio`; non compare nella lista di `SetClassicDeviceOption`), ma riproduce un solo suono, senza casualità né pause tra le ripetizioni
  (il loop di un clacson da 1 s suonerebbe di continuo). Soluzione senza Verse: **tracce Audio sui binding delle auto nella sequenza
  `LS_Viale_Traffico`** (60 s, già in loop per tutti con `Device_Cinematica_TrafficoViale`); il suono segue l'auto:
  | t (s) | Clacson | Auto (X al momento) |
  |---|---|---|
  | 3,00 | 03 | `Arte_Viale_Traffico_12` (~45 m, carreggiata città) |
  | 3,65 | 06 | idem (doppio colpo) |
  | 19,00 | 01 | `Arte_Viale_Traffico_00` (~71 m, carreggiata mare) |
  | 41,00 | 04 | `Arte_Viale_Traffico_08` (~74 m, carreggiata città) |
  Intervalli 16 / 22 / 22 s; volume sezione 0,45, pitch 1. Clacson_02 e _05 importati ma non usati. Lo schema si ripete identico ogni 60 s
  (niente casualità). `Device_Audio_TrafficoViale_SO`: audio = Clacson_01, nessuna riproduzione automatica, quindi **inerte**.
- **Traffico riallineato** ai centri corsia v2 (canale Y di ogni binding): −12515 → −12380, −12890 → −12860, −13335 → −13375, −13645 → −13685.

### Salvataggio, validazione, log, render
`save_dirty_packages` 11:14 e dopo la correzione dei temporanei: nessun pacchetto sporco. Validazione `LaSpezia/` + mappa: **492/492 validi,
0 errori**, avvisi = i 20 noti ("un solo LOD"); i 12 avvisi "MinLOD 2 fuori intervallo" sui 6 nuovi `TMPX_*` risolti (MinLOD 0). Log: nessun
errore dopo l'import (nessun "riferimento illegale" sui SoundWave, sulla sequenza o sui device). Attori nel livello: 196 (+4).
Render `docs/qa/uefn_incrocio_v3.png`: punto della foto dell'utente, Blender (15,6; 100,5; 2,1) → UE (1560, −10050, 210), yaw −90 (verso il viale),
pitch −10, FOV 90, 1024 px, ombre: asfalto continuo dall'imbocco del molo al viale, nessun cordolo.

### Temporanei e problemi aperti
- 6 nuovi `LaSpezia/_Temp/TMPX_SM_Viale_Italia_{Strada_v2,Strada_v2_Varco,Incrocio_v3}_LOD1/_LOD2`; eliminabili con conferma dell'utente.
- **(utente/qa-tester)** In sessione: brusio udibile ma di sottofondo; clacson lontani; le tracce Audio delle cinematiche suonano davvero in UEFN
  (non verificato in gioco). Piano B: Timer device + Audio Player, oppure Verse per la casualità vera.
- Asset ora inutilizzati (nessuna istanza visibile): `SM_Viale_Italia_Strada`, `SM_Viale_Italia_Incrocio` (restano finché l'utente non conferma).

## 27. Ponte Thaon di Revel v1 (2026-11-20, ~11:30-11:50 ora locale)

Sorgenti: `exports/ponte/` (4 asset + `_LOD1`/`_LOD2`, LOD con bake_rotation), `exports/ponte/ponte_posizioni_v1.csv` (tutti a (0,0,0), yaw 0),
texture `blender/textures/ponte/`. Controllo iniziale: nessun asset né attore con questi nomi. Metodo del §13/§22: LOD0 col nome finale in
`LaSpezia/Arte/Ponte` (`ImportFile`, materiali/texture off, combine on), LOD1/2 come `_Temp/TMPP_SM_Ponte_<pezzo>_LOD1/2`, `remove_lods`
(di nuovo 3 LOD automatici, anche sui temporanei) + `set_lod_from_static_mesh(..., True)`, sezioni dei LOD controllate slot per slot (nessuna da
rimappare), Nanite off, Use Simple Collision As Complex, soglie 1,0 / 0,2 / 0,08, MinLOD Low/Medium 2 (temporanei 0).
`remove_collisions` sugli stralli (ImportFile aveva aggiunto 1 convesso automatico) e attore stralli No Collision.
Nota: il prefisso `TMPP_` era già usato dai temporanei di auto/cartelli del §19-20 (nomi diversi, nessun conflitto).

| Asset (`Arte/Ponte`) | Tri LOD0/1/2 | Vertici LOD0 | Bbox (uu) | Convessi | Slot → MI |
|---|---|---|---|---|---|
| `SM_Ponte_Impalcato` | 13.538 / 6.698 / 1.964 | 18.864 | X −873..300 · Y 0..17900 · Z −300..437 | 14 | Legno, Acciaio, Paramento → `MI_Ponte_Legno`, `MI_Ponte_Acciaio`, `MI_Banchina_Paramento` |
| `SM_Ponte_Parapetti` | 33.472 / 17.148 / 4.944 | 37.392 | X −845..325 · Y 0..17893 · Z 10..551 | 22 | Acciaio, Cavo (LOD2 solo Acciaio: i cavi sono decimati) |
| `SM_Ponte_Antenne` | 1.436 / 572 / 380 | 1.088 | X −420..−171 · Y 7962..12938 · Z 350..3350 | 2 | Acciaio |
| `SM_Ponte_Stralli` | 3.360 / 2.016 / 448 | 6.048 | X −868..270 · Y 4737..16163 · Z 226..2953 | 0 | Cavo |
Totale LOD0 51.806 tri (budget 120k). **Segno di Y verificato:** Blender Y negativo → UE Y positivo, il ponte va verso Mirabello (Y +), come il blockout.

Texture (`TextureToolset.ImportFile`, una volta sola, condivise): `T_Ponte_Legno_D/N/ORM`, `T_Ponte_Acciaio_D/N/ORM` 4096, `T_Ponte_Cavo_D/N/ORM` 1024;
N = Normalmap senza flip, ORM = Masks, sRGB off. **Insidia nuova:** le 4096 arrivano con **LODBias 2** automatico (le 1024 con 0): portate a **0**
come da brief. MI nuove su `M_Morin_Master_PBR` (BaseColor/Normal/ORM): `MI_Ponte_Legno`, `MI_Ponte_Acciaio`, `MI_Ponte_Cavo`.

### Posa (Outliner `Arte/Ponte`, duplicati di `Arte_Arredi_Gazebo`: FortStaticMesh, Query Only, Static, nessun override di materiale)
`Arte_Ponte_Impalcato`, `Arte_Ponte_Parapetti`, `Arte_Ponte_Antenne`, `Arte_Ponte_Stralli` (No Collision) in (0,0,0), yaw 0, scala 1.
**Nascosto, non cancellato** (metodo §14): `Blockout_Ponte` (`SM_Blockout_Ponte`). `Blockout_Mirabello` resta visibile. Attori nel livello: 200 (+4).

### Verifiche (line trace in editor)
- **Calpestio:** griglia trasversale ogni 50 cm (Y −100..18000, ±4,5 m dall'asse, passo 10 cm) + profilo sull'asse ogni 10 cm: **nessun buco**.
  Rampa Z 0 → 430 (Y 0 → 7000, 6,1 %), piano 430 fino a Y ~13610, discesa a **130 a Y 17900**. Larghezza libera fra i parapetti **5,7 m**
  (X asse −280..+290), 7,7 m agli anelli delle antenne. Nessun gradino trasversale (0 cm) né longitudinale (max 3,1 cm ogni 50 cm di rampa).
- **Fori delle antenne** (Y ~7750-8250 e ~12750-13000): attorno a ogni antenna una ringhiera ad anello; ai lati due corsie di **2,8 m e 2,9 m**,
  nessuna cella senza collisione fra impalcato, ringhiera e antenna.
- **Raccordi:** passeggiata/impalcato a Y 0: `Arte_Molo_Pav_Masselli_03` Z +1 → impalcato Z 0..0,3, salto **1 cm**, nessuna fessura (passo 5 cm,
  28 colonne). Impalcato/spalla Mirabello a Y 17900: Z 130,0 → `Blockout_Mirabello` 129,4, salto **0,6 cm**, nessuna fessura.
- **Parapetti:** trace orizzontali ogni 25 cm (Y 25..17875) da dentro verso fuori, entrambi i lati, a +20/60/100/115 cm dal calpestio: **colpiti
  sempre**, a +125 e +140 mai → altezza 1,15-1,25 m (1,21 da Blender). Nessun varco.
- **Stralli:** 3.286 trace (Visibility e Camera, verticali e orizzontali nella bbox) senza alcun colpo; componente No Collision.
- **Linea di vista** dalla partenza (24000, −8250/−8400/−8450, 180) alle due antenne a Z 10/20/30 m: il primo colpo è sempre l'antenna (27-76 uu dal bersaglio).

### Memoria texture (metodo §21, ricalcolato su tutte le 138 texture di `LaSpezia/`, esclusi i `_Temp`)
- Ponte: Legno 42,7-53,3 + Acciaio 42,7-53,3 + Cavo 2,7-3,3 = **+88,0-110,0 MiB** (a LODBias 0).
- Totale progetto: prima **225,7-281,5 MiB**, ora **313,7-391,5 MiB**: **oltre la soglia di 245 MiB in entrambi i casi**. Nessuna modifica fatta.
- Proposta (NON applicata), risparmio basso-alto in MiB: `T_Ponte_Acciaio_*` a LODBias 1 (2048 effettive; antenne e parapetti bianchi, poco dettaglio
  da vicino) −32,0-40,0 · `T_Morin_Auto_v2_*` −10,0-14,0 · `T_Morin_Imbarco_*` e `T_Morin_Imbarco_Legno_*` −16,0-20,0 · `T_Pav_Terra_*` −8,0-10,0 ·
  `T_Banchina_Paramento_*` (lato mare, si vede solo dall'acqua) −8,0-10,0. Totale −74,0-94,0 → **239,7-297,5 MiB**: sotto soglia solo nel caso basso.
  Per chiudere il caso alto: "Compress Without Alpha" sulle D opache (il caso alto suppone che UE tenga l'alfa nei PNG RGBA) oppure Legno a LODBias 1.
  `T_Ponte_Legno_*` resta a 0 (ci si cammina sopra).

### Salvataggio, validazione, log
`save_dirty_packages` 11:38:32: 24 asset (4 mesh, 8 temporanei, 9 texture, 3 MI) + 5 OFPA (4 attori nuovi + `Blockout_Ponte`) + 1 external object,
date 11:38:34-38 su disco; **nessun pacchetto sporco**. Validazione `LaSpezia/`: **515/515 validi, 0 errori, 27 avvisi** = 20 noti + 6 "un solo LOD"
sui `TMPP_SM_Ponte_*` (temporanei; le antenne sono sotto soglia) + **`SM_Ponte_Parapetti`: "numero di vertici del LOD0 troppo elevato"** (37.392).
Log: nessun errore.

### Render (`docs/qa/`, 1024 px, ombre, `r.Streaming.FullyLoadUsedTextures 1`)
- `uefn_ponte_v1_calpestio.png`: (−120, 4300, 429), yaw 90, pitch 4, FOV 62 (= `CAM_Ponte_F1`), confronto con `arte_ponte_v1_confronto_calpestio.png`.
- `uefn_ponte_v1_passeggiata.png`: (24000, −8400, 180), yaw 142,3, pitch 3, FOV 70 (= `CAM_Ponte_Partenza`, X 240 m): due antenne visibili, nessun ostacolo.
- **Insidia:** il primo render del calpestio mostrava i parapetti **senza montanti** (proxy di rendering non aggiornato dopo la posa); dopo un
  `set_forced_lod_model` 1 → 0 sul componente (nessuna modifica salvata) i montanti compaiono. In sessione va controllato a occhio.
- **Stralli:** da vicino continui, con qualche tratto più scuro (ombra sui cilindri sottili); a ~120 m (vista di prova dall'acqua, FOV 40) restano
  visibili ma **tratteggiati** (aliasing dei cavi da pochi cm), non spariscono. In movimento è probabile uno sfarfallio: da verificare in sessione.

### Temporanei e problemi aperti
- 8 `LaSpezia/_Temp/TMPP_SM_Ponte_{Impalcato,Parapetti,Antenne,Stralli}_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente.
- **(utente)** Memoria oltre soglia: scegliere fra le proposte qui sopra.
- **(blender-artist)** `SM_Ponte_Parapetti` 37k vertici: avviso del validatore. Opzione: dividere in due mesh (lato sinistro/destro) o in moduli istanziati.
- **(blender-artist, facoltativo)** stralli tratteggiati a distanza: raggio un po' maggiore nei LOD1/2 o card.
- **(qa-tester)** In sessione: rampa e discesa, passaggio ai lati delle antenne, parapetti, montanti visibili, sfarfallio degli stralli.
- `Blockout_Mirabello`: a Y 18000 la rampa di arrivo ha un rialzo a +110 (parapetto del blockout) solo sul lato X+; sul lato X− bordo libero a ~1,2 m
  dal suolo (preesistente, non toccato).

### Memoria: "senza alpha + 5 a metà" applicato (scelta dell'utente, 2026-11-20 ~11:45)
1. **Compress Without Alpha** (`compression_no_alpha`) su **47 texture `_D` opache** di `LaSpezia/`: Tombino, Banchina Paramento/Ghisa/Ciglio/Blocchi,
   Fondale (Tenda, 10 Colline/Colle_Suolo, Facciata, Palazzo A/B/C, EdificioVetrate), Pav Lastre/Terra/Fascia/Cubetti, PalmaA_Tronco, Platano e Pino
   cortecce, Molo Asfalto/Facciate/Masselli, Chiosco, Dehors, Oleandro_Fusto, Prato, Bosso, Viale_Segnaletica, Auto, Auto_v2, Parcheggio_Asfalto,
   Cartelli, NewJersey, Imbarco, Imbarco_Legno, Incrocio_Props, Ponte Legno/Acciaio/Cavo.
   Controllo dell'alfa: grafi dei master (`GetGraph`): solo `M_Morin_Master_PBR_Masked` usa `BaseColor.A` (→ OpacityMask); PBR, Pav, Fondale,
   PBR_Emissive non usano mai il canale A; Vetro (traslucido) non ha texture. **Escluse** (MI sul master masked): `T_Morin_PalmaA_Fronde_D`,
   `T_Albero_Latifoglia_Chioma_D`, `T_Morin_PinoDomestico_Chioma_D`, `T_Morin_Oleandro_Chioma_D`, `T_Viale_Fiori_D`, `T_Morin_Gazebo_Fregio_D`.
   Il bosso è su `M_Morin_Master_PBR` opaco: incluso.
2. **LODBias 1** (19 texture): `T_Ponte_Acciaio_*`, `T_Morin_Auto_v2_*` (anche `_E`), `T_Morin_Imbarco_*`, `T_Morin_Imbarco_Legno_*`, `T_Pav_Terra_*`,
   `T_Banchina_Paramento_*`.
3. **Stima (metodo §21, 138 texture):** prima 313,7-391,5 MiB → **dopo 235,5-236,2 MiB**, sotto la soglia di 245 (ponte 54,0 MiB). Il caso alto ora
   differisce dal basso solo per `T_Morin_Auto_v2_E`.
`save_dirty_packages` 11:47:37 (60 texture), nessun pacchetto sporco; validazione `LaSpezia/` 515/515 validi, 0 errori, 27 avvisi (gli stessi).
Cattura di controllo `docs/qa/uefn_ponte_v1_calpestio_mem.png` (stessa camera di `uefn_ponte_v1_calpestio.png`): colori invariati.

## 28. Testata di Porto Mirabello v1 (2026-11-20, ~12:20-12:45 ora locale)

Sorgenti: `exports/mirabello/` (16 FBX), `exports/mirabello/mirabello_posizioni_v1.csv` (102 righe utili; nel CSV le auto sono **41**, non 47).
Controllo iniziale: nessun asset né attore con questi nomi. Metodo del §13/§27: LOD0 col nome finale in `LaSpezia/Arte/Mirabello`
(`ImportFile`, materiali/texture off, combine on), LOD1/2 come `_Temp/TMPMB_SM_Mirabello_<asset>_LOD1/2`, `remove_lods` (di nuovo 3 LOD
automatici su tutti) + `set_lod_from_static_mesh(..., True)`, sezioni di ogni LOD controllate (nessuna da rimappare), Nanite off,
Use Simple Collision As Complex, soglie 1,0 / 0,2 / 0,08, MinLOD Low/Medium 2 sui 4 asset a 3 LOD, 0 sui pezzi unici e sui temporanei.
`remove_collisions` dove non c'è UCX (Fondale, Pontile, YachtA/B, Fanale e temporanei: `ImportFile` aveva aggiunto 1 convesso automatico).
**Nessuna texture né materiale creato** (in `Arte/Mirabello` solo le 9 StaticMesh; texture di `LaSpezia/` sempre 138): slot `M_<x>` → MI
esistenti `MI_<x>` (Parcheggio_Asfalto, Viale_Segnaletica, Molo_Masselli/_Grigio, Morin_Bosso, Morin_Prato, Ponte_Legno, Ponte_Acciaio,
Banchina_Paramento, Pav_Fascia, Morin_Imbarco/_Legno).

| Asset (`Arte/Mirabello`) | Tri LOD0/1/2 | Bbox (uu) | Convessi |
|---|---|---|---|
| `SM_Mirabello_Suolo` | 104 | X −2020..980 · Y 16764..21800 · Z 0..100 | 4 |
| `SM_Mirabello_Pianerottolo` (+ scala) | 644 | X −1780..300 · Y 17900..18660 · Z 0..255 | 8 |
| `SM_Mirabello_Passerella` | 1.292 | X −60..4613 · Y 17660..18040 · Z 0..245 | 5 |
| `SM_Mirabello_Multipiano` | 1.319 | X −13600..3550 · Y 20770..30280 · Z 0..1030 | 1 (fronte X −2496..1504, Y 20828..21904, Z 0..810) |
| `SM_Mirabello_Fondale` | 549 | X −6000..11680 · Y 16120..25000 · Z −160..120 | 0 |
| `SM_Mirabello_Pontile` | 248 / 240 / 10 | X 0..4800 · Y ±148 · Z −55..100 | 0 |
| `SM_Mirabello_YachtA` | 600 / 272 / 126 | X −695..625 · Y ±200 · Z −85..350 | 0 |
| `SM_Mirabello_YachtB` | 522 / 282 / 122 | X −550..550 · Y ±180 · Z −70..1550 | 0 |
| `SM_Mirabello_Fanale` | 144 / 96 / 72 | X ±60 · Y ±60 · Z 0..630 | 0 |

### Posa (Outliner `Arte/Mirabello`; singoli duplicati da `Arte_Arredi_Gazebo`, HISM da `Arte_Arredi_Tombini` + `clear_instances`; `Rotator(roll, pitch, yaw)`)
- Singoli in (0,0,0): `Arte_Mirabello_Suolo`, `_Pianerottolo`, `_Passerella`, `_Multipiano` (Query Only, `FortStaticMesh`), `_Fondale` (No Collision);
  `Arte_Mirabello_Fanale` (10970, 16560, 2), No Collision.
- HISM nuovi (anche per gli asset riusati, che altrove sono già HISM): `Arte_Mirabello_Banchina_Moduli` (7, yaw 176,93 = −183,07),
  `_Banchina_Bitte` (2), `_Lampioni` (3), `_Panchine` (2), `_Cestini` (2), `_PalmaA` (3, scala 1) Query Only; `_Pontili` (5), `_YachtA` (9),
  `_YachtB` (23) No Collision; auto in 17 HISM `Arte_Mirabello_Auto{A,B,C}[_Col]_v2_<Colore>`.
- **Auto:** con la barriera spostata (sotto) 20 auto senza collisione del CSV cadevano nell'area giocabile (Auto_006, 009-018, 032-040, X −2116..4368):
  spostate negli HISM `_Col_v2_` dello stesso modello e colore (stessa regola del §20). Risultato: **25 con collisione, 16 senza** (tutte fuori area).
  L'HISM `Arte_Mirabello_AutoB_v2_Argento`, rimasto vuoto, è stato riusato (rinominato `..._AutoB_Col_v2_Argento`, mesh `_Col`, Query Only).
- **Nascosto, non cancellato** (metodo §14): `Blockout_Mirabello` (Visible falso, Hidden In Game, No Collision, Actor Enable Collision no).
- `Blockout_Fondale_v4` non toccato. Il suo blocco edificio dietro il multipiano (Z 700, X −15200..3150, Y 21850..30350) **sporge di 16 m**
  oltre il fianco ovest del multipiano (X −15200..−13600, tutta la profondità, alto 7 m); dentro l'impronta è coperto (multipiano alto 10,3 m).
  Attori nel livello: 234 (+34).

### Barriera (decisione dell'utente "Sposta la barriera")
Barrier device con le stesse opzioni (Scatola, invisibile, sempre, altezza 10, base −700); larghezza/profondità accettano solo 0,5 o valori interi.

| Label | Centro | Unità L × P | Ingombro (`BarrierBounds`) |
|---|---|---|---|
| `Barriera_Mirabello_LatoPiuX` (spostata, prima X 1110) | (5150, 18875, −700) | 0,5 × 12 | X 5022..5278 · Y 15803..21947 |
| `Barriera_Mirabello_FronteNE` (nuova, dup.) | (3448, 20572, −700) | 9 × 0,5 | X 1144..5752 · Y 20444..20700 |
| `Barriera_Mirabello_RaccordoNE` (nuova, dup.) | (1272, 21226, −700) | 0,5 × 3 | X 1144..1400 · Y 20458..21994 |

`LatoMenoX` e `Fondo` invariate. Perimetro: LatoMenoX → Fondo → Raccordo (dentro la X dell'UCX del multipiano, che finisce a 1504) →
FronteNE (davanti alla facciata: Y 20828 a X 1400, Y 20770 all'angolo X 2790; oltre X 1504 il multipiano non ha collisione) → LatoPiuX.
Area nuova: X 980..5022, dal mare a Y 20444 (passerella, parcheggio a due file, quai in masselli fino alla recinzione).
**Continuità** (passo 4 uu sulla linea mediana, quadrato ±120 uu attorno a ogni campione): nessun varco; le sole "mancanze" sono le due estremità
in mare (Y < 15925, lato mare aperto come prima) e l'angolo esterno Fondo/Raccordo (X 1272..1400, Y 21994..22008), chiuso dalla sovrapposizione
X 1144..1272 · Y 21752..21994. Sovrapposizioni: LatoMenoX/Fondo 256 × 195, Fondo/Raccordo 128 × 242, Raccordo/FronteNE 256 × 242, FronteNE/LatoPiuX 256 × 256.

### Verifiche (line trace in editor)
- **Ponte → pianerottolo** (X −790..−230 ogni 10 cm, Y 17850..17960 ogni 2 cm): nessuna fessura, salto max 0,2 cm (impalcato 131 → pianerottolo 130).
- **Scala** (5 profili X −1760..−1440, ogni 2 cm): rampa di collisione continua da Z 130 (Y 18260) a Z 0 (Y ~18660), pendenza ~19°, nessun buco.
- **Passerella** (3 profili Y 17700/17850/18000, ogni 5 cm): continua da Z 130 a 0, finisce a X 4610 a raso su `Blockout_Fondale_v4` (Z 0).
- **Ringhiere** (trace orizzontali a +20/60/100/115 cm, ogni 20-25 cm): colpite su passerella (entrambi i lati), scala (entrambi), pianerottolo O/S/E,
  testa della passerella; altezza ~1,15-1,25 m. **Bordo aperto:** pianerottolo lato N tra il parapetto del ponte e la testa della passerella,
  **X −190..−55 a Y 17900** (1,35 m), salto di 1,30 m sul suolo (Z 0) senza ringhiera (sotto non c'è acqua: non è una trappola).
- **Gradini** (griglia 50 cm su X −2000..5000, Y 16500..20450, prop esclusi): nessun gradino percorribile oltre 40 cm; i salti > 40 cm sono bordi di
  passerella/pianerottolo con ringhiera, la siepe (Z 100, con UCX) e il bordo aperto sopra. Suolo Mirabello +15 → fondale 0 a X 980 (15 cm).
- **Suolo continuo**: nessun buco interno nella griglia; nell'area nuova il suolo con collisione è `Blockout_Fondale_v4` a Z 0 (sotto il
  `SM_Mirabello_Fondale` visivo a +2/+5 cm). Senza collisione: **recinzione metallica** tra quai e parcheggio (si attraversa) e prati del Fondale;
  multipiano oltre X 1504 (chiuso dalla barriera).
- **Yacht, pontili, fanale**: nessun impatto (No Collision). Nell'area nuova il **Pontile_087** (X 2795, radice a Y 16500, 0,75 m dal ciglio) e i
  suoi yacht sono a portata di salto: chi ci sale cade in acqua. Altri yacht nell'acqua davanti all'area (X −1951..3659). Decide l'utente.

### Salvataggio, validazione, log, memoria
`save_dirty_packages` 12:39:26: 17 asset (9 mesh + 8 temporanei) + 36 OFPA + 1 external object (date su disco controllate); **nessun pacchetto
sporco**. Validazione `LaSpezia/`: **532/532 validi, 0 errori, 33 avvisi** = 27 noti + 6 "un solo LOD" (Fondale, Multipiano, Passerella,
Pianerottolo: pezzi unici; `TMPMB_..._YachtA_LOD1`, `_YachtB_LOD1`). Log: nessun errore (solo EOS/audio). **Memoria texture invariata:
235,5-236,2 MiB** (nessuna texture nuova, 138 texture); mesh nuove ~6,5k tri LOD0 in tutto.

### Render (`docs/qa/`, 1024 px, ombre, `r.Streaming.FullyLoadUsedTextures 1`)
- `uefn_mirabello_v1.png`: (−510, 15600, 440), pitch −9, yaw 90, FOV 80, dal calpestio del ponte verso l'arrivo. I parapetti del tratto finale
  si vedono **a giorno** (montanti, corrimano, cavi), **non** come pannelli pieni bianchi. Le auto del parcheggio appaiono quasi bianche
  (`T_Morin_Auto_v2_*` a LODBias 1 + mip in streaming, come nel §20): da guardare in sessione.
- `uefn_mirabello_v1_b.png`: (−1300, 19000, 180), pitch 4, yaw −84, FOV 80, dalla testata verso il ponte: scala, muro del pianerottolo in
  paramento, ringhiere, antenne e stralli.

### Temporanei e problemi aperti
- 8 `LaSpezia/_Temp/TMPMB_SM_Mirabello_{Pontile,YachtA,YachtB,Fanale}_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente.
- **(blender-artist)** Ringhiera mancante sul bordo N del pianerottolo, Blender X −1,9..−0,55, Y −179.
- **(blender-artist)** `Blockout_Fondale_v4`: il blocco Z 7 m sporge di 16 m a ovest del multipiano (X −152..−136 m): versione tagliata a X ≥ −136.
- **(blender-artist)** UCX per la recinzione del Fondale (ora attraversabile).
- **(utente)** Pontile_087 e yacht senza collisione raggiungibili dall'area nuova: accettare (si cade in acqua) o dare collisione.
- **(qa-tester)** In sessione: barriere nuove, scala a rampa, passerella fino a terra, bordo aperto, auto quasi bianche.

## 29. Correzioni Mirabello v2 e auto bianche (2026-11-20, ~13:00-13:15 ora locale)

### A. Import (metodo §28: `ImportFile` da zero con nomi nuovi, materiali/texture off; nessun asset vecchio cancellato)
| Asset | Tri LOD0/1/2 | Convessi | Note |
|---|---|---|---|
| `Arte/Mirabello/SM_Mirabello_Pianerottolo_v2` | 704 | 9 (UCX) | `remove_lods` (pezzo unico), bbox identica alla v1 (X −1780..300 · Y 17900..18660 · Z 0..255) |
| `Arte/Mirabello/SM_Mirabello_Fondale_v2` | 549 | 1 (UCX recinzione, **nessun `remove_collisions`**) | `remove_lods`; nessun convesso automatico in più |
| `Arte/Mirabello/SM_Mirabello_YachtB_v2` | 522 / 282 / 77 | 0 (`remove_collisions`) | LOD1/2 da `_Temp/TMPMB_SM_Mirabello_YachtB_v2_LOD1/_LOD2` (`set_lod_from_static_mesh`), soglie 1,0/0,2/0,08, MinLOD Low/Medium 2 |
| `Blockout/SM_Blockout_Fondale_v5` | 397 | 41 (UCX) | `remove_lods`; slot `M_Blockout_Fondale` → `M_Blockout_Fondale`, `M_Blockout_Verde` → `MI_Morin_Prato_Mondo` (come v4) |
Tutti: Nanite off, Use Simple Collision As Complex, slot → stesse MI degli asset v1 (nessuna texture né materiale nuovo).

Posa: `Arte_Mirabello_Pianerottolo` → mesh v2 (Query Only, invariato); `Arte_Mirabello_Fondale` → mesh v2, **No Collision → `FortStaticMesh` Query Only**;
`Arte_Mirabello_YachtB` (HISM) → mesh v2, 23/23 istanze, No Collision; nuovo `Blockout_Fondale_v5` (dup. di `Blockout_Fondale_v4`, (0,0,0), Query Only,
Outliner `Blockout`). **Nascosto, non cancellato** (§14): `Blockout_Fondale_v4` (Visible falso, Hidden In Game, No Collision, collisione attore off).
Attori nel livello: 235 (+1). `SM_Mirabello_Pianerottolo`, `_Fondale`, `_YachtB` e `SM_Blockout_Fondale_v4` restano inutilizzati nel Content Browser.

Line trace (in editor):
- **Ringhiera N** (X −195..−50 ogni 5 cm, da Y 17960 a 17840, calpestio Z 130): colpita **30/30 a +20/60/100/115 cm**, 1/30 a +125 (parapetto del ponte),
  0/30 a +140 → altezza ~1,15-1,25 m, varco chiuso.
- **Recinzione** (X 1000..5000 ogni 50 cm, da Y 16700 a 18300): colpita **81/81 a Z 10/20/60/100/120**, mai a 130 → alta ~1,25 m, a Y 17243..17500
  (leggermente ruotata). Suolo sotto = `Blockout_Fondale_v5` Z 0. Trace verticali sul Fondale (griglia 4 m, 1035 punti): **0 colpi** → prati e
  asfalto restano senza collisione, l'unico convesso è la recinzione.
- **Fondale v5 vs v4** (`line_trace_component` sulle due mesh, griglia 2,5 m su tutta la bbox, 47.718 punti): **204 differenze, tutte a X −150,5..−138,
  Y 21850..30100**: v4 Z 700 (blocco) → v5 nessuna superficie. Il blocco non sporge più a ovest del multipiano; dentro l'impronta (X −135..−120)
  resta il blocco a Z 700. Nota: nella fascia tagliata non c'è suolo con collisione (fuori dall'area giocabile, oltre la barriera `Fondo`).
- Yacht a vela: render `docs/qa/uefn_mirabello_v2_yacht.png` (1900, 17300, 500), yaw −90, FOV 60: genoa **bianco** sugli yacht vicini (LOD0).
  Sugli yacht a 20-45 m (LOD1/LOD2) lo strallo mostra ancora **tratti neri** vicino alla base e in testa: probabili UV dei LOD1/2 non aggiornate.

### B. Auto tutte bianche: causa e correzione
- **Sintomo** (`docs/qa/uefn_auto_colori_prima.png`, camera di `uefn_parcheggio_v2.png`): auto completamente bianche, senza vetri, fanali né cerchi, cioè
  non un mip basso (le celle dell'atlante 3 × 3 sono grandi, ~680 px; un mip mescolato darebbe colori medi e vetri scuri), ma **nessuna texture**.
- **Prove:** `TextureToolset.GetSize` = **0 × 0** su 4 texture su 138: `T_Morin_Auto_v2_D`, `T_Morin_Imbarco_D`, `T_Morin_Imbarco_Legno_D`, `T_Ponte_Acciaio_D`
  (le uniche con "senza alfa" **e** LODBias 1 cambiati insieme, insieme a Pav_Terra_D e Banchina_Paramento_D che invece si erano compilate). Log:
  `LogTexture: Warning: ... contains no miplevels! (Format: 0)` per tutte e 4 alle **11:47:19 ora locale** (= passo "senza alfa + LODBias" del §27).
  Il sorgente è intatto (`ExportPng` del D: atlante 2048 con i 9 colori corretti). Impostazioni del D normali: LOD Group World, Mip Gen da gruppo,
  MaxTextureSize 0, streaming normale (NeverStream off), sRGB on. MI corrette: `MI_Morin_Auto_v2` = D/N/ORM giusti, `MI_Morin_Auto_v2_Luci` = D/N/ORM + `_E`
  (Emissive_Intensita 4) usata solo dalle auto in movimento. La `_E` era sana (2048). Luce/esposizione non c'entrano (le altre superfici sono normali).
- **Causa:** il LODBias è stato scritto mentre la ricompilazione asincrona dovuta a "senza alfa" era in corso → dati di piattaforma vuoti → il materiale
  campiona la texture di default (bianca). Riprodotto: riscrivere `lod_bias` su quella texture ha di nuovo dato "no miplevels" (log 13:09:13).
- **Correzione (memoria invariata):** sulle 4 texture `compression_no_alpha` False → attesa compilazione → True → attesa (GetSize di nuovo 2048/2048/2048/4096),
  LODBias 1 lasciato. Dopo: 138/138 texture con dimensione valida, nessun nuovo avviso. `T_Morin_Auto_v2_E` invariata (LODBias 1).
  **Memoria texture: 235,5-236,2 MiB, invariata** (stesse impostazioni del §27; la stima già le contava).
- **Regola:** dopo un cambio di compressione aspettare la fine della compilazione (GetSize > 32) prima di toccare LODBias o altro, e controllare GetSize ≠ 0.
- Render: `docs/qa/uefn_auto_colori_fix.png` (stessa camera di `uefn_parcheggio_v2.png`): colori, vetri, fanali, targhe corretti;
  `docs/qa/uefn_mirabello_auto_fix.png` (−300, 18750, 330), pitch −12, yaw 35, FOV 70: parcheggio di Mirabello colorato. Lo stesso guasto
  riguardava gli asset sull'atlante Imbarco (battelli, multipiano, pontili, yacht) e l'acciaio del ponte: ora hanno di nuovo la texture (yacht verificati nel render).

### Salvataggio, validazione
`save_dirty_packages` 13:10:31: 10 asset (4 mesh, 2 temporanei, 4 texture) + 5 OFPA (Pianerottolo, Fondale, YachtB, Fondale_v4, Fondale_v5); date su disco
controllate; **nessun pacchetto sporco**. Validazione `LaSpezia/`: **538/538 validi, 0 errori, 37 avvisi** (33 noti + "un solo LOD" sui nuovi pezzi
unici e temporanei).

### Temporanei e problemi aperti
- 2 `LaSpezia/_Temp/TMPMB_SM_Mirabello_YachtB_v2_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente.
- **(blender-artist)** `SM_Mirabello_YachtB_v2_LOD1/_LOD2`: strallo con tratti neri da 20-45 m (UV del genoa non aggiornate nei LOD?).
- **(qa-tester)** Confermare in sessione e dopo un riavvio dell'editor che le 4 texture restino colorate.

## 30. Memoria reale di pubblicazione (Memory Calculation di UEFN, letta il 2026-11-20 ~13:30 ora locale)
Sola lettura, nessuna sessione avviata, nessuna modifica agli asset. Fonte: il calcolo ufficiale `LogValkyrieMemoryCalculation`
che UEFN rifà a ogni cook (avvio sessione / push changes) e pubblica nello **Spatial Profiler** come sorgente **"Pubblica"**
(metrica `ValkyrieFortniteEditorPublishMemory`, "Budget memoria mappa", categoria Pubblicazione). Letta con
`SpatialProfilerToolset.ProfilerToolset.ListSources/ListMetrics/GetMetricStats` e dal log dell'editor.

**Ultimo calcolo disponibile: cook delle 09:38 ora locale (2026-11-20)**, cioè con la sessione dell'utente del mattino.
È **precedente** a ponte (§27), riduzione texture (§27), Mirabello v1/v2 (§28-29): quei lavori entreranno nel prossimo cook.

| Voce | Byte | MiB | % del limite |
|---|---:|---:|---:|
| **Totale "Budget memoria mappa" (picco)** | **10.651.648** | **10,16** | **3,4 %** |
| Mesh statiche | 6.801.408 | 6,49 | 2,2 % |
| Blueprint (device, ecc.) | 1.133.568 | 1,08 | 0,36 % |
| Texture | 1.131.520 | 1,08 | 0,36 % |
| Materiali | 739.328 | 0,71 | 0,24 % |
| Livello | 494.592 | 0,47 | 0,16 % |
| Altro | 304.128 | 0,29 | 0,10 % |
| Audio | 47.104 | 0,04 | 0,01 % |
| **Limite (soglia di pubblicazione)** | **314.572.800** | **300** | 100 % |

Andamento nel log: 5,81 MB (19/11 16:56) → 8,16 MB (19/11 22:28) → 10,65 MB (20/11 09:38). Un solo campione
(`sampled=1`, cella da 2,59 km che copre tutta la mappa): il calcolo è fatto sull'isola intera, non per posizione.

**Lettura.** Il budget di pubblicazione conta la memoria **statica** dei pacchetti cotti. I mip delle texture in streaming
non ci entrano: alle 09:38 avevamo già ~200-260 MiB di texture secondo la stima a mano (§21-§26), ma la voce Texture vale 1,08 MiB.
Quindi **la stima a mano (236 MiB) e la soglia interna di 245 MiB non misurano il limite di Epic**: misurano (per eccesso) la memoria
texture a piena risoluzione, che conta per il pool di streaming e il download, non per il blocco di pubblicazione.

**LODBias → 0 su tutte (le 30 vicine alla corsia e le 19 del §27).** Effetto sul budget di pubblicazione: trascurabile
(la parte statica di una texture è l'header più la coda dei mip piccoli, indipendente dal LODBias; ordine dei KB, < 0,1 MiB in tutto).
Il ponte e Mirabello aggiungono soprattutto mesh: stima prudente del prossimo cook **15-25 MiB (5-8 %)**, margine > 90 % sul limite,
ben oltre il 15 % richiesto. Costo vero di LODBias 0: memoria texture a runtime (stima a mano: torna a 313,7-391,5 MiB di mip
a piena risoluzione, gestiti dallo streaming) e dimensione di download (limite 400 MiB; v7 era 21,4 MiB). **Nulla applicato**: decide l'orchestratore.

**Voci più pesanti per asset.** Gli strumenti MCP danno solo i totali per tipo e per cella; nessun elenco per asset, nessun file
di report su disco (`Saved/` del progetto e dell'editor controllati). Da leggere a mano nel pannello (vedi sotto).

**Streaming World Partition: NON attivo** (evidenza indiretta: `FortWorldSettings.bHideEnableStreamingWarning = false`, cioè
l'avviso "streaming disattivato" è ancora mostrato; e il calcolo usa un solo campione su tutta la mappa). La proprietà
`WorldPartition.bEnableStreaming` non è leggibile via MCP. Se si attivasse, il budget si calcolerebbe per posizione del giocatore
(picco della cella peggiore, non il totale): con 3,4 % sul totale non serve. Decisione del progetto invariata: non accettare il popup.

**Per l'utente, dopo la prossima sessione o push changes** (il cook rifà il calcolo): scheda **Spatial Profiler** → sorgente
**"Pubblica"** → metrica **"Budget memoria mappa"** (unità byte; soglia 314.572.800 = 300 MiB); sotto "Memoria mappa per tipo" le voci
Texture / Mesh statica / Materiale / Blueprint / Audio / Livello / Altra. Se il pannello mostra l'elenco degli asset della cella,
annotare i primi 15. In alternativa, nel registro di output cercare `Memory calculation complete: peak=` (byte).

**Proposta:** sostituire la soglia interna di 245 MiB con il limite reale (300 MiB di memoria statica, con allarme al 85 % = 255 MiB
del valore misurato) e trattare la memoria texture a piena risoluzione come voce di qualità/prestazioni, da verificare in sessione
con lo Spatial Profiler (metriche client, profilo Desktop) e non come vincolo di pubblicazione.

**Decisione (2026-11-20, utente tramite orchestratore):** la soglia interna di 245 MiB è sostituita dal limite reale: **300 MiB di memoria
statica di pubblicazione, allarme all'85 % (255 MiB)**, controllato sul valore **"Budget memoria mappa" della sorgente "Pubblica"** dello
Spatial Profiler. Le stime "metodo §21" restano solo informative (memoria texture a runtime). Riga in `docs/decisioni.md`.

## 31. LODBias 0 su tutte le texture (2026-11-20, ~13:18-13:22 ora locale)
- Inventario `LaSpezia/`: 138 Texture2D, **49 a LODBias 1** (nessuna a 2): `T_Morin_Gazebo_Fregio_*`, `T_Banchina_Paramento_*`, `T_Banchina_Ciglio_*`,
  `T_Pav_Terra_*`, `T_Albero_Latifoglia_Chioma_*`, `T_Molo_Asfalto/Facciate/Masselli_*`, `T_Morin_PinoDomestico_Chioma_*`, `T_Morin_Oleandro_Chioma_*`,
  `T_Morin_Prato_*`, `T_Parcheggio_Asfalto_*`, `T_Morin_Auto_v2_D/N/ORM/E`, `T_Morin_Imbarco_*`, `T_Morin_Imbarco_Legno_*`, `T_Ponte_Acciaio_*` (4096).
- Procedura (regola §29): **una texture alla volta**: `finish_all_asset_compilation` → `lod_bias = 0` → `finish_all_asset_compilation` →
  `TextureToolset.GetSize` > 32 → successiva. 49/49 a dimensione piena (2048, Ponte_Acciaio 4096; Fregio 2048 × 512). "Compress Without Alpha" non toccato.
- Controllo finale: **138/138** a LODBias 0 e dimensione valida; nessun nuovo `contains no miplevels` nel log (gli ultimi sono quelli già noti del §29).
- Salvati i 49 pacchetti; poi **0 pacchetti sporchi** (contenuti e mappe).
- Validazione `LaSpezia/` (`validate_assets_with_settings`): **538 controllati, 538 validi, 0 errori**, 37 avvisi tutti di `ValkyrieValidator_StaticMesh`
  (già noti, conteggio vertici); `ValkyrieValidator_Textures` 138, 0 avvisi.
- Render `docs/qa/uefn_lodbias0_parcheggio.png` (camera di `uefn_auto_colori_fix.png`: UE 2150, −10660, 212; yaw −8; pitch −6; FOV 78; 1024 px; ombre;
  mip forzati residenti 20 s): auto colorate con vetri, fanali e targhe; asfalto, strisce, chiome e palme nitidi.
- Memoria: budget di pubblicazione invariato in pratica (§30); stima a mano a piena risoluzione (solo informativa) ≈ 314-392 MiB a runtime in streaming.
  Da rileggere "Budget memoria mappa" (sorgente "Pubblica") dopo la prossima sessione dell'utente.

## 32. Blocco 2 v1: passeggiata X 251-566 (2026-11-20, ~13:00-13:25 ora locale)

Sorgenti: `exports/blocco2/` (5 asset con LOD, 7 pezzi unici, 9 CSV in coordinate UE), `exports/blockout/SM_Blockout_{Passeggiata_B2,Fondale_B2_Terreno}.fbx`,
texture `blender/textures/blocco2/T_Morin_Corten_D/N/ORM.png`. Metodo del §13/§21 (LOD0 col nome finale via `ImportFile`, materiali/texture off;
LOD1/2 come `_Temp/TMPB2_<asset>_LOD1/2`; `remove_lods` + `set_lod_from_static_mesh(..., True)`; sezioni dei LOD1/2 rimappate sugli slot 0/1;
Nanite off; Use Simple Collision As Complex; soglie 1,0/0,2/0,08; MinLOD Low/Medium 2 sulle mesh a 3 LOD, 0 sui pezzi unici e sui temporanei).
Tutti gli FBX LOD0 hanno UCX (controllato nei file): nessun `remove_collisions`. Nessun attore né asset cancellato.

### Asset (`LaSpezia/Arte/Blocco2`, blockout in `LaSpezia/Blockout`)
| Asset | Tri LOD0/1/2 | Bbox locale (uu) | Convessi | Slot → MI |
|---|---|---|---|---|
| `SM_Morin_Cannone` | 1.208 / 840 / 280 | X ±51 · Y −112..145 · Z 0..111 | 2 | `MI_Banchina_Ghisa`, `MI_Morin_Cannone_Legno` |
| `SM_Morin_Redamare` | 612 / 540 / 468 | X ±400 · Y ±30 · Z 0..135 | 2 | `MI_Morin_Corten` |
| `SM_Banchina_Angolo_MoloItalia` | 1.311 / 731 / 31 | X 0..762 · Y −55..3216 · Z −300..0 | 2 | `MI_Banchina_Blocchi`, `MI_Banchina_Paramento` |
| `SM_Morin_ChioscoOttagonale` | 138 / 122 / 106 | X ±370 · Y ±370 · Z 0..345 | 2 | `MI_Morin_Chiosco`, `MI_Morin_Dehors` |
| `SM_Morin_AstaBandiera` | 140 / 112 / 70 | X ±22 · Y ±21 · Z 0..1152 | 2 | `MI_Pav_Fascia` |
| `SM_Pav_Camminamento_4m_B2` | 2 | X 0..400 · Y −940..−54 · Z 0 | 1 (Z −30..0) | `MI_Pav_Lastre` |
| `SM_Pav_FasciaPalme_Fine` | 36 | X 0..900 · Y −10200..−8915 · Z ±15 | 1 | `MI_Pav_Cubetti`, `MI_Pav_Fascia` |
| `SM_Morin_Prato_Giardini_B2` | 105 | X 25000..55875 · Y −12085..−10190 · Z −5..8 | 3 | `MI_Morin_Prato` |
| `SM_Pav_Vialetti_B2` | 26 | X 28731..55875 · Y −11800..−10096 · Z 5..11 | 9 | `MI_Pav_Cubetti` |
| `SM_Pav_Piazzetta_Chiosco_B2` | 18 | X 52660..55875 · Y −11545..−10200 · Z 7..15 | 1 | `MI_Pav_Cubetti`, `MI_Pav_Fascia` |
| `SM_Pav_Piazzale_Fine_B2` | 10 | X 54927..56600 · Y −12100..−4709 · Z −300..0 | 3 | `MI_Pav_Cubetti` |
| `SM_Pav_Scritta_Morin` | 265 | X 55467..55802 · Y −9960..−9260 · Z 15,3 | 1 | `MI_Pav_Fascia` |
| `Blockout/SM_Blockout_Passeggiata_B2` | 19 | X 25000..55920 · Y −12100..−7927 · Z −300..−15 | 1 | `M_Blockout_Pietra` → `MI_Pav_Lastre` |
| `Blockout/SM_Blockout_Fondale_B2_Terreno` | 10 | X 33000..58000 · Y −30000..−12085 · Z −300..0 | 1 | `M_Blockout_Verde` → `MI_Morin_Prato_Mondo` |

- **Texture:** `T_Morin_Corten_D/N/ORM` 1024 (Poly Haven, CC0) in `Arte/Blocco2`; N = Normalmap senza flip, ORM = Masks, sRGB off, LODBias 0.
  Regola §29 rispettata (una alla volta, `GetSize` = 1024 dopo ogni cambio). Texture del progetto: 141 (+3).
- **MI nuove** (`Arte/Blocco2`, parent `M_Morin_Master_PBR`): `MI_Morin_Corten` (D/N/ORM corten) e `MI_Morin_Cannone_Legno`
  (`T_Morin_Imbarco_Legno_D/N/ORM`, Tinta 0,30 / 0,22 / 0,16). Tutti gli altri slot sulle MI esistenti.
- **Log:** `SM_Morin_ChioscoOttagonale` (e i suoi LOD) dà "basi tangenti degeneri / normali quasi nulle": facce degeneri nel modello (blender-artist).

### Posa (Outliner `Arte/Blocco2/<gruppo>`, blockout in `Blockout`; HISM nuovi, nessuna istanza aggiunta agli HISM del Blocco 1)
HISM duplicati da `Arte_Arredi_Tombini` (Query Only `FortStaticMesh`, Static) o da `Arte_Viale_PalazzoA` (No Collision) + `clear_instances`;
pezzi unici duplicati da `Arte_Arredi_Gazebo`, l'ancora da `Arte_Banchina_AncoraMonumento`, i blockout da `Blockout_Fondale_v5`. Trasformazioni dal CSV
(yaw, scala uniforme `scala`). **620 istanze** in 45 attori (654 righe − 34 auto statiche non posate).

| Gruppo | Attori (istanze) |
|---|---|
| banchina | `Arte_B2_Banchina_Mod4m_v2` (68), `_Mod4m_Nicchia` (6), `_Scaletta_v2` (6), `Arte_B2_Ancora_02` (1) |
| pav | `Arte_B2_Pav_Camminamento_4m_B2` (77), `_Cordolo_9m` (34), `_FasciaPalme_9m` (33), `_Aiuola` (68), `Arte_B2_Fascia_33` (FasciaPalme_Fine) |
| palme | `Arte_B2_Palme_Morin_PalmaA` (68) |
| arredi | `Arte_B2_Arredi_Morin_{Panchina 17, Cestino 11, Lampione 8, Tombino 10}` |
| giardini | `Arte_B2_Giardini_Morin_{OleandroAlberello_Bianco 27, _Rosa 26, PanchinaLunga_Mod 63}` |
| viale | `Arte_B2_Viale_Italia_Strada_v2` (13, No Collision), `Arte_B2_Viale_Spartitraffico_Fiori` (18, No Collision), `Arte_B2_Viale_Morin_Semaforo` (4) |
| fondale | `Arte_B2_Fondale_Palazzo_{A,B,C}` (2+2+2), `_Albero_LatifogliaA/B` (4/5), `_Morin_PinoDomestico` (7), `_Morin_PalmaA` (6): tutti No Collision (come `Arte_Viale_GP_*`) |
| chiosco | `Arte_B2_Chiosco_Morin_{Ombrellone, TavoloSet, Sgabello}` (4 ciascuno), `_Fioriera` (2), `_FiorieraB` (2), `_Lampione` (2) |
| nuovi | `Arte_B2_Nuovi_Morin_Cannone` (2), `_AstaBandiera` (3), `Arte_B2_Redamare`, `Arte_B2_Angolo_MoloItalia`, `Arte_B2_ChioscoOttagonale`, `Arte_B2_Morin_Prato_Giardini_B2`, `Arte_B2_Pav_{Vialetti_B2, Piazzetta_Chiosco_B2, Piazzale_Fine_B2, Scritta_Morin}`; `Blockout_Passeggiata_B2`, `Blockout_Fondale_B2_Terreno` |

**Nascosto, non cancellato** (§14): `Arte_Banchina_Testata_Fine`. Attori nel livello: 290 (+55).

### Barriere (`Device/Barriere`, copie con le stesse opzioni: Scatola, invisibile, sempre attiva, altezza 10, blocca proiettili)
Segno della Y verificato sulle esistenti: `Barriera_LatoCitta` a Y −11930 (città = Y negativo), `Barriera_Acqua_LatoMare` a Y +30928 (mare = Y positivo).
**Deroga:** `BarrierWidth` accetta solo valori fissi (… 20, 30, 40, 50, 60 …): 51 e 56 non esistono. Usati 50 e 60 con i centri richiesti.

| Label | Centro | Unità L × P | Ingombro (`BarrierBounds`) |
|---|---|---|---|
| `Barriera_FineBlocco` (spostata) | (56700, 10930, −700) | 0,5 × 90 | X 56572..56828 · Y −12110..33970 |
| `Barriera_LatoCitta_B2` (nuova) | (43872, −11930, −700) | **50** × 0,5 | X 31072..56672 · Y −12058..−11802 |
| `Barriera_Acqua_LatoMare_B2` (nuova) | (42700, 30928, −700) | **60** × 0,5 | X 27340..58060 · Y 30800..31056 |

Continuità sui bounds, passo 4 uu: lato città X −3510..56828 (tratto del parcheggio invariato), lato mare X −17600..56828, fine blocco
Y −12058..31056: **nessun varco**. Sovrapposizioni ai raccordi: LatoCitta/LatoCitta_B2 32 uu in X (stessa fascia Y), LatoCitta_B2/FineBlocco 100 uu,
LatoMare/LatoMare_B2 1140 uu; gli spigoli (56572; −11802) e (56572; 30800) sono dentro due barriere. Molo Italia chiuso da `Barriera_FineBlocco`.

### Acqua
Acqua V2 limitata a 100 tiles (512 m): `Acqua_Golfo_Device` resta X −17100..34100. Nuovo **`Acqua_Golfo_Device_B2`** (copia, stesse opzioni:
profondità 84, altezza 1, 100 % verticale, tipo Default, sempre attivo) al centro (45876, 9550, −484), larghezza **46** → volume
`FortWaterBodyCubeVolumeComponent` **X 34100..57652** · Y −11954..31054 · Z −484..−100, identico in Y e Z al primo. Bordo comune a X 34100:
**fessura 0, sovrapposizione 0** (il riquadro di sola edizione è rientrato di 115-250 uu, ma non è l'acqua).

### Traffico (`LS_Viale_Traffico`)
Le 34 auto statiche del CSV viale **non posate** (richiesta dell'utente). Sequenza estesa: giro **90 s** (frame 0-2700 a 30 fps, prima 60 s),
corsa **X −15000 ↔ 57300** (723 m, prima 480 m), sezioni Transform 0-2700, chiavi X lineari durante la corsa e costanti nell'attesa a Z −3000 (stesso schema
del §25; le auto a cavallo del giro hanno la stessa X a frame 0 e 2700). Corse: 62,0 s a 42 km/h, 76,6 s a 34, 65,1 s a 40, 84,0 s a 31.
**+7 auto** (`Arte_Viale_Traffico_14..20`, duplicate dalle esistenti: Movable, No Collision, `MI_Morin_Auto_v2_Luci`; binding possessable nuovi) per
mantenere la densità: 21 auto, partenze ogni 15 s (corsie mare 2 e città), 22,5 s (mare 1), 18 s (striscia città).
Verifica (scrub ogni 10 frame, interpolazione ricostruita dalle chiavi): tratto Blocco 1 (X −16..326 m) **7,8 auto in media** (max 9, come prima),
tratto Blocco 2 (X 326..573 m) 5,7 (max 8); distanza minima fra auto della stessa corsia **155 m**; nessun salto con l'auto visibile.
Le auto dei clacson sono in strada agli istanti delle tracce Audio (Traffico_12 a 3,0/3,65 s, _00 a 19 s, _08 a 41 s); lo schema ora si ripete ogni 90 s.
Salti: a X −150 m (come prima) e a **X +573 m**, fine dei moduli viale del Blocco 2 (visibile da lontano dal piazzale finale).

### Verifiche (line trace in editor; prop ignorati per suolo e gradini)
- **Suolo X 248..566** (griglia 100 × 100 uu dal ciglio a Y −11790, 12.748 punti): **0 buchi**; gli unici 30 senza impatto sono a X 566,0
  (bordo del piazzale, oltre la faccia interna della barriera a 565,72). `Blockout_Passeggiata_B2` non è mai la superficie più alta.
- **Gradini:** nessuno > 40 cm. Salti trovati: cordolo 15 cm, piazzetta/scritta/fascia → piazzale 15 cm (atteso), prato → fascia 7, vialetti 2-10, aiuole 2.
- **Raccordo B1/B2** (X 249..254, passo 10 × 20 uu, 5.661 punti): 0 buchi; profili lungo X a Y −79,9 / −82 / −85 / −88,8 / −89 / −90 / −95 / −101 m
  con salto massimo **0 cm** (2 cm sul bordo aiuola): camminamento Z 0, striscia tattile 1,2, cordolo e fascia 15, banchina −0,5 continui.
- **Angolo verso il Molo Italia:** bordo terra monotono (smusso da X 549 a Y −79 fino a X 554,2 a Y −48), nessun buco interno. Oltre Y −47,09 il piazzale
  finisce sull'acqua (ciglio, come la banchina): Blocco 3 non ancora costruito.
- **Collisione prop:** cannoni 2/2, aste 3/3, panchine 17/17, panchine lunghe 63/63, lampioni 8/8, cestini 11/11, palme 68/68, tavoli 4/4,
  REDAMARE 30/30 trace orizzontali, chiosco ottagonale colpito (22/30, i mancati sono oltre il raggio di 3,7 m).

### Salvataggio, validazione, render
`save_dirty_packages`: **0 pacchetti sporchi**; 97 `.uasset` con data nuova (57 OFPA, 17 in `Arte/Blocco2`, `LS_Viale_Traffico`, i 2 blockout).
Validazione `LaSpezia/`: **567/567 validi, 0 errori, 41 avvisi** (`ValkyrieValidator_StaticMesh`: i 37 noti + "un solo LOD" sui nuovi `TMPB2_*`).
Log: nessun errore nuovo sul progetto (solo `LogAudioMixer` di sistema e gli avvisi di tangenti del chiosco ottagonale).
Render 1024 px, ombre, mip forzati (`docs/qa/`): `uefn_blocco2_redamare.png` (25420, −9150, 165; yaw 90; pitch −4; FOV 70),
`uefn_blocco2_infilata.png` (26300, −9610, 185; yaw 0; pitch −2; FOV 75), `uefn_blocco2_fine.png` (56150, −9610, 180; yaw 180; pitch −12; FOV 75).

### Temporanei e problemi aperti
- 10 nuovi `LaSpezia/_Temp/TMPB2_SM_{Morin_Cannone, Morin_Redamare, Banchina_Angolo_MoloItalia, Morin_ChioscoOttagonale, Morin_AstaBandiera}_LOD1/_LOD2`;
  eliminabili con conferma dell'utente.
- **(blender-artist)** `SM_Morin_ChioscoOttagonale`: tangenti degeneri/normali nulle (facce ad area zero?).
- **(qa-tester)** In sessione: traffico a 90 s con 21 auto (loop, salto a X 573 m dal piazzale), barriere B2 (non visibili ai trace in modalità Crea),
  bordo acqua tra i due device Acqua V2 a X 341 m, piazzale finale sull'acqua oltre Y −47 m.
- Memoria: +3 texture 1024 (~2,7 MiB a runtime), mesh trascurabili; rileggere "Budget memoria mappa" dopo la prossima sessione (§30).

## 33. Blocco 2 v2 e Molo Italia v1 (2026-11-20, ~14:00-15:25 ora locale)

Sorgenti: `exports/blocco2/` (CSV `blocco2_nuovi_v2.csv`), `exports/molo_italia/` (65 FBX, CSV `molo_italia_posizioni_v1.csv`, 315 righe),
texture `blender/textures/blocco2/T_Morin_Bandiere_*` e `blender/textures/molo_italia/`. Metodo del §32 (LOD0 col nome finale via `ImportFile`,
materiali/texture off; LOD1/2 come `_Temp/TMPB2V2_*` e `_Temp/TMPB3_*`; `remove_lods` + `set_lod_from_static_mesh(..., True)`; sezioni rimappate
per nome di slot; Nanite off; Use Simple Collision As Complex; soglie 1,0/0,2/0,08). Nessun attore né asset cancellato.
**Insidia nuova:** modificare `sm.static_materials[i].material_interface` e riscrivere l'array non assegna nulla (le voci sono copie):
usare `StaticMesh.set_material(i, mi)`. Prima della correzione le mesh nuove risultavano con `WorldGridMaterial`.

### A. Blocco 2 v2 (`LaSpezia/Arte/Blocco2`)
| Asset | Tri LOD0/1/2 | Bbox locale (uu) | Convessi | Slot → MI |
|---|---|---|---|---|
| `SM_Morin_ScrittaLaSpezia` | 420 / 364 / 296 | X ±400 · Y ±30 · Z 0..135 | 2 | `MI_Morin_Corten` |
| `SM_Morin_ChioscoOttagonale_v2` | 138 / 138 / 106 | X ±370 · Y ±370 · Z 0..312 | 2 | `MI_Morin_Chiosco`, `MI_Morin_Dehors` |
| `SM_Pav_Piazzale_Fine_B2_v2` | 10 | X 54927..56600 · Y −12100..−4709 · Z −300..0 | 3 | `MI_Pav_Cubetti` |
| `SM_Morin_Bandiera_Italia/_Comune/_Aquile` | 96 / 24 / 4 | X 6..240 · Y −16..11 · Z 955..1125 | 0 | `MI_Morin_Bandiere` |
- Texture `T_Morin_Bandiere_D/N/ORM` 2048 (D con alfa), N Normalmap, ORM Masks sRGB off, LODBias 0, regola §29 (una alla volta, `GetSize` 2048).
- `MI_Morin_Bandiere` su `M_Morin_Master_PBR_Masked` (two-sided, il master delle chiome).
- **Sostituzioni (cambio di mesh sull'attore, stesse trasformazioni):** `Arte_B2_Redamare` → mesh `SM_Morin_ScrittaLaSpezia`, rinominato
  **`Arte_B2_ScrittaLaSpezia`** (25420, −8255, 0; yaw 0,1241): REDAMARE non è più in scena; `Arte_B2_ChioscoOttagonale` → `_v2` (55206, −10872, 15);
  `Arte_B2_Pav_Piazzale_Fine_B2` → `_v2`. Le mesh v1 restano nel Content Browser, non più referenziate dagli attori.
- **Bandiere:** 3 attori `Arte_B2_Bandiera_{Italia,Comune,Aquile}` (Outliner `Arte/Blocco2/nuovi`) alle posizioni delle 3 aste del CSV, yaw −70, No Collision.
- Avvisi di tangenti degeneri: **nessuno** sul chiosco v2 (log controllato dopo l'import).

### B. Molo Italia v1 (`LaSpezia/Arte/MoloItalia`)
| Asset | Tri LOD0/1/2 | Bbox (uu) | Convessi | MinLOD L/M |
|---|---|---|---|---|
| `SM_MoloItalia_Suolo` | 66 | X 55510..68870 · Y −4162..33260 · Z −300..12 | 4 | 0 |
| `SM_MoloItalia_Suolo_Radice` | 104 | X 55500..64000 · Y −12085..−130 · Z −300..0 | 4 | 0 |
| `SM_Molo_Scogliera_A/B/C` | 1362/342/182 · 1282/322/182 · 1442/362/182 | ~X −87..864 · Y −84..664 · Z −326..48 | 1 | 2 |
| `SM_MoloItalia_Dito` | 142 / 142 / 14 | X 0..4950 · Y ±300 · Z −350..1 | 1 | 0 |
| `SM_MoloItalia_Faro` | 2144 / 1316 / 432 | X ±205 · Y ±205 · Z 0..840 | 4 | 0 |
| `SM_MoloItalia_RistorantePiccioni` | 1748 / 1508 / 208 | X −1280..975 · Y −585..516 · Z −200..600 | 11 | 0 |
| `SM_MoloItalia_Capitaneria` | 998 / 766 / 98 | X 58630..61755 · Y −8075..−4395 · Z 0..1515 | 3 | 0 |
| `SM_MoloItalia_Edificio4P` | 266 / 266 / 34 | X 57895..59385 · Y −4085..−1905 · Z 0..2315 | 1 | 0 |
| `SM_MoloItalia_EdificioEst` | 50 / 50 / 34 | X 61514..63086 · Y −4136..−1935 · Z 0..1120 | 1 | 0 |
| `SM_MoloItalia_InfoPoint_Blu/_Rosso` | 38 | X ±185 · Y ±185 · Z 0..300 | 1 | 2 |
| `SM_Morin_LampionePastorale` | 768 / 508 / 160 | X −20..113 · Y ±23 · Z 0..505 | 2 | 2 |
| `SM_MoloItalia_RinghieraModulo` | 132 / 100 / 56 | X −3..203 · Y ±8 · Z 0..102 | 1 | 2 |
| `SM_MoloItalia_Monumento` | 465 / 423 / 333 | X 54835..55500 · Y −4705..−3855 · Z −120..285 | 13 | 0 |
| `SM_MoloItalia_MonumentoAlpini` | 72 | X ±110 · Y ±80 · Z 0..255 | 2 | 2 |
| `SM_MoloItalia_Rimorchiatore_Tiramolla/_Spingitutto/_Ostinato` | 2032/1488/124 · 2112/1568/124 · 1896/1352/124 | X ±1500 · Y ±540 · Z −360..1250 | 2 | 2 |
| `SM_MoloItalia_Motovedetta` | 1388 / 1340 / 72 | X ±800 · Y ±233 · Z −130..600 | 2 | 2 |
| `SM_MoloItalia_NaveCrociera` | 1126 / 1062 / 130 | X ±12500 · Y ±1615 · Z −800..5200 | 0 | 2 |
| `SM_MoloItalia_GruPortuale` | 92 | X −900..900 · Y −4000..1300 · Z 0..5910 | 0 | 2 |
- Slot → MI: `M_MoloItalia_Tinte/_Cemento/_Facciata` → `MI_MoloItalia_*`, `M_Molo_Scogliera` → `MI_Molo_Scogliera` (nuove, `M_Morin_Master_PBR`);
  `M_MoloItalia_FaroLuce` → `MI_MoloItalia_FaroLuce`; riusate `MI_Molo_Asfalto`, `MI_Morin_Ghisa`, `MI_Morin_Globo`, `MI_Pav_Fascia`, `MI_Pav_Cubetti`,
  `MI_Banchina_Paramento`. Nessuno slot senza MI.
- Texture (12, `Arte/MoloItalia`): `T_MoloItalia_Tinte_*`, `T_MoloItalia_Facciata_*`, `T_Molo_Scogliera_*` 1024, `T_MoloItalia_Cemento_*` 2048;
  LODBias 0, regola §29 rispettata, tutte con dimensione valida. Texture del progetto: 156 (+15).
- LOD2 sensibilmente più bassi del LOD0 (non è una rotazione): `Edificio4P` Z max 1480 contro 2315, `Capitaneria` 1000 contro 1515,
  rimorchiatori 800 contro 1250, motovedetta 330 contro 600: a distanza la sagoma si abbassa di colpo.

### Faro lampeggiante Fl R 4 s (senza Verse)
- Master nuovo **`Arte/Materiali/M_Morin_Master_Lampeggio`** (opaco, usage ISM e Nanite): Emissive = `Colore × Emissivo × If(fmod(Time + Fase, Periodo) < Acceso, 1, Spento_Residuo)`;
  BaseColor = `Colore × BaseColor_Mult`. Parametri: `Periodo` 4, `Acceso` 1, `Fase` 0, `Spento_Residuo` 0, `Emissivo`, `Colore`, `Roughness`, `BaseColor_Mult` 0,6.
- `MI_MoloItalia_FaroLuce`: Colore (1; 0,02; 0,01), Emissivo 3, Periodo 4, Acceso 1 → **1 s acceso, 3 s spento**. Verificato con 11 render a 0,7-0,8 s
  di distanza: lanterna accesa solo quando `fmod(t, 4) < 1`. Libreria shader +1 master.
- Facoltativo fatto: **`Luce_Faro_MoloItalia`** (Point Light, Outliner `Luci`) a (67860, 32710, 732) dentro la lanterna, rossa, 300 cd, raggio 2500,
  senza ombre, Movable, con light function **`Arte/MoloItalia/M_MoloItalia_FaroLampo_LF`** (stessa formula, 1 s su 4). Costo: una luce dinamica senza ombre.
- Insidia: i pin del nodo If si chiamano `A > B`, `A == B`, `A < B` (con spazi). Con `A>B` la connessione fallisce in silenzio e la validazione segnala
  "Missing If AGreaterThanB input".

### Posa (Outliner `Arte/MoloItalia/<gruppo>`)
HISM duplicati da `Arte_B2_Banchina_Mod4m_v2` (Query Only `FortStaticMesh`, Static) o da `Arte_B2_Fondale_Morin_PalmaA` (No Collision) + `clear_instances`;
pezzi unici duplicati da `Arte_B2_ChioscoOttagonale`; override di materiale azzerati. **315 istanze**, tutte le righe del CSV (yaw, scala uniforme).

| Gruppo | Attori (istanze) |
|---|---|
| suolo | `Arte_B3_Suolo`, `_Suolo_Radice`, `_Monumento`, `_Capitaneria`, `_Edificio4P`, `_EdificioEst` |
| banchina | `Arte_B3_banchina_Mod4m_v2` (107), `_Bitta_v2` (25) |
| scogliera | `Arte_B3_scogliera_Scogliera_A/B/C` (18/19/18) |
| dita | `Arte_B3_dita_Dito` (2), `_Bitta_v2` (16) |
| landmark | `Arte_B3_Faro`, `Arte_B3_RistorantePiccioni`, `Arte_B3_MonumentoAlpini` |
| arredi | `Arte_B3_arredi_{LampionePastorale 19, RinghieraModulo 14, Panchina 8, NewJersey 5}` |
| radice | `Arte_B3_radice_{InfoPoint_Blu 2, PalmaA 5, PinoDomestico 4}`, `Arte_B3_InfoPoint_Rosso` |
| auto | 9 HISM `Arte_B3_auto_Auto_*_Col_v2_*` (30) |
| barche | `Arte_B3_barche_Battello` (2), `_Motovedetta` (2), `Arte_B3_Rimorchiatore_{Tiramolla,Spingitutto,Ostinato}` |
| fondale | `Arte_B3_NaveCrociera`, `Arte_B3_fondale_GruPortuale` (5): No Collision |

Attori nel livello: 291 → **344** (+3 bandiere, +40 molo, +5 barriere nuove, +2 device Acqua V2 con i loro 2 `BP_FortWaterBodyCubeVolume_C`, +1 luce; `Arte_B2_Redamare` rinominato).

### Barriere (`Device/Barriere`, copie di `Barriera_LatoCitta_B2` con le stesse opzioni) e acqua
`BarrierWidth/Depth` accettano solo 0,01 · 0,05 · 0,5 · 1…20 · 30 … 100 (unità da 512 uu): servono 6 pezzi.

| Label | Centro | L × P | Ingombro |
|---|---|---|---|
| `Barriera_FineBlocco` (**spostata** da X 56700) | (64128, −7093, −700) | 0,5 × **20** | X 64000..64256 · Y −12213..−1973 |
| `Barriera_LatoCitta_B3` | (60416, −11957, −700) | 15 × 0,5 | X 56576..64256 · Y −12085..−11829 |
| `Barriera_Acqua_RadiceEst_B3` | (67968, −1026, −700) | 16 × 4 | X 63872..72064 · Y −2050..−2 |
| `Barriera_Acqua_LatoPiuX_B3` | (72128, 18430, −700) | 0,5 × 80 | X 72000..72256 · Y −2050..38910 |
| `Barriera_Acqua_LatoMare_B3` | (64576, 35128, −700) | 30 × 0,5 | X 56896..72256 · Y 35000..35256 |
| `Barriera_Acqua_Raccordo_B3` | (57932, 33004, −700) | 0,5 × 9 | X 57804..58060 · Y 30700..35308 |

- `Barriera_FineBlocco` non può arrivare a Y −130 (24 unità non esistono): il tratto Y −1973..−130 è chiuso da `RadiceEst_B3`, che occupa una striscia di
  1,28 m (X 63872..64000) all'angolo est della radice sul mare. Lato città a Y −12085 come richiesto (faccia esterna sul bordo della radice).
- Nessuna barriera sul ciglio del molo. `Barriera_Acqua_LatoMare_B2` (Y 30928, fino a X 58060) resta com'era; il raccordo la collega alla nuova linea Y 35000.
- **Continuità:** percorso lungo il perimetro (città B2 → città B3 → fine radice → costa est → lato +X → lato mare B3 → raccordo → mare B2) campionato
  ogni **4 uu**: 23.899 punti, **0 scoperti**; flood fill a 64 uu da (60000, 10000) nel riquadro X 50000..76000 · Y −14000..40000: **nessuna fuga**
  a est, a nord o verso la città.
- **Acqua V2** (copie di `Acqua_Golfo_Device_B2`, stesse opzioni, Z −484, altezza 1): **`Acqua_Golfo_Device_B3`** larghezza 29 × profondità 69 →
  X 57652..72500 · Y −130..35198; **`Acqua_Golfo_Device_B3_Nord`** 7,5 × 8,09375 → X 53812..57652 · Y 31054..35198. Bordi comuni con B2 a X 57652 e
  Y 31054 senza fessure né sovrapposizioni. Insieme a B2 coprono il box X 54000..72000 · Y −130..35000.

### Verifiche (line trace in editor)
- **Suolo continuo** (griglia 100 × 100 uu su X 54800..69200 · Y −12100..33500, 66.265 trace): ricerca in ampiezza dal piazzale B2 (56000, −9000)
  con gradino ≤ 40 cm: **raggiunte tutte** le celle di `Suolo`/`Suolo_Radice` (16.176 celle in tutto), 62 celle entro 5 m dal faro, Y max 33400.
- **Gradini** sul percorso (suolo, radice, piazzale B2, dita): massimo **15,3 cm** (scritta Morin, piazzetta); marciapiede del molo **12 cm**;
  B2 → radice 0 cm. Salti > 40 cm solo dentro la scogliera (pendenza 50-55 cm/m), sul monumento (gradoni 70 cm) e sullo zoccolo del faro.
- **Ristorante:** passerelle (Z −30..0) e coperta (Z −20) raggiungibili dal molo; **terrazza (Z 300) calpestabile ma NON raggiungibile**: la scala
  (cuneo X −915..−255 locale, Y 305..465) passa sotto la soletta della terrazza (convesso unico X ±955 · Y ±495 · Z 275..300). Sweep di capsula
  r 34 / hh 88 lungo la scala: blocco contro la soletta a Z 275 dopo ~2,4 m. Da correggere in Blender (vano scala aperto nella soletta e nel suo UCX).
- **Collisioni:** faro 1/1, ristorante 1/1, Capitaneria 16/16 trace orizzontali, Edificio4P 15/16 (il 16° colpisce un'auto parcheggiata a 40 cm dal muro),
  EdificioEst 16/16, monumento 8/8 sotto i 2,85 m, Monumento Alpini 1/1, lampioni 19/19, ringhiere 14/14, New Jersey 5/5, panchine 8/8, auto 30/30,
  info point 3/3, palme 5/5, pini 4/4, battelli 2/2, motovedette 2/2, rimorchiatori 3/3. **Senza collisione:** nave da crociera (0 impatti su 33 trace
  verticali) e gru (0/5).

### Salvataggio, validazione, log, render
`save_dirty_packages`: **0 pacchetti sporchi**. Validazione `LaSpezia/`: **671/671 validi, 0 errori, 56 avvisi** (`ValkyrieValidator_StaticMesh`:
i noti + "un solo LOD" sui temporanei `TMPB3_*`/`TMPB2V2_*`; MinLOD dei temporanei portato a 0). Log: nessun errore sul progetto dopo la correzione del nodo If.
Render 1024 px con ombre (`docs/qa/`): `uefn_blocco2_v2_laspezia.png` (camera di `uefn_blocco2_redamare.png`), `uefn_moloitalia_faro.png`
(64300, 29300, 300; yaw 45; pitch 4; FOV 55), `uefn_moloitalia_ristorante.png` (56300, 2600, 320; yaw 50; pitch −6; FOV 70),
`uefn_moloitalia_infilata.png` (56450, −3000, 180; yaw 90; pitch −2; FOV 75), `uefn_moloitalia_alto.png` (49000, −9000, 9000; yaw 58; pitch −28; FOV 80).

### Temporanei e problemi aperti
- 52 nuovi temporanei in `LaSpezia/_Temp` (`TMPB2V2_*` 10, `TMPB3_*` 42), nessun referencer; eliminabili con conferma dell'utente.
- **(blender-artist)** Scala del ristorante bloccata dalla soletta della terrazza (vedi sopra). LOD2 di Edificio4P, Capitaneria, rimorchiatori e motovedetta più bassi.
- **(qa-tester)** In sessione: lampo del faro (`Time` del materiale in gioco) e luce rossa; bordo dell'acqua oltre le barriere (l'acqua finisce a
  Y 352 m e X 725 m, cioè ~20-25 m oltre il faro: si vede il vuoto?); sfumature verdi sotto l'acqua del bacino interno lungo la costa X 640-720
  (probabile terreno di `Arte_Fondale_Citta_NE_01`, senza collisione); barriere B3 dall'acqua.
- Memoria: +15 texture (≈ 30 MiB a runtime, stima informativa), mesh trascurabili; rileggere "Budget memoria mappa" dopo la prossima sessione (§30).

## 34. Molo Italia v2 e acqua oltre il faro (2026-11-20, ~15:40-15:55 ora locale)

Sorgenti: `exports/molo_italia/*_v2{,_LOD1,_LOD2}.fbx` (13 asset), `exports/fondale/SM_Fondale_Colline_NE_v2.fbx`. Metodo §32/§33: LOD0 col nome
finale via `ImportFile` (materiali/texture off) in `Arte/MoloItalia` (colline in `Arte/Fondale`), LOD1/2 come `_Temp/TMPB3V2_<asset>_v2_LOD1/2`,
`remove_lods` + `set_lod_from_static_mesh(..., True)`, MI con `StaticMesh.set_material` (insidia §33) copiate slot per slot dalla v1, sezioni dei LOD
controllate per nome di slot (§22: nessuna da rimappare), Nanite off, Use Simple Collision As Complex, soglie 1,0/0,2/0,08, MinLOD Low/Medium = v1
(rimorchiatori, motovedetta, lampione, scogliere 2; gli altri 0; temporanei 0). Nessun attore né asset cancellato: le v1 restano nel Content Browser.

### Asset v2 (bbox e convessi = v1, salvo dove indicato)
| Asset | Tri LOD0/1/2 | Convessi | Bbox LOD1/LOD2 vs LOD0 |
|---|---|---|---|
| `SM_MoloItalia_RistorantePiccioni_v2` | 1884 / 1604 / 272 | **17** (v1 11) | 0,05 % |
| `SM_MoloItalia_Edificio4P_v2` | 266 / 266 / 82 | 1 | 0,01 % (Z 2315 in tutti i LOD) |
| `SM_MoloItalia_Capitaneria_v2` | 998 / 766 / 114 | 3 | 0,00 % (Z 1515) |
| `SM_MoloItalia_Faro_v2` | 2144 / 1316 / 440 | 4 | 0,00 % |
| `SM_MoloItalia_Rimorchiatore_{Tiramolla,Spingitutto,Ostinato}_v2` | 2032/1488/160 · 2112/1568/160 · 1896/1352/160 | 2 | 0,14 % (Z 1250) |
| `SM_MoloItalia_Motovedetta_v2` | 1388 / 1340 / 80 | 2 | **1,37 %** (larghezza 466/469/460; Z 600) |
| `SM_MoloItalia_Dito_v2` | 142 / 142 / 46 | 1 | 0,00 % |
| `SM_Morin_LampionePastorale_v2` | 768 / 508 / 174 | 2 | 0,00 % |
| `SM_Molo_Scogliera_{A,B,C}_v2` | 1362/342/182 · 1282/322/182 · 1442/362/182 | 1 | 0,00 % |
| `SM_Fondale_Colline_NE_v2` | 7005 (solo LOD0, come le altre colline) | 0 (convesso automatico rimosso) | — |
Bbox letta con GeometryScript dalla mesh sorgente di ogni LOD dell'asset finale. Slot → MI identici alla v1; sul faro lo slot `M_MoloItalia_FaroLuce`
resta `MI_MoloItalia_FaroLuce` (lampeggio). Colline: `MI_Fondale_Colline_NE`, MinLOD 0, nessuna collisione.

### Cambio di mesh (stesse trasformazioni, nessun override di materiale)
Singoli: `Arte_B3_RistorantePiccioni`, `_Edificio4P`, `_Capitaneria`, `_Faro`, `Arte_B3_Rimorchiatore_{Tiramolla,Spingitutto,Ostinato}`.
HISM (istanze e trasformazioni identiche prima/dopo): `Arte_B3_barche_Motovedetta` (2), `Arte_B3_dita_Dito` (2), `Arte_B3_arredi_LampionePastorale` (19),
`Arte_B3_scogliera_Scogliera_A/B/C` (18/19/18). Fondale: `Arte_Fondale_Colline_NE` (518000, 48000, 0) → `_v2`, sempre No Collision, senza ombre.
Insidia: uno script unico con 14 `set_static_mesh` + confronto di tutte le trasformazioni ha fatto cadere la connessione MCP (ECONNRESET, nessuna
modifica applicata); a gruppi piccoli funziona.

### Acqua oltre il faro (3 device Acqua V2 nuovi, copie di `Acqua_Golfo_Device_B3_Nord`: stesse opzioni, Z −484, altezza 1, 100 %, Default, sempre attivo)
| Label | Centro | L × P (unità 512) | Volume `FortWaterBodyCubeVolume` |
|---|---|---|---|
| `Acqua_Golfo_Device_B3_Mare` | (75444, 45438, −484) | 84,5 × 40 | X 53812..97076 · Y 35198..55678 |
| `Acqua_Golfo_Device_B3_Est` | (84788, 20606, −484) | 48 × 57 | X 72500..97076 · Y 6014..35198 |
| `Acqua_Golfo_Device_B2_Mare` | (43956, 43366, −484) | 38,5 × 48,09375 | X 34100..53812 · Y 31054..55678 |
- Dal faro (67860, 32710): acqua fino a **230 m** verso il mare aperto (+Y), **292 m** verso est (+X), 338 m verso ovest. Bordi comuni con B2, B3 e
  B3_Nord senza fessure né sovrapposizioni. La nave da crociera (X 85002..94997) ora galleggia sull'acqua.
- `B3_Est` parte da **Y 6014** e non da −130: a X 725-820 m, fino a Y ~60 m, ci sono i blocchi di `Arte_Fondale_Citta_NE_01` con la base a
  Z −1,3..−2,9 m e, a X 726-750 m, un fondale a −8 m: coprirli faceva comparire edifici "in acqua" e nuove macchie chiare. Il rettangolo X 725-971 m ·
  Y −1,3..60 m resta senz'acqua come prima (terra del porto a Z −0,3..−0,5 m).
- **Barriere invariate.** Flood fill a 64 uu dall'interno del Blocco 3 (60000, 10000) nel riquadro X 26000..90000 · Y −14000..58000 con i box reali
  delle barriere (centro ± unità × 256): 470.045 celle raggiunte, **nessuna** dentro i tre volumi nuovi, nessuna sui bordi est/nord/città del riquadro
  (tocca solo il bordo X 26000, cioè la continuazione verso i Blocchi 1-2).
- Log: alla duplicazione 3 avvisi "TimelinePostUpdateFunc / Vertical Water Movement Timeline: Unable to find function" (riferiti al device sorgente):
  il riempimento verticale non è usato (100 % fisso); da guardare in sessione.

### Verifiche (line trace e sweep in editor)
- **Ristorante:** percorso molo (locale X −1450, Y 385) → passerella (Z 0) → piede della scala (X −920) → rampa fino a Z 300 (X −255, pendenza ~26°,
  19,4 cm ogni 40 cm) → terrazza Z 300 → centro terrazza: sweep di capsula r 34 / hh 88 a passi di 10 cm, **0 blocchi**, salto massimo fra due passi
  4,8 cm, altezza libera minima 2,35 m (sotto la copertura a Z ~5,4 m). Vano aperto nella soletta Y 295..480 locali con ringhiera sui lati.
  (Con la capsula appoggiata a 3 cm dalla rampa lo sweep "tocca" la rampa stessa: artefatto del test, sparisce sollevandola di 20 cm come fa lo step-up.)
- **LOD:** bbox LOD1/LOD2 entro il 2 % del LOD0 su tutti i 13 asset (max 1,37 % motovedetta).
- **Bacino X 640-720 m:** vista zenitale e obliqua: nessuna macchia verde sott'acqua; resta solo la riga di costa (terra sopra l'acqua).

### Salvataggio, validazione, log, render
`save_dirty_packages`: **0 pacchetti sporchi**. Validazione `LaSpezia/`: **711/711 validi, 0 errori, 57 avvisi** (i 56 noti + "un solo LOD" su
`SM_Fondale_Colline_NE_v2`, come le altre colline). Log: nessun errore sul progetto (solo `LogHotfixManager`, `LogEOSSDK`, `LogAudioMixer` di sistema).
Attori nel livello: 344 → **350** (+3 device Acqua V2 e i loro 3 `BP_FortWaterBodyCubeVolume_C`).
Render 1024 px con ombre (`docs/qa/`): `uefn_moloitalia_v2_terrazza.png` (59065, 5430, 480; yaw 195; pitch −14; FOV 80),
`uefn_moloitalia_v2_bacino.png` (68000, 6000, 14000; zenitale; FOV 70), `uefn_moloitalia_v2_testata.png` (67550, 32500, 185; yaw 75; pitch −3; FOV 90).

### Temporanei e problemi aperti
- 26 nuovi temporanei `LaSpezia/_Temp/TMPB3V2_*_v2_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente (insieme alle mesh v1 ora
  non più usate: 13 `SM_MoloItalia_*`/`SM_Molo_Scogliera_*`/`SM_Morin_LampionePastorale` e `SM_Fondale_Colline_NE`).
- **(qa-tester)** In sessione: salita alla terrazza; acqua oltre il faro e bordo a X 971 m / Y 557 m visto dalla testata; device Acqua V2 copiati
  (avviso della timeline); il rettangolo senz'acqua a est del bacino (X 725-971 m, Y < 60 m) visto dal molo.
- **(blender-artist, facoltativo)** `Arte_Fondale_Citta_NE_01`: basi dei blocchi a X 725-820 m sotto il livello dell'acqua (Z −1,3..−2,9 m) e fondale
  a −8 m sotto l'edificio a X ~745 m, Y ~35 m: se si vuole l'acqua anche lì vanno alzate o ritagliate.

## 35. Diagnosi difetti e audit realismo (2026-11-20, ~16:00-16:30 ora locale)

Solo diagnosi: nessun asset, attore, device o impostazione modificati, niente sessioni di gioco, nessun commit. Catture con `RenderLevelPOVs`
(ombre attive, `r.Streaming.FullyLoadUsedTextures 1`), analisi geometrica con GeometryScript sulle render data dei LOD.
Coordinate UE (X, Y, Z in uu); in Blender Y = −Y UE / 100. Superficie dell'acqua Acqua V2: **Z −100**.

### A. Forme verdi sull'acqua del Blocco 2: `Arte_Fondale_Colline_NE` (`SM_Fondale_Colline_NE_v2`, `MI_Fondale_Colline_NE`)
- Bounds degli attori su X 250-580 m, lato mare (Y UE > −7900): l'unica mesh visibile con superficie fra Z −484 e Z 0 è il fondale colline NE
  (bbox X 33000..1002000, Y −330000..426000, Z −1000..31931; attore a (518000, 48000, 0), Static, No Collision, senza ombre).
  `Blockout_Fondale_v5` finisce a X 33000; `Blockout_Fondale_B2_Terreno`, `Blockout_Passeggiata_B2`, `SM_Morin_Prato_Giardini_B2` e `Colline_SE`
  non hanno triangoli in quell'area (0 punti). `Blockout_Fondale_v2/v3/v4` sono già invisibili.
- Campionamento dei triangoli della mesh (griglia 100 uu, quota massima per punto), due macchie **sopra** la superficie:

| Macchia | X (m) | Y UE (uu) → Y Blender (m) | Z (uu) | Area |
|---|---|---|---|---|
| A | 340-380 | −8000..−6000 → 80..60 | −80 (≈ 20 cm sopra l'acqua) | ~440 m² |
| B | 519-580 | −8000..+2000 → 80..−20 | −55..−100 (media −75) | ~2.830 m² |

  Altri ~1.160 m² fra 0 e 2 m **sotto** la superficie (X 341-577, Y Blender 79..−25) si vedono in trasparenza come velo verde.
  Tinta del materiale (0,34; 0,52; 0,38): è il verde visto nelle catture.
- Catture: `docs/qa/diag_b2_acqua_passeggiata_X380.png`, `_X500.png` (dalla passeggiata), `diag_b2_acqua_alto.png` (zenitale, X 170-670 m),
  `diag_b2_acqua_macchia_X340_380.png`, `diag_b2_acqua_macchia_X520_580.png` (obliqua: il cuneo verde contro il ciglio vicino all'angolo del Molo Italia).
- **Correzione (blender-artist):** in `SM_Fondale_Colline_NE_v2` abbassare sotto Z −5 m (fondo dell'acqua −4,84 m) o eliminare le facce con
  X < 580 m e Y Blender > −100 m (tutto il lato mare del Blocco 2): sotto la passeggiata c'è già il suolo del Blocco 2.
  Il fondale non va nascosto: è anche il profilo delle colline NE.
- Da verificare (non richiesto): sullo stesso fondale, fra X 577 e 971 m e Y Blender 1..−93 m, ci sono ~2 ha con Z fra −1 m e +0,05 m. Gran parte è
  sotto il suolo del molo o nel rettangolo senz'acqua del §34; il controllo con trace dall'alto ha fatto cadere la connessione MCP e non è concluso.

### B. Chiosco ottagonale v2 (`Arte_B2_ChioscoOttagonale`, `SM_Morin_ChioscoOttagonale_v2`): **normali del corpo invertite**
- Attore: (55206, −10872, 15), yaw 0, scala 1, nessun override di materiale; slot `MI_Morin_Chiosco`, `MI_Morin_Dehors`; MinLOD 0, LOD forzato 0.
  Nessun attore usa la v1 (`SM_Morin_ChioscoOttagonale`) e nulla si sovrappone (vicini: ombrelloni, sgabelli, tavoli, piazzetta).
- LOD: 3; soglie 1,0 / 0,2 / 0,08; tri 138 / 138 / 106; in tutti i LOD 2 sezioni, sezione 0 → slot 0, sezione 1 → slot 1 (corretto).
- Materiali: `MI_Morin_Chiosco` e `MI_Morin_Dehors` (`Arte/Chiosco`, master `M_Morin_Master_PBR`, opaco) **non two-sided**, nessun override.
  Texture D/N/ORM 2048 presenti (le stesse del chiosco del Blocco 1, che si vede bene).
- Normali per faccia nel LOD0 (uguale nel LOD1; LOD2 stesso schema), classificate rispetto all'asse del chiosco:

| Parte | Mat | Tri | Area | Normale |
|---|---|---|---|---|
| Tetto (Z ~3 m) | 0 | 6 | 21,4 m² | in su, **giusta** |
| Gronda/fascia del tetto (Z 2,42-2,72) | 0 | 32 | 12,2 m² | verso fuori, **giusta** |
| Pareti posteriori, 3 lati (azimut 225°, 270°, 315°; Z 0-2,62; r ≈ 2,6 m) | 0 | 12 | ~19 m² | **verso l'interno** |
| Fascia alta dei 5 lati anteriori (Z 1,10-2,62; r ≈ 2,0 m) | 0 | 10 | ~12 m² | **verso l'interno** |
| Bancone dei 5 lati anteriori (Z 0-1,10; r ≈ 2,6 m) | 1 | 10 | 12,4 m² | **verso l'interno** |
| Piano del bancone (Z ~1,1) | 1 | 10 | 5,6 m² | **verso il basso** |

  Normali di vertice concordi con quelle di faccia (0 discordanze), 0 triangoli degeneri. Nessuna parete verticale del corpo ha la normale verso fuori.
  La v1 aveva normali miste (12 tri verso fuori, 18 verso dentro, piano del bancone in su): l'inversione è stata introdotta nella v2.
- Effetto: da fuori le facce vicine sono scartate dal back-face culling (materiale a una faccia) e si vede l'interno, buio, delle 2-3 pareti lontane:
  è "un terzo della parete" e il blocco scuro senza texture delle catture.
- Catture `docs/qa/diag_chiosco_{vicino,lontano}_{E,S,O,N}.png` (11 m e 50 m, FOV 60): LOD0 e LOD1 hanno la stessa geometria, il difetto è identico.
  `_vicino_N` è coperta da un tronco di palma.
- **Correzione (blender-artist):** ricalcolare le normali verso l'esterno del corpo (pareti, fascia, bancone) e verso l'alto del piano del bancone,
  esportare `SM_Morin_ChioscoOttagonale_v3` con i LOD; non rendere two-sided il materiale (raddoppia il costo e illumina male l'interno).

### C. Nave da crociera (`Arte_B3_NaveCrociera`, `SM_MoloItalia_NaveCrociera`, `MI_MoloItalia_Tinte`)
- Attore (90000, 26000, −103), yaw −74, scala 1 → Blender (900; −260), rotZ 74°. Bounds mesh X ±12500 · Y ±1615 · Z −800..5200.
- **Misure:** lunghezza **250 m**, larghezza **32,3 m**, altezza sull'acqua **52 m** (cima a Z 5097), immersione 8 m. Estremità a (93450, 13988) e
  (86550, 38012) UE. Distanze minime dallo scafo: dalla lanterna del faro **~180 m**, dalla fine della passeggiata (56600, −8000) **~430 m**,
  dal punto simulato di `giardini.webp` (38000, −10800) ~640 m al centro.
- Confronto con una nave grande (290-330 × 38 m, 55-65 m sull'acqua): la nostra è **più piccola** del tipico. La scala non è il problema.
- Causa probabile: **posizione**. La nave è in acqua aperta, ~180 m a est del faro, di traverso (asse ~N-S), senza banchina. Nella foto
  `ref/foto/arredi/giardini.webp` la nave è una striscia sottile all'orizzonte, cioè molto più lontana (le navi ormeggiano nel porto commerciale,
  Molo Garibaldi, `ref/molo_italia.md` §14: posizione [S]). Contribuiscono la nebbia debole (densità 0,004: quasi nessuna prospettiva aerea a 400-600 m)
  e la sagoma a gradoni bianca piatta, che sembra vicina.
- Catture: `docs/qa/diag_nave_giardini.png` (dai Giardini verso NE, FOV 80), `diag_nave_fine_passeggiata.png` (dal piazzale finale: la nave è coperta
  dalla Capitaneria e dagli edifici del molo), `diag_nave_faro.png` (dalla testata: la fiancata riempie metà dell'inquadratura).
- **Correzione:** geo-scout misura la posizione reale di ormeggio (Molo Garibaldi) da OSM; uefn-builder sposta e ruota l'attore (solo trasformazione,
  scala 1:1). Facoltativo (blender-artist): sagoma meno a gradoni (prua, balconate, scialuppe) e un tratto di banchina sotto.

### D. Audit realismo: 10 catture a occhio d'uomo (`docs/qa/realismo_00..09.png`, 1024 px, ombre)
Materiali individuati con trace dalla camera (griglia 20 × 20) e lettura delle MI. Master: `M_Morin_Master_PBR` (solo `UV_Tiling`, `Roughness_Mult`),
`M_Morin_Master_Pav` (`Tile_m`, `Roughness_Mult`, `Tinta`); nessuna MI controllata usa `Roughness_Mult` diverso da 1.

| # | Inquadratura (posizione; pitch, yaw; FOV) | Materiali meno realistici e cosa non va |
|---|---|---|
| 00 | Partenza B1, X 240 m verso il ponte (24000, −8400, 180; 3, 142,3; 75) | **Acqua V2**: specchio bianco-azzurro con increspatura fine ripetuta, nessuna profondità né colore del golfo. **`MI_Banchina_Blocchi`** (ciglio): bianco piatto, nessuna usura né segni d'acqua. **`MI_Pav_Lastre`**: chiazze arancioni di luce fra le fronde troppo sature; giunti tutti uguali. Le antenne del ponte si leggono appena (sottili e chiare sul cielo chiaro) |
| 01 | Pavimentazione ravvicinata (8000, −8500, 170; −35, 200; 70) | **`MI_Pav_Lastre`** (Tile_m 3,2, 2048): stesse macchie ripetute ogni 3,2 m, giunti dipinti senza rilievo (normal debole), roughness uniforme, tono freddo-violaceo. **`MI_Pav_Fascia`** (cordolo, Tile_m 1): bianco marmo troppo chiaro, sembra plastica. **`MI_Pav_Cubetti`**: violaceo |
| 02 | Banchina e acqua verso l'imbarco (12500, −8250, 170; −8, 165; 75) | **Acqua V2** (riflesso del cielo quasi bianco, increspatura a pixel). **`MI_Banchina_Blocchi`** (ciglio uniforme). **`MI_Morin_PalmaA_Tronco`**: tronchi lontani quasi neri |
| 03 | Giardini a Mare e Viale Italia (15300, −9650, 180; −3, −90; 90) | **`MI_Morin_Prato`** (UV_Tiling 1): verde lime uniforme, senza variazioni né ciuffi, troppo saturo rispetto a `giardini.webp`. **`MI_Pav_Cubetti`**: viola-bruno, ventagli troppo grandi. **`MI_Albero_Latifoglia_Chioma`**: chiome a grumi scuri "dipinti", bordo delle card visibile. `MI_Pav_Terra` (aiuole) rosata |
| 04 | Parcheggio (2150, −10660, 212; −6, −8; 78) | **`MI_Morin_Auto_v2`**: carrozzerie lattiginose, tetti polverosi, nessun riflesso (roughness alta). **`MI_Parcheggio_Asfalto`**: macchie scure grandi e ripetute, nessuna grana fine. **`MI_Morin_PinoDomestico_Corteccia`**: tronchi arancio piatti |
| 05 | Incrocio (1560, −10050, 210; −2, −90; 90) | **`MI_Pav_Cubetti`** (scala e tinta). **`MI_Albero_Latifoglia_Chioma`**. **`M_Blockout_Fondale`** su `Blockout_Fondale_v5`: a sinistra si vedono ancora volumi grigio-bianchi del blockout |
| 06 | Ponte, calpestio (−120, 4300, 429; 4, 90; 75) | **`MI_Ponte_Acciaio`** (4096): bianco pieno senza sfumature né riflessi, sovraesposto. **`MI_Ponte_Legno`**: doghe rosate e tutte uguali, fughe poco scure. `MI_Ponte_Cavo`: cavi tratteggiati (aliasing) |
| 07 | Mirabello, testata verso il ponte (−1300, 19000, 180; 4, −84; 80) | **`MI_Parcheggio_Asfalto`** su `SM_Mirabello_Suolo`: rosato e piatto; **`MI_Molo_Masselli`** a toppe che sembrano decal. **`MI_Banchina_Paramento`**: muro scuro e uniforme |
| 08 | Blocco 2, scritta LA SPEZIA (25420, −9150, 165; −4, 90; 70) | **`MI_Morin_Corten`** (1024): arancio-bruno uniforme, niente colature né variazioni di ruggine, risoluzione bassa per un asset vicino alla corsia. **`MI_Pav_Fascia`** (cordolo bianco). Sullo sfondo la macchia verde B del §35.A |
| 09 | Molo Italia verso il faro (64300, 29300, 180; 3, 45; 70) | **`MI_MoloItalia_Cemento`**: bianco quasi saturo, griglia di piastrelle visibile, nessuna sporcizia. **`MI_Molo_Scogliera`** (1024): massi beige "spugnosi", texture a scala troppo grande. **`MI_Molo_Asfalto`**: viola-grigio a chiazze. `MI_Morin_NewJersey`: plastica bianca |

Problemi comuni: grigi e pietre virano al **viola/freddo**; i bianchi (cemento, fascia, ciglio, acciaio del ponte, New Jersey) sono **sovraesposti**
e piatti; diverse texture vicine alla corsia sono a **1024** (corten, scogliera, New Jersey, tinte); nessuna variazione a grande scala (le stesse
macchie si ripetono a ogni modulo).

### E. Luce e post-process (letti, NON modificati)
- **`Luce_OraDelGiorno`** (`BP_DaySequenceModifier_Device_C`, Outliner `Luci`): sempre attivo, **orario fisso 18,0**, priorità 2000, velocità 1,
  senza volume. Override **nebbia: SÌ**: densità **0,004**, colore (0,30; 0,38; 0,52), diminuzione in altezza 0,02, dispersione direzionale
  (0,67; 0,48; 0,30), nebbia secondaria 0, dispersione volumetrica del sole 1, opacità massima 1. Override sole, luce cielo, cielo e nuvole: **NO**
  (valori di default della Day Sequence di Fortnite alle 18). Sequenza giorno utente: nessuna.
- **`IslandSettings0`**: orario, luminosità luce, colore luce, densità e colore nebbia = **Predefinito** (nessun override); luce di contorno 0.
- Nel livello non ci sono Post Process Volume, Directional Light, Sky Light, Sky Atmosphere né Exponential Height Fog propri: tutto viene dalla
  Day Sequence. L'unica luce piazzata è `Luce_Faro_MoloItalia`. Il device non espone l'esposizione.
- Nelle catture: cielo pallido e lattiginoso, orizzonte quasi bianco, poco contrasto; ombre lunghe ma morbide; dominante fredda su grigi e pietre;
  le colline lontane hanno un po' di foschia, gli oggetti a 400-600 m (nave, città NE) quasi niente.
- **Proposte (da NON applicare senza l'utente; da verificare in sessione, perché il render dell'editor può differire dal gioco):**
  1. Override sole: sole radente da ovest-sud-ovest (`SunlightRotationZ/X`, azimut ~250°, elevazione ~15-20°), colore caldo (1,0; 0,86; 0,70),
     intensità ~8 invece di 10: luce dorata e meno bianchi bruciati.
  2. Override luce cielo: intensità 0,7-0,8, colore neutro-caldo (1,0; 0,97; 0,93), per togliere la dominante viola.
  3. Nebbia: densità 0,006-0,008, colore meno saturo (0,45; 0,52; 0,62), diminuzione 0,03-0,05, opacità massima 0,9: prospettiva aerea per nave,
     città e colline senza farle sparire.
  4. Nuvole: override con copertura 0,25-0,35, come i cumuli delle foto.
  5. Lato materiali (blender-artist): albedo dei bianchi ≤ 0,75; `Roughness_Mult` più basso per auto e acciaio del ponte; variazione a grande scala
     (seconda texture) su lastre, cubetti, prato e asfalto; texture 2048 per corten, scogliera, New Jersey.

### Temporanei e problemi aperti
- Nessun asset o attore temporaneo creato; script di lavoro solo nella scratchpad della sessione.
- **(blender-artist)** colline NE sopra l'acqua del Blocco 2 (§35.A); normali del chiosco v2 (§35.B); materiali dell'audit (§35.D).
- **(geo-scout → uefn-builder)** posizione reale della nave da crociera (§35.C).
- **(utente)** scegliere se e quali proposte di luce e nebbia applicare (§35.E).

## 36. Luce e atmosfera v1 (2026-11-20, ~16:40 ora locale)

### A. Valori PRIMA della modifica (per tornare indietro)
Device `Luce_OraDelGiorno` (`BP_DaySequenceModifier_Device_C_UAID_F068E322B343471603_1565984562`, Outliner `Luci`), letti con `ListClassicDeviceOptions`:
- Abilita durante la fase TUTTO · Modalità ORARIO FISSO · Tempo 18,0 · Priorità 2000 · Velocità dissolvenza 1 · Usa volume NO · Sequenza giorno utente nessuna.
- **Override luce sole: NO** (valori inattivi: intensità 10, colore (1; 1; 1; 0), rotazione Z 0, rotazione X 0, componente sole SÌ, brillamento SÌ).
- **Override nebbia: SÌ** · componente SÌ · densità **0,004** · colore (0,30; 0,38; 0,52; 1) · diminuzione altezza 0,02 ·
  dispersione direzionale (0,666667; 0,481005; 0,302083; 1) · nebbia secondaria densità 0, diminuzione 0,65, sfalsamento 0 ·
  dispersione volumetrica sole 1 · opacità massima 1.
- **Override luce cielo: NO** (inattivi: intensità 1, colore (1; 1; 1; 1)).
- **Override cielo: NO** (inattivi: sfumatura gradiente 0, basso (0,408; 0,719; 0,880), medio (0,068; 0,338; 0,948), alto (0,0037; 0,039; 0,141),
  dimensione sole 2, intensità sole 1, colore sole (0,906; 0,924; 1), sfumatura colore sole 0; luna 0,1 / 0,2; stelle 0).
- **Override nuvole: NO** (inattivi: colore chiaro (0,255; 0,255; 0,255), luminosità 5, copertura 0,4, opacità 1, colore ombra (0,151; 0,281; 0,5),
  velocità 1, direzione (1; 0), dimensione 1).

Valori effettivi letti sui componenti della Day Sequence del livello (`DSA_UEFN_Ch5S1_C_0`, generata da Fortnite, non salvata nel livello) alle 18,0:
- Sole: rotazione (pitch −27,2; yaw 41,9; roll −14,9) → luce che viaggia verso yaw UE 41,9: **sole da azimut geografico ~263° (ovest), elevazione 27°**
  (X UE = azimut 41,3°); intensità 12,96; colore (255; 219; 168); angolo sorgente 1,5; ombre dinamiche 3 cascate fino a 45 m.
- Luce cielo: intensità 4,37, cubemap specificata, colore bianco.
- Nebbia: come l'override sopra.
- Post process della Day Sequence (non modificabili dal device): `PostProcess` (priorità −10, unbound): esposizione istogramma, bias 0,15,
  luminosità min 0,06 / max 1,5, saturazione e contrasto 1, bloom 0,2, film toe 0,55, white temp non sovrascritta (6500).
  `ExposureLowEndPostProcess` (−8, solo low end): esposizione base 0,8-1,0. `BloomConvoutionHighEndPostProcess` (−6): bloom 0,4.
- `IslandSettings0`: orario, luce, nebbia = Predefinito. Nessun Post Process Volume nel livello.

### B. Come funzionano gli override (verificato leggendo il sole della Day Sequence dopo ogni modifica)
- Con *Override luce sole* = SÌ, **Rotazione Z luce solare = yaw assoluto della luce** (direzione in cui viaggia, in coordinate UE). Azimut geografico
  del sole = Z + 180° + 41,3° (X UE = azimut 41,3°). **Rotazione X fa ruotare attorno all'asse X (rollio/inclinazione laterale), non alza o abbassa il sole.**
- L'**elevazione** dipende solo dall'orario: 18,0 → 28°, 18,5 → 23°, 18,8 → 20°, 19,0 → 18°, 19,2 → 16° (~10°/h).
- *Intensità luce cielo* in override è **assoluta**: la Day Sequence di default alle 18 dà 4,37; 0,8 la riduce di ~5,5 volte (ombre più scure e meno blu).
- Esposizione, contrasto, saturazione e temperatura colore **non sono esposti** dal device. Stanno nei Post Process della Day Sequence (§36.A),
  non modificabili. Il *Post Process device* di Creative (`PID_CP_Devices_PostProcess`) offre solo effetti preimpostati, non l'esposizione:
  non usato. Non è stato piazzato nessun Post Process Volume.

### C. Valori DOPO (applicati con `SetClassicDeviceOption` sullo stesso device; nessun secondo modifier)
| Opzione | Prima | Dopo |
|---|---|---|
| Tempo ciclo giorno-notte | 18,0 | **18,5** (sole a 23° di elevazione) |
| Override luce sole | NO | **SÌ** |
| Intensità luce solare | (10) | **8** |
| Colore luce solare | (1; 1; 1; 0) | **(1,0; 0,86; 0,70; 1)** |
| Rotazione Z / X luce solare | (0 / 0) | **20 / 0** → sole da azimut **~241°** (OSO) |
| Override luce cielo | NO | **SÌ** |
| Intensità / colore luce cielo | (1; bianco) → effettiva 4,37 | **0,8 / (1,0; 0,97; 0,93; 1)** |
| Densità nebbia | 0,004 | **0,007** |
| Colore nebbia | (0,30; 0,38; 0,52) | **(0,45; 0,52; 0,62)** |
| Diminuzione altezza nebbia | 0,02 | **0,04** |
| Opacità massima nebbia | 1 | **0,9** |
| Dispersione direzionale nebbia | (0,667; 0,481; 0,302) | **(0,85; 0,62; 0,40)** |
| Override nuvole | NO | **SÌ**, copertura **0,3** (altri valori di nuvole = default del device) |
| Override cielo | NO | NO (invariato) |

Per tornare indietro: rimettere i valori della colonna "Prima" (§36.A); gli override a NO bastano per sole, cielo e nuvole.

**Ritocco luce cielo (2026-11-20 ~17:52, approvato dall'orchestratore, vedi §38.H):** colore luce cielo (1,0; 0,97; 0,93) → **(1,0; 0,92; 0,84)**,
intensità 0,8 → **1,0**. Per tornare indietro: `SkylightColor` (R=1, G=0,97, B=0,93, A=1) e `SkylightIntensity` 0,8.

**Taratura del sole (catture zenitali sulla passeggiata a X 150 m, scartate):** con l'azimut proposto 250° (Z 28,7) e 15-20° di elevazione le
ombre dei due filari di palme, lunghe ~3 volte l'altezza e spostate di ~15 m verso il mare, coprono **tutto** il camminamento e finiscono in acqua:
camminamento uniformemente in ombra, nessuna striscia leggibile. Anche la luce originale (azimut ~263°, 27°) lo copriva quasi tutto.
Con il sole più a sud (Z 20 → 241°) e 23° di elevazione le ombre corrono in diagonale e lasciano lame di sole verso il ciglio: scelto questo.
Deroga dalla proposta: azimut 241° invece di 250° ed elevazione 23° invece di 15-20°.

### D. Catture dopo (`docs/qa/realismo_luce_00..09.png`, stessi punti, FOV e risoluzione del §35.D, ombre attive) e confronto
`docs/qa/realismo_luce_confronto.png`: prima a sinistra, dopo a destra, per partenza (00), Giardini (03), ponte (06).
- **Migliora:** il cielo ha cumuli e un blu più profondo, l'orizzonte non è più bianco; luce calda e radente con **ombre lunghe e diagonali**
  di palme, panchine e lampioni sul camminamento (00, 01, 02, 03, 07); i bianchi non bruciano più (acciaio del ponte con chiaroscuro e stralli leggibili
  in 06, cemento del Molo Italia in 09, ciglio della banchina); grigi e cubetti meno viola; l'acqua riflette un cielo più blu e prende colore;
  foschia leggibile su colline e fondale (prospettiva aerea).
- **Non migliora o peggiora:** dove la vista è tutta in ombra (incrocio 05, scritta LA SPEZIA 08, parte del parcheggio 04) l'immagine è più scura
  e piatta; le chiome delle latifoglie in controluce sono quasi nere; le antenne del ponte dalla partenza (00) restano poco leggibili (ora per la
  foschia, prima per il cielo bianco); i difetti di materiale del §35.D (ripetizione delle lastre, corten, scogliera, prato lime) restano tutti:
  la luce non li corregge.
- **Attenzione:** le catture sono `RenderLevelPOVs` dell'editor, con la Day Sequence in anteprima. In gioco esposizione automatica (istogramma,
  0,06-1,5), bloom, scalabilità delle ombre e nuvole possono dare un risultato diverso: va controllato in sessione.

### E. Salvataggio e validazione
- Salvato l'unico pacchetto sporco (attore esterno del device `.../__ExternalActors__/LasPezia_Island/4/I8/YS7RUD2FV4XAJUCMZN3Z7R`); dopo il salvataggio
  nessun pacchetto sporco (contenuti e mappe). `ValidateAssets` sul livello: 1 controllato, 0 errori, 0 avvisi.
- Nessun attore creato o cancellato, nessuna sessione di gioco, nessun commit. Prove intermedie solo nella scratchpad.

## 37. Chiosco ottagonale v3, nave da crociera v2, colline NE v3, acqua del Molo Garibaldi (2026-11-20, ~16:40-16:55 ora locale)

Sorgenti: `exports/blocco2/SM_Morin_ChioscoOttagonale_v3*`, `exports/molo_italia/SM_MoloItalia_NaveCrociera_v2*` (+ `molo_italia_posizioni_v2.csv`),
`exports/fondale/SM_Fondale_Colline_NE_v3*`, texture `blender/textures/blocco2/T_Morin_ChioscoOtt_v3_*` e `blender/textures/molo_italia/T_MoloItalia_NaveCrociera_v2_*`.
Metodo §32/§33: LOD0 col nome finale via `ImportFile` (materiali/texture off), LOD1/2 come `_Temp/TMPB2V3_*`, `_Temp/TMPB3V3_*`, `_Temp/TMPF3_*`,
`remove_lods` + `set_lod_from_static_mesh(..., True)`, MI assegnate con `StaticMesh.set_material`, Nanite off, Use Simple Collision As Complex, soglie
1,0/0,2/0,08, temporanei MinLOD 0. Un cambio per chiamata MCP (una chiamata che creava due MI e le assegnava ha fatto cadere la connessione,
ECONNRESET, nessuna modifica applicata; rifatta a passi con `MaterialInstanceToolset`). Nessun attore né asset cancellato; le mesh precedenti restano
nel Content Browser.

### Asset
| Asset | Tri LOD0/1/2 | Bbox locale (uu) | Convessi | Slot → MI | MinLOD L/M |
|---|---|---|---|---|---|
| `Arte/Blocco2/SM_Morin_ChioscoOttagonale_v3` | 428 / 376 / 218 | X ±355,7 · Y ±355,7 · Z 0..384 (LOD1/2 identica) | 4 (UCX) | `MI_Morin_ChioscoOtt_v3`, `MI_Morin_ChioscoOtt_v3_Vetro` | 2 (come v2) |
| `Arte/MoloItalia/SM_MoloItalia_NaveCrociera_v2` | 2170 / 1350 / 1281 | X ±15000 · Y ±1960 · Z −850..6100 | **0** (2 UCX rimossi: fondale, come la v1) | `MI_MoloItalia_NaveCrociera_v2` | 2 (come v1) |
| `Arte/Fondale/SM_Fondale_Colline_NE_v3` | 7652 / 4082 / 1457 | come v2 | 0 (convesso automatico rimosso) | `MI_Fondale_Colline_NE` | 0 (come v2) |

- **Insidia §22 di nuovo:** sezione 1 dei LOD1/2 del chiosco sullo slot 0 → `set_lod_material_slot(mesh, 1, lod, 1)`: sezioni [0,1] in tutti i LOD.
- Texture (regola §29, una alla volta, LODBias 0, `GetSize` controllato): `Arte/Blocco2/T_Morin_ChioscoOtt_v3_D/N/ORM` 2048,
  `T_Morin_ChioscoOtt_v3_Vetro_D` 512; `Arte/MoloItalia/T_MoloItalia_NaveCrociera_v2_D/N/ORM` 2048. N Normalmap senza flip, ORM Masks sRGB off,
  D opache con "Compress Without Alpha" (§27). Vetro_N/ORM non importate (il master del vetro non ha texture).
- **Vetro:** `MI_Morin_ChioscoOtt_v3_Vetro` su `M_Morin_Master_Vetro` (Translucent, Volumetric Directional) con override **Two Sided = falso**,
  `Opacita` 0,28, `Colore` (0,30; 0,36; 0,38). Il master ha solo parametri scalari/vettore: la alpha di `T_Morin_ChioscoOtt_v3_Vetro_D` (macchie
  chiare) **non è campionata**; la texture è importata ma non referenziata. Per l'opacità da texture serve un parametro texture nel master
  (tocca anche `MI_Molo_Vetro`).
- Log degli import: nessun avviso (né tangenti degeneri né normali nulle).

### Posa (stessa cartella Outliner, nessun override di materiale)
- `Arte_B2_ChioscoOttagonale` → v3, (55206, −10872, 15), yaw 0, `FortStaticMesh` invariato.
- `Arte_B3_NaveCrociera` → v2, **(109466,41; 35323,52; −103), yaw 137,3163**, scala 1, No Collision. Bounds X 97111..121822 · Y 23713..46934 · Z −953..5997.
- `Arte_Fondale_Colline_NE` → v3, (518000, 48000, 0), No Collision, senza ombre (invariati).
- **Insidia nuova:** `StaticMeshComponent.set_static_mesh` e `set_actor_location` da Python **non marcano sporco il pacchetto OFPA**: dopo
  `save_dirty_packages` i 3 attori non risultavano salvati. Corretto con `actor.modify()` + `component.modify()` e nuovo salvataggio
  (file `__ExternalActors__/.../3/OG/WJ6C…`, `7/R6/TWRA…`, `7/WT/S8DG…` con data nuova). Controllare sempre la data dei file OFPA.

### Acqua: `Acqua_Golfo_Device_B3_Garibaldi` (Outliner `Acqua`, copia di `_B3_Est`, stesse opzioni: sempre attivo, altezza 1, 100 %, Default)
- Centro (114228, 30846, −484), larghezza **67** × profondità **97** → volume **X 97076..131380 · Y 6014..55678 · Z −484..−100**. Bordo comune con
  `_B3_Est` (Y 6014..35198) e `_B3_Mare` (Y 35198..55678) a X 97076: fessura 0, sovrapposizione 0. Esteso fino a X 1314 m (non 1260) perché il
  bacino del Molo Garibaldi, senza fondale, chiude solo a X ~1290-1310 m: un bordo a 1260 m lasciava un buco sul vuoto.
- Fondale sotto il volume (rasterizzazione dei triangoli LOD0 a 2 m su X 960-1280 m e a 5 m fino a X 1520 m):
  sotto lo scafo il fondale è a −3,9..−10 m (bacino nelle colline); attorno, terra di `Colline_NE`/`Colline_E` a **−0,85..−0,40 m**
  (20-60 cm sopra l'acqua, come le banchine; solo 5 celle a −1,00..−0,95 m a X 1018-1026 m, Y 62 m, sul bordo sud).
  Edifici di `Citta_NE_01`/`Citta_E_01` dentro il volume: tutti su terra sopra l'acqua, **tranne un blocco di `Arte_Fondale_Citta_E_01`** a
  X 1000-1014 m, Y UE 478-492 m (Blender Y −478..−492), ~140 m² di impronta sulla scarpata a mare (terreno < −1 m): la base risulta in acqua.
  Il volume non si può ritagliare lì (serve acqua fino a X ~1008 m alla stessa Y). **Conflitto segnalato a blender-artist.**
- **Barriere invariate** (area non giocabile, oltre `Barriera_Acqua_LatoPiuX_B3`). Log: alla duplicazione lo stesso avviso
  "TimelinePostUpdateFunc ... Unable to find function" del §34.

### Verifiche
- **Chiosco:** catture `docs/qa/uefn_chiosco_ott_v3_{E,S,O,N,SE}.png` (8-11 m, FOV 60, ombre; E = +X, S = +Y lato mare, O = −X, N = −Y lato città):
  tutte le 8 pareti si vedono da fuori, nessuna trasparente o buia; dietro i 3 banconi vetrati si vedono scaffali e frigo; insegna e tettoia corrette.
  Collisione: 24 trace orizzontali (8 direzioni × Z 60/200/330) → 23 sul chiosco (r 2,95 m), 1 su uno sgabello davanti.
- **Nave:** `docs/qa/uefn_nave_v2_faro.png` (64300, 29300, 180; yaw 30; pitch 2; FOV 75), come `ref/foto/vista/faro_2.png`: nave a sinistra del faro,
  parallela alla costa del Molo Garibaldi, sull'acqua. Rispetto alla foto appare ~1,5 volte più grande nell'inquadratura (punto di ripresa della
  foto non noto con precisione).
- **Colline NE v3, Blocco 2:** rasterizzazione a 1 m su X 330-580 m, lato mare (Y UE > −7900): nessun punto sopra l'acqua né sotto la superficie
  che non sia coperto da suolo con collisione (radice del Molo Italia, piazzale), salvo 7 punti a −3,2..−4,7 m nello smusso X 549-554 m.
  Catture `docs/qa/uefn_b2_acqua_fix.png` (passeggiata X 380, punto di `diag_b2_acqua_passeggiata_X380.png`), `uefn_b2_acqua_fix_X550.png`
  (52000, −8300, 170; yaw 60), `uefn_b2_acqua_fix_alto.png` (42000, −1000, 36000; zenitale; FOV 70, come `diag_b2_acqua_alto.png`):
  **le macchie verdi A e B sono sparite**. Restano rettangoli d'acqua leggermente più chiari lungo la banchina (fondo a −5 m in trasparenza), non verdi.

### Salvataggio, validazione, log
`save_dirty_packages`: **0 pacchetti sporchi** (contenuti e mappe); 19 asset nuovi + 4 OFPA salvati. Validazione `LaSpezia/`: **730/730 validi,
0 errori, 57 avvisi** (i noti di `ValkyrieValidator_StaticMesh`). Log: nessun errore sul progetto (solo `LogEOSSDK` di sistema, l'avviso di timeline
del device Acqua e due errori di una mia query con indice di sezione sbagliato, senza effetti). Attori nel livello: 350 → **352** (+device Acqua V2
e il suo `BP_FortWaterBodyCubeVolume_C`).

### Temporanei e problemi aperti
- 6 nuovi temporanei `LaSpezia/_Temp/TMPB2V3_*`, `TMPB3V3_*`, `TMPF3_*` (LOD1/LOD2), nessun referencer; eliminabili con conferma dell'utente insieme a
  `SM_Morin_ChioscoOttagonale_v2`, `SM_MoloItalia_NaveCrociera`, `SM_Fondale_Colline_NE_v2`, ora non usate.
- **(blender-artist)** blocco di `Arte_Fondale_Citta_E_01` con la base in acqua a X 1000-1014 m, Y Blender −478..−492 m.
- **(blender-artist / utente, facoltativo)** opacità del vetro da texture: serve un parametro texture in `M_Morin_Master_Vetro`.
- **(qa-tester)** In sessione: vetro del chiosco (traslucenza, interno visibile), nave e bordo dell'acqua a X 1314 m visti dal faro.

## 38. Texture v2 realistiche e macro-variazione (2026-11-20, ~17:40 ora locale)

Istruzioni: `docs/texture_v2.md`. Sorgenti `blender/textures/v2/*.png`. Nessuna texture v1 sovrascritta: cambiano solo i riferimenti nelle MI.

### A. Valori PRIMA della modifica (per tornare indietro)
Percorso radice `LaSpezia/Arte/`. Tutte le MI usano i parametri texture `BaseColor`, `Normal`, `ORM` (+ `Emissive` per le luci delle auto) con le
texture `<cartella>/<nome>_D/_N/_ORM` indicate. Nessuna MI aveva override di `Roughness_Mult` (default del master 1,0) né di `UV_Tiling` (default 1,0).

| MI (cartella) | Master | Texture v1 (prefisso) | Scalari / vettori con override |
|---|---|---|---|
| `MI_Pav_Lastre` (Pavimentazione) | Pav | `Pavimentazione/T_Pav_Lastre` | `Tile_m` 3,2 · `Tinta` (0,60; 0,56; 0,48; 1) |
| `MI_Pav_Cubetti` (Pavimentazione) | Pav | `Pavimentazione/T_Pav_Cubetti` | `Tile_m` 3,2 · `Tinta` (0,62; 0,58; 0,52; 1) |
| `MI_Pav_Fascia` (Pavimentazione) | Pav | `Pavimentazione/T_Pav_Fascia` | `Tile_m` 1,0 |
| `MI_Banchina_Blocchi` (Banchina) | PBR | `Banchina/T_Banchina_Blocchi` | — |
| `MI_Morin_Prato` (Viale) | PBR | `Viale/T_Morin_Prato` | — |
| `MI_Morin_Prato_Mondo` (Viale) | Pav | `Viale/T_Morin_Prato` | `Tile_m` 4,0 |
| `MI_Parcheggio_Asfalto` (Parcheggio) | PBR | `Parcheggio/T_Parcheggio_Asfalto` | — |
| `MI_Molo_Asfalto` (Molo) | PBR | `Molo/T_Molo_Asfalto` | — |
| `MI_MoloItalia_Cemento` (MoloItalia) | PBR | `MoloItalia/T_MoloItalia_Cemento` | — |
| `MI_Molo_Scogliera` (MoloItalia) | PBR | `MoloItalia/T_Molo_Scogliera` | — |
| `MI_Morin_Corten` (Blocco2) | PBR | `Blocco2/T_Morin_Corten` | — |
| `MI_Ponte_Legno` (Ponte) | PBR | `Ponte/T_Ponte_Legno` | — |
| `MI_Ponte_Acciaio` (Ponte) | PBR | `Ponte/T_Ponte_Acciaio` | — |
| `MI_Morin_NewJersey` (Parcheggio) | PBR | `Parcheggio/T_Morin_NewJersey` | — |
| `MI_Banchina_Paramento` (Banchina) | PBR | `Banchina/T_Banchina_Paramento` | — |
| `MI_Morin_PalmaA_Tronco` (Palme) | PBR | `Palme/T_Morin_PalmaA_Tronco` | — |
| `MI_Morin_PinoDomestico_Corteccia` (Alberi) | PBR | `Alberi/T_Morin_PinoDomestico_Corteccia` | — |
| `MI_Albero_Latifoglia_Chioma` (Alberi) | PBR_Masked | `Alberi/T_Albero_Latifoglia_Chioma` | — |
| `MI_Morin_Auto_v2` (Auto) | PBR | `Auto/T_Morin_Auto_v2` (D, N, ORM) | — |
| `MI_Morin_Auto_v2_Luci` (Auto) | PBR_Emissive | `Auto/T_Morin_Auto_v2` (D, N, ORM) + `Auto/T_Morin_Auto_v2_E` | `Emissive_Intensita` 4,0 |

Master prima della modifica: `M_Morin_Master_PBR` 10 espressioni (UV0 × `UV_Tiling` → BaseColor/Normal/ORM; BaseColor × `Tinta`; ORM.G × `Roughness_Mult`;
ORM.R → AO, ORM.B → Metallic). `M_Morin_Master_Pav` 33 espressioni (UV da posizione mondo / `Tile_m`·100 con proiezione verticale, BaseColor × `Tinta`,
ORM.G × `Roughness_Mult`; 8 nodi orfani non collegati, lasciati). Default: `UV_Tiling` 1, `Tile_m` 3,2, `Roughness_Mult` 1, `Tinta` bianco.
Per tornare indietro: rimettere nelle MI i riferimenti e i valori della tabella e portare `Macro_Int` a 0 (il default).

### B. Import (`LaSpezia/Arte/Texture_v2`, 54 texture, nomi nuovi, nessun reimport sulle v1)
- `AssetImportTask` (automated, replace off) **una texture alla volta**; poi le impostazioni **una proprietà alla volta** con
  `finish_all_asset_compilation` prima e dopo ogni `set_editor_property` (in Python `Texture2D` non ha `post_edit_change`; ogni set ricompila),
  infine `TextureToolset.GetSize` > 32 prima della texture successiva (regola §29).
- D: sRGB on, Default, **Compress Without Alpha on** (tranne `T_Albero_Latifoglia_Chioma_v2_D`: alfa conservata). N: Normalmap, sRGB off, nessun flip.
  ORM e `T_Morin_MacroVar`: Masks, sRGB off. Tutte: gruppo World, LODBias 0, mip da gruppo.
- Dimensioni lette: 4096 per `T_Pav_Lastre_v2`, `T_Pav_Cubetti_v2`, `T_Parcheggio_Asfalto_v2`, `T_Molo_Asfalto_v2`, `T_MoloItalia_Cemento_v2`,
  `T_Ponte_Legno_v2`, `T_Ponte_Acciaio_v2` (7 set, 21 texture; il documento dice "nove set" ma ne elenca 7); 2048 per tutte le altre.
- Controllo finale: **217/217 texture di `LaSpezia/` con GetSize > 32**; nessun `contains no miplevels` nel log.

### C. Master: macro-variazione (`T_Morin_MacroVar`, coordinate mondo, 32 m)
Aggiunti a `M_Morin_Master_PBR` e `M_Morin_Master_Pav` (gruppo `Macro`) 13 nodi ciascuno, formula di `docs/texture_v2.md`:
`WorldPosition.xy / 3200` → `MacroVar` (TextureSampleParameter2D, sampler Masks, campionatore condiviso Wrap World) → R = M;
BaseColor = (BaseColor × Tinta) × lerp(1, 2M, `Macro_Int`); Roughness = saturate(ORM.G × `Roughness_Mult` + (M − 0,5) × 0,3 × `Macro_Int`).
`Macro_Int` default **0** (le MI che non lo impostano restano invariate). Nessun altro nodo toccato; i nodi orfani del Pav restano.
Statistiche (`MaterialToolset.GetStatistics`, prima → dopo): PBR **213 → 225** istruzioni pixel, campioni 3 → 4, campionatori 3 → 4;
Pav **213 → 225**, campioni 6 → 7, campionatori 3 → 4; vertex invariati. +12 istruzioni (+5,6 %): costo ragionevole. Compilazione senza errori
(22 shader, nessun errore `LogMaterial`/`LogShaderCompilers`). Nota: anche le MI con `Macro_Int` 0 pagano il campione in più
(niente static switch, per non creare permutazioni).

### D. MI ricollegate (20: le 19 della tabella del documento + `MI_Morin_Auto_v2_Luci`)
| MI | Texture | Tile_m / UV_Tiling | Roughness_Mult | Macro_Int | Altro |
|---|---|---|---|---|---|
| `MI_Pav_Lastre` | `T_Pav_Lastre_v2` | Tile_m **4,8** | 1,0 | 0,35 | `Tinta` → bianco (1; 1; 1) |
| `MI_Pav_Cubetti` | `T_Pav_Cubetti_v2` | Tile_m **2,8** | 1,0 | 0,30 | `Tinta` → bianco |
| `MI_Pav_Fascia` | `T_Pav_Fascia_v2` | Tile_m **2,0** | 1,0 | 0,25 | |
| `MI_Banchina_Blocchi` | `T_Banchina_Blocchi_v2` | UV 1 | 1,0 | 0,25 | |
| `MI_Morin_Prato` / `MI_Morin_Prato_Mondo` | `T_Morin_Prato_v2` | UV 1 / Tile_m 4 | 1,0 | 0,45 | |
| `MI_Parcheggio_Asfalto` / `MI_Molo_Asfalto` | `T_Parcheggio_Asfalto_v2` / `T_Molo_Asfalto_v2` | UV 1 | 1,0 | 0,35 | |
| `MI_MoloItalia_Cemento` | `T_MoloItalia_Cemento_v2` | UV 1 | 1,0 | 0,30 | |
| `MI_Molo_Scogliera` | `T_Molo_Scogliera_v2` | UV 1 | 1,0 | 0,20 | |
| `MI_Ponte_Legno` | `T_Ponte_Legno_v2` | UV 1 | 1,0 | 0,20 | |
| `MI_Banchina_Paramento` | `T_Banchina_Paramento_v2` | UV 1 | 1,0 | 0,25 | |
| `MI_Ponte_Acciaio` | `T_Ponte_Acciaio_v2` | UV 1 | **0,9** | 0 | |
| `MI_Morin_Corten`, `MI_Morin_NewJersey`, `MI_Morin_PinoDomestico_Corteccia` | rispettive `_v2` | UV 1 | 1,0 | 0 | |
| `MI_Morin_PalmaA_Tronco` | `T_Morin_PalmaA_Tronco_v2` | — | 1,0 | 0 | |
| `MI_Albero_Latifoglia_Chioma` (Masked) | `T_Albero_Latifoglia_Chioma_v2` | — | 1,0 | (non nel master) | |
| `MI_Morin_Auto_v2` | D/ORM `T_Morin_Auto_v3`, N `T_Morin_Auto_v2_N` | — | 1,0 | 0 | |
| `MI_Morin_Auto_v2_Luci` (Emissive) | D/ORM `T_Morin_Auto_v3`, N ed E v2 | — | 1,0 | (non nel master) | `Emissive_Intensita` 4 invariato |

Deroga annotata: `Tinta` di lastre e cubetti portata a bianco come chiede la tabella (`Tinta` 1): l'albedo v2 è già tarato, il vecchio
(0,6; 0,56; 0,48) lo avrebbe scurito del 40 %.

### E. Catture (`docs/qa/realismo_tex_00..09.png`, stessi punti e FOV del §35.D, 1024 px, ombre, `r.Streaming.FullyLoadUsedTextures 1`, doppio render con 8 s di attesa)
Extra: `realismo_tex_extra_10.png` (asfalto del parcheggio dall'alto, pitch −40), `_11` (cubetti e fascia ravvicinati), `_12` (cubetti dell'incrocio).
Confronto `docs/qa/realismo_tex_confronto.png`: a sinistra `realismo_luce_*` (texture v1), a destra `realismo_tex_*`; righe 01 pavimentazione,
03 giardini, 06 ponte, 09 molo.
- **Migliora:** cubetti finalmente porfido credibile (cubetti piccoli, ventagli più stretti, fughe scure, niente viola-bruno uniforme);
  fascia e cordoli in pietra opaca invece di plastica bianca; cemento del Molo Italia sporco e senza griglia di piastrelle (09); scogliera con
  massi rocciosi veri; asfalto del parcheggio senza i rettangoli scuri ripetuti, con macro-variazione morbida; corten con chiazze e colature (08);
  New Jersey grigio cemento invece di bianco; tronchi delle palme più chiari; auto con riflessi della vernice.
- **Scacchiera delle lastre:** resta una variazione di tono **per lastra** ben visibile (alcune lastre più scure, distribuite in modo regolare):
  meno "macchia ripetuta" della v1, ma a 5-15 m si legge ancora come una scacchiera leggera. In più le lastre v2, senza la vecchia `Tinta` calda,
  sono **più chiare e fredde (grigio-azzurro)** della v1 e della foto `pav_1.png`: da valutare con l'utente (rimedio rapido: `Tinta` ~(0,95; 0,92; 0,86)).
- **Macchie d'olio lucide sull'asfalto:** nelle catture (anche quella ravvicinata extra_10, con sole radente) **non si vede nessun riflesso lucido**:
  le macchie si percepiscono appena e l'asfalto da vicino è piuttosto uniforme e un po' morbido. Nessun difetto, ma nemmeno l'effetto cercato.
- **Verde del prato:** non più lime: verde oliva più scuro e naturale (03); la macro-variazione a 0,45 dà chiazze molto morbide, ma a distanza il
  prato resta abbastanza uniforme.
- **Cubetti:** il miglioramento più netto. Difetti: in ombra virano al **lilla** (luce cielo fredda sulla tinta grigio-bruna) e con tile 2,8 m i
  ventagli si ripetono in modo visibile sui piazzali larghi (extra_12).
- **Invariato o quasi:** legno del ponte (06) quasi identico alla v1; acciaio del ponte poco diverso (già meno bruciato con la luce v1);
  strisce pedonali con macchie bianco-grigie (texture non rifatta); paramento della radice del molo (07) ancora scuro e uniforme.
- Attenzione: sono catture dell'editor (`RenderLevelPOVs`), non in gioco.

### F. Salvataggio, validazione, memoria
- `save_dirty_packages`: 76 pacchetti (54 texture, 2 master, 20 MI); su disco 76 `.uasset` con data 17:43:47; dopo il salvataggio
  **0 pacchetti sporchi** (contenuti e mappe). Nessun attore toccato (352), nessuna sessione, nessuna cancellazione.
- Validazione `LaSpezia/`: **784/784 validi, 0 errori, 57 avvisi** (i noti di `ValkyrieValidator_StaticMesh`); `ValkyrieValidator_Textures` 217, 0 avvisi.
- Log: nessun errore di texture, materiali o shader; solo `LogEOSSDK` di sistema.
- **Memoria texture a runtime (stima a mano, solo informativa, metodo §21):** texture v2 a piena risoluzione con mip (BC1 0,5 B/px per D e ORM
  opachi, BC5 1 B/px per N, BC3 per la chioma, ×1,33): 7 set 4096 ≈ **299 MiB**, 10 set 2048 ≈ 109 MiB, auto v3 + MacroVar ≈ 8 MiB, **≈ 416 MiB**
  in più se fossero tutte residenti. Le v1 sostituite restano nel progetto ma queste MI non le referenziano più. Lo streaming ne tiene residente
  solo una parte e il budget di pubblicazione (300 MiB statici, §30) non conta i mip in streaming: rileggere "Budget memoria mappa" (sorgente
  "Pubblica") dopo la prossima sessione dell'utente. Per ridurre: cemento del Molo Italia e asfalto del molo a 2048 (come suggerisce il documento).

### Problemi aperti
- **(utente)** Giudizio sulle catture: tono freddo e chiaro delle lastre (`Tinta`), lilla dei cubetti in ombra, ripetizione dei ventagli.
- **(blender-artist, facoltativo)** Macchie d'olio dell'asfalto troppo deboli per sembrare lucide; legno del ponte quasi uguale alla v1;
  strisce pedonali e paramento della radice del molo non rifatti.
- **(qa-tester)** Verifica in sessione (esposizione automatica) e, dopo un riavvio dell'editor, che le 54 texture restino valide.
- Le texture v1 restano nel progetto (nessuna cancellazione); eliminabili solo con conferma dell'utente.

### G. Ritocco Tinta (approvato dall'orchestratore, reversibile)
- `MI_Pav_Lastre`: `Tinta` (1; 1; 1) → **(0,95; 0,92; 0,86)**. `MI_Pav_Cubetti`: `Tinta` (1; 1; 1) → **(0,97; 0,94; 0,90)**. Per tornare indietro: rimettere (1; 1; 1).
- Catture `docs/qa/realismo_tex_01b.png` e `realismo_tex_03b.png` (stessi punti di 01/03). Lastre: leggermente più calde, ma nelle zone in ombra
  resta una dominante grigio-azzurra; la foto `ref/foto/pavimentazione/pavimento verso il ponte.png` è un grigio neutro-caldo. La differenza residua
  viene soprattutto dalla luce cielo fredda sulle ombre, non dall'albedo. Cubetti: al sole un po' più caldi; il lilla in ombra cambia poco, quindi
  **viene dal cielo** (luce cielo e nebbia del §36), non dall'albedo. Correggerlo con altra tinta scurirebbe/arrosserebbe le parti al sole.
- Salvati i 2 pacchetti, 0 sporchi; validazione `LaSpezia/` 784/784, 0 errori, 57 avvisi noti.

### H. Luce cielo più calda (approvato dall'orchestratore; valori vecchi annotati nel §36.C)
- Device `Luce_OraDelGiorno`, `SetClassicDeviceOption`: `SkylightColor` (1; 0,97; 0,93) → **(1,0; 0,92; 0,84)**; provate intensità 0,8 e 1,0
  (catture 01, 03, 05 per entrambe). Scelta **1,0**: con 0,8 le ombre dell'incrocio restano più scure; con 1,0 sono un po' più aperte, i cubetti in
  ombra diventano grigio-bruni neutro-caldi (niente più lilla) e le lastre in ombra perdono quasi tutta la dominante azzurra. Le zone al sole non bruciano.
- Catture `docs/qa/realismo_tex_01c.png`, `_03c.png`, `_05c.png` (stessi punti del §35.D).
- Salvato l'attore esterno del device (`__ExternalActors__/LasPezia_Island/4/I8/YS7RUD2FV4XAJUCMZN3Z7R`, data 17:52:40); 0 pacchetti sporchi;
  validazione `LaSpezia/` 784/784, 0 errori, 57 avvisi noti. Da confermare in sessione (esposizione automatica).

## 39. Marina del Blocco 1 v1: pontili, passerelle, colonnine, circolo, 544 barche (2026-11-20, ~18:05-18:30 ora locale)

Sorgenti: `exports/marina/` (68 FBX), `marina_pontili_v2.csv` (101 righe), `marina_barche_v2.csv` (544), texture `blender/textures/marina/`.
Controllo iniziale: nessun asset né attore con questi nomi. Nessun attore esistente spostato, nascosto o cancellato. Nessuna sessione avviata.

### Import (metodo §13/§22/§29)
- LOD0 col nome finale in `LaSpezia/Arte/Marina` con `StaticMeshToolset.ImportFile` (materiali e texture **off**: l'atlante incorporato negli FBX
  non è stato importato 68 volte), LOD1/2 come `_Temp/TMPMA_<asset>_LOD1/_LOD2` (44), `remove_lods` (di nuovo 3 LOD automatici) +
  `set_lod_from_static_mesh(..., True)`, sezioni dei LOD controllate per nome di slot (nessuna da rimappare), Nanite off,
  Use Simple Collision As Complex, soglie 1,0/0,2/0,08, MinLOD Low/Medium 2 sui 22 asset a 3 LOD, 0 su largo, circolo e temporanei.
- Barche: `remove_collisions` (0 convessi). Pontili: UCX arrivati con l'import, nessun convesso automatico in più.
- Texture **una sola volta** (`AssetImportTask`, una alla volta, attesa della compilazione dopo ogni proprietà, `GetSize` 2048 su tutte e 3;
  nessun `no miplevels` nel log): `T_Morin_Marina_D` sRGB, Default, Compress Without Alpha; `_N` Normalmap senza flip; `_ORM` Masks sRGB off;
  LODBias 0. `MI_Morin_Marina` su `M_Morin_Master_PBR` (BaseColor/Normal/ORM). Nota: l'attesa giusta in Python è
  `unreal.AutomationUtilsBlueprintLibrary.finish_all_asset_compilation()` (non esiste `unreal.AssetCompilingManager`).
- Slot: `M_Morin_Marina` → `MI_Morin_Marina` (barche, colonnina, circolo), `M_Morin_Imbarco` / `M_Morin_Imbarco_Legno` → MI esistenti di `Arte/Imbarco`
  (pontili, passerella, largo, circolo). In `Arte/Marina`: 24 mesh, 3 texture, 1 MI. **Nessun duplicato** di texture o materiali.

| Asset | Tri LOD0/1/2 | Bbox locale (uu) | Convessi |
|---|---|---|---|
| `SM_Morin_Barca_Gommone_{Grigio,Nero,Rosso}` / `_Prua` | 980 / 488 / 222 | X −320..266 (prua −272..315) · Y ±110 · Z −38..124 | 0 |
| `SM_Morin_Barca_Gozzo_{FasciaAzzurra,FasciaVerde,Legno}` / `_Prua` | 718 / 454 / 200 | X −346..298 (prua −297..347) · Y ±115 · Z −42..180 | 0 |
| `SM_Morin_Barca_Motoscafo_{TelaBlu,TelaBeige,Blu}` | 1.134 / 660 / 272 | X −465..366 · Y ±135 · Z −50..209 | 0 |
| `SM_Morin_Barca_Vela9_{CoprirandaBlu,CoprirandaGrigio,Blu}` | 974 / 488 / 192 | X −488..455 · Y ±150 · Z −40..1300 | 0 |
| `SM_Morin_Marina_Pontile12` | 246 / 98 / 58 | X 0..1200 · Y ±150,5 · Z −55..12 | 1 (X 0..1200, Y ±140, Z −55..0) |
| `SM_Mirabello_Pontile_Col` | 248 / 248 / 48 | X 0..4800 · Y ±148 · Z −55..100 | 6 (calpestio + 5 colonnine 30 × 30 cm **in asse**, ogni 10 m) |
| `SM_Morin_Marina_Passerella` | 204 / 188 / 92 | X −35..395 · Y ±140 · Z −58..103,5 | 3 (rampa + 2 corrimano) |
| `SM_Morin_Marina_Colonnina` | 66 / 58 / 46 | X ±16 · Y −16..13 · Z 0..116 | 1 |
| `SM_Morin_Marina_PontileLargo` | 998 | X 0..3470 · Y ±250 · Z −220..38 | 1 |
| `SM_Morin_Marina_Circolo` | 862 | X ±850 · Y −800..650 · Z −220..700 | 5 |

Bbox dei LOD1/LOD2 entro 5 uu dal LOD0 (Pontile12 LOD1/2 Y ±148 contro ±150,5). Triangoli = PLAN.

### Posa (Outliner `Arte/Marina/<gruppo>`)
HISM duplicati: pontili da `Arte_Arredi_Tombini` (`FortStaticMesh`, Query Only), barche da `Arte_Mirabello_YachtA` (Custom, No Collision);
singoli da `Arte_Arredi_Gazebo`; `clear_instances`, poi `Rotator(roll, pitch, yaw)` dal CSV. Tutti Static.

| Attore | Mesh | Istanze |
|---|---|---|
| `Arte_Marina_Pontili_PontileCol` / `_Pontile12` / `_Passerelle` | Pontile_Col / Pontile12 / Passerella | 22 / 46 / 3 |
| `Arte_Marina_Arredi_Colonnine` | Colonnina | 28 |
| `Arte_Marina_PontileLargo`, `Arte_Marina_Circolo` (singoli) | Largo (12690, −8008,7, 0) yaw 89,67 · Circolo (16100, −7200, 0) yaw 0 | 1 + 1 |
| `Arte_Marina_Barche_<Tipo>_<Variante>[_Prua]` (18 HISM, cartella `Barche`) | barche | 461 |
| `Arte_Marina_Yacht_YachtA` / `_YachtB_v2` (cartella `Yacht`) | `Arte/Mirabello/SM_Mirabello_YachtA` / `_YachtB_v2` (riusati) | 38 / 45 |
| `Arte_Marina_Pontili_Raccordi` (vedi sotto) | Pontile12 scalato in X | 10 |

Totale: 101 pezzi del CSV + 544 barche + 10 raccordi. Attori nel livello 352 → **379**.
- **Quota delle barche: −103** (CSV). Nelle catture ravvicinate il fondo rosso antivegetativa emerge già di ~10 cm; a −100 emergerebbe di più,
  quindi resta −103 (gli yacht di Mirabello restano a −100).
- **Verso "+X = prua":** viste dall'alto di YachtA e YachtB_v2: prua in +X, poppa sul pontile. Controllo su tutte le 544 (trace orizzontali a Z −70
  in avanti e indietro fino al pontile): le 487 normali hanno la poppa verso il pontile, le 57 `_Prua` la prua: **544/544 coerenti** col CSV.

### Raccordi (deroga di posa, da sostituire con la correzione del CSV)
Line trace a griglia (fascia ±1 m dall'asse di ogni pontile) + "caduta" di una capsula r 34 / hh 88 sui punti senza pavimento: con i soli pezzi
del CSV c'erano **buchi veri**: radici dei fingers F1-F5 staccate dal fianco della spina di **57 / 46 / 39 / 23 / 17 cm** (la spina devia di 0,28°
e il CSV mette le radici a X 152-153 m); gomiti della spina (UE 15030, 8600 e 19550, 13200: tacche triangolari fino a 1 m sul bordo esterno,
capsula sostenuta) e del pontile esterno 2 (UE 19600, 21284 e 21375, 22956: distacco 52 e 41 cm + tacca, **la capsula cadeva in acqua**);
angolo del pontile a L (quadrato 2,8 × 1,4 m mancante). Aggiunti 10 pezzi `SM_Morin_Marina_Pontile12` in un HISM a parte,
**Z −46** (1 cm sotto il calpestio, come le sovrapposizioni del CSV), scala X = lunghezza / 12 m: radici 0,37-0,77 m lungo l'asse del finger
(da 10 cm dentro la spina a 10 cm dentro il finger), gomiti 1,3-2,0 m sulla bisettrice, angolo L 2,9 m. Nei gomiti i pezzi sporgono di
pochi cm dal bordo (≤ 12 cm sugli UCX). La correzione vera va fatta nel generatore (segnalata); poi l'HISM si toglie.

### Verifiche (line trace e sweep in editor)
- **Percorrenza** (15 catene: spina, esterno, esterno 2, F1-F8, L gamba/testa/ramo, NE; partenza dalla banchina a Y −8400 per spina, L e NE):
  griglia 10 cm, 311.002 punti: nessun buco salvo le linee di giunzione fra moduli (strisce di 1 campione, larghezza 0) e punti oltre le
  testate; **0 cadute di capsula**, abbassamento massimo della capsula 3 cm (radice F7). Gradini fra campioni a 10 cm: **max 3,1 cm**
  (passerella: Z 0 sul ciglio → −45 in 3,9 m, continua); raccordi −46 contro −45.
- **Sweep di capsula** (r 34, hh 88, 20 cm sopra il pavimento, passo 10 cm) su corsie a ±60 cm dall'asse: **0 blocchi** dalla banchina alla
  punta di ogni finger. In asse la capsula urta le colonnine centrali del `Pontile_Col` (30 × 30 cm ogni 10 m) e le `Colonnine`: si passa di lato.
- **Barche:** 3.264 trace verticali (canali Visibility e Camera, 3 punti per barca): **0 colpi**.
- **Zone libere** (OBB delle istanze contro le zone del generatore): specchi davanti alle scalette X 92/140/188 (±4 m, Y 66-82 Blender)
  **liberi**; zona del battello X 55-90 m: nessuna barca; vi entrano solo le punte OSM del pontile a L (testa fino a X 89,4 m, ramo 88,9 m), 0,5-1,1 m.
- **Barriere: invariate.** Lato mare del Blocco 1 = `Barriera_Acqua_LatoMare` (X −17600..28480) + `Barriera_Acqua_LatoMare_B2` (X 27340..58060),
  entrambe Y 30800..31056, sovrapposte per 1140 uu: nessun varco. I pontili arrivano al massimo a Y +23118 (esterno 2, Blender −231 m), 77 m dentro.
  Nessun'altra barriera interseca l'impronta della marina (X 8800..31700, Y −8100..23200). `Acqua_Golfo_Device` arriva a X 33850, Y 30844: copre tutto.

### Salvataggio, validazione, log, memoria
`save_dirty_packages` 18:11 (68 asset), 18:13 (27 OFPA + 5 external object delle cartelle), raccordi su disco 18:20; poi **0 pacchetti sporchi**;
date dei 27 `.uasset` in `__ExternalActors__` controllate su disco. Validazione `LaSpezia/`: **856/856 validi, 0 errori, 80 avvisi** = 57 noti +
"un solo LOD" su largo, circolo (pezzi unici) e sui 21 temporanei `TMPMA_*_LOD1` delle barche. Log: nessun errore sul progetto (solo
`LogAudioMixer` di sistema e deprecazioni Python di `TraceTypeQuery`). Memoria texture: +1 set 2048 D/N/ORM ≈ **+10,7 MiB** con i mip.
Una chiamata MCP con 6 HISM in un colpo ha fatto cadere la connessione (ECONNRESET, nessuna modifica applicata): rifatta a 2 HISM per chiamata (§34).

### Catture (`docs/qa/`, 1024 px, ombre, `r.Streaming.FullyLoadUsedTextures 1`, doppio render)
- `uefn_marina_banchina.png`: (30000, −8100, 170), yaw 173,5, pitch −0,2, FOV 64. **Nota:** con la camera Blender `CAM_Mar_Banchina` (X 282 m)
  l'ancora del monumento sta accanto alla camera; l'inquadratura di `arte_marina_v1_banchina_confronto.png` (pontile NE con passerella a sinistra,
  ancora ~15 m avanti, circolo in fondo) torna con la camera a **X 300 m**: usata questa.
- `uefn_marina_finger.png`: (15600, −1880, 120), yaw 0,8, pitch −1,6, FOV 70 (sul finger F3 verso la punta).
- `uefn_marina_alto.png`: (7500, −17500, 11000), yaw 56,3, pitch −29, FOV 62.

### Temporanei e problemi aperti
- 44 `LaSpezia/_Temp/TMPMA_*_LOD1/_LOD2`, nessun referencer; eliminabili con conferma dell'utente.
- **(blender-artist)** Correggere nel generatore le radici dei fingers, i 4 gomiti e l'angolo del pontile a L (vedi Raccordi), poi togliere
  `Arte_Marina_Pontili_Raccordi`.
- **(blender-artist, verifica)** `CAM_Mar_Banchina` dello script (X 282) non corrisponde all'immagine di confronto (sembra X ~300).
- **(qa-tester)** In sessione: passerelle, raccordi, colonnine in asse sui `Pontile_Col`, barche senza collisione, acqua attorno ai pontili.

## 40. Marina: pontili v3 e raccordi tondi (2026-11-20, ~18:35-18:50 ora locale)

Sorgenti: `exports/marina/SM_Morin_Marina_Raccordo{,_LOD1,_LOD2}.fbx`, `marina_pontili_v3.csv` (111 righe, coordinate UE). Nessun attore né asset
cancellato, nessuna sessione avviata.

### Import (metodo §39)
- LOD0 col nome finale `LaSpezia/Arte/Marina/SM_Morin_Marina_Raccordo` (`StaticMeshToolset.ImportFile`, materiali/texture off, combine on),
  LOD1/2 come `_Temp/TMPMA_SM_Morin_Marina_Raccordo_LOD1/_LOD2`; `remove_lods` su tutti e tre, `set_lod_from_static_mesh(..., True)`.
- **Insidia:** dopo la copia la sezione 1 dei LOD1/2 puntava allo slot 0 (nei temporanei era [0, 1]): rimappata con
  `set_lod_material_slot(mesh, 1, lod, 1)` → tutti i LOD [0, 1]. Controllare sempre le sezioni per indice, non solo per nome.
- Slot `M_Morin_Imbarco` → `MI_Morin_Imbarco`, `M_Morin_Imbarco_Legno` → `MI_Morin_Imbarco_Legno` (anche sui temporanei). Nanite off,
  Use Simple Collision As Complex, soglie 1,0/0,2/0,08, MinLOD Low/Medium 2 (temporanei 0).
- Tri **110 / 78 / 22**, bbox di tutti i LOD X ±150 · Y ±150 · Z −55..0, **1 convesso** (UCX arrivato con l'import).

### Posa
- `Arte_Marina_Pontili_PontileCol` 22, `_Pontile12` **50** (era 46), `Arte_Marina_Arredi_Colonnine` **27** (era 28): `clear_instances` +
  `add_instances` dal CSV v3, `Rotator(roll, pitch, yaw)` come in §39. Quote dal CSV: moduli −45, radici −45,5, ultimo modulo prima di un gomito −46.
- **`Arte_Marina_Pontili_Raccordo`** (nuovo, cartella `Arte/Marina/Pontili`): duplicato di `_Pontile12` (HISM `FortStaticMesh`, Query Only,
  Static), mesh `SM_Morin_Marina_Raccordo`, **7 istanze** a Z −47 (Spina_v1/v2/v3/fine, Esterno2_v1/v2, L_Gamba_v1).
- Passerelle (3), `Arte_Marina_PontileLargo`, `Arte_Marina_Circolo`: già identici al CSV v3, non toccati.
- **`Arte_Marina_Pontili_Raccordi` (10 pezzi provvisori) nascosto, non cancellato** (metodo §14): Actor Hidden In Game sì, componente
  Visible falso, Collision Enabled No Collision, Actor Enable Collision no. Per riattivarlo: inverso, profilo Query Only.
- Attori nel livello 379 → **380**.

### Barche: Z −103 → −110
Catture a filo d'acqua (camera 7 m di lato, Z −80): a −103 la fascia rossa emergeva ~10-12 cm su gozzo e motoscafo. Abbassate a **−110** le
461 istanze dei 18 HISM `Arte_Marina_Barche_*` (Gommone, Gozzo, Motoscafo, Vela9, anche `_Prua`); **yacht di Mirabello invariati** (−100).
Dopo: sul galleggiamento resta la riga scura, il rosso si vede solo nel riflesso. Log decisioni in `docs/decisioni.md`.

### Verifiche (editor, nessuna sessione)
- **Line trace** a griglia 10 cm su ogni pezzo del CSV (Pontile12, Pontile_Col, passerelle; fascia ±1 m dall'asse, 60 cm oltre le testate di ogni
  pezzo per coprire giunti, radici e gomiti) = **370.944 punti** + dischi r 1,4 m sui 7 raccordi: **0 buchi veri**. I 233 "buchi" della griglia
  sono campioni esattamente sulle linee di giunzione fra moduli (larghezza 0): riprovati a ±1 cm hanno tutti calpestio. Gradino massimo fra
  campioni vicini **3,2 cm** (piede della passerella, Z 0 → −45), sui raccordi 2,0 cm.
- **Caduta di capsula** (r 34, hh 88) ogni 50 cm su asse e ±60 cm di tutti i pezzi + su tutti i campioni di giunzione + 5 punti per raccordo:
  **10.951 prove, 0 cadute** dentro i pontili; le uniche cadute sono 50 cm oltre le **15 testate** (nessun calpestio nei 3 m successivi).
- **Barche:** profilo Custom / No Collision su tutti i 20 HISM; 9 trace per barca (544): 0 colpi su barche, **0 punti barca sopra un pontile**.
- Validazione `LaSpezia/` + mappa: **860/860 validi, 0 errori, 80 avvisi** (gli stessi di §39: "un solo LOD" su temporanei, largo, circolo,
  blockout). Log: nessun errore; il raccordo e i suoi temporanei passano senza avvisi.
- `save_dirty_packages` 18:45 (23 OFPA: 18 HISM barche, 3 HISM ripopolati, `_Raccordo`, `_Raccordi`; asset su disco 18:40), poi **0 pacchetti sporchi**.

### Catture (`docs/qa/`, 1024 px, ombre, doppio render, stesse camere di §39)
- `uefn_marina_finger_v3.png`: (15600, −1880, 120), yaw 0,8, pitch −1,6, FOV 70.
- `uefn_marina_alto_v3.png`: (7500, −17500, 11000), yaw 56,3, pitch −29, FOV 62.

### Temporanei e problemi aperti
- Temporanei `_Temp/TMPMA_*` ora 46 (+2 del raccordo) e `Arte_Marina_Pontili_Raccordi` nascosto: eliminabili con conferma dell'utente.
- `marina_barche_v2.csv` ha ancora Z −103 per le 4 famiglie nuove: va allineato a −110 al prossimo giro (blender-artist).
- (qa-tester) In sessione: gomiti e radici raccordati, colonnine, barche senza collisione.
