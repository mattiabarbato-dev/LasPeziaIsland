# QA — Prova di percorrenza del blockout (Blocco 1)

Data: 2026-11-18 · Agente: qa-tester · Livello: `LasPezia_Island` (blockout del commit `94aaec7`)
Coordinate in XYZ nativo Unreal (X avanti, Y destra, Z su; l'editor mostra LUF: Left = −Y, Up = Z, Forward = X).
Nessuna modifica a livello, asset o codice. Nessun caricamento né pubblicazione.

## Sintesi

**La sessione di gioco non è partita.** `SessionToolset.StartSession` fallisce per 3 volte su 3, anche con Play From Here,
con l'errore di matchmaking `errors.com.epicgames.fortnite.invalid_region` ("Invalid matchmaking region: 'NONE'").
Dal log: la valutazione QoS è riuscita (IT 75 ms, raccomandata la subregione DE), ma il `QosRegionManager` resta su
"Best region: '' / No region currently set". Il problema è un'impostazione di account o editor, non dell'isola.

Tutto ciò che si poteva misurare **in editor** l'ho misurato: profili delle superfici, percorso simulato con sweep di capsula,
larghezze, linea di vista, coperture delle barriere, impostazioni dell'isola e render. Le voci che richiedono il gioco vero
(spawn, palme HISM a runtime, nuoto, barriere attive, tempo cronometrato) restano **non verificate**.

| # | Voce | Esito |
|---|---|---|
| 1 | Sessione, spawn sui pad, log client e Verse | **KO / non verificato**: sessione bloccata dal matchmaking (regione NONE) |
| 2 | Palme: visibili e con collisione | **OK in editor** · non verificato in gioco |
| 3 | Tempo partenza → fine ponte / testata | **Stima**: 80 s di scatto, 112 s di corsa base (vedi §3) |
| 4 | Punti d'incastro | **OK in editor**: nessun incastro sul percorso con 2 capsule; 3 note minori |
| 5 | Linea di vista sulle antenne | **OK** da 6 punti (traccia + render) |
| 6 | Caduta in acqua | **Non verificato** (serve la sessione); analisi delle rive raggiungibili a nuoto: 3 uscite fuori area |
| 7 | Scala percepita | **OK (in editor, senza personaggio)**: render ad altezza occhi e confronto con la capsula del giocatore |
| 8 | Barriere | **OK la copertura geometrica** · attivazione in gioco non verificata · 1 varco a nuoto a fine blocco |

## Metodo

- **Capsula del giocatore**, letta dal CDO di `/Game/Athena/PlayerPawn_Athena`: raggio 32, semi-altezza 75 uu.
  Controprova con la capsula nativa `FortPlayerPawnAthena` (raggio 42, semi-altezza 88).
  Movimento (`FortMovementComp_CharacterAthena`): MaxWalkSpeed 450 uu/s, MaxStepHeight 45 uu, pendenza calpestabile 44,8°,
  MaxSwimSpeed 300 uu/s.
- **Camminatore simulato** (script Python in editor): avanza a passi di 25 uu lungo una polilinea. A ogni passo fa uno sweep
  orizzontale della capsula, alzato di 45 uu (gradino massimo); se trova un ostacolo non calpestabile segna BLOCCATO.
  Poi fa uno sweep verso il basso per trovare il pavimento e segnala vuoti, cadute oltre 50 uu e pendenze non calpestabili.
  Profilo di collisione `Pawn`, solo collisione semplice (UCX), come in gioco.
- **Limite del metodo:** non riproduce lo scivolamento lungo i muri, il salto, l'arrampicata (mantle) né la fisica dell'acqua.
  Se il camminatore si ferma vuol dire che c'è un ostacolo frontale, non per forza un incastro. Gli ostacoli segnalati qui
  sotto li ho controllati uno per uno.
- **Linea di vista:** line trace (canale Visibility) dagli occhi (pavimento + 160 uu) verso ogni antenna a Z 8, 15, 22, 30 e 33 m.
- **Render:** `SceneCaptureToolset.Capture` sul mondo dell'editor, modalità Lit, 1280×720.

## 1. Sessione — KO (bloccata)

- `StartSession` (×2) e `StartSession` con Play From Here a (24000, −8450, 120), yaw 180: tutte `Failed`, `invalid_region`.
- Log editor: `LogMatchmakingServiceClient: ObtainTicket ... Status: 400 ... Invalid matchmaking region: 'NONE'`;
  `LogQos: Best region is '', recommended subregion is 'DE'`.
- Non c'è un client avviato, quindi niente log client (`GetClientLogEntries`) né output Verse da leggere.
  `GetSessionStatus` = Disconnected: non c'è nessuna sessione da fermare.
- Dopo il terzo tentativo l'editor ha smesso di rispondere alle chiamate MCP (timeout). È probabile che sia rimasta aperta la
  finestra di errore "Impossibile giocare": va chiusa a mano.
- **Causa probabile:** regione di matchmaking non impostata (o "Auto" senza esito) nelle impostazioni di Fortnite/UEFN dell'utente.
- **Correzione:** l'utente imposta una regione di matchmaking esplicita (Europa) e riavvia UEFN se serve. Poi si ripete questo test.
- Spawn, controllato solo in editor: i pad sono a (24000, −8250/−8650), con il pavimento a Z 0 sotto il centro.
  Lo spawn non si può verificare senza sessione.

## 2. Palme — OK in editor, non verificato in gioco

- `Blockout_Palme_HISM`: componente `HierarchicalInstancedStaticMesh` con profilo bloccante per `Pawn`. Uno sweep di capsula
  contro `Palma_F1_01` (1200, −9260) si ferma a Y −9315, con normale (0, −1, 0) sul componente HISM: la collisione del tronco c'è.
- Visibili nel render `qa_scala_palme.png` (filari sfalsati, chiome a 8-10 m, ombre sul camminamento).
- Le palme sono sulla fascia verde (Y −9260 / −9960). La corsia (Y −8040..−8925) resta libera: il percorso principale non
  le tocca mai.
- **Resta da verificare in sessione** che l'HISM aggiunto via Python sia replicato e collida nel client.

## 3. Tempo di percorrenza — stima, non misura

Lunghezze misurate con il camminatore sulla linea ideale di gara (corsia a Y −8450, curva sul molo a X 600, imbocco del ponte,
corsia esterna attorno a ciascuna antenna, centro della testata a (−500, 20745)):

| Tratto | Lunghezza |
|---|---|
| Partenza (24000, −8450) → fine ponte (Y 17900, Z 1,30 m) | **502 m** |
| Partenza → centro della zona traguardo di Mirabello | **530,5 m** |
| di cui: camminamento X 24000 → 600 | 234 m |
| di cui: ponte Y 0 → 17900 (con rampa 6,1 %, quota 4,3 m, discesa 7 %) | ~180 m |

| Velocità (fonte) | Fine ponte | Testata Mirabello |
|---|---|---|
| 450 uu/s: corsa base, `MaxWalkSpeed` dal CDO di `PlayerPawn_Athena` | 112 s | 118 s |
| 630 uu/s: scatto = 450 × 1,4, il "Moltiplicatore velocità scatto" predefinito di Island Settings (opzione oggi inattiva) | **80 s** | **84 s** |

- **Esito:** con lo scatto continuo la corsa è **dentro l'obiettivo di 60-90 s, ma vicina al limite alto**. A velocità base
  è fuori (112-118 s). Island Settings riporta anche un costo dello scatto di 20 energia/s (opzione inattiva): se in gioco
  lo scatto consumasse energia, il tempo reale cadrebbe tra i due valori.
- **Il tempo va cronometrato in sessione:** queste sono stime, non misure.
- Nessun tratto fa perdere tempo per la geometria: salita massima per passo 0,5 uu sul ponte, nessuna caduta, nessun gradino.

## 4. Punti d'incastro — OK in editor

Percorsi simulati con entrambe le capsule (r 32 / hh 75 e r 42 / hh 88), nessun blocco e nessuna caduta:

| Percorso | Esito |
|---|---|
| Linea principale, corsie a +X delle antenne (≈ +1,9 m dal centro) | OK, 530,5 m, Z 0 → 430 → 0 |
| Linea principale, corsie a −X delle antenne | OK, 530,5 m |
| Vialetto dei giardini (Y −10900, X 24000 → 1500) | OK, 225 m piatti |
| Rasente il ciglio (Y −8045) | OK, 225 m: non si cade se si corre dritti |
| Rasente il cordolo (Y −8880) fino al molo | OK, salita max 0,7 uu |
| Attraverso le aiuole (X 9000: cordolo 0,2 → aiuola 0,4 → vialetto → aiuola 0,3) | OK, salita max per passo 33-35 uu (< 45) |
| Attraverso un varco (X 6000) | OK, salita max 25 uu |
| Giro della testata di Mirabello | OK, 88 m piatti |

Punti critici della richiesta:

- **Imbocco del ponte sul molo (Y 0):** OK. La rampa parte a Z 0 in mezzo al molo, con i parapetti da 1,1 m fin dall'inizio.
  Dai lati non si entra (il camminatore si ferma sui parapetti, normale ±X): l'accesso è solo frontale, largo 5,7 m.
  Nota: le testate dei parapetti a Y 0 sono spigoli verticali di 1,1 m in mezzo al molo. Chi taglia la curva verso il ponte
  ci sbatte contro (vedi `qa_imbocco_ponte.png`). Non incastrano.
- **Anelli attorno alle antenne:** corsie misurate a quota +0,5 m sull'impalcato:
  antenna 1 (Y 8040) **3,37 m** a sinistra (X −601..−264) e **3,38 m** a destra (X −174..164);
  antenna 2 (Y 12860) **3,36 m** e **3,39 m**. Sezione dell'antenna circa 0,9 m. Requisito ≥ 3 m rispettato,
  ma con 8 giocatori la strozzatura è sensibile.
- **Giunzione ponte / rampa di Mirabello (Y 17900):** OK, continua (Z 137 → 123 a Y 18000), nessun gradino.
  La rampa di Mirabello ha pareti laterali (normale ±X): ci si esce solo dal fondo.
- **Cordolo 0,2 m** (Y −8925..−8950, largo solo 0,25 m) e **aiuole 0,3-0,4 m:** si superano camminando (gradino max 45 uu).
- **Varchi dei giardini** (4 m): OK.
- **Angolo smussato passeggiata/molo:** smusso a 45° da (1900, −8030) a (1100, −7230). Il bordo del molo è "a denti":
  ciglio a X 1010-1020 fino a Y −6250, poi a X ~900 fino a Y −1820, poi a X ~800. Non incastra; chi corre rasente
  il ciglio cade in acqua sui denti (prova "rasente angolo": caduta a (1068, −7141)).
- **Corridoio sul molo davanti all'edificio di fondale** (facciata a X 170-197, ciglio a X 1010-1020, Y −7000..−6300):
  **8,2-8,5 m**, appena sopra gli 8 m della corsia libera.
- **Sacca cieca:** il camminamento prosegue oltre la curva fino a sbattere contro l'edificio di fondale (facciata a X 94-139,
  Y −9300..−8000). È una sacca di ~5 m in fondo alla passeggiata: aperta, non incastra.
