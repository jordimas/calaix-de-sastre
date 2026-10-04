# Cercador de reutilització de Softcatalà

`softcatala_reuse.py` cerca evidències de reutilització als repositoris públics de GitHub i GitLab. Python 3.10 o superior, sense dependències externes.

## Execució

Des de l’arrel del repositori, entra primer al directori:

```bash
cd reuse-softcatala
```

GitHub requereix autenticació per cercar codi: configura `GH_TOKEN` o `GITHUB_TOKEN`, o inicia sessió amb `gh auth login`. El script també accepta `GITLAB_TOKEN`, amb accés de lectura a l’API de GitLab.com. No desa ni imprimeix els tokens.

```bash
python3 softcatala_reuse.py --all-resources --output softcatala-informe
```

Descobreix tots els repositoris públics propis de l’organització Softcatala i cerca consumidors externs, sense un límit arbitrari de 30 projectes. Sense `--all-resources`, fa servir una selecció de 17 recursos. Les cerques àmplies poden durar força i consumir quota de les API.

Els resultats són:

- `products.html`: vista de productes, amb identitats revisades i evidències agregades.
- `graph-products.svg`: gràfic tipus Gource de productes, una connexió per producte i recurs.
- `products.json`: productes, repositoris associats, totes les evidències i repositoris pendents d’identificar.
- `index.html`: gràfic interactiu, filtres i evidències clicables; obre’l al navegador.
- `graph.svg`: gràfic estàtic dels resultats classificats amb evidència al codi.
- `graph-gource.svg`: arbre estàtic tipus Gource, amb fons fosc i branques de colors: Softcatalà → recurs → organització → projecte. Cada projecte enllaça a la seva evidència. Es regenera a cada desament.
- `reuse.csv`: evidències per fitxer, per treballar amb un full de càlcul.
- `reuse.json`: dades completes, recursos, configuració d’abast i limitacions.

## Ampliar GitLab

```bash
python3 softcatala_reuse.py --all-resources \
  --gitlab-search whisper --gitlab-search catalan \
  --gitlab-project https://gitlab.com/gd-pub/lettera-ink \
  --gitlab-url https://gitlab.com --gitlab-url https://git.uibk.ac.at \
  --output softcatala-informe
```

Cada servidor necessita el seu token: per exemple, `GITLAB_TOKEN_GIT_UIBK_AC_AT` per a `git.uibk.ac.at`. El token de GitLab.com no s’envia a altres servidors.

La cerca global de codi de GitLab depèn de l’autenticació, el pla i la configuració del servidor. Quan no és accessible, el script descobreix projectes pel nom/descripció i en llegeix els fitxers de text. Això pot perdre consumidors que no esmentin el recurs a les metadades. `--gitlab-project` permet afegir repositoris coneguts i `--gitlab-search` amplia els termes de descoberta.

## Repetir i ajustar

```bash
# Cerca limitada per recurs, amb límits explícits per fer una prova ràpida.
python3 softcatala_reuse.py --resource whisper-ctranslate2 \
  --max-pages 1 --max-gitlab-files 40 --output prova

# Actualitza les dades de les API; per defecte es reutilitza la memòria cau.
python3 softcatala_reuse.py --all-resources --refresh

# Refés el gràfic amb les dades desades, sense peticions de xarxa.
python3 softcatala_reuse.py --from-report softcatala-informe/reuse.json \
  --output softcatala-informe-regenerat
```

`--cache` canvia el directori de memòria cau; `--offline` només llegeix respostes ja desades. Una execució interrompuda conserva les respostes descarregades. La memòria cau no caduca automàticament: fes servir `--refresh` per actualitzar-la.

`--resources-file` accepta una llista JSON de recursos amb `name`, `terms` i `queries`, per incloure noms antics, imports, URL i identificadors de paquets:

```json
[
  {
    "name": "whisper-ctranslate2",
    "terms": ["whisper-ctranslate2", "whisper_ctranslate2", "Softcatala/whisper-ctranslate2"],
    "queries": ["whisper-ctranslate2", "whisper_ctranslate2"]
  }
]
```

`terms` identifica les línies d’evidència; `queries` dirigeix les cerques de codi de GitHub. Les cerques globals GitLab utilitzen el nom del recurs o la referència de l’organització. `--evidence-file` permet incorporar una llista JSON de troballes revisades manualment, amb la mateixa estructura dels elements de `findings` de `reuse.json`.

