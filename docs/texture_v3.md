# Texture v3: migliorie rimaste dal passaggio v2 (2026-11-20)

Richiesta: i punti aperti del §38 di `docs/uefn_arte.md` (legno del ponte quasi uguale alla v1, strisce pedonali mai rifatte, ventagli dei
cubetti che si ripetono sui piazzali, prato uniforme da lontano). Script `blender/scripts/morin_texture_v3.py` (`make_all()` ~6 min,
`confronto_render()`); texture in `blender/textures/v3/`; file del confronto `blender/arte_texture_v3.blend`;
render `docs/qa/arte_texture_v3_confronto.png` (a sinistra la versione in uso, a destra la nuova; righe: legno, strisce, cubetti, prato).
Convenzioni come la v2 (`docs/texture_v2.md`): D sRGB; N **DirectX** (nessun *Flip Green*); ORM = AO/Roughness/Metallic, sRGB off, Masks.
Fonti: Poly Haven CC0 già scaricate (`wood_planks_grey`, `asphalt_04`, `patterned_cobblestone`) e le v2 del prato; le foto dell'utente solo per
tarare colore, scala e disposizione (nessun pixel copiato, niente [SV]). Nessuna texture v1 o v2 sovrascritta: nomi nuovi.

## Elenco e parametri MI

| Texture (`_D/_N/_ORM`) | MI | Ris. | Tile | Albedo medio | Roughness (5-95 %) | Parametri MI consigliati |
|---|---|---|---|---|---|---|
| `T_Ponte_Legno_v3` | `MI_Ponte_Legno` | 4096 | 6 m (UV del ponte, come v1/v2) | 103/100/95 | 0,80 (0,69-0,94) | `UV_Tiling` 1, `Roughness_Mult` 1,0, `Macro_Int` **0,15** |
| `T_Viale_Segnaletica_v2` | `MI_Viale_Segnaletica` | 2048 | **2 m** (la mesh ha UV in metri) | 203/201/193 | 0,64 (0,58-0,86) | **`UV_Tiling` 0,5**, `Roughness_Mult` 1,0, `Macro_Int` 0 |
| `T_Pav_Cubetti_v3` | `MI_Pav_Cubetti` | 4096 | **5,6 m** | 115/106/97 (v2 118/109/101) | 0,80 (0,69-0,90) | **`Tile_m` 5,6**, `Tinta` invariata (0,97; 0,94; 0,90), `Roughness_Mult` 1,0, `Macro_Int` **0,35** |
| `T_Morin_Prato_v3` | `MI_Morin_Prato` / `MI_Morin_Prato_Mondo` | 4096 | **8 m** | 80/103/41 | 0,87 (0,80-0,93) | **`UV_Tiling` 0,5** (PBR) / **`Tile_m` 8** (Pav), `Roughness_Mult` 1,0, `Macro_Int` **0,6** con `MacroVar` = `T_Morin_Prato_MacroVar` |
| `T_Morin_Prato_MacroVar` (solo `.png`, grigio) | parametro texture `MacroVar` delle due MI del prato | 2048 | 32 m (coord. mondo, come `T_Morin_MacroVar`) | media 0,50 (5-95 %: 0,20-0,76; la generale: 0,30-0,73) | — | sRGB off, Grayscale/Masks |

### 1. Legno del ponte `T_Ponte_Legno_v3`
- **Doghe trasversali** (perpendicolari all'asse del ponte), come nelle foto `ref/foto/ponte/ponte1.png` e `ponte_verso_passegiata.png`:
  la v1/v2 le aveva longitudinali. 48 doghe da 12,5 cm per tile, giunto continuo sull'asse (u 0,5, la riga chiara in mezzo alle foto),
  il 18 % con un secondo giunto (riparazione).
- **Due file di borchie** metalliche (Ø 3,4 cm, metallic 0,85, roughness 0,38) a ±1,0 m dall'asse, una per doga (in foto le due "linee
  di puntini" che vanno verso il pennone); viti scure sulle travi (asse e bordi).
- Variazione per doga ±11 %, 12 % doghe più scure (sostituite/umide), 8 % più brune, 10 % argentate; grana di `wood_planks_grey` (CC0)
  orientata lungo la doga.
- **Usura sulla linea di passaggio** (gaussiana larga 1,3 m al centro): grana meno marcata, legno un po' più scuro e caldo (sporco delle
  scarpe), roughness 0,66 al centro contro 0,84 ai lati; bordi argentati e sporco verdastro contro i cordoli.
- Tinta: grigio-bruno quasi neutro (R−B = 8), più vicina alla foto (118/116/112 al sole) della v2 (108/104/96, più bruna).
- Le UV del ponte non cambiano: u = attraverso l'impalcato (6 m, centro u 0,5), v = lungo il ponte. Se in UEFN le doghe risultassero
  **longitudinali**, le UV della mesh sono ruotate rispetto a `morin_ponte.py`: dirlo a blender-artist (non ruotare in MI).

