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

Pour éteindre l'alarme une fois qu'elle a été déclenchée, il faut la désactiver
(à la clé ou via l'interface web). Alors, la sonnerie s'arrête et les lumières
d'alerte et extérieure s'éteignent.

Quand l'alarme passe en écoute, les lumières intérieures s'éteignent. L'alimentation,
si elle est en mode automatique (cf. plus bas), est coupée.

### Mise en écoute

Entre les deux phases, il y a la **mise en écoute**. Le voyant sur le boitier est
orange. Cette phase dure `Délai avant mise en écoute` et permet de quitter le
bâtiment sans déclencher l'alarme.

L'alarme est mise en écoute le midi et la nuit à des heures configurables. Elle
n'est jamais éteinte automatiquement, donc doit l'être manuellement en actionnant
la clé ou via l'interface web.

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
