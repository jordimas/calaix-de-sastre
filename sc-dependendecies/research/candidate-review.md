# Revisió d’indicis de reutilització

S’han consultat les metadades i README dels repositoris i els fitxers a les revisions identificades a l’informe. El material complet es conserva a `candidate-review-material.json`; les decisions i evidències revisades són a `reviewed-candidate-findings.json`.

| Producte | Recurs | Evidència i abast |
| --- | --- | --- |
| Itzune (https://github.com/xezpeleta/itzune-models) | nmt-softcatala | `bleu.sh` instal·la les eines de Softcatalà i executa `model_to_txt`. El README atribueix els scripts adaptats al basc a Softcatalà. No es tracta d’un fork declarat. |
| Uploader Recny Model (https://github.com/fscholze/uploader-recny-model-webapp) | open-dubbing | El servidor original `fscholze/uploader-recny-model-server` instal·la al contenidor una variant d’open-dubbing. La variant és un fork de Softcatalà; es compta l’aplicació integradora, no aquest fork. |
| OpenDubbing Docker (https://github.com/kotet/opendubbing-docker) | open-dubbing | Dependència explícita al manifest i script que executa el CLI per doblar fitxers a japonès. Es tracta d’un entorn de desplegament, sense prova de nombre d’usuaris. |
| Dubbing Project (https://github.com/meherubahasin/dubbing_project) | open-dubbing | Dependència a requirements i codi que executa el CLI com a alternativa al flux propi de doblatge. |
| ALT Linux (https://www.altlinux.org/) | sinonims-cat | La recepta `mythes-ca` publicada per l’organització ALT Linux descarrega el tesaurus de Softcatalà i instal·la els fitxers `.dat` i `.idx`. Es compta la distribució, no el repositori de receptes com a producte nou. |
| Fedora (https://fedoraproject.org/) | sinonims-cat | S’ha baixat la recepta del repositori oficial de Fedora; declara com a font el `.oxt` de Softcatalà i instal·la el tesaurus. La còpia local és `fedora-mythes-ca.spec`. |

S’exclouen les mencions d’open-dubbing incrustades al README de faster-whisper dins de METADATA a XINNIAN_PI i Eiinmado. També s’exclouen el catàleg generat de PyPI de houseofsuns i els repositoris de major i praiskup que copien receptes de Fedora per analitzar-les.

El catàleg web de Hugging Face s’ha utilitzat com a alternativa per inventariar els models quan l’API no ha respost. Els datasets i Spaces s’han consultat a l’API pública. L’inventari de models no es presenta com a exhaustiu ni com una prova de reutilització externa.
