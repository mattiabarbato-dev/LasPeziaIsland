# PLAN — Piazza di La Spezia in Fortnite

Legenda stato: [ ] da fare · [~] in corso · [x] fatto · [!] bloccato

## Fase 0 — Setup e riferimenti
- [ ] (utente) Confermare la piazza: proposta **Piazza Verdi** (alternativa: Piazza Europa / Piazza Garibaldi)
- [ ] (orchestratore) `git init`, creare cartelle ref/ blender/ exports/ docs/, `.gitignore` per file temporanei
- [ ] (geo-scout) Definire il bounding box dell'area (piazza + un isolato di contorno) in lat/lon
- [ ] (geo-scout) Raccogliere riferimenti: elenco edifici affacciati, altezze stimate (n. piani), elementi notevoli
- [ ] (utente) Scattare foto delle facciate e degli elementi notevoli -> ref/foto/

## Fase 1 — Blockout (forme semplici, scala corretta)
- [ ] (blender-artist) Test scala: cubo 1 m -> FBX -> exports/test/
- [ ] (uefn-builder) Importare il cubo di test in UEFN e verificare 100 uu; annotare preset in docs/scala.md
- [ ] (blender-artist) Import OSM con Blosm (edifici + strade) per il bounding box
- [ ] (blender-artist) Pulizia: altezze corrette, terreno piatto, separare edifici in blocchi, export FBX
- [ ] (uefn-builder) Importare i blocchi, posizionarli, verificare percorribilità con una sessione di prova

## Fase 2 — Prototipo di gioco
- [ ] (utente) Scegliere la modalità (es. nascondino, zone wars, caccia al tesoro tra i portici)
- [ ] (verse-dev) Logica base in Verse / device
- [ ] (qa-tester) Prima sessione di test + report

## Fase 3 — Dettaglio
- [ ] Facciate degli edifici affacciati sulla piazza (texture da foto)
- [ ] Elementi notevoli (portali, fontana, aiuole, arredi)
- [ ] Pavimentazione e materiali

## Fase 4 — Ottimizzazione
- [ ] Collisioni UCX_ su tutti gli asset
- [ ] Verifica budget poligoni / memoria ("Dimensioni del progetto" in UEFN)
- [ ] Profilazione con unreal-insights

## Fase 5 — Rilascio
- [ ] docs/CREDITS.md completo
- [ ] (utente) Caricamento in versione privata e test con amici

## Log decisioni
- 
