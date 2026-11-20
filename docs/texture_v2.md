# Texture v2: passaggio per il realismo (2026-11-20)

Richiesta dell'utente: "migliorare le texture e rendere il tutto più realistico". Diagnosi di partenza: `docs/uefn_arte.md` §35.D e §36.
Script: `blender/scripts/morin_texture_v2.py` (`make_all()` rigenera tutto, ~20 min; `confronto_render()` rifà il render).
Texture: `blender/textures/v2/`. Sorgenti Poly Haven (CC0) scaricate in `blender/textures/src/<asset>/` (jpg 2k o 4k: diff, nor_gl, rough, ao, disp).
File Blender del confronto: `blender/arte_texture_v2.blend`. Render prima/dopo: `docs/qa/arte_texture_v2_confronto.png`.

Convenzioni, uguali alla v1: D in sRGB; N in formato **DirectX** (verde invertito: in UEFN non serve *Flip Green*); ORM con R = AO,
G = Roughness, B = Metallic (sRGB off, compressione Masks). I valori di albedo qui sotto sono medie dei pixel sRGB salvati (0-255).
Nessuna texture contiene pixel delle foto dell'utente o di Street View: le foto sono servite solo per tarare colore e scala (niente marca [SV]).

## Elenco

"Tile" è il numero di metri coperti da una ripetizione della texture. Per le MI su `M_Morin_Master_Pav` va in `Tile_m`; per le MI su
`M_Morin_Master_PBR` lo decidono le UV della mesh: la v2 copre gli stessi metri della v1, quindi `UV_Tiling` resta 1.

