# IA en local · Llibertat i sobirania

Presentació en català de 16 diapositives, preparada per a projecció.

Contingut: context i sobirania, IA local i lliure, casos d'ús,
maquinari, eines, models i una demostració de revisió de codi en català.

## Obrir al terminal actual

Cal tenir `presenterm` instal·lat i disponible al `PATH`.

```bash
./presentar-ia-local.sh
```

El llançador conserva la mida de lletra del terminal i presenterm recarrega
la presentació quan es desa el fitxer. Activeu la pantalla completa i
ajusteu la lletra abans de presentar. La mida mínima comprovada és de
**72 columnes × 22 files**, amb presenterm 0.16.1.

Espai o fletxes per navegar; `q` per sortir.

## Obrir una finestra de projecció

En un escriptori GNOME amb Ptyxis:

```bash
./presenta.sh
```

Obre una finestra independent a pantalla completa amb Ubuntu Mono de 28 punts.
La configuració queda a `.terminal-config/`. El nombre de columnes i files
resultant depèn de la resolució i de l'escala de la pantalla.

## Comprovar la mida de projecció

Des del terminal i amb la mida de lletra que fareu servir:

```bash
stty size
./presentar-ia-local.sh --validate-overflows
```

`stty size` mostra primer les files i després les columnes. Amb menys de
22 files o 72 columnes, reduïu la lletra o amplieu la finestra.
La validació de presenterm comprova totes les diapositives i mostra un error
si hi ha desbordaments; si tot cap, obre la presentació normalment.

Les estimacions de memòria no són mesures de rendiment. Els exemples
requereixen les eines i els models corresponents i no s'executen automàticament.
