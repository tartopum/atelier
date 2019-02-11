# Manuel d'utilisation

## Clôture

La clôture a deux propriétés :

* Activée/désactivée
* Allumée/éteinte

Quand la clôture est **désactivée**, elle est nécessairement éteinte (on ne peut
pas l'allumer sans l'activer) mais la lumière d'avertissement n'est pas allumée. 
Cette fonctionnalité peut notamment être utilisée l'hivers, quand les animaux sont
rentrés et que la clôture n'est jamais allumée.

Quand la clôture est **activée**, elle peut être soit allumée (le courant passe)
soit éteinte. Dans le second cas, la lumière d'avertissement est allumée pour
prévenir que les animaux ont plus de probabilité de s'échapper.

## Lumières

Pour changer l'état d'une lumière intérieure (l'allumer si elle est éteinte et
inversement), presser le bouton correspondant pendant la durée renseignée comme
`Durée de pression des boutons` dans la configuration.

Pour changer l'état de la lumière extérieure, presser les deux boutons en même
temps pendant cette durée.

Au bout d'un certain temps sans détection de mouvement, défini par `Délai d'inactivité`
dans la configuration, les lumières intérieures s'éteignent.

## Alarme

L'alarme peut être dans trois états :

* Éteinte
* Mise en écoute
* En écoute

### Éteinte

Quand l'alarme est **éteinte**, elle n'interagit pas avec le système. Alors, le
voyant sur le boitier est vert.

L'alimentation, si elle est en mode automatique (cf. plus bas), est activée quand
l'alarme est éteinte.

### En écoute

Quand l'alarme est **en écoute**, le voyant sur le boitier est rouge. Elle se
déclenche quand un mouvement est détecté pendant la durée `Délai avant déclenchement`
définie dans la configuration, ce qui provoque :

* L'allumage de la lumière rouge d'alerte
* L'allumage de la lumière extérieure
* La sonnerie d'alarme
* L'envoi d'un SMS

Pour éteindre l'alarme une fois qu'elle a été déclenchée, il faut la désactiver.
Alors, la sonnerie s'arrête et les lumières d'alerte et extérieure s'éteignent.

Quand l'alarme passe en écoute, les lumières intérieures s'éteignent. L'alimentation,
si elle est en mode automatique (cf. plus bas), est coupée.

### Mise en écoute

Entre les deux phases, il y a la **mise en écoute**. Le voyant sur le boitier est
orange. Cette phase dure `Délai avant mise en écoute` et permet de quitter le
bâtiment sans déclencher l'alarme.

L'alarme est mise en écoute le midi et la nuit à des heures configurables. Elle
n'est jamais éteinte automatiquement, donc doit l'être manuellement.

Si l'alarme est mise en écoute automatiquement (le midi et la nuit) ou via
l'interface web et que du mouvement est détecté, une faible sonnerie s'allume en
plus du voyant orange pour avertir le bricoleur qu'il va déclencher l'alarme s'il
ne la désactive pas et reste sur les lieux.

## Alimentation

Si l'alimentation de l'atelier est en **mode automatique**, elle sera coupée
dès lors que l'alarme sera en écoute (mais pas pendant la phase de mise en écoute). 
L'alimentation sera réactivée quand l'alarme sera désactivée.

Si l'alimentation de l'atelier est en **mode manuel**, elle conserve l'état
dans lequel elle est. Cela permet notamment de recharger ponctuellement des batteries
la nuit. Pour ne pas oublier de repasser en mode automatique (plus économe en
énergie), un SMS de rappel est envoyé quand `Délai en mode manuel avant rappel`
est atteint.

## Eau

Le système peut être soit en mode manuel (dans lequel il est au démarrage), soit
en mode automatique. Nous détaillons le comportement de chaque composant dans
chacun de ces modes. Changer de mode se fait via l'interface web.

## Pompe de puits

Cette pompe remonte l'eau du puits dans la cuve. Elle peut avoir trois états :

* Allumée
* Éteinte
* Désactivée (en cas de panne) 

Quel que soit le mode, quand la pompe est **désactivée** elle ne peut qu'être éteinte.
La pompe se désactive dans un des cas suivants :

* Le moteur est bloqué ;
* Le filtre est encrassé ;
* Elle n'a pas remonté d'eau lors du dernier cycle (ce qui suggère une panne).

Pour la réactiver, il faut cliquer dessus sur l'interface web.

En **mode manuel**, la pompe reste dans l'état dans lequel elle est et il faut l'allumer
ou l'éteindre manuellement. Les pannes mentionnées juste au-dessus sont détectées
en mode manuel et mèneront à la désactivation de la pompe.

En **mode automatique**, la pompe se met en marche tous les `Durée entre deux remplissages`.
Elle s'arrête quand le débit de pompage passe en-dessous de `Débit minimal de la pompe du puits`.
Il est possible de mettre en marche la pompe manuellement via l'interface (en cas
de besoin d'eau urgent). Elle s'arrêtera également toute seule quand le débit
deviendra trop faible.

Quel que soit le mode, la pompe de puits ne s'allume pas si la cuve est pleine.

## Filtre

Le filtre assainit l'eau provenant du puits avant de l'envoyer dans la cuve.

Quand le filtre est encrassé, la pression monte et un capteur se déclenche, ce
qui désactive la pompe de puits.

En **mode manuel**, le filtre reste dans l'état dans lequel il est. Il est
possible de l'ouvrir ou le fermer à sa guise via l'interface web.

En **mode automatique**, le filtre a le comportement suivant :

1. Allumage de la pompe du puits
2. Attente pendant `Temps mis par l'eau pour remonter le puits`
3. Ouverture du filtre (pour le nettoyer)
4. Filtre ouvert pendant `Durée d'ouverture du filtre`
5. Fermeture du filtre
6. Attente pendant `Durée entre deux ouvertures consécutives du filtre`
7. Ouverture du filtre (pour parfaire le nettoyage)
8. Filtre ouvert pendant `Durée d'ouverture du filtre`
9. Fermeture du filtre

