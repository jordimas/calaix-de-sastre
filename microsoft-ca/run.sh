python3 tbx-to-po.py MicrosoftTermCollection-ca-ES.tbx ca-ES.po
python3 tbx-to-po.py MicrosoftTermCollection-ca-ES-valencia.tbx ca-ES-valencia.po

python3 tbx-to-po.py MicrosoftTermCollection-es-ES.tbx es-ES.po
python3 tbx-to-po.py MicrosoftTermCollection-es-MX.tbx es-MX.po

python3 cmp-po.py ca-ES.po ca-ES-valencia.po > ca-ca-ES-valencia.txt
python3 cmp-po.py es-ES.po es-MX.po > es-ES-es-MX.txt