`--gitlab-projects-only` omet la descoberta i limita GitLab als projectes indicats explícitament amb `--gitlab-project`.

L’informe HTML, SVG, CSV i JSON es desa cada 10 cerques o lectures de repositoris completades i en acabar cada plataforma. `--checkpoint-every N` canvia l’interval; `0` desactiva els desaments periòdics. Els informes provisionals mostren l’estat parcial i el progrés. Cada fitxer es substitueix de manera atòmica: pots consultar-lo mentre continua la cerca. Recarrega l’HTML per veure les dades noves.

## Interpretació

`confirmed` significa que una regla identifica una dependència, instal·lació, distribució, diccionari incorporat, import/invocació en codi o integració explícita com a component extern (p. ex. `.gitmodules` o `third_party/`). No prova ús en producció. Una cadena amb un nom o URL en codi no basta. Les mencions documentals es marquen `needs_review`; els crèdits i alguns catàlegs es marquen `excluded`. Els forks es descarten de les sortides. Els gràfics i la taula HTML mostren només ús o integració amb evidència; JSON/CSV conserven les altres candidates per revisar-les. Revisa les evidències abans de publicar conclusions.

També es descarten els miralls declarats a les metadades, al nom del repositori o amb descripcions com «mirror of»/«fork of». Els repositoris copiats que no declarin aquesta relació requereixen revisió manual.

El recompte identifica repositoris, no productes independents: una aplicació que incorpora LanguageTool pot aparèixer per la reutilització indirecta del diccionari. `project_names.json` permet posar noms llegibles a les etiquetes, identificant cada repositori per `organització/nom` o URL. Canviar-ne el nom no fusiona repositoris diferents. El repositori exacte continua al JSON/CSV i a l’enllaç d’evidència.

## Vista de productes

`products_catalog.json` defineix la identitat de cada producte: `id`, `name`, `organization`, `kind`, `url`, `identity_source`, `reviewed` i una llista d’URL exactes a `repositories`. Només les entrades revisades entren a la vista de productes, i només si hi ha evidència d’ús. Un mateix producte pot tenir diversos repositoris; es fusionen les connexions i es conserven totes les evidències. Una còpia de LanguageTool dins una altra aplicació no s’assigna automàticament a LanguageTool. No es fusionen repositoris pel nom, ni es converteixen miralls personals de Nixpkgs en nous productes.

El catàleg inicial és parcial. La identitat s’ha associat amb les descripcions i fonts dels repositoris; les regles d’evidència no certifiquen ús en producció. `products.json` conserva els repositoris amb indicis que no tenen una associació revisada dins les categories seleccionades, per ampliar el catàleg sense inventar identitats. Un nombre petit de productes mostrats no implica poca reutilització: implica que queden identitats per revisar.

Per defecte es mostren totes les categories revisades: aplicacions, serveis, distribucions, biblioteques, eines i models. Pots restringir la vista sense repetir la cerca de xarxa:

```bash
python3 softcatala_reuse.py --from-report softcatala-reuse-report/reuse.json \
  --product-kind application --product-kind service --product-kind distribution
```

Edita el catàleg i regenera amb `--from-report` per ampliar la vista de productes. `--products-file` permet un catàleg alternatiu. `--reclassify-cached` reaplica les regles actuals als fitxers GitHub de la memòria cau, sense xarxa.

## Fonts fora de GitHub/GitLab

La cerca per noms de paquets i URL de GitHub no detecta totes les reutilitzacions: algunes còpies antigues només atribueixen Softcatalà pel nom, i alguns recursos viuen en altres repositoris o registres. `external_sources.json` configura comprovacions revisades de fonts oficials. S’executen abans de les cerques i fan servir la mateixa memòria cau i polítiques de reintent.

- Chromium: es comprova la dependència a `DEPS` i es llegeix l’atribució a la revisió exacta declarada de `hunspell_dictionaries`, mitjançant Gitiles. El recurs és el MySpell 0.1 de 2002: una còpia històrica de la família de diccionaris, no la versió actual del paquet. El node diu Chromium; no s’estén aquesta evidència automàticament a Chrome, Edge o altres navegadors.
- Firefox: es comproven a l’API oficial de Mozilla Add-ons el tipus `dictionary`, l’autoria de Softcatalà i la compatibilitat amb Firefox. La integració és un diccionari opcional, no una prova que vingui instal·lat de sèrie.

