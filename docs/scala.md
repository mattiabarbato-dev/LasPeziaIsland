# Test di scala Blender -> UEFN

Data: 2026-11-18 · Agente: uefn-builder · Riferimento: CLAUDE.md §3-4

## Esito finale (giro 3): scala OK, assi OK con rotazione −90° Z in export

- Scala (giro 2): `FBX_SCALE_NONE` + `bake_space_transform=True` → il cubo da 1 m misura **100 uu**.
- Assi (giro 3): col preset del giro 2 **più una rotazione di −90° attorno a Z applicata solo in export**
  si ottiene **Blender +X → UE +X, Blender +Y → UE −Y, Blender +Z → UE +Z** (misurato con line trace).
- Cambiare `axis_forward` **non serve**: con `axis_forward='X'` la mappatura resta identica al giro 2,
  perché l'importer UEFN converte dal sistema di assi dichiarato nell'header del file.
- La scelta finale del preset spetta all'orchestratore (task "Decidere gli assi" in `PLAN.md`).

Pulizia UEFN 2026-11-18: asset e attori di test rimossi (4 attori della cartella Outliner `Test`, 5 asset `SM_Test_*`,
cartella asset `LaSpezia/Test`). Gli FBX in `exports/test/` restano su disco e in Git. Le tabelle sotto sono lo storico delle misure.

---

## Script di export

Script ufficiale: `blender/scripts/morin_export.py`. Applica il preset raccomandato (giro 3) e ripristina la scena.

    import sys, importlib, bpy
    sys.path.append(r"C:/Users/matti/Documents/LaSpeziaFortnite/LaSpezia-Fortnite/blender/scripts")
    import morin_export; importlib.reload(morin_export)
    morin_export.export_fbx([bpy.data.objects["SM_Morin_PalmaA"]],
                            "//../exports/vegetazione/SM_Morin_PalmaA.fbx", mode="asset")
    morin_export.export_selected("//../exports/blockout/SM_Blockout_Ponte.fbx", mode="scene")

- `mode="asset"`: per gli asset istanziati. La radice deve avere origine in (0,0,0) world, altrimenti l'export viene rifiutato.
- `mode="scene"`: per i blockout già posati sull'origine comune. Ruota tutto attorno a (0,0,0) world.
- Aggiunge da solo gli `UCX_<Nome>_NN` e avvisa se un mesh non ha UCX. Blocca l'export se le unità non sono METRIC/1.0,
  se il percorso è fuori da `exports/` o se il file esiste già (`overwrite=True` per forzare).
- Stampa e restituisce un report: byte, triangoli per mesh e budget, bbox in metri e bbox prevista in uu.
- Verificato il 2026-11-18: `exports/test/SM_Test_Assi_Script.fbx` ha header, UnitScaleFactor, vertici e indici
  identici a `SM_Test_Assi_RotZm90.fbx` (differenza 0,0). La Lcl Rotation Z vale −89,999989° invece di −90,000009°,
  cioè 2·10⁻⁵ gradi di arrotondamento. Le matrici, la selezione e l'oggetto attivo tornano identici dopo l'export.

---

## Giro 3 — verifica degli assi (SM_Test_AssiX / SM_Test_Assi_RotZm90)

Stessa geometria del giro 2 (cubo 1 m con origine al centro della base, marcatore LUNGO che sporge 40 cm su Blender +X,
marcatore CORTO che sporge 20 cm su Blender +Y, UCX = solo il cubo). Stessa procedura di import del giro 2
(`StaticMeshToolset.ImportFile`, cartella `LaSpezia/Test`, `bCombineMeshes=true`, niente materiali o texture).
In UEFN non è stata applicata nessuna scala o rotazione.

### Contenuto dei file FBX (header letto dal binario)

| File | Preset | Header assi | UnitScaleFactor | Lcl Rotation oggetti |
|---|---|---|---|---|
| `SM_Test_AssiX.fbx` | giro 2 ma `axis_forward='X'` | Up=+Z · Front=−X · Coord=−Y | 1 | nessuna |
| `SM_Test_Assi_RotZm90.fbx` | giro 2 (`axis_forward='-Y'`) + oggetti ruotati −90° Z | Up=+Z · Front=+Y · Coord=−X (come il giro 2) | 1 | (0, 0, −90°) su mesh e UCX |

