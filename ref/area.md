# Area del Blocco 1 — Ponte Thaon di Revel + Passeggiata Morin (tratto SW) + testata Mirabello

Legenda: **[V]** verificato (fonte citata) · **[S]** stima motivata, da confermare.
Dati OSM scaricati il 2026-11-18 dall'API OpenStreetMap (`/api/0.6/map`), © OpenStreetMap contributors (ODbL).
Distanze calcolate con proiezione locale equirettangolare (errore < 0,1 % su queste distanze).

---

## 1. Origine del progetto (0,0,0)

| Voce | Valore | Stato |
|---|---|---|
| Punto | Inizio della way OSM del ponte lato passeggiata (node **10249190464**, primo nodo della way 228262848 "Ponte Thaon di Revel") | [V] OSM |
| Coordinate | **lat 44.1016154, lon 9.8252769** | [V] OSM |
| Quota Z=0 | quota del camminamento in banchina | [S] la banchina è a ~+1,5 m s.l.m. (vedi `sezione.md`) |

Nota: la *spalla* strutturale del ponte (inizio della campata da 65 m) è circa 15 m più avanti verso il mare
(Y ≈ -15). Lo ricavo confrontando i 65 m della fonte progettuale con gli 80 m di OSM fino al pennone 1 [S].
I primi ~15 m sono probabilmente la rampa d'accesso. Per l'origine si tiene il nodo OSM, che è verificabile.

## 2. Assi del progetto

| Asse | Direzione | Valore | Stato |
|---|---|---|---|
| +X | lungo la passeggiata verso NE | **azimut 41,3°** (da nord, in senso orario) | [V] calcolato da OSM: footway 238848819 (41,3°) e coastline (41,5°) |
| +Y | verso la città (NW) | azimut 311,3° | [V] (perpendicolare a X) |
| +Z | in alto | — | — |

**Trasformazione per Blender** (Blosm importa con X=Est, Y=Nord):
1. traslare la scena in modo che il node 10249190464 vada in (0,0,0);
2. ruotare la scena attorno a Z di **-48,7°** (in senso orario). L'angolo è 90° - 41,3°.