Per afegir o actualitzar aquestes evidències en un informe existent:

```bash
python3 softcatala_reuse.py --from-report softcatala-reuse-report/reuse.json \
  --update-external-sources
```

`--no-external-sources` omet aquestes comprovacions; `--external-sources-file` permet una configuració alternativa. Si una comprovació falla, no s’hi afegeix una integració positiva. Els errors queden a l’informe. `--from-report` sense `--update-external-sources` continua sense fer peticions de xarxa.

## Trobar més integracions

La descoberta ha de buscar també el recurs distribuït, no només el nom actual del seu repositori. Per a `catalan-dict-tools`, el script ja cerca `softcatala-spell`, `ispellcat` i l’URL històric `softcatala.org/diccionaris/actualitzacions`. Són pistes de la família de diccionaris; no impliquen que es distribueixi la versió actual del paquet. Pots afegir altres noms i URL amb `--resources-file`.

`discovery_candidates.json` conté pistes documentades en fonts primàries: paquets de distribucions, catàlegs d’extensions i avisos de programari de tercers. No entra automàticament al gràfic. Per cada candidat cal:

1. Identificar l’origen de Softcatalà amb URL, atribució o contingut del paquet.
2. Comprovar la incorporació al producte mitjançant manifests, scripts de construcció, registre d’extensions o avisos de components distribuïts.
3. Registrar la versió i distingir ús directe, component incorporat, complement opcional o reutilització indirecta.
4. Confirmar la identitat del producte i descartar còpies/miralls com a productes nous.
5. Incorporar una comprovació reproduïble a `external_sources.json` quan l’adaptador la suporti, o una troballa revisada amb `--evidence-file`; associar-la a `products_catalog.json`.

El seguiment en tercers de Softcatalà ajuda a descobrir candidats, però els números de versió poden ser antics: la verificació final ha de consultar la font del distribuïdor. Els avisos de llicències permeten detectar també productes propietaris; una llicència genèrica de Hunspell no prova que incorporin el diccionari català de Softcatalà.

No estima usuaris: les estrelles del repositori són només metadades. No limita la sortida a un nombre de projectes. Tampoc garanteix exhaustivitat: GitHub limita cada consulta a 1.000 resultats i al codi indexat de la branca per defecte; GitLab té restriccions pròpies. Els límits de mida, paginació, fitxers i els errors apareixen a l’informe. Els miralls no identificats com a bifurcacions poden aparèixer com a projectes diferents.

## Dependències inverses de Debian

```bash
python3 debian_reverse_dependencies.py
python3 debian_reverse_dependencies.py --offline
python3 debian_integrations.py
python3 softcatala_reuse.py --from-report softcatala-reuse-report/reuse.json \
  --evidence-file debian-report/reviewed-integrations.json
```

Baixa l’índex oficial `stable/main/amd64` i exporta `debian-report/dependencies.json` i `.csv`. Es pot canviar la distribució amb `--suite`, l’arquitectura amb `--architecture` i el component amb `--component`. `--refresh` actualitza la memòria cau. Només compta dependències explícites dels paquets catalans; dependències genèriques del motor Hunspell no compten. Distingeix dependències obligatòries, recomanacions, suggeriments i alternatives. Els paquets binaris s’agrupen també pel paquet font; cap dels dos recomptes representa automàticament productes. Les troballes són candidats per revisar abans d’afegir-los al gràfic.

`debian_integrations.py` exporta només les correspondències revisades de `debian-products.json` i les afegeix al catàleg de productes. Els tres metapaquets s’agrupen sota Debian. LibreOffice s’inclou pel tesaurus `mythes-ca`, atribuït a Joan Montané de Softcatalà al copyright oficial de Debian; `hyphen-ca` té una atribució diferent i no s’hi afegeix com a recurs de Softcatalà. El nom `catalan-dict-tools` al gràfic representa la família de recursos dels diccionaris, sense afirmar que tots siguin la versió actual d’aquest repositori.

## Recursos de Hugging Face

```bash
python3 huggingface_resources.py
python3 softcatala_reuse.py --resources-file huggingface-resources.json \
  --merge-report softcatala-reuse-report/reuse.json
```