- **Bordi delle barriere:** in editor le barriere non hanno collisione (`BarrierBounds` = NO_COLLISION, si attiva a runtime),
  quindi l'incastro sui bordi non si può simulare.

## 5. Linea di vista sulle antenne — OK

Traccia occhi → antenna a Z 8 / 15 / 22 / 30 / 33 m; la sommità di entrambe le antenne misurata è a Z 3350.

| Punto di osservazione | Antenna 1 (Y 8040) | Antenna 2 (Y 12860) | Render |
|---|---|---|---|
| Partenza (24000, −8450) | 5/5 libere | 5/5 libere | `qa_ldv_1_partenza.png` |
| Camminamento X 16000 | 5/5 | 5/5 | `qa_ldv_2_x160.png` |
| Camminamento X 8000 | 5/5 | 5/5 | `qa_ldv_3_x80.png` |
| Curva X 1500 | 5/5 | 5/5 | `qa_ldv_4_angolo.png` |
| Molo (600, −3000) | 5/5 | 5/5 | `qa_ldv_5_molo.png` |
| Sul ponte, Y 4000-5000 | 5/5 | coperta dall'antenna 1 (sono allineate) | `qa_ldv_6_ponte.png` |

Le palme non coprono mai le antenne. Dalla partenza le antenne sono due sottili fusi bianchi sopra la linea dell'orizzonte,
a ~500 m: riconoscibili ma piccole. Si leggono meglio quando avranno il loro materiale definitivo (Fase 3).