En mode automatique, il est possible de déclencher manuellement un cycle
de nettoyage (ouverture - attente - fermeture) via l'interface web.

## Pompe de surpresseur

La pompe de surpresseur se situe entre la cuve et le ballon d'eau permettant
de garder de la pression dans le circuit d'eau. Elle peut être :

* Allumée/Éteinte
* Désactivée par panne
* Désactivée par manque d'eau

Quel que soit le mode, quand la pompe est **désactivée par panne** elle ne peut qu'être éteinte.
La pompe se désactive par panne dans un des cas suivants :

* Le moteur est bloqué ;
* Le circuit est en surpression ;
* La pompe a fonctionné trop longtemps (donc probablement dans le vide) : `Durée maximale de fonctionnement de la pompe du surpresseur`.

Pour la réactiver, il faut cliquer dessus sur l'interface web. Quand la pompe
est désactivée par panne, le réseau urbain s'ouvre.

En **mode manuel**, la pompe reste dans l'état dans lequel elle est et il faut l'allumer
ou l'éteindre manuellement via l'interface web. Les pannes mentionnées juste
au-dessus sont détectées en mode manuel et mèneront à la désactivation par
panne de la pompe. La désactivation par manque d'eau ne se fait pas en mode
manuel (on peut donc l'allumer même si la cuve est vide).

En **mode automatique**, la pompe du supresseur peut être désactivée par panne
comme décrit plus haut. Elle peut être désactivée par manque d'eau dans un des
cas suivants :

* La cuve est vide ;
* La cuve n'est pas vide mais il y a eu moins de `Volume dans la cuve avant d'éteindre la ville` d'eau collectée depuis la dernière fois qu'elle l'a été.

La seconde condition permet d'attendre un peu avant d'alimenter de nouveau la
ferme via la cuve pour éviter que le niveau d'eau ne fasse qu'osciller autour
du niveau bas :

1. Niveau bas atteint : désactivation de la pompe
2. Remplissage sans consommation : on repasse au-dessus du niveau bas et rebascule sur la cuve
3. On consomme plus qu'on ne collecte : le niveau d'eau baisse rapidement et on repart en 1

Quand la pompe n'est pas désactivée (pas de panne ni de manque d'eau), elle
s'allume et s'éteint toute seule (en mode automatique) en fonction de la pression
dans le ballon d'eau.

## Electrovanne de ville

L'électrovanne de ville permet d'ouvrir ou fermer le réseau urbain.

En **mode manuel**, elle reste dans l'état dans lequel elle est, sauf si la pompe
de surpresseur est désactivée (auquel cas le réseau urbain est ouvert). Elle
peut être commandée via l'interface web.

En **mode automatique**, l'électrovanne est fermée quand la pompe de surpresseur
est activée (pas de panne ni de manque d'eau). Quand la pompe de surpresseur est
désactivée par panne ou par manque d'eau, le réseau urbain est ouvert.
