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
Per exemple, els agents de programació estan canviant com desenvolupem programari.

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
- **Encara no resol tots els casos d'ús**, però cada cop permet fer més coses.

<!-- end_slide -->


# Què és una IA local?

**IA local:** el model s'executa al nostre ordinador
o servidor, sense enviar les consultes a un servei extern.

- **Privacitat:** controlar on van les dades.
- **Autonomia:** poder treballar sense xarxa.
- **Continuïtat:** conservar les versions.
- **Control:** triar models i integracions.

Cal disposar del model i d'una eina que permeti executar-lo localment.

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

# Què hi podem fer amb la IA en local?

Temporalitat de les tasques:

**En lot** (p. ex., mentre som absents)

- Classificar documents i extreure'n informació.
- Extreure dades de factures i transcriure enregistraments.
- Revisar codi i generar proves.

**Ús interactiu** (cal bona latència i recursos al moment)

- Conversar amb un assistent: traducció, resums i preguntes.
- Transcriure en directe i conversar per veu.
- Programació amb agents.

<!-- end_slide -->

# Maquinari que tens ara

| Equip | Preu aprox. | Gemma 4 12B |
| --- | ---: | ---: |
| PC Intel / AMD · 32 GB · GPU integrada | 800–1.000 € | 3–6 tok/s |
| PC RTX 5060 Ti GPU (16 GB) · 32 GB | 1.500–2.000 € | 35–50 tok/s |
| MacBook Air M5 · 13" · 16 GB  | 1.300–1.500 € | 12–16 tok/s |

* **Tokens/s de generació estimats amb Gemma 4 12B a 4 bits**,
amb context curt i un usuari. Primera fila: només CPU.
No són mesures pròpies; depenen de la configuració.

* Preus orientatius d'equips nous a Catalunya (setembre de 2026).
PC: només la torre. Mac: portàtil complet.

<!-- end_slide -->

# Com escollir model i maquinari

**Model i programari**

- Proveu un model petit amb tasques reals en català.
- **Q4_K_M:** bon equilibri entre qualitat, memòria i velocitat.
- **MoE:** menys càlcul per token, però cal memòria per a tots els pesos.

**Maquinari**

- Proveu primer el vostre equip i comproveu que les eines hi funcionen.
- Reserveu memòria per als **pesos, el context i el sistema**.
- Per a ús interactiu, prioritzeu l'acceleració GPU; en lot, podeu esperar.

<!-- end_slide -->

# Per començar: la guia de Softcatalà

**La intel·ligència artificial al vostre ordinador personal**

Orientada a **eines amb interfície gràfica (UI)**, sense haver d'utilitzar la línia d'ordres (CLI).

- **Orienteu-vos sobre la compatibilitat** segons l'equip i la memòria.
- **Enteneu els conceptes clau** abans de començar.
- **Seguiu els tutorials** per fer servir models de llenguatge, transcriure i subtitular.
- **Trieu models per treballar en català.**

[softcatala.org/ia-local](https://www.softcatala.org/ia-local/)

**Primer pas:** consulteu el vostre equip i trieu una tasca per provar.

<!-- end_slide -->
