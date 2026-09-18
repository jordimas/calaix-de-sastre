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

<span style="color: #b6eada">**Jordi Mas**</span>

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

A principis dels anys 2000 usar Linux era molt més complex que ara: faltava suport de maquinari i aplicacions, i calia millorar la usabilitat, entre altres aspectes. Molta gent no creia que pogués ser mai una opció, però amb els anys els problemes s'han solucionat i ha esdevingut una peça clau del món digital actual.

Amb la IA local passa el mateix, però a un ritme més ràpid. Models i maquinari estan evolucionant ràpidament per fer-la possible. Encara no és una solució perfecta ni funciona per a tots els casos d'ús, però hi arribarem.

<!-- end_slide -->


# Què és una IA local?

**IA local:** el model s'executa al nostre ordinador
o servidor, sense enviar les consultes a un servei extern.

- **Privacitat:** controlar on van les dades.
- **Autonomia:** poder treballar sense xarxa.
- **Continuïtat:** conservar les versions.
- **Control:** triar models i integracions.

Per fer això, es requereixen **pesos oberts**.

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

**En lot**

- Resumir, traduir i classificar documents.
- Extreure dades de factures i transcriure enregistraments.
- Revisar codi i generar proves.

Podem esperar i programar la càrrega de CPU/GPU.

**Temps real**

- Consultar documents i assistir en la redacció.
- Transcriure en directe i conversar per veu.
- Programació agentica

Cal bona latència i recursos disponibles al moment.

<!-- end_slide -->

# Local també té costos

- Maquinari, electricitat i manteniment.
- Compromisos de qualitat i velocitat.
- Responsabilitat sobre permisos i dades.

No sempre és més barat ni consumeix menys.

**Comparem el cost per tasca ben resolta.**

<!-- end_slide -->

# Abans de comprar

1. Quina tasca i quina llengua?
2. Quina qualitat mínima?
3. Quants usuaris alhora?
4. Quina espera i quant context?

**Comencem amb l'equip que ja tenim.**

<!-- end_slide -->

# Quin maquinari?

- **CPU + RAM:** reutilitzar l'equip actual.
- **GPU dedicada:** acceleració amb límit de VRAM.
- **Memòria unificada:** CPU i GPU la comparteixen.
- **Servidor:** recursos compartits entre usuaris.

Més memòria no garanteix més velocitat.

<!-- end_slide -->

# Punts de partida

| Equip | Primera prova |
|-------|---------------|
| CPU + 16 GB RAM | 1–4B quantitzat |
| GPU 8–12 GB VRAM | 7–8B quantitzat |
| GPU 16–24 GB VRAM | 14B quantitzat |

Estimacions, no garanties.
Reservem memòria per al context i el sistema.

**Mesurem primer; ampliem després.**

<!-- end_slide -->

# Models densos i MoE

**Dens:** utilitza tots els paràmetres per processar cada token.

**MoE (barreja d’experts):** activa només una part dels experts
per a cada token.

- Paràmetres totals: pes del conjunt del model.
- Paràmetres actius: part que intervé en cada token.

**Menys paràmetres actius no implica carregar menys pesos.**

<!-- end_slide -->

# Quanta memòria?

Pesos ≈ paràmetres × bits / 8

| Model | 16 bits | 4 bits |
|-------|---------|--------|
| 3B | 6 GB | 1,5 GB |
| 8B | 16 GB | 4 GB |
| 14B | 28 GB | 7 GB |
| 32B | 64 GB | 16 GB |

GB decimals. Només pesos; càlcul teòric.
**Cal sumar context, memòria de treball i sistema.**

<!-- end_slide -->

# Quantització i context

**Quantitzar:** menys precisió, menys memòria.

- La qualitat pot variar segons la tasca.
- Més context necessita memòria addicional.
- Més usuaris també poden necessitar-ne més.

En MoE, pesos totals ≠ paràmetres actius.

**Cabre al disc no vol dir cabre a la GPU.**

<!-- end_slide -->

# Les capes del programari

```text
Interfície: terminal o xat
           ↓
Motor d'inferència
           ↓
Model i pesos
           ↓
CPU / GPU / memòria
```

GGUF és un format, no una llicència.

<!-- end_slide -->

# llama.cpp

**Control des del terminal**

- Models compatibles en format GGUF.
- Execució a CPU o GPU.
- Eines de terminal i servidor local.

```bash
llama-cli -m ./model.gguf -p "Hola!"
```

Cal disposar d'un model compatible.

<!-- end_slide -->

# Compatibilitat amb llama.cpp

| Plataforma | Acceleració |
|------------|-------------|
| NVIDIA | CUDA |
| AMD | HIP / ROCm o Vulkan |
| Intel | SYCL o Vulkan |
| Apple Silicon | Metal a macOS |
| CPU x86 / ARM | CPU |

**Comprovem GPU exacta, sistema i versió.**

<!-- end_slide -->

# Ollama

**Gestió pràctica de models**

```bash
ollama list
ollama run NOM_DEL_MODEL_LOCAL
```

Substituïm el nom pel d'un model disponible.

També té funcions al núvol: triem execució local.
La descàrrega inicial necessita connexió.

<!-- end_slide -->

# Interfície gràfica i veu

**LM Studio**

Xat i documents locals amb interfície gràfica.
Pot funcionar sense xarxa un cop preparat.

**whisper.cpp**

Transcripció local d'àudio.

Revisem la llicència de cada eina i model.

<!-- end_slide -->

# Sobirania també és llengua

- Avaluar el català amb exemples propis.
- Adaptar vocabulari i registres.
- Crear eines per a les nostres comunitats.

**Salamandra:** família multilingüe amb català.
La versió 7B Instruct declara Apache 2.0.

«Multilingüe» no garanteix un bon català.

<!-- end_slide -->

# Com ho avaluem?

Preparem **20 tasques representatives**.

- Qualitat, català i instruccions.
- Temps fins a la resposta completa.
- RAM, VRAM i consum.
- Errors i preguntes difícils.

Anotem model, quantització, context i equip.

<!-- end_slide -->

# Resultats comparatius en català

**Pendent d’incorporar els resultats per model.**

Compararem qualitat del català, seguiment d’instruccions
i resolució de les tasques amb el mateix conjunt de proves.

Indicarem versió del model, quantització i equip utilitzat.

<!-- end_slide -->

# Selecció de models

**Pendent de concretar els models recomanats.**

- Model petit per començar amb l’equip disponible.
- Model d’ús general amb bon rendiment en català.
- Model especialitzat segons la tasca.

Per a cada recomanació: qualitat, memòria necessària i llicència.

<!-- end_slide -->

# Models lliures fora del nostre equip

**Pendent de concretar les opcions i els serveis.**

Un model lliure també es pot executar en un servidor remot.
La llicència del model i les condicions del servei són diferents.

Compararem control de les dades, cost i possibilitat
de migrar a una execució local.

**Lliure no vol dir necessàriament gratuït.**

<!-- end_slide -->

# Comencem!

1. Una tasca concreta.
2. Un model petit.
3. Una eina compatible.
4. Una prova sense xarxa.
5. Avaluació en català.

**Local: més capacitat de decisió.**
**Lliure: estudiar, adaptar i compartir.**

<!-- end_slide -->

# Preguntes?
