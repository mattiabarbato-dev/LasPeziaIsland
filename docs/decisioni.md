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
