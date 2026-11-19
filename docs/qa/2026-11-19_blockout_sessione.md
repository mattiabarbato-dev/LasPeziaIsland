# QA — Prova in sessione del blockout (Blocco 1)

Data: 2026-11-19 · Agente: qa-tester · Livello: `LasPezia_Island` · Seguito di `2026-11-18_blockout_percorrenza.md`
Coordinate in XYZ nativo Unreal (X avanti, Y destra, Z su). Nessuna modifica a livello, asset o codice.

## Sintesi

**La sessione parte.** Con la regione di matchmaking impostata su Europa il matchmaking riesce (niente più `invalid_region`):
sessione assegnata, client avviato, contenuto caricato in ~28 s, partita in corso, personaggio in gioco alla partenza.
Nel log client non c'è nessun errore legato ai contenuti dell'isola.

**Quasi tutti i controlli in gioco però non si possono fare via MCP.** Il client Fortnite non registra gli strumenti MCP:
nel suo log, ogni 10 s, compare `LogLiveEditObject: Error: Request function is not registered for ReceivedMessage(): 'MCPListToolsets'`
e `BeaconClientsToolset.ListClients` restituisce sempre una lista vuota. Di conseguenza `FortPlayerToolset.GetLocalPlayerState`
risponde "No game viewport world is running" e `SceneCaptureToolset.CaptureGameViewport` non vede il mondo del client.
In ogni caso `FortPlayerToolset` legge soltanto: non ha comandi per muovere il giocatore.
Non ho mandato input simulati (tastiera o mouse) alla finestra del gioco. L'unica osservazione diretta è uno screenshot
della finestra del client (PrintWindow), `docs/qa/qa_sessione_spawn_partenza.png`.

| # | Voce (§ del report 2026-11-18) | Esito |
|---|---|---|
| 1 | Avvio della sessione e log client | **Verificato in sessione: OK** |
| 1b | Spawn alla partenza, orientamento verso il ponte | **Verificato in sessione (screenshot): OK**. Posizione numerica non leggibile |
| 2 | Palme HISM visibili e con collisione | **Non verificabile** via MCP (nello screenshot la fascia verde è coperta dal menu) |
| 3 | Tempo partenza → fine ponte e → traguardo | **Non verificabile**: serve muovere il giocatore. Nessun tempo misurato |
| 6 | Caduta in acqua, nuoto, risalita sul ciglio | **Non verificabile** |
| 7 | Scala con il personaggio accanto a parapetti e palme | **Parziale**: il personaggio sul camminamento ha proporzioni credibili. Parapetti e palme non inquadrati |
| 8 | Barriere attive (lato città, fine blocco anche a nuoto, Mirabello) | **Non verificabile** |
| — | Costruzione disattivata | **Non verificabile in gioco** (impostazione confermata solo in editor) |
| — | Nuovo: ciclo giorno/notte attivo, in sessione è notte | **KO (estetica, bassa)**, vedi sotto |

## 1. Avvio della sessione — OK

- Sequenza dal log dell'editor (`LogValkyrieActivityTracker`), 2026-11-19 04:36:13 → 04:37:33 UTC:
  Matchmaking → QueryEncryptionKey → QueryUserSessionIdToken → ConnectToBeacon → invio contenuto → LoadingNewContent →
  client pronto (`MapLoadTime_Checkpoint_ReadyToStartMatch`, durata 23,5 s). Il matchmaking assegna un server DE
  (stato `Finished`, `bSuccess: 1`): l'errore `invalid_region` è risolto.
- **Nota sul comando:** quando ho chiamato `StartSession` (04:36:15) un avvio era già in corso, partito alle 04:36:13,
  e il tool ha risposto "The Play command is not currently available". Poi la sessione ha completato l'avvio da sola.
  `GetGameState` era già `Running` e `StartGame` ha risposto "The match is not in a startable state": la partita parte
  da sola con la sessione. Nessuna finestra di errore è rimasta aperta.
- `GetVerseOutput`: vuoto (il progetto non ha ancora Verse). Nessun errore runtime.
- **Log client** (`FortniteGame.log`, 26 439 righe): 890 righe `Error`, 1469 `Warning`, tutte della piattaforma (stagione BR,
  catalogo negozio, binding UI, hitch di caricamento, plugin non installati). Per l'isola ci sono solo due voci, entrambe
  rumore standard di UEFN e innocue:
  - `LogGameFeatures: Error: Game feature '.../705655d7-.../705655d7-....uplugin' has an unknown value '' for BuiltInInitialFeatureState`;
  - `LogDownloadOnDemandGameplay: Warning: Didn't find any Asset Data for this plugin : 705655d7-... v2`.
  Nessun errore su mesh, collisioni, HISM, barriere, acqua o Island Settings.
- Alla chiusura: `StopGame` = Completed, `StopSession` eseguito, `GetSessionStatus` = Disconnected. Il processo
  `FortniteClient-Win64-Shipping` resta aperto (torna alla lobby): lo chiude l'utente.

## 1b. Spawn e orientamento — OK (da screenshot)

`qa_sessione_spawn_partenza.png` (finestra del client 1920×1080, ridotta a 1280×720; il menu di pausa era aperto):
- il personaggio è sul camminamento chiaro, vicino al ciglio, con l'acqua a sinistra (lato +Y, mare) e la superficie
  calpestabile a destra. È coerente con il pad Player 1 a (24000, −8250), 2,5 m dal ciglio a Y −8000;
