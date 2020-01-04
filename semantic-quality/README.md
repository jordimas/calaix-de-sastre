
A sets of scripts to use machine translation to spot semantic quality issues
in already existing translations translations


* program-apertium-fr.py

Concept: if FR and ES translations differ from CA we may have a problem

How it works:

1) Translates fr -> ca using Apertium
2) Translates es -> ca using Apertium
3) If a) and b) are similiar then compares if these translations are far from 
already existing translation for Catalan and spots a potential quality problem

* program-apertium.py

Concept: if ES translation differs from CA we may have a problem

How it works:

1) Translates es -> ca using Apertium
3) if a) is far from  already existing translation for Catalan and spots a potential 
quality problem


* program.py

As program-apertium.py using Yandex instead of Apertium