## 6. Caduta in acqua — non verificato

- Acqua (device Acqua V2) a Z −150. Il ciglio di tutte le rive (passeggiata, molo, Mirabello, fondale) è a Z 0: salto
  costante di 1,5 m, nessuna scaletta o punto più basso.
- Il pawn ha `MaxOutOfWaterStepHeight` 40 uu: non basta per risalire 150 uu camminando. La risalita dipende quindi
  dall'arrampicata (mantle) dall'acqua; in Island Settings c'è "Altezza minima arrampicata in acqua = NORMALE" (opzione inattiva).
  **Probabile, non verificato.** Serve la sessione.
- **Rive fuori area raggiungibili a nuoto** (se l'arrampicata funziona):
  1. **Fine blocco:** `Barriera_FineBlocco` entra in mare solo fino a Y −6990 e `Barriera_LatoCitta` finisce a X 27210.
     Girando a nuoto attorno alla barriera si entra nella tasca d'acqua X 25000..33000 e si risale sul fondale cittadino
     (Z 0) tra X 27210 e 33000, a Y ≈ −11800, **fuori area e senza barriera**.
  2. **Area militare:** riva a Z 0 per X < −1360, Y fino a ~2300, a ovest della barriera del molo. Raggiungibile dal mare.
     Ci si resta chiusi dentro (la barriera impedisce di tornare a piedi): si può solo rituffarsi.
  3. **Intorno a Mirabello:** fondale a Z 0 da X −6000 a 8000 per Y ≥ 16800. Le barriere chiudono solo la testata
     (X −2278..1238): si risale ovunque fuori da quell'intervallo.
- Comportamento attuale atteso: niente rientro al checkpoint (Fase 2). Danni da caduta: in Island Settings "SÌ" ma inattivo;
  il dislivello massimo dal ponte è 4,3 + 1,5 m verso l'acqua, quindi non ci si aspetta danno.

## 7. Scala percepita — OK in editor (senza personaggio)

Nel livello non c'è un manichino. Non l'ho aggiunto, perché il mio compito non prevede modifiche al livello. Il confronto è fatto
con render ad altezza occhi (1,6-1,65 m) e con la capsula del giocatore (≈ 1,5 m; personaggio visivo Fortnite ≈ 1,8-1,9 m).

- **Parapetti 1,1 m** (`qa_scala_parapetto.png`): arrivano a ~60 % dell'altezza del personaggio, cioè all'anca o alla vita.
  Visti ad altezza occhi sembrano parapetti veri. Impalcato libero tra i parapetti: **5,7 m**, come da deroga (5-6 m).
- **Palme** (`qa_scala_palme.png`): 9 m di tronco + chioma a 8-10 m ≈ 5 personaggi. Credibili come palme da lungomare.
  Il passo di 9 m dà un buon ritmo.
- **Cordolo 0,2 m e aiuole 0,3-0,4 m** (`qa_scala_cordolo_aiuole.png`): sotto il ginocchio, si leggono come bordi e non come muri.
- Camminamento ciglio → cordolo: **9,25 m** (≥ 8 m).
- **Da rifare in sessione** con il personaggio vero, per la conferma del Cancello 1.

## 8. Barriere — copertura OK, attivazione non verificata

Coperture lette da `BarrierBounds` di ogni device: tutte coincidono con `docs/uefn_blockout.md`, da Z −700 a 3140.
- Lato città (Y −12058..−11802, X −3510..27210): sta subito dietro la siepe da 1,5 m (fine a Y −11825).
  Chi scavalca la siepe con un salto o un'arrampicata finisce dentro la barriera: corretto.
- Barriera del molo e barriera lato città si sovrappongono a X −1360 (nessun varco a terra).
- Testata di Mirabello chiusa su 3 lati.
- **Varco:** la barriera di fine blocco si aggira a nuoto (vedi §6, punto 1).
- In editor la collisione delle barriere è disattivata per costruzione: se "tengano" davvero lo dice solo una sessione.

## Altri rilievi

- **Costruzione attiva:** Island Settings → "Consenti costruzione = TUTTI", risorse non infinite. In una corsa i giocatori
  possono costruire rampe o passerelle (per esempio sull'acqua verso il fondale, o per tagliare la curva del molo)
  e cambiare il percorso. Va deciso in Fase 2.
- "Consente la rigenerazione manuale = SÌ" e "Tempo di rigenerazione 1 s": oggi, se si resta bloccati fuori area,
  l'unico rientro è la rigenerazione manuale.

## Problemi, in ordine di gravità

| # | Gravità | Problema | Causa probabile | A chi |
|---|---|---|---|---|
| 1 | Bloccante (verifica) | La sessione non parte: `invalid_region` (regione NONE) | Regione di matchmaking non impostata nell'account o nell'editor | **utente** (impostare la regione Europa), poi qa-tester ripete §1, 2, 3, 6, 7, 8 |
| 2 | Alta | Uscite fuori area a nuoto: oltre la fine del blocco (fondale X 27210..33000), area militare, rive attorno a Mirabello | Barriere solo sui confini a terra; rive del fondale a Z 0, arrampicabili | **verse-dev** (rientro dall'acqua entro 3 s, già in Fase 2); in attesa, **uefn-builder**: prolungare `Barriera_LatoCitta` fino a X ≥ 33000 o allungare in mare `Barriera_FineBlocco` |
| 3 | Alta | Costruzione consentita a tutti | Impostazione predefinita di Island Settings | **uefn-builder** (Consenti costruzione = Nessuno), da confermare con l'utente in Fase 2 |
| 4 | Media | Tempo stimato 80-84 s di scatto, 112-118 s di corsa base: al limite alto di 60-90 s | 502-530 m di percorso | **qa-tester** (cronometrare in sessione); se è lungo, decide l'orchestratore (la regola di CLAUDE.md copre solo il caso "troppo corto") |
| 5 | Media | HISM delle palme, spawn, nuoto e risalita, barriere attive: non verificati in gioco | Sessione bloccata | **qa-tester** dopo il punto 1 |
| 6 | Bassa | Strozzature di 3,36-3,39 m attorno alle antenne, con 8 giocatori | Deroga dell'anello a 8 m | Nessuna azione ora; rivalutare con 8 giocatori in Fase 2 (**blender-artist** se serve allargare) |
| 7 | Bassa | Testate dei parapetti a Y 0: spigoli verticali da 1,1 m in mezzo al molo | Parapetti che partono a quota piena dall'imbocco | **blender-artist** (parapetti svasati o rastremati all'imbocco, Fase 3) |
| 8 | Bassa | Ciglio del molo "a denti" (X 1020 → 900 → 800) e smusso stretto; sacca cieca di ~5 m contro l'edificio di fondale | Forme ricavate da OSM | **blender-artist** (kit banchina, Fase 3: ciglio continuo) |
| 9 | Info | Corridoio sul molo 8,2-8,5 m davanti all'edificio di fondale | Edificio OSM sul molo | Nessuna: è nel requisito, ma non va ristretto ancora |
| 10 | Info | Dopo il terzo `StartSession` fallito l'editor non risponde più a MCP | Probabile finestra di errore modale aperta | **utente**: chiudere la finestra in UEFN |

## Cancello 1 — parere

**Non superato, perché non è verificabile:** il cancello chiede un tempo *misurato*, la corsa senza incastri *in gioco* e la scala
giudicata *con un personaggio*. In editor la geometria passa tutte le prove: nessun incastro con due capsule, pendenze ≤ 7 %,
nessun gradino, corsie ≥ 3,36 m, antenne sempre visibili, proporzioni credibili. Mi aspetto quindi che il cancello si superi
appena la sessione parte, a meno di sorprese sull'HISM delle palme. Prima di chiuderlo serve la sessione (punto 1).
I punti 2 e 3 non bloccano il Cancello 1, ma vanno risolti prima del Cancello 2.

## File prodotti

- Report: questo file.
- Render (docs/qa/): `qa_ldv_1_partenza.png`, `qa_ldv_2_x160.png`, `qa_ldv_3_x80.png`, `qa_ldv_4_angolo.png`,
  `qa_ldv_5_molo.png`, `qa_ldv_6_ponte.png`, `qa_scala_parapetto.png`, `qa_scala_palme.png`,
  `qa_scala_cordolo_aiuole.png`, `qa_imbocco_ponte.png`, `qa_mirabello_arrivo.png`.
