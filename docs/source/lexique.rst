Lexique / vocabulaire commun
============================

Le monde de l'entreprise et de la CAE possèdent leur jargon, avec parfois
plusieurs mots pour désigner une même chose. Au sein d'autonomie, il est
souhaitable d'utiliser un vocabulaire cohérent (toujours le même terme pour
désigner la même chose).

Les termes listés en titre de sections sont les **termes dont l'usage est
recommandé**.

Personne
--------

code : `User`.

Catégorie la plus large de personnes, englobe toutes **Travailleurs**,
**Entrepreneurs**, et **Personne extérieure**.

Travailleur
------------

code : une partie des ``User`` (+ ``UserData``), réunion des groupes ``contractor`` et ``manager``.

Toute personne en contrat de travail ou CAPE avec la coopérative.

Inclut entrepreneurs salariés (en CESA, CDI, ou CAPE), CDD et équipe d'appui.

.. warning:: À ne pas confondre avec *« salarié »* ou *« entrepreneur »*, «
             utilisateur » également n'a pas grand sens métier.

Entrepreneur
------------

code : une partie des ``User`` (+ ``UserData``), groupe ``contractor``

Entrepreneur, qu'il soit en CAPE, ou en CESA. Inclut également les CDD.

Accompagnateur
--------------

code: une partie des ``User`` (+ ``UserData``) : groupe ``manager``

Personne de l'équipe d'appui faisant le suivi d'un entrepreneur.

.. note:: Parfois appelée, selon la CAE *« chargée d'accompagnement »*, *«
          conseiller »* ou *« chargé d'accompagnement »*.


Personne extérieure
-------------------

Dans le code : ``User`` (+ ``UserData``) : groupe ``external``

Personnes référencées dans autonomie comme ``User`` mais n'ayant pas forcément
de lien contractuel long avec la coopérative. Ces personnes n'ont généralement
pas d'identifiants pour se connecter à autonomie, mais on peut les inscrire à
des Ateliers, ou elle peuvent être notées comme (co)-organisatrices d'ateliers.

.. warning:: En chantier : le groupe ``external`` n'existe pas encore.

Enseigne
--------

code : ``Company``.

Nom commercial regroupant un ou plusieurs entrepreneurs.

.. warning:: À éviter (source de confusion) : *« entreprise »* ou *« activité »*.


