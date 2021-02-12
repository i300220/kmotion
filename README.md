Présentation:
Kmotion est un logiciel libre (écrit en python) de vidéosurveillance permettant de gérer jusqu'à 16 cameras (webcam) avec le logiciel libre motion à travers une interface web, et facilite ainsi l'utilisation de motion.

Pré-requis:
Disposer des droits d'administration.
Disposer d'une connexion à Internet configurée et activée.
Avoir une webcam qui fonctionne. (pour vérifier l'installation de votre webcam saisir dans un terminal :
gstreamer-properties
dans Video/Test, le test devrait afficher l'image de votre webcam).

Installation:
kmotion v2 a les dépendances suivantes :

apache2 … v2.2.x
apache2 python module v3.3.x
motion … v3.2.x
python … v2.4.x
apache2 libapache2-mod-python motion python

ou

sudo apt-get install apache2 libapache2-mod-python motion python

Décompresser
(il faut rendre les scrypt *.py exécutables)

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