### 2. Segnaletica `T_Viale_Segnaletica_v2`
Vernice bianco sporco (226/225/216) su `asphalt_04` (CC0) ritagliato a 2 m e reso periodico. Copertura ~75 %: consumata a chiazze
(gli inerti escono prima, bordo frastagliato), screpolature larghe (celle ~15 cm, a tratti) e fini (~4 cm, solo vicino all'usura),
scaglie mancanti dove è già consumata, residui bianchi negli avvallamenti, sporco grigio. Vernice in rilievo 0,4 mm, roughness 0,58-0,7;
asfalto 0,86. Con `UV_Tiling` 0,5 copre 2 m: le strisce pedonali da 4 m mostrano due ripetizioni diverse per l'usura a grande scala.

### 3. Cubetti `T_Pav_Cubetti_v3`: la soluzione scelta
Ho scelto il **tile più grande** e non una seconda texture da miscelare: la ripetizione visibile è nella *forma* dei ventagli e nei singoli
cubetti riconoscibili, che una texture di colore sopra non rompe; e non serve toccare il master.
- 2 × 2 ventagli di `patterned_cobblestone` su 5,6 m (stessa scala della v2: cubetto ~9 cm, ventaglio ~1,3 m), **deformati** con un campo
  morbido periodico (±6 cm, due ottave): archi irregolari come nella posa a mano, i quattro quadranti non sono più uguali.
- **Tinta per cubetto** (segmentazione dei cubetti dall'altezza, ±13 % di luminosità, ±3,5 % rosso/grigio, ±4 % roughness), chiazze a media
  scala (0,5-2 m), sporco terroso variabile nelle fughe, poche macchie scure, zone impolverate.
- Risoluzione: 731 px/m (la v2 1463 px/m a 2,8 m); il cubetto resta di ~66 px, sufficiente anche da vicino.
- La macro-variazione (32 m) resta e va un po' più su: **`Macro_Int` 0,35** (era 0,30).

### 4. Prato `T_Morin_Prato_v3` + `T_Morin_Prato_MacroVar`
- Tile **8 m** (stessa densità della v2: 512 px/m). Base: la v2 ripetuta 2 × 2 e mescolata con sé stessa traslata di 2 m attraverso una
  maschera morbida (niente ripetizione esatta a 4 m).
- Variazione a media scala unica su 8 m: zone **fitte** (più scure e sature, rilievo della normal più forte), zone **rade** (più chiare,
  giallo-verdi, terra che affiora a puntini), chiazze di trifoglio più scuro, macchie secche.
- **Seconda macro solo per il prato**: `T_Morin_Prato_MacroVar` (32 m, coordinate mondo) ha chiazze più contrastate (3-12 m) e qualche
  zona più chiara. Non serve cambiare il master: il parametro texture `MacroVar` esiste già in `M_Morin_Master_PBR` e `M_Morin_Master_Pav`
  (§38.C), basta **sovrascriverlo nelle due MI del prato** e portare `Macro_Int` a **0,6** (era 0,45). Con 0,6 la luminosità del prato
  varia di circa ±20 % fra le chiazze (5-95 %).
- Alternativa senza la seconda texture: `Macro_Int` 0,6 con la `T_Morin_MacroVar` generale (variazione ±14 %, più morbida).

## Cosa fare in UEFN (uefn-builder)
1. Importare i 13 PNG di `blender/textures/v3/` in `LaSpezia/Arte/Texture_v3` col metodo del §38.B (una texture alla volta, impostazioni una
   proprietà alla volta): D sRGB, Compress Without Alpha; N Normalmap; ORM e `T_Morin_Prato_MacroVar` Masks, sRGB off; LODBias 0.
2. Ricollegare e impostare le MI secondo la tabella. Valori attuali da annotare prima (per tornare indietro): `MI_Ponte_Legno` → v2, macro 0,2;
   `MI_Viale_Segnaletica` → `Viale/T_Viale_Segnaletica`, `UV_Tiling` 1; `MI_Pav_Cubetti` → v2, `Tile_m` 2,8, macro 0,3;
   `MI_Morin_Prato`/`_Mondo` → v2, `UV_Tiling` 1 / `Tile_m` 4, macro 0,45, `MacroVar` = `T_Morin_MacroVar`.
3. Catture agli stessi punti del §35.D (06 ponte, 01/03 pavimentazione e giardini, extra_12 cubetti dell'incrocio, una strisce pedonali del viale).
4. Memoria: 3 set 4096 + 1 set 2048 + la macro del prato, ~+130 MiB con le mip se tutti residenti (stima col metodo del §38.F); le texture
   sostituite (legno, cubetti e prato v2, segnaletica v1) non sono più referenziate dalle MI. Controllare "Budget memoria mappa" dopo la sessione.
