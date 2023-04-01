# Algorisme de recomanacions de Twitter i llengües

El 31 de març de 2023 [es va publicar](https://twitter.com/elonmusk/status/1641876892302073875) el codi de l'algorisme de Twitter.

Cal destacar que una anàlisi amb un codi com aquest no pot ser mai concloent: no es té certesa que aquesta sigui la versió del codi que realment s'executa, poden faltar mòduls importants que impacten el sistema (per exemple, càlculs de prediccions fetes en altres sistemes que es guarden directament en l'emmagazematge i impacten el comportament). És difícil també entendre algunes relacions si el codi no s'executa, cosa que no és possible.

Algunes coses que he observat respecte al tractament de llengües

**1**. Selecció de candidats

A molt alt nivell els algorismes de recomanació tenen dos grans parts: la selecció de candidats, candidats potencialment a recomanar, i rànquing on s'ordenen per rellevància basant-se en moltes característiques (preferències de l'usuari, qualitat del contingut, etc).

La selecció de candidats és molt important ja que fa un subcojunt petit de contingut sobre el que treballa després l'algorisme. El contingut que no entri aquí mai serà recomanat. Després la fase de ràquing es decidirà quin pes li donem a cada contingut, però només dels que s'han escollit.

Aquí destacar que en el procés de selecció de candidats es cerca específicament contingut provinent [d'usuaris que seguim, el país, i l'idioma](https://github.com/twitter/the-algorithm/blob/7f90d0ca342b928b479b512ec51ac2c3821f5922/cr-mixer/server/src/main/scala/com/twitter/cr_mixer/candidate_generation/FrsTweetCandidateGenerator.scala#L72). 

Tots aquests paràmetres es poden escollir al perfil de l'usuari, podeu canviar-los i veure quin impacte té en el contingut que veieu.


**2**. El català es troba entre les [51 llengües que](https://github.com/twitter/the-algorithm/blob/7f90d0ca342b928b479b512ec51ac2c3821f5922/home-mixer/server/src/main/scala/com/twitter/home_mixer/functional_component/gate/SupportedLanguagesGate.scala#L18) Twitter considera que tenen [una traducció prou completa](https://github.com/twitter/the-algorithm/blob/7f90d0ca342b928b479b512ec51ac2c3821f5922/home-mixer/server/src/main/scala/com/twitter/home_mixer/functional_component/gate/SupportedLanguagesGate.scala#L12). Això és interessant perquè crea una relació directa entre el fet que la traducció sigui completa i el tractament que se li donarà en l'algorisme.

Aquesta informació sembla usar-se amb el subsistema SimClusters que s'usa per intentar descobrir i recomanar comunitats. Sembla usar com a senyal en moltes parts de l'aplicació tal com expliquen en [aquest article](https://dl.acm.org/doi/pdf/10.1145/3394486.3403370).

**3**. A la funció de boosting (donar més pes) de l'algorisme de rànquing de les piulades es té en compte la llengua que l'usuari té configurada a la UI i es [baixa la puntuació](https://github.com/twitter/the-algorithm/blob/7f90d0ca342b928b479b512ec51ac2c3821f5922/src/java/com/twitter/search/earlybird/search/relevance/scoring/FeatureBasedScoringFunction.java#L589) si el contingut no es coincideix. 

També en aquest [fragment de codi](https://github.com/twitter/the-algorithm/blob/ec83d01dcaebf369444d75ed04b3625a0a645eb9/home-mixer/server/src/main/scala/com/twitter/home_mixer/functional_component/decorator/HomeTweetTypePredicates.scala#L125) sembla indicar com filtren per idioma. És important destacar el *device_language_matches_tweet_language*.
Primer miren la llengua que l'usuari té configurada però també miren després la lengua del dispositiu. 

És a dir, el que sempre hem dit, configurar-se la llengua del dispositiu és important, però també la interfície de l'usuari i les llengües preferides. Tot.


