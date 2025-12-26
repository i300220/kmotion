Présentation:
Kmotion est un logiciel libre (écrit en python) de vidéosurveillance permettant de gérer jusqu'à 16 cameras (webcam) avec le logiciel libre motion à travers une interface web, et facilite ainsi l'utilisation de motion.

Pré-requis:
Disposer des droits d'administration.
Disposer d'une connexion à Internet configurée et activée.
Avoir une webcam qui fonctionne. (pour vérifier l'installation de votre webcam saisir dans un terminal :
gstreamer-properties
dans Video/Test, le test devrait afficher l'image de votre webcam).

Installation:
kmotion v2 a les dépendances suivantes pour debian trixie:

apache2 2.4.x

apache2 python module mod-python 3.5.0+git20211031 

motion v4.7.x

python v3.13.x

ou

sudo apt-get install apache2 motion python

libapache2-mod-python n'est malheureusement plus supporte alors il faut le recompiler dans un environnement debian 11 ou 12 et python 3.9 ou 3.12.

Décompresser
(il faut rendre les scripts *.py exécutables)

Aller dans le dossier parent de kmotion
Lancer dans un terminal :
sudo chmod -R a+rx kmotion
Aller dans le répertoire kmotion.
cd /kmotion
Lancer dans un terminal :
sudo ./install.py 
kmotion start

Configuration:
Voir également les options de motion, et son fichier de configuration qui est utilisé par kmotion pour le lancement de motion, les threads pour différentes caméra sont rajoutés par la suite.

Vous pouvez ajouter au démarrage de la machine

chromium-browser http://kmotion:kmotion@localhost:8085
Dans la configuration changer de mot de passe pour des raison de sécurité

Désinstallation:
Aller dans le répertoire kmotion.
Lancer dans un terminal :
sudo ./uninstall.py