L'import combina le mesh e incorpora la Lcl Rotation nei vertici dell'asset: l'asset risultante è già ruotato.

### Risultati in UEFN (XYZ nativo)

| Verifica | `SM_Test_AssiX` | `SM_Test_Assi_RotZm90` | Atteso RotZm90 |
|---|---|---|---|
| Bounds locali X | −70..50 | **−50..90** | −50..90 |
| Bounds locali Y | −90..50 | **−70..50** | −70..50 |
| Bounds locali Z | 0..100 | 0..100 | 0..100 |
| Triangoli LOD0 | 36 (72 vertici) | 36 (72 vertici) | 36 |
| Collisione | 1 convesso; trace solo semplice: facce a ±50 in X e Y, top a 100 | idem | 1 primitiva ±50 · 0..100 |
| Mesh UCX separata | nessuna | nessuna | nessuna |
| Materiali | 1 slot `WorldGridMaterial` | idem | — |
| Nanite / collisione | Nanite attivo · Project Default · BlockAll | idem | — |

In `LaSpezia/Test` ora ci sono 5 asset: `SM_Test_Cubo1m`, `SM_Test_Assi`, `SM_Test_AssiCm`, `SM_Test_AssiX`, `SM_Test_Assi_RotZm90`.
Nessun asset esistente è stato sovrascritto.

### Attori di prova (cartella Outliner `Test`, rotazione 0, scala 1, livello salvato)

| Label | XYZ | Bounds in world |
|---|---|---|
| `Test_AssiX` | (3072, −2048, 0) | X 3002..3122 · Y −2138..−1998 · Z 0..100 |
| `Test_Assi_RotZm90` | (3584, −2048, 0) | X 3534..3674 · Y −2118..−1998 · Z 0..100 |

Line trace orizzontali a Z=50 verso il centro dell'attore. "Complessa" colpisce la mesh visibile (anche i marcatori),
"semplice" colpisce solo la collisione UCX.

| Traccia da | `Test_AssiX` complessa (locale) | semplice | `Test_Assi_RotZm90` complessa (locale) | semplice |
|---|---|---|---|---|
| +X | +50 (cubo) | +50 | **+90 (marcatore LUNGO)** | +50 |
| −X | **−70 (marcatore CORTO)** | −50 | −50 (cubo) | −50 |
| +Y | +50 (cubo) | +50 | +50 (cubo) | +50 |
| −Y | **−90 (marcatore LUNGO)** | −50 | **−70 (marcatore CORTO)** | −50 |
| dall'alto | Z 100 | Z 100 | Z 100 | Z 100 |

La collisione semplice è il solo cubo da 100 uu, orientato come la mesh, in entrambi gli asset.

### Mappature misurate

| Blender | `SM_Test_AssiX` (UE XYZ / LUF) | `SM_Test_Assi_RotZm90` (UE XYZ / LUF) |
|---|---|---|
| +X (marcatore lungo) | −Y / +Left | **+X / +Forward** |
| +Y (marcatore corto) | −X / −Forward | **−Y / +Left** |
| +Z | +Z / +Up | +Z / +Up |

### Quale modello dell'importer è confermato

- **Modello "header": confermato.** `SM_Test_AssiX` ha vertici e header diversi dal giro 2, ma dà la stessa identica mappatura
  (B+X → UE −Y, B+Y → UE −X). L'importer converte dal sistema dichiarato nell'header, quindi `axis_forward` cambia il file ma
  non il risultato in UEFN.
- **Modello alternativo** (B+X → −X, B+Y → +Y): **scartato**.
- `SM_Test_Assi_RotZm90` dà B+X → UE +X e B+Y → UE −Y, come previsto da entrambi i modelli.
  La mappatura resta rigida, cioè senza specchio: determinante −1 tra Blender destrorso e Unreal sinistrorso.

### Preset raccomandato

