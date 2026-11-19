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
4. **(blender-artist)** Mesh di pavimentazione: la fascia delle palme oggi mostra lastre (slot Pietra unico del blockout, ora sulla copia
   `SM_Blockout_Passeggiata_Arte`). Con la mesh dedicata si ripunta l'attore e si toglie l'offset Z +2,5 dei moduli.
5. **(utente)** Impostare il percorso del Mali Offline Compiler per avere `GetCost`.
6. **(qa-tester, in sessione)** Palme e bitte HISM visibili e solide in gioco; risalita dalle scalette; nuoto con l'acqua a −1 m;
   rilettura di Project Size e memoria dopo la cottura.
7. I materiali `M_Banchina_*`/`M_Morin_PalmaA_*` creati dall'import FBX non sono usati: si possono eliminare (serve conferma).
