---
theme:
  name: dark
  override:
    default:
      margin:
        percent: 3
    slide_title:
      font_size: 1
      padding_top: 0
      padding_bottom: 1
    code:
      alignment: center
      minimum_size: 0
      minimum_margin:
        percent: 0
      padding:
        horizontal: 0
        vertical: 0
---

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

# Tot seguit: aprofita la IA al teu ordinador

Una xerrada de **Martí SC**, enginyer de dades.

- Entendre com els models fan servir la memòria.
- Triar models adequats per al vostre ordinador.
- Ajustar-ne el rendiment i interpretar-ne la velocitat.

Hi aprofundirà amb explicacions tècniques i visualitzacions.

**Us recomano que us hi quedeu!**

<!-- end_slide -->

# Context: en quin moment ens trobem (1/2)

**La IA és una tecnologia transformadora**

Està canviant com realitzem moltes tasques.
Per exemple, els agents de programació han redefinit com desenvolupem programari.

**El tancament com a avantatge competitiu**

Molts laboratoris punters es reserven el coneixement perquè l'han convertit en un avantatge competitiu.
Anècdota: irònicament, OpenAI rep el nom de ClosedAI.

<!-- end_slide -->

# Context: en quin moment ens trobem (2/2)

**Neguit creixent**

Ara, per a moltes tasques habituals, depenem d'una tecnologia tancada, que s'executa al núvol i sobre la qual no tenim cap control.

**Moment "Linux"**

- Anys 2000: mancances de maquinari, aplicacions i usabilitat.
- Es dubtava que pogués ser una alternativa.
- Avui és una peça clau del món digital.

**Què succeeix amb la IA local ara?**

- Models i maquinari evolucionen ràpidament.
- **Encara no resol tots els casos d'ús per a tothom.**
- Cada cop permet fer més coses.

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

# Què podem fer amb la IA en local?

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

# Maquinari comú que es pot comprar a 2026

| Equip | Preu aprox. | Gemma 3 12B |
| --- | ---: | ---: |
| PC Intel / AMD · 32 GB | 800–1.000 € | 3–6 tok/s |
| PC RTX 5060 Ti 16 GB¹ | 1.500–2.000 € | 35–50 tok/s |
| MacBook Air M5 · 16 GB | 1.300–1.500 € | 12–16 tok/s |

**Tokens/s de generació estimats amb Gemma 3 12B a 4 bits**,
amb context curt i un usuari. Primera fila: només CPU.
No són mesures pròpies; depenen de la configuració.

Preus orientatius d'equips nous a Catalunya (setembre de 2026).
PC: només la torre. Mac: portàtil de 13". ¹ RAM: 32 GB.

<!-- end_slide -->

# Com escollir model i maquinari

**Model i programari**

- Proveu un model petit amb tasques reals en català.
- **Q4_K_M:** bon equilibri entre qualitat, memòria i velocitat.
- **MoE:** menys càlcul; memòria per a tots els pesos.

**Maquinari**

- Comproveu primer les eines al vostre equip.
- Reserveu memòria per als **pesos, el context i el sistema**.
- Ús interactiu: prioritzeu la GPU. En lot, podeu esperar.

<!-- end_slide -->

# Eines per executar-ho a casa

| Eina | Per a qui |
| --- | --- |
| **LM Studio** | Descoberta fàcil de models, UI amable |
| **Ollama** | Terminal + UI, més control |
| **AnythingLLM** | Consultar els teus documents (RAG) |

Totes tres funcionen a **macOS, Windows i Linux**.

**Guia de Softcatalà:** instal·lació i primer ús pas a pas.

[softcatala.org/ia-local](https://www.softcatala.org/ia-local/)

<!-- end_slide -->

# Quin model, segons la teva RAM

**Recomanacions per treballar en català**, basades en les
[avaluacions de models d'IA de Softcatalà](https://www.softcatala.org/ia-local/models-en-catala/llm/).

| Memòria de l'ordinador | Model recomanat | Alternativa |
| --- | --- | --- |
| 8 GB | Qwen3.5 9B · Q4 | Gemma 3 4B · Q4 |
| 16 GB | Gemma 3 12B · Q4 | Qwen3 14B · Q4 |
| 32 GB | Muse-Glimmer 30B · Q4 | Qwen3.8 27B · Q4 |

**Transcripció d'àudio:**
- **whisper-large-v3-ca-3catparla** (Aina): més precisió.
- **whisper-large-v3-turbo** — més ràpid, qualitat similar.

**Avís honest:** els models Qwen (xinesos) poden evitar certs temes
històrics i polítics. Pesos oberts no vol dir neutralitat.

<!-- end_slide -->

# Demostració: revisar codi en català

**El meu equip:** Ryzen AI Max+ PRO 395 · Radeon 8060S · 128 GB de RAM.
**Qwen CLI → llama.cpp local → Qwen3-Coder-Next Q4_K_M.**

```python
def mitjana(valors):
    return sum(valors) / len(valors)
```

**Encàrrec:** detecta l'error, corregeix-lo i proposa tres proves.
Respon en català. Si la llista és buida, cal retornar `None`.

```bash
bash demo-qwen.sh
```

<!-- end_slide -->

# Demostració: resultat comprovat

Qwen detecta un **ZeroDivisionError** quan la llista és buida.

```python
def mitjana(valors):
    if len(valors) == 0:
        return None
    return sum(valors) / len(valors)

assert mitjana([1, 2, 3]) == 2.0
assert mitjana([10, 20]) == 15.0
assert mitjana([]) is None
```

**3 proves superades** en executar el codi amb Python.

<!-- end_slide -->

# Quant triga? Primera consulta i repetició

**Maquinari:** AMD Ryzen AI Max+ PRO 395 · Radeon 8060S · 128 GB RAM.\
**Model LLM:** Qwen3-Coder-Next · 80B MoE (actius 3B) · Q4_K_M (~48,4 GB).\
**Execució:** Qwen CLI → llama.cpp local amb acceleració GPU.

| Mesura | Sense *cache* | Amb *cache* |
| --- | --- | --- |
| Temps total | **46,6 s** | **16,6 s** |
| Prompt | 38,2 s | 9,6 s |
| Generació | 7,0 s · 199 tokens | 6,0 s · 172 tokens |
| Tokens reutilitzats | 0 | 11.431 |

**La generació es manté en uns 28–29 tokens/s:** l'estalvi principal és processar menys context.

<!-- end_slide -->

# Comença aquesta setmana

1. **Comprova el teu equip** amb l'eina de compatibilitat.
2. **Instal·la** LM Studio o Ollama.
3. **Descarrega el model** que et toqui segons la RAM.
4. **Prova-ho:** redacció, resum o transcripció.

Tot el recorregut, pas a pas, a la guia de Softcatalà:

## [softcatala.org/ia-local](https://www.softcatala.org/ia-local/)

<!-- end_slide -->

<!-- alignment: center -->
<!-- no_footer -->
<!-- jump_to_middle -->

**Moltes gràcies!**

<span style="color: #ff5555">\*\*\*    \*\*\*</span>\
<span style="color: #ff5555">\*\*\*\*\*  \*\*\*\*\*</span>\
<span style="color: #ff5555">\*\*\*\*\*\*\*\*\*\*\*\*\*\*</span>\
<span style="color: #ff5555">\*\*\*\*\*\*\*\*\*\*\*\*</span>\
<span style="color: #ff5555">\*\*\*\*\*\*\*\*</span>\
<span style="color: #ff5555">\*\*\*\*</span>\
<span style="color: #ff5555">\*\*</span>