Descobreix models, datasets i Spaces públics de `softcatala`, amb paginació i memòria cau. `--offline` reutilitza la memòria cau; `--refresh` actualitza l’inventari. Les cerques utilitzen l’identificador complet `softcatala/nom`, que detecta tant URL com càrregues amb `from_pretrained`, `load_dataset` o `snapshot_download`. Una menció o un nom en una configuració requereix revisió; no es considera ús confirmat automàticament. `--fallback-file research/huggingface-web-resources.json` permet usar el catàleg web revisat quan l’API falla; cada entrada d’aquest origen queda marcada amb cobertura parcial. Els informes conserven aquesta procedència als recursos.

La revisió dels indicis anteriors és a `research/candidate-review-material.json` i `research/reviewed-candidate-findings.json`: les mencions dins de metadades d’un altre paquet i els catàlegs que copien receptes no compten com a productes. Les decisions manuals es conserven en regenerar i reclassificar l’informe.

## Recursos mantinguts fora de l’organització

`maintained-resources.json` inclou CTranslate2 amb el seu origen `OpenNMT/CTranslate2` i la relació de manteniment indicada per l’usuari. La vista de productes inclou també biblioteques, eines i models amb identitat revisada; es pot restringir amb `--product-kind`.

```bash
# Cerca global de CTranslate2; pot ser molt llarga.
python3 softcatala_reuse.py --resources-file maintained-resources.json \
  --merge-report softcatala-reuse-report/reuse.json

# Comprovació dirigida d’un consumidor.
python3 softcatala_reuse.py --resources-file maintained-resources.json \
  --github-repo SYSTRAN/faster-whisper --output ctranslate2-report
```

La consulta general de CTranslate2 retornava 119.552 fitxers en aquesta revisió. S’han comprovat onze consumidors i s’han trobat integracions explícites en deu: faster-whisper, WhisperX, Argos Translate, Buzz, LinguaMiner, WhisperLive, WhisperS2T, Whisper-WebUI, OpenNMT-py i OpenNMT-tf. L’ampliació és reproduïble amb `--github-repo` per a cada repositori i les evidències es conserven a `ctranslate2-expanded-report/reuse.json`. LibreTranslate no tenia evidència directa en aquesta consulta; no se li ha atribuït automàticament la dependència d’Argos Translate. La cobertura de CTranslate2 es declara dirigida a `scope.ctranslate2_search`; les consultes concretes queden a `github-coverage.json`. El gràfic no implica que s’hagin revisat les 119.552 coincidències.

## Límits de les particions

El script divideix les consultes per intervals de mida del fitxer i pagina cada interval amb fins a 100 resultats per petició. `github-coverage.json` registra la cobertura i els límits no resolts. `--refresh-search` refresca les cerques conservant la memòria cau dels fitxers; `--merge-report PATH` acumula les noves evidències amb un informe anterior. Una mida exacta amb més de 1.000 coincidències continua limitada i queda marcada com a parcial. La cerca només cobreix el codi indexat per GitHub.

## Verificació del cercador

```bash
python3 -m unittest discover -s . -p 'test_*.py'
python3 softcatala_reuse.py --help
```

## Artefactes conservats

`artifacts/` conté l’informe de la prova real de GitLab, el gràfic inicial de 30 projectes i el PNG per publicar. `research/` conserva les dades i evidències de la recerca; els dos scripts inicials han estat substituïts pels punts d’entrada reutilitzables.

`api_client.py` centralitza la memòria cau, autenticació i reintents; `storage.py`, la lectura UTF-8 i l’escriptura atòmica de JSON/CSV; `github_review.py`, la lectura de fitxers i revisions per als dos scripts de revisió. `product_catalog.is_usage` defineix la mateixa regla per als gràfics i les taules. Els exportadors Debian agrupen totes les expressions d’un mateix paquet i camp en una evidència, evitant sobreescriure dependències.

Per fusionar informes desats sense consultar la xarxa:

```bash
python3 softcatala_reuse.py --from-report softcatala-reuse-report/reuse.json \
  --merge-report ctranslate2-report/reuse.json
```

`--merge-report` es pot repetir. La fusió elimina evidències duplicades i conserva recursos, consultes i àmbits de cobertura dels informes d’origen. El SVG mostra la URL sota el nom de cada producte i cada recurs; per als recursos, usa l’origen explícit del catàleg.