**Preset giro 2 + rotazione −90° Z applicata solo in export.** Nel .blend gli oggetti restano con rotazione 0.
Lo script di export li ruota di −90° attorno a Z (al pivot dell'asset, o all'origine comune se si esporta una scena posizionata),
esporta con il preset sotto e poi ripristina la rotazione. **Va automatizzato con uno script di export** (compito del blender-artist):
farlo a mano è facile da dimenticare e l'errore si vede solo su asset asimmetrici.

### Regola di conversione definitiva Blender → UEFN (col preset raccomandato)

Posizioni (Blender in metri, UE in uu, stessa origine):

    UE_X =  Blender_X × 100
    UE_Y = −Blender_Y × 100
    UE_Z =  Blender_Z × 100

In LUF dell'editor: Forward = Blender_X × 100 · Left = Blender_Y × 100 · Up = Blender_Z × 100.

Rotazione delle istanze attorno a Z: **Yaw UE = −RotZ Blender** (in gradi). Un asset esportato con rotazione 0 e piazzato
con yaw 0 ha la stessa orientazione che ha in Blender.

Esempio: un punto a 10 m lungo la passeggiata e 5 m verso la città (Blender X=10, Y=5) va in UE (1000, −500, 0),
cioè in LUF Forward 1000, Left 500. La passeggiata corre lungo +X di UE (Forward nell'editor), come vuole CLAUDE.md §3,
e la città sta verso −Y di UE (Left nell'editor).

La regola del giro 2 (UE_X = −B_Y·100, UE_Y = −B_X·100) vale solo per FBX esportati **senza** la rotazione −90°:
non mescolare i due tipi di asset nello stesso livello.

---

## Giro 2 — cubo asimmetrico (SM_Test_AssiCm / SM_Test_Assi)

Sorgente: `blender/test_assi.blend`. Geometria in Blender: cubo 1 m (origine al centro della base),
marcatore LUNGO (sporge 0,4 m) sulla faccia Blender +X e marcatore CORTO (sporge 0,2 m) sulla faccia Blender +Y.
Bounds in Blender: X −0,5..0,9 · Y −0,5..0,7 · Z 0..1. Collisione UCX = solo il cubo da 1 m.

Import: `EditorToolset.StaticMeshToolset.ImportFile`, cartella `/705655d7-c848-4957-8e94-8a1c399ddeea/LaSpezia/Test`,
`bCombineMeshes=true`, `bImportMaterials=false`, `bImportTextures=false`. Nessuna scala o rotazione applicata in UEFN.

### Contenuto dei file FBX (letto dal binario)

| File | Preset | UnitScaleFactor | Vertici mesh nel file | Lcl Rotation |
|---|---|---|---|---|
| A `SM_Test_AssiCm.fbx` | `FBX_SCALE_NONE` + `bake_space_transform=True` | 1 | X −90..50 · Y −70..50 · Z 0..100 (cm, X e Y già negati) | nessuna |
| B `SM_Test_Assi.fbx` | `FBX_SCALE_ALL` | 100 | X −0,5..0,9 · Y −0,5..0,7 · Z 0..1 (m) | (0, 0, 180°) |

Header assi, uguale nei due file: UpAxis=Z(+), FrontAxis=Y(+), CoordAxis=X(−).
La rotazione di 180° nasce da `axis_forward='-Y'`: in A è incorporata nei vertici, in B sta nel nodo.

### Risultati in UEFN (XYZ nativo)

| Verifica | A `SM_Test_AssiCm` | B `SM_Test_Assi` |
|---|---|---|
| Bounds locali X | −70..50 | −0,7..0,5 |
| Bounds locali Y | −90..50 | −0,9..0,5 |
| Bounds locali Z | 0..100 | 0..1 |
| Lato del cubo | **100 uu: OK** | 1 uu: KO (×0,01, come previsto) |
| Triangoli LOD0 | 36 (72 vertici): OK | 36: OK |
| Collisione | 1 convesso, 8 vertici, box −50..50 · −50..50 · 0..100: OK | 1 convesso, box ±0,5 · 0..1 (scala KO) |
| Mesh UCX separata | nessuna: OK | nessuna: OK |
| Materiali | 1 slot `WorldGridMaterial` | idem |
| Nanite | attivo (default UEFN) | attivo |

In `LaSpezia/Test` ci sono ora 3 asset: `SM_Test_Cubo1m` (giro 1, intatto), `SM_Test_AssiCm`, `SM_Test_Assi`.

### Attore di prova

- Label `Test_AssiCm`, cartella Outliner `Test`, XYZ (2560, −2048, 0), rotazione 0, scala 1. Salvato.
- Bounds in world: X 2490..2610 · Y −2138..−1998 · Z 0..100, coerenti con l'asset.
- Line trace orizzontali a Z=50 verso il centro dell'attore (la traccia colpisce la collisione complessa, quindi anche i marcatori):

| Traccia da | Colpisce a | Coordinata locale | Lettura |
|---|---|---|---|
| +X | X = 2610 | +50 | faccia del cubo |
| −X | X = 2490 | **−70** | marcatore CORTO |
| +Y | Y = −1998 | +50 | faccia del cubo |
| −Y | Y = −2138 | **−90** | marcatore LUNGO |
| dall'alto | Z = 100 | 100 | faccia superiore |

- Render di controllo: `docs/qa/scala_giro2_dallalto.png` (vista zenitale, in alto = +X UE, a destra = +Y UE: marcatore lungo a sinistra,
  marcatore corto in basso) e `docs/qa/scala_giro2_prospettiva.png`. Riferimento: la griglia del GridPlane, con celle da 512 uu.
  Il cubo occupa circa 1/5 del lato di una cella, quindi è coerente con 100 uu. Nel livello non c'è un personaggio o un manichino.
  Gli spawn pad del template (alti circa 196 uu) sono a 25 m di distanza e non sono stati spostati.

### Mappatura assi misurata (uguale per A e B)

| Blender | UE XYZ nativo | Editor UEFN (LUF) |
|---|---|---|
| +X (marcatore lungo) | **−Y** | **+Left** |
| +Y (marcatore corto) | **−X** | **−Forward** (cioè Back) |
| +Z | +Z | +Up |

Atteso ideale (Blender +X → UE +X, Blender +Y → UE −Y): **non verificato**. Rispetto all'ideale gli assi X e Y sono scambiati.
La mappatura ha determinante −1 tra un sistema destrorso (Blender) e uno sinistrorso (Unreal), quindi è una rotazione:
la mesh **non** è specchiata. Il marcatore che in Blender è "a destra" del marcatore corto resta a destra anche in UEFN.

Spiegazione dedotta: il file A contiene (−X, −Y) di Blender (180° di `axis_forward='-Y'`), e l'importatore UEFN
scambia gli assi del file (UE X = file Y, UE Y = file X), perché converte dal sistema dichiarato nell'header.
In pratica l'asse scelto come `axis_forward` (Blender −Y) diventa il +X di UE.

### Regola di conversione coordinate Blender → UEFN (con il preset attuale)

Posizioni (Blender in metri, UE in uu, stessa origine):

    UE_X = −Blender_Y × 100
    UE_Y = −Blender_X × 100
    UE_Z =  Blender_Z × 100

In LUF dell'editor: Left = Blender_X × 100 · Forward = −Blender_Y × 100 · Up = Blender_Z × 100.

Rotazione di istanze (solo attorno a Z): **Yaw UE = −RotZ Blender** (in gradi).
Un asset esportato da Blender con rotazione 0 si piazza con yaw 0 e arriva già orientato come in Blender
dentro il sistema convertito. Se un oggetto in Blender è ruotato di θ attorno a Z e lo si esporta "pulito" (rotazione applicata
a 0) per istanziarlo, in UEFN va messo a yaw −θ.

Esempio: un punto a 10 m lungo la passeggiata (Blender X=10, Y=0) va in UE (0, −1000, 0).

### Decisione aperta (per l'orchestratore) — superata dal giro 3: l'opzione 2 non funziona, vedi "Preset raccomandato"

CLAUDE.md §3 vuole "X lungo la passeggiata" sia in Blender che in UEFN. Con il preset attuale in UEFN la passeggiata
corre lungo −Y (Left nell'editor). Due strade:
1. **Tenere il preset e la regola sopra.** Funziona già, la scala è verificata. Basta che tutti gli agenti usino la regola per le posizioni.
2. **Giro 3 con `axis_forward='X'`, `axis_up='Z'`** (stesso resto del preset). Ipotesi da verificare: siccome l'asse forward
   di Blender diventa il +X di UE, si dovrebbe ottenere Blender +X → UE +X e Blender +Y → UE −Y, cioè la regola
   UE = (X·100, −Y·100, Z·100). È un'ipotesi, non una misura: va ripetuto il test con il cubo asimmetrico prima di adottarla.

Consiglio la 2, perché costa un solo export e rende le coordinate leggibili. Fino ad allora vale la 1.

### Preset di export Blender definitivo (scala verificata)

| Parametro | Valore |
|---|---|
| Versione | Blender 5.3 |
| `use_selection` | True (Selected Objects) |
| `apply_scale_options` | **`FBX_SCALE_NONE`** ("All Local") |
| `global_scale` | 1.0 |
| `bake_space_transform` | **True** (Apply Transform) |
| `axis_forward` / `axis_up` | `-Y` / `Z` (`X` provato nel giro 3: nessun effetto sul risultato in UEFN) |
| Rotazione in export | **−90° attorno a Z**, applicata solo durante l'export e poi annullata (giro 3, raccomandato) |
| `use_mesh_modifiers` | True (Apply Modifiers) |
| `embed_textures` / `path_mode` | True / `COPY` |
| Scena Blender | `unit_settings.scale_length = 1.0`, oggetti con rotazione 0 e scala 1 applicate |
| Collisione | oggetto `UCX_<NomeMesh>_00` nello stesso FBX; import con `bCombineMeshes=true` |

**Da non usare:** `FBX_SCALE_UNITS` e `FBX_SCALE_ALL` (con `global_scale=1` producono lo stesso file: geometria in metri,
UnitScaleFactor=100, e l'import MCP la legge come centimetri, quindi 1 m = 1 uu).

---

## Giro 1 — cubo simmetrico (SM_Test_Cubo1m)

### Esito: KO (fattore 0,01)

Il cubo da 1 m arriva in UEFN largo **1 uu** invece di 100 uu. Il preset di export attuale
**non** va usato per gli import futuri finché il test non viene ripetuto con esito OK.

## Misure in UEFN

Asset: `/705655d7-c848-4957-8e94-8a1c399ddeea/LaSpezia/Test/SM_Test_Cubo1m` (Esplora contenuti: `LaSpezia/Test`)

| Verifica | Atteso | Misurato | Esito |
|---|---|---|---|
| Bounding box locale | 100 × 100 × 100 uu | X -0,5..0,5 · Y -0,5..0,5 · Z 0..1 = **1 × 1 × 1 uu** | KO (×0,01) |
| Pivot alla base | min Z = 0 | min Z = 0, centrato in X/Y | OK |
| Triangoli LOD0 | 12 | 12 (24 vertici) | OK |
| Collisione | 1 primitiva semplice da UCX | `CollisionPrims = 1`, `SectionsWithCollision = 1`; line trace dall'alto colpisce la faccia superiore | OK |
| Mesh UCX separata | nessuna | nessuna: nella cartella c'è un solo asset | OK |
| Materiali | nessuno importato | 1 slot con `WorldGridMaterial` (predefinito) | OK |

Attore nel livello: label `Test_Cubo1m`, cartella Outliner `Test`, posizione XYZ (2048, -2048, 0),
lontano dai due spawn pad vicini all'origine. Bounds in world: 1 × 1 × 1 uu (coerente con l'asset).
Il confronto visivo con un personaggio o una parete da 384 uu non è stato fatto: a 1 cm il cubo non si vede.

## Diagnosi (letta dall'FBX binario)

- `GlobalSettings.UnitScaleFactor = 100` (l'unità del file dichiarata è il metro)
- Vertici scritti in metri: ±0,5 / 0..1
- `Lcl Scaling` degli oggetti = 1
- L'import tramite `StaticMeshToolset.ImportFile` (FbxFactory) **non applica** la conversione delle
  unità di scena: legge i valori grezzi come centimetri, quindi 1 m diventa 1 uu.

Con `apply_scale_options='FBX_SCALE_UNITS'` Blender mette la conversione delle unità solo nell'header
(UnitScaleFactor) e lascia la geometria in metri. Funziona solo se l'importatore applica
"Convert Scene Unit", che con questo strumento è disattivato e non si può impostare.

### Correzione proposta (lato Blender, da ripetere il test)
Esportare con **`apply_scale_options='FBX_SCALE_ALL'`** ("FBX All"), oppure `'FBX_SCALE_NONE'` ("All Local").
Così Blender applica il ×100 alla geometria o alle trasformazioni, e il file contiene già i centimetri.
Deve restare la scala della scena Blender `unit_settings.scale_length = 1.0`.
Dopo il nuovo export: reimport e verifica 100 uu, **senza scalare in UEFN**.

In alternativa si può reimportare in UEFN con "Convert Scene Unit" attivo (finestra di import manuale o Python).
È sconsigliato perché dipende da un'opzione che i tool MCP non espongono, quindi non è riproducibile.

### Altra anomalia da verificare in Blender
Entrambi gli oggetti (mesh e UCX) hanno nell'FBX `Lcl Rotation = (0, 0, 180°)`.
Sul cubo non si vede perché è simmetrico. Su asset non simmetrici e nella posa con l'origine comune
porterebbe a un'inversione di X e Y. Va controllato se gli oggetti in `blender/test_scala.blend` hanno
una rotazione Z di 180° non applicata, o se nasce dalla conversione degli assi (`axis_forward='-Y'`).
Va risolto prima dell'export del blockout.

Risolta nel giro 2: la rotazione nasce da `axis_forward='-Y'`, gli oggetti in Blender hanno rotazione 0.

## Preset di export Blender del giro 1 (superato, vedi preset definitivo sopra)

| Parametro | Valore usato | Valore proposto |
|---|---|---|
| Versione | Blender 5.3 | — |
| use_selection | True (Selected Objects) | invariato |
| apply_scale_options | `FBX_SCALE_UNITS` | **`FBX_SCALE_ALL`** |
| axis_forward / axis_up | `-Y` / `Z` | da confermare dopo il controllo della rotazione 180° |
| apply modifiers, embed textures, path mode copy | come da CLAUDE.md §4 | invariato |
| Naming collisione | `UCX_<Mesh>_00` | invariato (funziona) |

## Opzioni di import UEFN usate

Strumento: `EditorToolset.StaticMeshToolset.ImportFile`
- `folderPath`: `/705655d7-c848-4957-8e94-8a1c399ddeea/LaSpezia/Test` (radice del progetto = mount `/705655d7-.../`, non `/Game`)
- `assetName`: `SM_Test_Cubo1m`
- `bCombineMeshes`: **true** (l'UCX viene riconosciuto come collisione, non diventa mesh visibile)
- `bImportMaterials`: false · `bImportTextures`: false
- Uniform scale e rotazione: non esposti dallo strumento (default 1,0 e nessuna rotazione). Nessuna conversione delle unità di scena.

Impostazioni che UEFN applica da solo all'import, da tenere a mente:
- Nanite **attivo**, 3 LOD generati, MinLOD su mobile = 2
- `CollisionComplexity` = Simple And Complex · `DefaultCollision` = BlockAll

## Avvertenze per gli import futuri

- **Coordinate:** l'editor mostra all'utente le posizioni in LUF (Left-Up-Forward, convenzione Verse).
  I tool MCP lavorano invece in XYZ nativo Unreal (X avanti, Y destra, Z su), senza conversione.
  Le coordinate di Blender (X lungo la passeggiata, Y verso la città, Z su) vanno passate ai tool in XYZ.
  Blender è destrorso, Unreal sinistrorso. Verificato nei giri 2 e 3 con un asset asimmetrico: col preset raccomandato
  (rotazione −90° Z in export) vale UE = (B_X·100, −B_Y·100, B_Z·100) e yaw UE = −rotZ Blender (vedi giro 3).
- I piani griglia del template stanno a Z = 0 (faccia superiore): la quota del camminamento coincide con Z = 0.
- Gli spawn pad del template sono a ±378 uu dall'origine. L'origine è riservata all'imbocco del ponte,
  quindi gli spawn andranno spostati quando arriverà il blockout.
