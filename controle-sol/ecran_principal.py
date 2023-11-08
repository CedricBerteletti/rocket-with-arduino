# -*- coding: utf-8 -*-
"""
@author: Cédric Berteletti
Ecran principal
"""

import logging
import time

import graphiques
import settings

from tkinter import Tk, StringVar, Text
from tkinter import Button, Entry, Frame, LabelFrame, PanedWindow
from tkinter.constants import VERTICAL, TOP, LEFT, BOTTOM, X, BOTH, VERTICAL, HORIZONTAL, RAISED, DISABLED, NORMAL, W, N, E, S



class EcranPrincipal(Frame):
    "Classe représentant l'écran principal"


    def __init__(self, controleur, telemetrie, centrale):
        super().__init__()
        self.actif = True
        self.controleur = controleur
        self.telemetrie = telemetrie
        self.centrale = centrale
        self.graphs_refresh_delay_ms = settings.get("graphs.refresh_delay_ms")
        self.init_ui()


    def init_ui(self):
        # Préparation de l'écran
        self.pack(fill=BOTH, expand=True)
        Tk.update(self)
        panneaux = PanedWindow(self, orient=HORIZONTAL, sashrelief = RAISED, sashpad=2)
        panneaux.pack(fill=BOTH, expand=True)

        # Panneau de gauche
        panneauGauche = PanedWindow(panneaux, orient=VERTICAL, sashrelief = RAISED, sashpad=2, width=self.winfo_width()/2)
        panneaux.add(panneauGauche)

        # 2 sous-panneaux horizontaux de gauche
        visualisation = LabelFrame(panneauGauche, text="Vue")
        panneauGauche.add(visualisation, height=self.winfo_height()*2/3)

        controles = LabelFrame(panneauGauche, text="Contrôle")
        panneauGauche.add(controles, height=self.winfo_height()/3)
        boutons = Frame(controles)
        boutons.pack(side=TOP)
        btnConnect = Button(boutons, text="Connexion")
        btnConnect.pack(padx=5, pady=5, side=LEFT)
        btnEtages = Button(boutons, text="Etages")
        btnEtages.pack(padx=5, pady=5, side=LEFT)
        btnLancer = Button(boutons, text="Lancement !")
        btnLancer.pack(padx=5, pady=5, side=LEFT)
        btnViderLogs = Button(boutons, text="Vider logs", command=self.vider_logs)
        btnViderLogs.pack(padx=5, pady=5, side=LEFT)

        self.logs = Text(controles, height=1, bg="#000000", fg="#FFFFFF")
        self.logs.config(state=DISABLED)
        self.logs.pack(padx=5, pady=5, fill=BOTH, expand=1)
        self.commandeText = StringVar()
        commande = Entry(controles, textvariable=self.commandeText)
        commande.pack(padx=5, pady=5, side=BOTTOM, fill=X)
        commande.bind('<Return>', self.nouvelles_commandes)
      
        # Panneau de droite
        panneauDroit = PanedWindow(panneaux, orient=VERTICAL, sashrelief = RAISED, sashpad=2)
        panneaux.add(panneauDroit)
        frameImu = LabelFrame(panneauDroit, text="Centrale inertielle")
        panneauDroit.add(frameImu, height=self.winfo_height()*4/5)
        #panneauDroit.pack(fill=BOTH, expand=1)
        #panneauDroit.pack(side=TOP)

        # 2 sous-panneaux de droite contenant les informations de trajectoire
        #self.graphiques = GraphiquesIndependants(panneauDroit, height=self.winfo_height()*4/5)
        boutonsImu = Frame(frameImu)
        boutonsImu.pack(side=TOP)
        btnViderLogsImu = Button(boutonsImu, text="Vider logs CI", command=self.vider_logs_imu)
        btnViderLogsImu.pack(padx=5, pady=5, side=LEFT)
        btnCalibrerImu = Button(boutonsImu, text="Calibrer CI", command=self.calibrer)
        btnCalibrerImu.pack(padx=5, pady=5, side=LEFT)
        if settings.get_bool("graphs.debug"):
            self.graphiques = graphiques.DebugGraphiquesIntegres(frameImu, height=self.winfo_height()*4/5)
        else:
            self.graphiques = graphiques.GraphiquesIntegres2(frameImu, height=self.winfo_height()*4/5)
        self.graphiques.pack(side=TOP)
        #panneauDroit.add(self.graphiques)

        self.imuLogs = Text(panneauDroit, bg="#000000", fg="#FFFFFF", height=self.winfo_height()/5)
        self.imuLogs.config(state=DISABLED)
        panneauDroit.add(self.imuLogs, height=self.winfo_height()/5)        

        # MAJ régulière
        self.maj()


    def maj(self):
        if self.actif:
            logging.debug(self)
            self.maj_loggers()
            self.maj_graph()
            self.after(self.graphs_refresh_delay_ms, self.maj)

    def maj_loggers(self):
        "Mise à jour des loggers toutes les 100 ms"

        # Logs courants
        self.logs.config(state=NORMAL)
        s = self.telemetrie.logSuivant()
        nouveauLog = False
        while s:
            nouveauLog = True
            self.logs.insert("end", s + "\n")
            s = self.telemetrie.logSuivant()
        if nouveauLog:
            self.logs.see("end")
        self.logs.config(state=DISABLED)

        # Logs de la centrale inertielle
        self.imuLogs.config(state=NORMAL)
        s = self.telemetrie.logImuSuivant()
        nouveauLog = False
        while s:
            nouveauLog = True
            self.imuLogs.insert("end", s + "\n")
            self.centrale.ajouter_telemetrie(s)
            s = self.telemetrie.logImuSuivant()
        if nouveauLog:
            self.imuLogs.see("end")
        self.imuLogs.config(state=DISABLED)

        # MAJ graphique sur un échantillon des données
        if nouveauLog:
            self.graphiques.ajouter_telemetrie(self.centrale.data_liste[0].t, self.centrale.courant)

    def maj_graph(self):
        self.graphiques.maj()

    def stop(self):
        logging.debug("Fermeture de la fenêtre principale")
        self.actif = False

    def vider_logs(self):
        self.logs.config(state=NORMAL)
        self.logs.delete(1.0, "end")
        self.logs.config(state=DISABLED)

    def vider_logs_imu(self):
        self.imuLogs.config(state=NORMAL)
        self.imuLogs.delete(1.0, "end")
        self.imuLogs.config(state=DISABLED)
        self.centrale.effacer_donnees()
        self.graphiques.effacer()

    def calibrer(self):
        self.centrale.calibrer()

    def nouvelles_commandes(self, event):
        commandes = self.commandeText.get().splitlines()
        self.executer_commandes(commandes)
        self.commandeText.set("")

    def executer_commandes(self, commandes):
        for commande in commandes:
            self.executer_commande(commande)
            # Attente d'envoi de la commande (risque de perte sinon : UDP et non TCP)
            time.sleep(0.2)

    def executer_commande(self, commande):
        if commande[0:13] == "wifi.initUdp ":
            connect, ip, port = commande.split()
            self.controleur.connecter(ip, int(port))
        else:
            self.controleur.envoyer_commande_brute(commande)