- la camera guarda verso −X: sullo sfondo si vedono le **due antenne** del ponte e il profilo dell'impalcato sull'acqua.
  L'orientamento verso il ponte funziona (PlayerStart yaw 180);
- il personaggio è in piedi, non cade e non è incastrato. Ha 100 di salute e 0 di scudo.
- **Non verificato:** le coordinate esatte (non leggibili senza `FortPlayerToolset`) e quale dei due pad è stato usato.

## 2, 3, 6, 8 — Non verificabili via MCP

Servono un giocatore che si muova o la lettura della sua posizione, e nessuna delle due cose è disponibile.
Non ho stimato nulla: per i tempi restano le **stime** di ieri (502 m fino a fine ponte: 80 s di scatto, 112 s a velocità base),
che **non sono misure**.
Nuova informazione che cambia la stima: nel log client compare `TacSprintStamScene` (UI della resistenza dello scatto tattico,
preset "BR attuale"). Lo scatto quindi consuma resistenza, e il tempo reale con scatto sarà probabilmente **sopra gli 80 s**,
tra 80 e 112 s. Va misurato.

## 7. Scala — parziale

Nello screenshot il personaggio (≈ 1,9 m) occupa una frazione credibile del camminamento da 9 m, e le antenne a ~500 m
sembrano sottili fusi alti sull'orizzonte, come nei render di ieri. Parapetti del ponte e palme non sono nell'inquadratura,
quindi il confronto richiesto dal Cancello 1 resta da fare.

## Nuovo rilievo — ciclo giorno/notte

- Nella sessione la scena è **notturna**: cielo blu scuro con stelle e luce fredda (screenshot). Il log client mostra
  `DaySequence_... EMovieScenePlayerStatus::Playing`: il ciclo giorno/notte del template avanza. In editor, invece, i render
  avevano il sole radente.
- Effetto: la luce non è costante. Di notte la pavimentazione chiara e l'acqua quasi si confondono e il ciglio si legge peggio
  (pilastro 2). Le antenne restano visibili.
- **Causa probabile:** Day Sequence / ora del giorno lasciati al valore predefinito del template (ciclo attivo).
- **A chi:** uefn-builder. Bloccare l'ora del giorno sul tardo pomeriggio (CLAUDE.md §2.4). Si può anche anticipare
  rispetto alla Fase 3, perché aiuta le prove.

## Problemi, in ordine di gravità

| # | Gravità | Problema | Causa probabile | A chi |
|---|---|---|---|---|
| 1 | Bloccante (verifica) | Il client non espone gli strumenti MCP (`MCPListToolsets` non registrato, `ListClients` vuoto): niente posizione del giocatore né cattura del viewport di gioco. `FortPlayerToolset` comunque non muove il giocatore | Limite della build client/editor attuale (43.10), non dell'isola | **utente**: fare a mano la corsa di prova con la checklist qui sotto (o autorizzare un altro metodo). In alternativa **verse-dev**: un device Verse di debug che con `Print()` scriva tempi e posizioni in `GetVerseOutput` (lettura via MCP) |
| 2 | Media | Tempo di gara non misurato. Lo scatto consuma resistenza (`TacSprintStamScene`), quindi la stima di 80 s è ottimistica | Preset di locomozione "BR attuale" | **qa-tester** (cronometrare appena c'è un modo); poi decide l'orchestratore |
| 3 | Media | Palme HISM, nuoto e risalita, barriere attive e costruzione disattivata: ancora non verificati in gioco | Vedi punto 1 | **qa-tester** / **utente** |
| 4 | Bassa | Ciclo giorno/notte attivo: in sessione è notte e il ciglio si legge peggio | Day Sequence predefinita del template | **uefn-builder** (ora del giorno fissa, tardo pomeriggio) |
| 5 | Info | Dopo `StopSession` il processo del client resta aperto | Comportamento normale di UEFN | nessuna |

## Checklist per la prova manuale (utente, ~10 minuti)

Nell'ordine, partendo dalla sessione avviata:
1. Allo spawn: si guarda verso le antenne? Si è sul camminamento (non sul pad di un altro giocatore, non in acqua)?
2. Correre (con scatto) dalla partenza alla fine del ponte e cronometrare. Poi fino al centro della testata di Mirabello.
   Ripetere una volta a velocità base, senza scatto.
3. Fermarsi accanto a una palma della fascia verde (es. X 12000, Y −9260): si vede? Ci si sbatte contro?
4. Sul ponte, accanto al parapetto: screenshot in terza persona. Il parapetto arriva all'anca o alla vita?
5. Tuffarsi dal ciglio (es. X 15000): si galleggia? Si riesce a risalire sul ciglio (1,5 m) con l'arrampicata?
6. Provare a costruire (tasti di costruzione): deve essere impossibile.
7. Barriere: saltare la siepe lato città (Y ≈ −11800); a piedi oltre X 25000; a nuoto verso X 25130 lungo il mare;
   a nuoto attorno alla testata di Mirabello. Ci si deve fermare ovunque.
Annotare tempi e punti problematici con uno screenshot (anche dal telefono va bene).

## Cancello 1 — parere

**Ancora non verificabile.** Oggi è caduto il blocco della sessione: il gioco parte, lo spawn è corretto, il ponte si vede
e i log sono puliti. Restano da misurare in gioco il tempo, la corsa senza incastri e la scala accanto a parapetti e palme,
e via MCP oggi non si può. La decisione spetta all'orchestratore.

## File prodotti

- Report: questo file.
- Screenshot: `docs/qa/qa_sessione_spawn_partenza.png` (client in gioco alla partenza, menu di pausa aperto).
