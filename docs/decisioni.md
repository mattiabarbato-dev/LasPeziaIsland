# Log decisioni — Morin Rush

Deroghe alla scala reale, scelte di design e cambi di piano. Il riepilogo breve resta in `PLAN.md`.

| Data | Decisione | Motivo | Chi |
|---|---|---|---|
| 2026-11-18 | Soggetto: Passeggiata Morin invece di Piazza Verdi | Scelta dell'utente | utente |
| 2026-11-18 | Primo blocco: ponte + ~250 m | Tratto più riconoscibile, dimensione gestibile | utente |
| 2026-11-18 | Stile Fortnite stilizzato, niente fotogrammetria | Licenze, prestazioni, coerenza visiva | utente |
| 2026-11-18 | Impalcato del ponte allargato da 3,6 m (reale) a 5-6 m nel gioco | Regola CLAUDE.md §3 (< 4 m), pilastro 3 | orchestratore |
| 2026-11-18 | Export FBX: `FBX_SCALE_NONE` + `bake_space_transform=True` (non "FBX Units Scale") | Test di scala: con FBX_SCALE_UNITS/ALL il cubo arriva a 1 uu; vedi `docs/scala.md` | utente (CLAUDE.md §4 aggiornato) |
| 2026-11-18 | Assi: preset sopra + rotazione −90° Z solo in export → Blender +X = UE +X, Blender +Y = UE −Y | Giro 3 misurato in UEFN; rispetta CLAUDE.md §3 (passeggiata lungo X); `axis_forward='X'` provato e inefficace | utente (giro 3) |
| 2026-11-18 | Blockout: impalcato 6 m, anelli ai pennoni resi come allargamento a 8 m (Y ±4,5 m attorno al pennone, raccordi da 3 m) con il pennone al centro: due corsie da ~3,5 m ai lati | Versione semplice della biforcazione reale (anello OSM ~6,5 m); passaggi secondari >= 3 m (CLAUDE.md §3) | blender-artist |
| 2026-11-18 | Quote del ponte [S]: acqua Z −1,5; calpestio massimo Z 4,3 (= 5,8 m s.l.m.) da Y −70 a Y −136,1; rampa d'accesso Y 0 → −70 al 6,1 %; discesa verso Mirabello al 7,0 % (Z 1,30 a Y −179) | Da `ref/ponte.md` (intradosso 5 m + travi): pendenze <= 7 %, niente gradini | blender-artist |
| 2026-11-18 | Scala finale di Mirabello (14 gradini, ~2,3 m) sostituita da una rampa al 7 %: il ponte scende già fino a Z 1,30 e la rampa `SM_Blockout_Mirabello_Rampa` (6 m × 18,5 m) arriva a Z 0 a Y −197,5 | Pilastro 3: niente gradini > 40 cm senza rampa. Il ponte reale finisce in quota a ~2,3 m; nel gioco l'ultimo tratto scende di più | blender-artist |
| 2026-11-18 | Testata Mirabello a Z 0 (= quota banchina, [S]), 30 × 49,4 m (X −20,2..9,8, Y −168..−217,4): zona traguardo di 30 × 20 m oltre il piede della rampa | Quota del suolo di Mirabello non nota: stessa quota della banchina; il parcheggio di fondale è arretrato a Y < −218 | blender-artist |
| 2026-11-18 | Rampa lato Revel (Y 0 → −70) piena fino al molo e spalla piena sotto il ponte a Mirabello (Y −168..−179) | Evita fessure basse tra impalcato e suolo dove il giocatore si incastra (pilastro 3) | blender-artist |
| 2026-11-18 | Giardini a Mare: aiuole alte 0,4 m (fronte, Y 102-107) e 0,3 m (retro, Y 111-116), vialetto a Z 0 largo 4 m (Y 107-111) come percorso alternativo, 4 varchi da 4 m verso la corsia (X 58-62, 118-122, 178-182, 228-232), siepe di limite alta 1,5 m a Y 116-118 | Richiesta del task (>= 2 varchi da >= 3 m), gradini <= 40 cm | blender-artist |
| 2026-11-18 | Palme segnaposto: 2 filari a Y 92,6 e 99,6, passo 9 m [S], sfalsati di 4,5 m (F1 da X 12, F2 da X 16,5), fino a X 250: 53 palme | Passo e disposizione non noti (`ref/sezione.md` §3): proposta da confermare con foto | blender-artist |
| 2026-11-18 | Acqua del golfo con il **device Acqua V2** (volume a scatola, superficie Z −150) invece di un Water Body Lake/Ocean nativo | Il WaterBodyLake piazzato dall'editor referenzia asset `/Water/` che il validatore UEFN segnala come illegali (isola non caricabile); il device è supportato, leggero e senza onde | uefn-builder |
| 2026-11-18 | Blockout UEFN: LOD automatiche rimosse (solo LOD0), Nanite off | Mesh già low-poly; con MinLOD 2 su Low/Medium il mobile avrebbe mostrato LOD dimezzate e bucate | uefn-builder |
| 2026-11-18 | GridPlane del template spostati a Z −10000 (non cancellati) | A Z 0 coprivano il mare sotto il ponte e davanti al molo; la cancellazione la decide l'utente | uefn-builder |
| 2026-11-18 | Barriere invisibili: base a Z −700 e alte 38 m; quella di fine blocco e i lati di Mirabello entrano 10 m in mare | Impedire di aggirarle a nuoto lungo la banchina; lato mare per il resto aperto | uefn-builder |
| 2026-11-18 | Fondale: un box orientato per edificio OSM (47). Altezze Blosm (casuali per building=yes) ridotte a 6 m sul molo e a 8 m nell'area militare, tettoia 4 m, capannone 6 m; chiosco dei Giardini a Mare escluso (diventerà prop) | Edifici bassi sul molo 4-7 m [S] (`ref/elementi.md`) | blender-artist |
| 2026-11-19 | CLAUDE.md §2.2 e §4: l'acqua è il device Acqua V2, non più il Water Body nativo | Conferma dell'utente alla scelta di uefn-builder del 2026-11-18 (validatore UEFN) | utente |
| 2026-11-19 | Island Settings: costruzione disattivata (Nessuno) | Corsa a tempo: percorso uguale per tutti, niente scorciatoie costruite | utente |
| 2026-11-19 | Scatto attivo | Stima 80-84 s con scatto (dentro 60-90 s) contro 112-118 s senza | utente |
