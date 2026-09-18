<!-- new_line -->
<!-- alignment: center -->
<!-- no_footer -->

<span style="color: #b4ccff">**IA en local**</span>

<span style="color: #a5d7e8">Llibertat i sobirania</span>

```text
    .----------------------.   .--------.
    |                      |   | ====== |
    |       IA LOCAL       |   | ====== |
    |       > Hola!_       |   |        |
    |                      |   |  (o)   |
    '----------------------'   |        |
              ||               |  .  .  |
          ____||____           '--------'
         '----------'
```

<span style="color: #b6eada">**Jordi Mas (Softcatalà)**</span>

<span style="color: #b6eada">GitHub: jordimas · X: @jordimash</span>

<!-- end_slide -->

# Context: en quin moment ens trobem

**La IA és una tecnologia transformadora**

La IA és una tecnologia transformadora que està canviant com realitzem moltes tasques.
Per exemple, des de fa menys d'un any, els programadors depenem completament d'agents per treballar.

**El tancament com a avantatge competitiu**

Molts laboratoris punters es reserven el coneixement perquè l'han convertit en un avantatge competitiu.
Anècdota: irònicament, OpenAI rep el nom de ClosedAI.

<!-- end_slide -->

# Context: en quin moment ens trobem

**Neguit creixent**

Ara, per a moltes tasques habituals, depenem d'una tecnologia tancada, que s'executa al núvol i sobre la qual no tenim cap control.

**Moment "Linux"**

- A principis dels anys 2000, Linux tenia mancances de suport de maquinari, aplicacions i usabilitat.
- Molts dubtaven que fos una alternativa viable; avui és una peça clau del món digital.

**Què succeeix amb la IA local ara?**

- La IA local viu un moment semblant, amb models i maquinari que evolucionen ràpidament.
- E̲n̲c̲a̲r̲a̲ ̲n̲o̲ ̲r̲e̲s̲o̲l̲ ̲t̲o̲t̲s̲ ̲e̲l̲s̲ ̲c̲a̲s̲o̲s̲ ̲d̲'̲ú̲s̲, però cada cop permet fer més coses.

<!-- end_slide -->


# Què és una IA local?

**IA local:** el model s'executa al nostre ordinador
o servidor, sense enviar les consultes a un servei extern.

- **Privacitat:** controlar on van les dades.
- **Autonomia:** poder treballar sense xarxa.
- **Continuïtat:** conservar les versions.
- **Control:** triar models i integracions.

Per fer això, es requereixen **pesos oberts**.

<!-- end_slide -->

# Què és una IA lliure?

No hi ha consens, però hi ha components clau:
- Dades d'entrenament obertes i avaluacions obertes.
- Codi i receptes d'entrenament accessibles.
- Pesos reutilitzables i codi d'inferència lliure.

Pesos oberts no vol dir necessàriament IA lliure.

**En la meva opinió**, perquè una IA sigui lliure, cal poder reproduir l'entrenament
amb el maquinari adequat, a partir de dades, codi i metodologia
publicats, seguint els principis de la **ciència oberta**.

<!-- end_slide -->

# Què hi podem fer?

Temporalitat de les tasques:

**En lot** (p. ex execució mentre som austents)

- Extracció de text d'àudio, classificació, etc
- Extreure dades de factures i transcriure enregistraments.
- Revisar codi i generar proves.

**Temps real** (Cal bona latència i recursos al moment)

- Usar-lo com una xat bot normal: traducció, resums, preguntes
- Transcriure en directe i conversar per veu.
- Programació agèntica

<!-- end_slide -->

# Maquinari que tens ara

| Equip | Preu aprox. | Gemma 4 12B |
| --- | ---: | ---: |
| PC Ultra 5 / Ryzen 5 · 32 GB · sense GPU | 800–1.000 € | 3–6 tok/s |
| PC RTX 5060 Ti GPU (16 GB) · 32 GB | 1.500–2.000 € | 35–50 tok/s |
| MacBook Air M5 · 13" · 16 GB · 512 GB | 1.300–1.500 € | 12–16 tok/s |

* **Tok/s estimats amb Gemma 4 12B**, quantitzat a 4 bits,
en generació de text amb context curt i un sol usuari.

* Preus orientatius d'equips nous a Catalunya (setembre de 2026).

<!-- end_slide -->

# Consells a l'hora d'escollir model

- Useu quantització ("comprimeix" el model), per exemple Q4_K_M
  - Un model de 32B ocupa 16GB de RAM i anirà més ràpid
  - Q4_K_M acostuma a oferir un bon equilibri entre qualitat, ús de memòria i velocitat.
- Si teniu poca memòria, useu arquitectures MoE

<!-- end_slide -->

# Consells a l'escollir maquinari

- Si voleu fer coses en temps real, us cal GPU
- Us cal poder carregar el model a la memòria:
  - Models de 32GB necessiten 48GB de RAM
- Les targetes NVIDIA donen el millor rendiment

<!-- end_slide -->
