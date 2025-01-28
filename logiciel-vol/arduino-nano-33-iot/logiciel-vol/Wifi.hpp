/*
 * --------------------------------------------------------------------------
 * Module gérant les connexions wifi
 * --------------------------------------------------------------------------
 * @author Cédric Berteletti
 */

#ifndef Wifi_h
#define Wifi_h


#include <WiFiNINA.h>
#include "aides.hpp"
#include "secrets.h"

// Constantes générales
inline constexpr int NOMBRE_MAX_CLIENTS = 5;
inline constexpr int DELAI_ENVOI_UDP = 2;

class Wifi
{
  public:
    Wifi();
    bool actif = false;
    bool loggingIo = false;
    void listerReseaux();
    void connecter();
    void connecterAvecFallback(const char ssid[], const char pwd[]);
    void logStatut();
    void lireUdp(char message[]);
    void ecrireUdp(const char message[]);
    void confClientUdp(int n);
  private:
    static const char MODULE_WIFI[];
    static const unsigned int PORT_LOCAL;
    // Une seule allocation des strings au chargement de l'instance
    char strLog[LONGUEUR_MAX_CHAINE_CARACTERES];
    char strTmp[LONGUEUR_MAX_CHAINE_CARACTERES];
    WiFiUDP udp;
    IPAddress currentRemoteIp;
    unsigned int currentRemotePort;
    IPAddress remoteIps[NOMBRE_MAX_CLIENTS];
    unsigned int remotePorts[NOMBRE_MAX_CLIENTS] {0};
    void connecter(const char ssid[], const char pwd[]);
    void typeChiffrement(char str[], int type);
    void adresseIp(char addresse[], IPAddress ip);
    void log(const char module[], const char message[], const char details[], bool toWifi);
    void logIo(const char parameter[], const char message[]);
};

#endif