Formule (E, N in metri rispetto all'origine):
`X = E·sin(41,3°) + N·cos(41,3°) = 0,660·E + 0,751·N`
`Y = -E·cos(41,3°) + N·sin(41,3°) = -0,751·E + 0,660·N`

**Attenzione: in questa terna il ponte corre verso -Y (verso il mare), non lungo X.**
Ponte e passeggiata sono quasi ortogonali (91,7°).

## 3. Bounding box

| Box | Rettangolo in coordinate progetto | lat min | lat max | lon min | lon max |
|---|---|---|---|---|---|
| **Blocco 1 (giocabile)** | X -60…270, Y -215…150 | **44.09993** | **44.10433** | **9.82337** | **9.82953** |
| Import Blosm esteso (fondale: cortina edilizia, Garibaldi, Mirabello) | X -150…330, Y -260…260 | 44.09906 | 44.10539 | 9.82159 | 9.83045 |

Il Blocco 1 copre: molo e ponte fino a Mirabello (Y -179) con la testata d'arrivo, la passeggiata dall'angolo
(X 9) fino a X ≈ 260 (circa 250 m), i Giardini a Mare e Viale Italia fino al bordo dei Giardini pubblici (Y ≈ 145).

## 4. Punti chiave (coordinate progetto, in metri)

| Punto | lat, lon | X | Y | Fonte |
|---|---|---|---|---|
| Origine: inizio way ponte | 44.1016154, 9.8252769 | 0,0 | 0,0 | OSM node 10249190464 |
| Angolo banchina/passeggiata (inizio Passeggiata Morin) | 44.1021853, 9.8245441 | 9,0 | 85,8 | OSM node 301277132 |
| Radice del molo, spigolo NE (coastline) | 44.1021115, 9.8246860 | 10,3 | 71,9 | OSM coastline |
| Radice del molo, spigolo SW | 44.1014101, 9.8253873 | -11,3 | -21,7 | OSM area pedonale 850396604 |
| Punta del molo (coastline) | 44.1011493, 9.8262013 | 9,8 | -89,7 | OSM coastline |
| Pennone 1 (centro dell'anello di biforcazione) | 44.1011245, 9.8260120 | -2,3 | -80,1 | OSM way 1256322501 |
| Pennone 2 (centro dell'anello) | 44.1008281, 9.8264537 | -3,8 | -128,4 | OSM way 1256322398 |
| Fine ponte lato Mirabello (inizio scala da 14 gradini) | 44.1005200, 9.8269154 | -5,2 | -178,7 | OSM node 5146240473 |
| Pontile galleggiante d'imbarco (radice) | 44.1025792, 9.8251118 | 71,8 | 80,6 | OSM way 175935430 |
| Fine Passeggiata Morin (NE) | 44.1059054, 9.8291032 | 560,0 | 85,3 | OSM node 301277131 |
| Radice Molo Italia | 44.105970, 9.829182 | 570 | 85 | OSM way 132740887 |
| Gomito Molo Italia | 44.104261, 9.831837 | 567 | -199 | OSM way 801989878 |
| Faro rosso Molo Italia | 44.1042608, 9.8339460 | 678 | -326 | OSM node 1327347929 (man_made=lighthouse, luce rossa, h luce 8 m) |

---

## 5. Quadro generale verificato (correzioni a CLAUDE.md §2.1)

| Dato in CLAUDE.md | Dato verificato | Stato |
|---|---|---|
| Andamento SW/NE, mare a SE | **Confermato.** Asse della passeggiata con azimut 41,3°, mare a SE | [V] OSM |
| Lunghezza 500-600 m | **551 m** (footway "Passeggiata Costantino Morin" 238848819, dall'angolo del ponte alla radice del Molo Italia). Distanza in linea retta: 551 m | [V] OSM |
| Ponte all'estremità "meridionale" | Il ponte è all'estremità **sud-ovest**. **Non prosegue la passeggiata in linea**: parte ad angolo retto verso il mare (azimut ~133°). Prima si percorre un molo di ~86 m (strada "Banchina Thaon di Revel", way 183535303, in pavé), poi si sale sul ponte, che arriva a Mirabello, ~180 m più a SE | [V] OSM |
| Ponte lungo ~150 m | **~160 m** tra le spalle (fonte progettuale). **176 m** complessivi secondo inforMARE (2013). 178,7 m in OSM, rampe incluse | [V] vedi `ponte.md` |
| Molo Italia all'estremità NE, due rami (~90° e ~137°) | **Confermato.** Radice a X ≈ 570. Il primo ramo è ortogonale alla banchina (284 m verso -Y). Il secondo piega di ~136° verso est fino al faro rosso | [V] OSM |
| Giardini a Mare sul lato città | **Confermato.** Una fascia di ~14 m ("leisure=park", way 850396610) tra banchina e Viale Italia. Oltre il viale ci sono i **Giardini pubblici** storici, profondi ~50-150 m | [V] OSM |
| Viale Italia tra giardini e città | **Da correggere.** Viale Italia corre tra i Giardini a Mare e i Giardini pubblici, a ~42-49 m dal camminamento. La cortina edilizia vera è **oltre i Giardini pubblici**: a Y ≈ 206-242 per X > 178 e a Y > 294 per X < 138, cioè 120-210 m dalla banchina | [V] OSM |
| Battelli per le Cinque Terre | **Confermato e localizzato.** Pontile galleggiante in legno a X ≈ 71, lungo 28,9 m verso il mare. Lì terminano le rotte ferry OSM per Portovenere e Palmaria. Terminal Traghetti a X 72, Y 80 | [V] OSM |
| — (non in CLAUDE.md) | Davanti alla passeggiata, da X ≈ 89 a 290, c'è il **porto turistico Assonautica** con pontili e yacht | [V] OSM |
| — (non in CLAUDE.md) | A SW del molo del ponte c'è un'**area militare** (Circolo Ufficiali M.M.), recintata: fondale non accessibile | [V] OSM |

**Schema della pianta (coordinate progetto):**
```
 Y (città)
 ^   Giardini pubblici (Y 145-294) ... cortina edilizia (Y > 206)
 |   Viale Italia (Y ~128-135)
 |   Giardini a Mare (Y 102-116)        palme (Y 92,6 e 99,6)
 |== passeggiata / banchina (Y 80-102) ========================== X=560 Molo Italia ->
 |  [molo X -11..10]   pontile imbarco X 71   marina Assonautica X 89-290
 |  [ponte su X≈-3, da Y 0 a Y -179]
 |  Mirabello (Y < -170)
 +---------------------------------------------------------------> X (NE)
```

## Da verificare con foto o misura dell'utente
- Cosa c'è sotto la prima campata (Y 0 … -80): OSM mappa un **molo pavimentato** largo ~21 m e il ponte gli corre sopra.
  Il testo del progettista parla invece del "Circolo velico M.M." sotto il ponte. Serve una foto laterale del ponte dalla banchina.
- Punto esatto in cui parte la rampa del ponte rispetto al nodo-origine: serve una foto dall'imbocco.
