# -*- coding: utf-8 -*-
"""
@author: Cédric Berteletti
Calculs à partir des données de la centrale inertielle
"""

import logging

from dataclasses import dataclass


class CentraleInertielle():
    "Classe gérant toutes les données inertielles"

    def __init__(self):
        self.courant = DonneesInertielles()
        logging.debug(self.courant)
        self.data_liste = []
        self.offset_ax = 0.0
        self.offset_ay = 0.0
        self.offset_az = 0.0
        self.offset_valpha = 0.0
        self.offset_vbeta = 0.0
        self.offset_vgamma = 0.0
        
    def ajouter_telemetrie(self, log):
        if(log):
            data = DonneesInertielles()
            tokens = log.split("\", \"")
            if(len(tokens[1]) > 1):
                values = tokens[1][:-1].split(", ")
                # Récupération des valeurs de la télémétrie, en tenant compte de la calibration
                data.t = int(values[0])
                data.ax = float(values[1]) + self.offset_ax
                data.ay = float(values[2]) + self.offset_ay
                data.az = float(values[3]) + self.offset_az
                data.valpha = float(values[4]) + self.offset_valpha
                data.vbeta = float(values[5]) + self.offset_vbeta
                data.vgamma = float(values[6]) + self.offset_vgamma

                # Calcul de l'orientation et de la position
                temps_ecoule = (data.t - self.courant.t) / 1000
                logging.debug("Calcul du nouvel angle ", temps_ecoule, data.alpha, self.courant.alpha, data.valpha)
                data.alpha = self.courant.alpha + data.valpha * temps_ecoule
                data.beta = self.courant.beta + data.vbeta * temps_ecoule
                data.gamma = self.courant.gamma + data.vgamma * temps_ecoule
                # TODO

                # Mise à jour de la liste
                self.courant = data
                self.data_liste.append(data)

    def effacer_donnees(self):
        self.data_liste = []
        self.courant = DonneesInertielles()
        self.offset_ax = 0.0
        self.offset_ay = 0.0
        self.offset_az = 0.0
        self.offset_valpha = 0.0
        self.deltavabeta = 0.0
        self.deltavagamma = 0.0

    def calibrer(self):
        sum_ax = 0.0
        sum_ay = 0.0
        sum_az = 0.0
        sum_valpha = 0.0
        sum_vbeta = 0.0
        sum_vgamma = 0.0
        n = 0
        
        # Calcul de la déviation sur tous les échantillons
        for data in self.data_liste:
            sum_ax = sum_ax + data.ax
            sum_ay = sum_ay + data.ay
            sum_az = sum_az + data.az
            sum_valpha = sum_valpha + data.valpha
            sum_vbeta = sum_vbeta + data.vbeta
            sum_vgamma = sum_vgamma + data.vgamma
            n = n + 1
        
        # Déviation moyenne en fonction du nombre n d'échantillons
        self.offset_ax = - sum_ax / n
        self.offset_ay = - sum_ay / n
        self.offset_az = - sum_az / n
        self.offset_valpha = - sum_valpha / n
        self.offset_vbeta = - sum_vbeta / n
        self.offset_vgamma = - sum_vgamma / n

        logging.info("CALIBRATION ", self.offset_ax, self.offset_ay, self.offset_az, self.offset_valpha, self.deltavabeta, self.deltavagamma)






@dataclass
class DonneesInertielles:
    "Classe représentant les données de la centrale inertielle et les valeurs calculées à un instant t donné"
    t : int = 0         # en ms
    ax : float = 0.0
    ay : float = 0.0
    az : float = 0.0
    vx : float = 0.0
    vy : float = 0.0
    vz : float = 0.0
    x : float = 0.0
    y : float = 0.0
    z : float = 0.0
    valpha : float = 0.0
    vbeta : float = 0.0
    vgamma : float = 0.0
    alpha : float = 0.0
    beta : float = 0.0
    gamma : float = 0.0