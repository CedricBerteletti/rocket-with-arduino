# -*- coding: utf-8 -*-

from connexion import Connexion

class Controleur():
    "Classe pour gérer les commandes envoyées à la fusée"

    def __init__(self, connexion):
        self.connexion = connexion

    def envoyer_commande_brute(self, commande):
        self.connexion.envoyer(commande)

    def connecter(self, ip, port):
        self.connexion.init(ip, port)
        self.envoyer_commande_brute("connect " + ip + " " + str(port))
        