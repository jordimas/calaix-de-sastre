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

| Equip | Preu aprox. | Gemma 3 12B |
| --- | ---: | ---: |
| PC Intel / AMD · 32 GB · GPU integrada | 800–1.000 € | 3–6 tok/s |
| PC RTX 5060 Ti GPU (16 GB) · 32 GB | 1.500–2.000 € | 35–50 tok/s |
| MacBook Air M5 · 13" · 16 GB  | 1.300–1.500 € | 12–16 tok/s |

* **Tokens/s de generació estimats amb Gemma 3 12B a 4 bits**,
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

# Eines per executar-ho a casa

| Eina | Per a qui |
| --- | --- |
| **LM Studio** | Descoberta fàcil de models, UI amable |
| **Ollama** | Terminal + UI, més control |
| **AnythingLLM** | Consultar els teus documents (RAG) |

Totes tres funcionen a **macOS, Windows i Linux**.

Les tres estan documentades a la guia de Softcatalà, amb instruccions
d'instal·lació i primer ús pas a pas.

<!-- end_slide -->

# Quin model, segons la teva RAM

| RAM | Recomanat | Alternativa |
| --- | --- | --- |
| 8 GB | Qwen3.5 9B · Q4 | Gemma 3 4B |
| 16 GB | Gemma 3 12B · Q4 | Qwen3 14B |
| 32 GB | Mistral 30B · Q4 | Qwen3 27B · Q4 |

**Transcripció d'àudio:**
- **whisper-large-v3-ca-3catparla** (projecte Aina) — millor precisió en català.
- **whisper-large-v3-turbo** — més ràpid, qualitat similar.

**Avís honest:** els models Qwen (xinesos) poden evitar certs temes
històrics i polítics. Pesos oberts no vol dir neutralitat.

<!-- end_slide -->

# Demostració: revisar codi en català

**El meu equip:** Ryzen AI Max+ PRO 395 · Radeon 8060S · 122 GiB de RAM utilitzable.
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

**Maquinari:** AMD Ryzen AI Max+ PRO 395 · Radeon 8060S · 122 GB RAM.\
**Model LLM:** Qwen3-Coder-Next · 80B MoE (actius 3B) · Q4_K_M (~48,4 GB).\
**Execució:** Qwen CLI → llama.cpp local amb acceleració GPU.

| Mesura | Sense *cache* | Amb *cache* |
| --- | --- | --- |
| Temps total | **46,6 s** | **16,6 s** |
| Processament del prompt | 38,2 s | 9,6 s |
| Generació de la resposta | 7,0 s · 199 tokens | 6,0 s · 172 tokens |
| Tokens de context reutilitzats | 0 | 11.431 |

**La generació es manté en uns 28–29 tokens/s:** l'estalvi principal és processar menys context.

<!-- end_slide -->

# Comença aquesta setmana

1. **Comprova el teu equip** amb l'eina de compatibilitat.
2. **Instal·la** LM Studio o Ollama.
3. **Descarrega el model** que et toqui segons la RAM.
4. **Prova-ho** amb una tasca real: redacció, resum o transcripció.

Tot el recorregut, pas a pas, a la guia de Softcatalà:

## [softcatala.org/ia-local](https://www.softcatala.org/ia-local/)

<!-- end_slide -->

<!-- alignment: center -->

# Moltes gràcies!
