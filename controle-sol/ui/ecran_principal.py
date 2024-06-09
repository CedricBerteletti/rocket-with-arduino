# -*- coding: utf-8 -*-
"""
@author: Cédric Berteletti
Écran principal
"""


import logging
import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QGridLayout, QFileDialog, QGroupBox, QLineEdit, QTextEdit, QPushButton, QSplitter, QCheckBox

import ui.graphiques as graphiques
from ui.ui_utils import set_default_layout_params
from ui.visualisation_fusee import VisualisationFusee
import services.settings as settings


class EcranPrincipal(QFrame):
    "Classe représentant l'écran principal"


    def __init__(self, controleur, telemetrie, centrale):
        super().__init__()
        self.actif = True
        self.controleur = controleur
        self.telemetrie = telemetrie
        self.centrale = centrale
        self.graphs_refresh_delay_ms = settings.get_int("graphs.refresh_delay_ms")
        self.init_ui()


    def init_ui(self):
        # Préparation de l'écran
        splitter_general = QSplitter(Qt.Orientation.Horizontal)
        self.setLayout(QHBoxLayout())
        set_default_layout_params(self.layout())
        self.layout().addWidget(splitter_general)

        # Panneau de gauche
        panneau_gauche = QFrame()
        #panneau_gauche.setFrameShape(QFrame.Shape.StyledPanel)
        panneau_gauche.setLayout(QVBoxLayout())
        set_default_layout_params(panneau_gauche.layout())
        splitter_general.addWidget(panneau_gauche)        
        splitter_panneau_gauche = QSplitter(Qt.Orientation.Vertical)
        panneau_gauche.layout().addWidget(splitter_panneau_gauche)

        frame = QFrame()
        splitter_panneau_gauche.addWidget(frame)
        #frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setLayout(QVBoxLayout())
        set_default_layout_params(frame.layout())
        self.creer_groupe_visualisation()
        frame.layout().addWidget(self.grp_visu)

        frame = QFrame()
        splitter_panneau_gauche.addWidget(frame)
        #frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setLayout(QVBoxLayout())
        set_default_layout_params(frame.layout())
        self.creer_groupe_commandes()
        frame.layout().addWidget(self.grp_command)
        self.creer_groupe_logs()
        frame.layout().addWidget(self.grp_logs)
      
        # Panneau de droite
        panneau_droit = QFrame()
        #panneau_droit.setFrameShape(QFrame.Shape.StyledPanel)
        panneau_droit.setLayout(QVBoxLayout())
        set_default_layout_params(panneau_droit.layout())
        splitter_general.addWidget(panneau_droit)

        self.creer_groupe_graphiques()
        panneau_droit.layout().addWidget(self.grp_graphs)
        # TODO Ajouter splitter entre ces deux groupes de widgets graphiques
        self.creer_groupe_imu()
        panneau_droit.layout().addWidget(self.grp_imu)

        # Rafraichissement périodique des graphiques et des logs        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.maj)
        self.timer.start(self.graphs_refresh_delay_ms) # time in milliseconds.


    def creer_groupe_visualisation(self):
        self.grp_visu = QGroupBox("Visualisation")
        self.grp_visu.setLayout(QVBoxLayout())
        set_default_layout_params(self.grp_visu.layout())
        self.visualisation = VisualisationFusee()
        self.grp_visu.layout().addWidget(self.visualisation)


    def creer_groupe_commandes(self):
        self.grp_command = QGroupBox("Commandes générales")
        self.grp_command.setLayout(QGridLayout())
        set_default_layout_params(self.grp_command.layout())

        button = QPushButton("Connecter")
        self.grp_command.layout().addWidget(button, 0, 0)
        # TODO

        button = QPushButton("Charger")
        self.grp_command.layout().addWidget(button, 0, 1)
        button.clicked.connect(self.charger_programme)

        button = QPushButton("Vider logs")
        self.grp_command.layout().addWidget(button, 0, 2)        
        button.clicked.connect(self.vider_logs)

        button = QPushButton("Lancer !")
        self.grp_command.layout().addWidget(button, 0, 3)
        # TODO


    def creer_groupe_logs(self):
        self.grp_logs = QGroupBox("Logs généraux")
        self.grp_logs.setLayout(QVBoxLayout())
        set_default_layout_params(self.grp_logs.layout())

        self.tb_logs = QTextEdit ()
        self.tb_logs.setReadOnly(True)        
        self.tb_logs.setStyleSheet("background-color: rgb(0, 0, 0); color: rgb(255, 255, 255); ")
        self.grp_logs.layout().addWidget(self.tb_logs)
        self.tb_command = QLineEdit ()
        self.grp_logs.layout().addWidget(self.tb_command)
        self.tb_command.returnPressed.connect(self.nouvelles_commandes)


    def creer_groupe_graphiques(self):
        self.grp_graphs = QGroupBox("Graphiques IMU")
        self.grp_graphs.setLayout(QVBoxLayout())
        set_default_layout_params(self.grp_graphs.layout())

        if settings.get_bool("graphs.debug"):
            self.graphiques = graphiques.BaseGraphiquesIntegres(self.grp_graphs)
        else:
            self.graphiques = graphiques.GraphiquesIntegres(self.grp_graphs)
        self.grp_graphs.layout().addWidget(self.graphiques)


    def creer_groupe_imu(self):
        self.grp_imu = QGroupBox("IMU")
        self.grp_imu.setLayout(QVBoxLayout())
        set_default_layout_params(self.grp_imu.layout())
       
        layout_command = QGridLayout()
        set_default_layout_params(layout_command)
        self.grp_imu.layout().addLayout(layout_command)

        button = QPushButton("Vider logs")
        layout_command.addWidget(button, 0, 0)
        button.clicked.connect(self.vider_logs_imu)

        button = QPushButton("Vider et effacer")
        layout_command.addWidget(button, 0, 1)
        button.clicked.connect(self.imu_vider_et_effacer)

        button = QPushButton("Calibrer")
        layout_command.addWidget(button, 0, 2)        
        button.clicked.connect(self.calibrer)

        self.cb_imu_logs_defil = QCheckBox("Défilement auto")
        self.cb_imu_logs_defil.setChecked(True)
        layout_command.addWidget(self.cb_imu_logs_defil, 0, 3)

        self.tb_imu_logs = QTextEdit ()
        self.tb_imu_logs.setReadOnly(True)
        self.tb_imu_logs.setStyleSheet("background-color: rgb(0, 0, 0); color: rgb(255, 255, 255);")
        self.grp_imu.layout().addWidget(self.tb_imu_logs)

    def charger_programme(self):
        fileName = QFileDialog.getOpenFileName(self, "Charger programme de la fusée", "",
                                               "Fichiers rfp (*.rfp)")
        with open(fileName[0]) as f:
            lines = f.read().splitlines()
            self.executer_commandes(lines)

    def maj(self):
        if self.actif:
            logging.debug(self)
            self.maj_loggers()
            self.maj_graph()

    def maj_loggers(self):
        "Mise à jour des loggers"

        # Logs courants
        s = self.telemetrie.logSuivant()
        nouveauLog = False
        while s:
            nouveauLog = True
            s = self.controleur.traduire_logs(s)
            self.tb_logs.insertPlainText(s + "\n")
            s = self.telemetrie.logSuivant()
        if nouveauLog:
            self.tb_logs.moveCursor(QTextCursor.MoveOperation.End)

        # Logs de la centrale inertielle
        s = self.telemetrie.logImuSuivant()
        nouveauLog = False
        while s:
            nouveauLog = True
            self.centrale.ajouter_telemetrie(s)
            s = self.controleur.traduire_logs_imu(s)
            self.tb_imu_logs.insertPlainText(s + "\n")
            s = self.telemetrie.logImuSuivant()
        if nouveauLog and self.cb_imu_logs_defil.isChecked():
            self.tb_imu_logs.moveCursor(QTextCursor.MoveOperation.End)

        # MAJ graphique sur un échantillon des données
        if nouveauLog:
            self.graphiques.ajouter_telemetrie(self.centrale.data_liste[0].t, self.centrale.courant)

    def maj_graph(self):
        self.graphiques.maj()

    def stop(self):
        logging.debug("Fermeture de la fenêtre principale")
        self.actif = False

    def vider_logs(self):
        self.tb_logs.clear()

    def vider_logs_imu(self):
        self.tb_imu_logs.clear()

    def imu_vider_et_effacer(self):
        self.vider_logs_imu()
        self.graphiques.effacer()

    def calibrer(self):
        self.centrale.calibrer()

    def nouvelles_commandes(self):
        commandes = self.tb_command.text().splitlines()
        self.tb_command.clear()
        self.executer_commandes(commandes)

    def executer_commandes(self, commandes):
        for commande in commandes:
            self.executer_commande(commande)
            # Attente d'envoi de la commande (risque de perte sinon : UDP et non TCP)
            time.sleep(0.05)

    def executer_commande(self, commande):
        self.tb_logs.insertHtml(f"<h1 style=\"color:blue;\">> {commande}</h1>\n")
        self.tb_logs.insertPlainText("\n")
        
        if commande[0:24] == "wifi.broadcastUdpClient ":
            connect, pc_id, rocket_ip, rocket_port = commande.split()
            commande_envoyee = self.controleur.connecter(pc_id, rocket_ip, int(rocket_port))
        else:
            commande_envoyee = self.controleur.envoyer_commande_brute(commande)
        self.tb_logs.insertPlainText(f"Commande envoyée : {commande_envoyee}\n")

        self.tb_logs.moveCursor(QTextCursor.MoveOperation.End)
