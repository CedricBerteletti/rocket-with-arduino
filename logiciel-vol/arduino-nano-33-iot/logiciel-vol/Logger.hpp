/*
 * --------------------------------------------------------------------------
 * Logger
 * --------------------------------------------------------------------------
 * @author Cédric Berteletti
 */

#ifndef Logger_h
#define Logger_h

#include <Arduino.h>
#include <SD.h>
#include "aides.hpp"
#include "Wifi.hpp"

class Logger
{
  public:
    Logger();
    void initCarteSd();
    void logStatut();
    void log(const char module[], const char message[], const char details[]);
    void forcerEcritureSurCarteSd();
    void viderFichierCarteSd();
    long tailleFichierCarteSd();
    bool logSerieActif = true;
    bool logCarteSdActif = false;
    bool logUdpActif = false;
    bool logForcageEcritureSurCarteSd = true;
    Wifi *wifi;
  private:
    static const char MODULE_LOGGER[];
    static const char NOM_FICHIER_LOGS[];
    // Une seule allocation des buffers/strings au chargement de l'instance
    char strLog[LONGUEUR_MAX_CHAINE_CARACTERES];
    char strTmp[LONGUEUR_MAX_CHAINE_CARACTERES];
    Sd2Card carteSd;
    SdVolume volume;
    SdFile root;
    File fichier;
};

#endif