| Texture (`_D/_N/_ORM`) | MI di destinazione | Ris. | Fonte (licenza) | Tile | Albedo medio | Roughness (5-95 %) | Parametri MI consigliati |
|---|---|---|---|---|---|---|---|
| `T_Pav_Lastre_v2` | `MI_Pav_Lastre` | 4096 | procedurale (layout 40 × 60 cm, 12 × 8 lastre, corsi lungo Y) + grana di `rock_surface` (PH, CC0) per lastra | **4,8 m** (era 3,2) | 147/142/133 | 0,84 (0,73-0,95) | `Tile_m` **4,8**, `Tinta` 1, `Roughness_Mult` 1,0, macro 0,35 |
| `T_Pav_Cubetti_v2` | `MI_Pav_Cubetti` | 4096 | `patterned_cobblestone` (PH, CC0, 2,5 m, porfido a ventagli) ritarato | **2,8 m** (cubetto ~9 cm, ventaglio ~1,3 m) | 118/109/101 | 0,80 (0,70-0,90) | `Tile_m` **2,8**, `Tinta` 1, `Roughness_Mult` 1,0, macro 0,30 |
| `T_Pav_Fascia_v2` | `MI_Pav_Fascia` (fasce, cordoli, piedistalli) | 2048 | `rock_boulder_dry` (PH, CC0) ritarato, sporco procedurale | **2,0 m** (era 1,0) | 176/170/159 | 0,70 (0,61-0,80) | `Tile_m` **2,0**, `Roughness_Mult` 1,0, macro 0,25 |
| `T_Banchina_Blocchi_v2` | `MI_Banchina_Blocchi` (ciglio v2, angolo Molo Italia) | 2048 | layout v1 + grana `rock_boulder_dry` (CC0) | UV ~2,5 m (come v1) | 173/171/163 (era 194/191/186) | 0,80 (0,70-0,90) | `UV_Tiling` 1, `Roughness_Mult` 1,0, macro 0,25 |
| `T_Morin_Prato_v2` | `MI_Morin_Prato`, `MI_Morin_Prato_Mondo` | 2048 | fili procedurali v1 + `leafy_grass` (CC0) ×2, chiazze di trifoglio e secco, margheritine | 4 m (come v1) | 80/103/45 (era 94/120/51, lime) | 0,88 | `UV_Tiling` 1 / `Tile_m` 4, `Roughness_Mult` 1,0, macro **0,45** |
| `T_Parcheggio_Asfalto_v2` | `MI_Parcheggio_Asfalto` (parcheggio, `SM_Mirabello_Suolo`) | 4096 | `asphalt_04` (PH, CC0, 4,04 m) ×2, rattoppi morbidi, macchie d'olio | 8 m (come v1) | 92/90/87 | 0,86 (0,74-0,96) | `UV_Tiling` 1, `Roughness_Mult` 1,0, macro 0,35 |
| `T_Molo_Asfalto_v2` | `MI_Molo_Asfalto` (molo, Viale Italia, Molo Italia) | 4096 | `asphalt_04` (CC0) ×1 | 4 m (come v1) | 87/86/83 | 0,86 (0,75-0,95) | `UV_Tiling` 1, `Roughness_Mult` 1,0, macro 0,35 |
| `T_MoloItalia_Cemento_v2` | `MI_MoloItalia_Cemento` | 4096 | `dirty_concrete` (PH, CC0, 3 m → 4 m) | 4 m (come v1) | 161/158/150 (era 179/173/163); niente griglia di piastrelle | 0,86 (0,78-0,95) | `UV_Tiling` 1, `Roughness_Mult` 1,0, macro 0,30 |
| `T_Molo_Scogliera_v2` | `MI_Molo_Scogliera` | 2048 (era 1024) | `seaside_rock` (PH, CC0, 2 m → 2,5 m); fascia di alghe v < 0,12 e bagnato fino a v 0,26 come v1 | UV ~2,5-2,9 m (come v1) | 121/114/100 | 0,76 (0,42 bagnato - 0,93) | `UV_Tiling` 1, `Roughness_Mult` 1,0, macro 0,20 |
| `T_Morin_Corten_v2` | `MI_Morin_Corten` (scritta LA SPEZIA, Redamare) | 2048 (era 1024) | `rust_coarse_01` (PH, CC0): ritaglio di 1 m tileable, rampa bruno → arancio, chiazze, colature | UV 1 m (come v1) | 118/62/33 | 0,84 (0,75-0,93) | `UV_Tiling` 1, `Roughness_Mult` 1,0, metallic 0, macro 0 |
| `T_Ponte_Legno_v2` | `MI_Ponte_Legno` | 4096 | layout v1 identico (44 doghe, viti, borchie) + grana di `wood_planks_grey` (PH, CC0) per segmento di doga | 6 m (come v1) | 108/104/96, tinta per doga ±8 %, 10 % più scure, 8 % argentate | 0,80 (0,73-0,93); borchie 0,35 metal 0,85 | `UV_Tiling` 1, `Roughness_Mult` 1,0, macro 0,20 |
| `T_Ponte_Acciaio_v2` | `MI_Ponte_Acciaio` | 4096 | v1 ritarata (stesso layout) | 4 m (come v1) | **190/190/185** (era 250), max 205 | **0,32** (0,25-0,40) | `UV_Tiling` 1, `Roughness_Mult` **0,9** (vernice semi-lucida), macro 0 |
| `T_Morin_NewJersey_v2` | `MI_Morin_NewJersey` | 2048 (era 1024) | layout v1 + grana `dirty_concrete` (CC0) | u 2 m, v profilo (come v1) | 158/155/146 (era 184/184/173) | 0,88 | `UV_Tiling` 1, `Roughness_Mult` 1,0 |
| `T_Banchina_Paramento_v2` | `MI_Banchina_Paramento` (banchina, ponte, Molo Italia) | 2048 | layout v1 + grana `seaside_rock` (CC0), alghe a chiazze | UV ~3,3 m (come v1) | 86/84/78 (era 59/59/59) | 0,77 (0,66-0,85) | `UV_Tiling` 1, `Roughness_Mult` 1,0, macro 0,25 |
| `T_Morin_PalmaA_Tronco_v2` | `MI_Morin_PalmaA_Tronco` | 2048 | atlante v1 schiarito e desaturato (N = v1) | atlante | 119/104/88 (era 89/71/56) | 0,90 | `Roughness_Mult` 1,0 |
| `T_Morin_PinoDomestico_Corteccia_v2` | `MI_Morin_PinoDomestico_Corteccia` | 2048 (era 1024) | `pine_bark` (PH, CC0): u = 1 m (ritaglio tileable), v = 2 m | u 1 m × v 2 m (come v1) | 110/86/71 | 0,88 | `UV_Tiling` 1, `Roughness_Mult` 1,0 |
| `T_Albero_Latifoglia_Chioma_v2` (RGBA) | `MI_Albero_Latifoglia_Chioma` (Masked) | 2048 | atlante v1: alfa invariata, foglie schiarite e variate, RGB esteso fuori dall'alfa (push-pull) | atlante | 85/101/45 | 0,75 | `Roughness_Mult` 1,0; nella texture **sRGB on**, compressione default (alfa) |
| `T_Morin_Auto_v3_D` / `_ORM` (N ed E: quelle v2) | `MI_Morin_Auto_v2`, `MI_Morin_Auto_v2_Luci` | 2048 | atlante v2: vernice (37 % dei pixel) roughness 0,13 ± 0,03 e metallic × 0,35; albedo compresso sopra 0,72 (bianchi ~0,78) | atlante | — | vernice 0,13 | `Roughness_Mult` 1,0 (per più lucido 0,8) |
| `T_Morin_MacroVar` (solo `.png`, grigio) | vedi sotto | 2048 | rumore procedurale | **32 m** | media 0,50 (5-95 %: 0,30-0,73) | — | — |

