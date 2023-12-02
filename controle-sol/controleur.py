# -*- coding: utf-8 -*-
"""
@author: Cédric Berteletti
Envoi des commandes à la fusée et réception
"""

from connexion import Connexion


# Dictionnaire de compilation
dict_compilation = {"wifi.connectNetwork": "WC",
                    "wifi.broadcastUdpClient": "WB",
                    "wifi.status": "WS",

                    "system.delay": "0D",

                    "logger.status": "LS",
                    "logger.initSdcard": "LC",
                    "logger.flushToSdcard": "LF",
                    "logger.activateLogImuData": "LI 1",
                    "logger.deactivateLogImuData": "LI 0",
                    "logger.activateLogFlush": "LW 1",
                    "logger.deactivateLogFlush": "LW 0",
                    "logger.activateLogRocketStatus": "LR 1",
                    "logger.deactivateLogRocketStatus": "LR 0",
                    
                    "rocket.status": "RS",
                    "rocket.launch": "F0",
                    "rocket.stage": "RE",
                    
                    
                    "flightplan.start": "F0",
                    "flightplan.stop": "FZ",
                    "flightplan.configureStep": "FC",
                    "flightplan.getSteps": "FS",
                    "flightplan.goStep": "FG",
                    
                    "pin.setMode": "PC",
                    "pin.digitalWrite": "PD",
                    "pin.fire": "PD {} 1",
                    "pin.tone": "PT",
                    "pin.toneStop": "PR",
                    
                    "servo.setPosition": "SP",
                    }


ERROR_COMMANDE_INCONNUE = "ERREUR : commande inconnue"


class Controleur():
    "Classe pour gérer les commandes envoyées à la fusée et la réception des informations"

    def __init__(self, connexion):
        self.connexion = connexion

    def connecter(self, pc_id, rocket_ip, rocket_port):
        self.connexion.init(rocket_ip, rocket_port)
        self.envoyer_commande_brute("wifi.broadcastUdpClient " + pc_id + " " + rocket_ip + " " + str(rocket_port))

    def envoyer_commande_brute(self, commande_brute):
        commande = self.compiler_commande(commande_brute)
        if commande[0:3] != "ERR":
            self.connexion.envoyer(commande)
        return commande

    def compiler_commande(self, commande_brute):
        if " " in commande_brute:
            operation, arguments = commande_brute.strip().split(sep=" ", maxsplit=1)
        else:
            operation = commande_brute
            arguments = ""

        if operation in dict_compilation:
            operation_abbregee = dict_compilation[operation]

            if operation_abbregee[0:2] == "FC":
                # Cas particulier de l'instruction déclarant les instructions du plan de vol
                num_instruction, duree, commande_planifiee_brute = arguments.split(sep=" ", maxsplit=2)
                commande_planifiee = self.compiler_commande(commande_planifiee_brute)
                if commande_planifiee[0:3] != "ERR":
                    commande = f"FC {num_instruction} {duree} {commande_planifiee}"
                else:
                    commande = ERROR_COMMANDE_INCONNUE
            elif "{}" not in operation_abbregee:
                # Remplacement simple
                commande = f"{operation_abbregee} {arguments}"
            else:
                # Remplacement en respectant un formatage
                args = arguments.split(" ")
                commande = operation_abbregee.format(args)
        else:
            commande = ERROR_COMMANDE_INCONNUE

        return commande

    def traduire_logs(self, log):
        # TODO
        return log
    
    def traduire_logs_imu(self, log):
        # TODO
        return log
    
        