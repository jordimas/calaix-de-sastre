# Demostració de Qwen CLI en local

Mesura feta el 18 de setembre de 2026. Dues execucions, model ja carregat en totes dues.

- Equip: AMD Ryzen AI Max+ PRO 395, Radeon 8060S, 122 GiB de RAM utilitzable segons Linux.
- Sistema: Ubuntu 26.04.1 LTS.
- Client: Qwen Code 0.20.0, amb --safe-mode i directori de treball buit.
- Servidor: llama.cpp local, http://localhost:9090/v1.
- Model verificat a /v1/models: qwen3-coder-next, 79.674.391.296 paràmetres, Q4_K - Medium.
- Context del servidor: 65.536 tokens.
- Temps de paret de Qwen CLI: 46,59 s (inclou inici, prompt i resposta; no la càrrega del model).
- Temps de l'API reportat pel client: 45,489 s.
- Entrada: 14.552 tokens, inclòs el context afegit pel client; sortida: 199 tokens.
- Qwen no ha fet crides a eines ni ha modificat fitxers.
- No s'ha mesurat el temps fins al primer token; la velocitat de generació es calcula amb els comptadors del servidor detallats més avall.
- Les tres comprovacions s'han executat després amb Python, fora de Qwen CLI.

## Reproducció

Amb el servidor configurat i engegat, executeu des de presentacions:

```bash
bash demo-qwen.sh
```

El prompt és a demo-qwen-prompt.txt. El resultat pot variar entre execucions.

## Resposta completa del model

L'error és que quan `valors` és una llista buida, `len(valors)` és 0, i la divisió `sum([]) / 0` (0/0) genera un `ZeroDivisionError`.

**Correcció:** Afegir una comprovació per retornar `None` quan la llista estigui buida.

```python
def mitjana(valors):
    if len(valors) == 0:
        return None
    return sum(valors) / len(valors)
```

**Tres comprovacions amb assert:**

```python
assert mitjana([1, 2, 3]) == 2.0      # llista normal
assert mitjana([10, 20]) == 15.0      # dos valors
assert mitjana([]) is None            # llista buida
```

## Repetició i memòria cau

Mateixa ordre i mateix fitxer de prompt, amb una nova sessió de Qwen CLI.

| Mesura | Primera execució | Repetició |
| --- | ---: | ---: |
| Temps de paret | 46,59 s | 16,57 s |
| Entrada (inclou context del client) | 14.552 tokens | 14.561 tokens |
| Entrada reutilitzada | 0 tokens | 11.431 tokens |
| Sortida | 199 tokens | 172 tokens |
| Processament de prompt al servidor | ~38,22 s | ~9,55 s |
| Generació al servidor | ~6,98 s | ~5,96 s |

Els temps del servidor provenen de les diferències dels comptadors de /metrics
abans i després de les execucions. No s'han detectat altres peticions en aquests intervals.
La repetició processa 3.130 tokens no reutilitzats. No és un encert de memòria cau complet:
el context afegit pel client no és idèntic entre les dues sessions.
La generació és d'aproximadament 28–29 tokens/s en totes dues proves;
el guany principal ve de reutilitzar el context. Les respostes tenen longitud diferent.
No s'ha mesurat una pregunta de seguiment dins la mateixa conversa.
No s'ha mesurat el temps fins al primer token.

### Resposta de la repetició

L'error és que `len(valors)` és 0 per a una llista buida, causant una divisió per zero (`ZeroDivisionError`). A més, `sum([])` és 0, així que l'expressió donaria `0/0`.

**Correcció:**
```python
def mitjana(valors):
    if not valors:  # llista buida
        return None
    return sum(valors) / len(valors)
```

**Comprovacions amb assert:**
```python
assert mitjana([]) is None
assert mitjana([2, 4]) == 3.0
assert mitjana([1, 2, 3, 4, 5]) == 3.0
```