Totale: 18 set (53 PNG) + `T_Morin_MacroVar`. Nove set a 4096 (lastre, cubetti, asfalti, cemento, legno e acciaio del ponte).

## Macro-variazione `T_Morin_MacroVar` (da aggiungere ai master in UEFN)

Rumore morbido a 4 ottave (chiazze da ~2 a ~15 m) più qualche chiazza più scura; media 0,5. Si legge in **coordinate mondo**, così
non dipende dalle UV e rompe la ripetizione di ogni tile:

```
UVmacro   = WorldPosition.xy / 3200          (32 m)
M         = T_Morin_MacroVar(UVmacro).r
BaseColor = BaseColor * lerp(1, 2*M, Macro_Int)        // M = 0,5 -> invariato
Roughness = saturate(Roughness * Roughness_Mult + (M - 0.5) * 0.3 * Macro_Int)
```

Parametro scalare nuovo `Macro_Int` (default 0) nei master `M_Morin_Master_PBR` e `M_Morin_Master_Pav`; texture `T_Morin_MacroVar` con
sRGB **off**, compressione Grayscale/Masks, mip normali. Intensità consigliate (colonna "macro" della tabella): prato 0,45; lastre, asfalti 0,35;
cubetti, cemento 0,30; fascia, blocchi, paramento 0,25; legno del ponte, scogliera 0,20; corten, acciaio, auto, alberi 0.
Per le mesh istanziate (palme, auto) la coordinata mondo cambierebbe tinta istanza per istanza: lì non serve (intensità 0).
Nel render di confronto la colonna "dopo" ha la macro-variazione applicata con queste intensità.

## Roughness_Mult per le MI non rifatte
Le v2 hanno la roughness già tarata (Roughness_Mult 1,0, salvo acciaio 0,9). Per le MI che restano sulle texture v1:
`MI_Morin_Auto_v2` se non si ricollega la v3 → 0,6; `MI_Ponte_Cavo` 0,9; `MI_Banchina_Ghisa` / `MI_Morin_Ghisa` 1,0;
`MI_Molo_Masselli` 1,1; `MI_Banchina_Ciglio` (v1, non più usata dal ciglio v2) 1,2.

## Render di confronto
`docs/qa/arte_texture_v2_confronto.png`: a sinistra v1, a destra v2; righe dall'alto: lastre, cubetti, fascia, blocchi del ciglio, prato,
asfalto del parcheggio. Piano 40 × 40 m, occhio a 1,7 m, sole caldo (1; 0,86; 0,70) a 23° di elevazione, EEVEE, vista Standard.
Note: lastre più fredde e grigie, giunti con rilievo, nessuna macchia ripetuta ogni 3,2 m (resta una variazione per lastra marcata, come
in `pav_1.png`); cubetti di porfido reali, grigio-bruni, ventagli più piccoli; fascia di pietra opaca e sporca invece del bianco
lucido con riflesso; blocchi meno bianchi e senza riflesso a specchio; prato meno lime con trifoglio e chiazze secche; asfalto più fine,
senza i rettangoli scuri ripetuti.

## Cosa resta (uefn-builder)
1. Importare i PNG di `blender/textures/v2/` in `Arte/Texture_v2` (D sRGB; N Normalmap; ORM e MacroVar Masks, sRGB off;
   la chioma RGBA con alfa), **nomi nuovi**, nessun reimport sulle v1.
2. Ricollegare le MI della tabella alle v2 e impostare `Tile_m` (lastre 4,8, cubetti 2,8, fascia 2,0) e `Roughness_Mult`.
3. Aggiungere `Macro_Int` + `T_Morin_MacroVar` ai due master (formula sopra) e impostare le intensità.
4. Memoria: nove set 4096 (~27 texture da 4k) pesano ~350-450 MB in VRAM compressi con le mip: controllare "Dimensioni del progetto"
   dopo l'import. Se serve, scendere a 2048 per cemento e asfalto del molo (meno vicini all'occhio).
5. Catture `RenderLevelPOVs` agli stessi 10 punti del §35.D per il confronto in gioco.

## Seguito: texture v3 (2026-11-20)
Legno del ponte, segnaletica, cubetti e prato sono stati rifatti in `blender/textures/v3/`: vedi `docs/texture_v3.md` (nuovi parametri MI
per `MI_Ponte_Legno`, `MI_Viale_Segnaletica`, `MI_Pav_Cubetti`, `MI_Morin_Prato`, `MI_Morin_Prato_Mondo`).
