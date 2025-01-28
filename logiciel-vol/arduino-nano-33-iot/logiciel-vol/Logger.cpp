/*
 * --------------------------------------------------------------------------
 * Logger
 * --------------------------------------------------------------------------
 * @author Cédric Berteletti
 */

#include "Logger.hpp"

const int chipSelect = 10;
const char Logger::MODULE_LOGGER[] = "LOGGER";
const char Logger::NOM_FICHIER_LOGS[] = "rlogs.csv";


Logger::Logger() {}

void Logger::initCarteSd() {
  logCarteSdActif = false;

  if (!carteSd.init(SPI_HALF_SPEED, chipSelect)) {
    log(MODULE_LOGGER, "ERROR_SDCARD_INIT", "Erreur d'initialisation de la carte SD");
  }
  else {
    log(MODULE_LOGGER, "SDCARD_INITIALIZED", "Carte SD initialisée");
    switch (carteSd.type()) {
      case SD_CARD_TYPE_SD1:
        log(MODULE_LOGGER, "SDCARD_TYPE", "SD1");
        break;
      case SD_CARD_TYPE_SD2:
        log(MODULE_LOGGER, "SDCARD_TYPE", "SD2");
        break;
      case SD_CARD_TYPE_SDHC:
        log(MODULE_LOGGER, "SDCARD_TYPE", "SDHC");
        break;
      default:
        log(MODULE_LOGGER, "SDCARD_TYPE", "Unknown");
    }

    if (!volume.init(carteSd)) {
      log(MODULE_LOGGER, "ERROR_SDCARD_VOLUME", "Aucune partition FAT16/FAT32 trouvée.");
    }
    else {
      itoa(volume.clusterCount(), strLog, 10);
      log(MODULE_LOGGER, "SDCARD_VOLUME_CLUSTERS", strLog);
      itoa(volume.blocksPerCluster(), strLog, 10);
      log(MODULE_LOGGER, "SDCARD_VOLUME_BLOCKS_PER_CLUSTER", strLog);
      itoa(volume.blocksPerCluster() * volume.clusterCount(), strLog, 10);
      log(MODULE_LOGGER, "SDCARD_VOLUME_BLOCKS", strLog);
      itoa(volume.fatType(), strLog, 10);
      log(MODULE_LOGGER, "SDCARD_VOLUME_FAT_TYPE", strLog);
      uint32_t volumesize;
      volumesize = volume.blocksPerCluster(); // clusters are collections of blocks
      volumesize *= volume.clusterCount(); // we'll have a lot of clusters
      volumesize /= 2; // SD card blocks are always 512 bytes (2 blocks are 1KB)
      volumesize /= 1024;
      itoa(volumesize, strLog, 10);
      log(MODULE_LOGGER, "SDCARD_VOLUME_SIZE_MB", strLog);
    }
  }

  if (!SD.begin(chipSelect)) {
    log(MODULE_LOGGER, "ERROR_SDCARD_INIT", "Erreur d'initialisation de la carte SD");
  }
  else {
    log(MODULE_LOGGER, "SDCARD_INITIALIZED", "Carte SD initialisée");

    fichier = SD.open(NOM_FICHIER_LOGS, FILE_WRITE);
    if(fichier) {
      log(MODULE_LOGGER, "LOG_FILE_OPEN", "Fichier de logs ouvert");
      logCarteSdActif = true;
    }
    else {
      log(MODULE_LOGGER, "ERROR_LOG_FILE", "Impossible d'ouvrir le fichier de logs");
    }
  }
}

void Logger::logStatut()
{
  sprintf(strTmp, "Logger série %i | Logger SD %i | Logger wifi %i", logSerieActif, logCarteSdActif, logUdpActif);
  log(MODULE_LOGGER, "STATUS", strTmp);
}

// Force l'écriture du cache sur la carte SD
void Logger::forcerEcritureSurCarteSd() {
  if(fichier) {
    fichier.flush();
    if(logForcageEcritureSurCarteSd) log(MODULE_LOGGER, "SDCARD_FLUSH", "Ecriture des données du cache sur la carte SD");
  }
}

// Renvoie la taille du fichier de logs
long Logger::tailleFichierCarteSd() {
  sprintf(strTmp, "%i", fichier.size());
  log(MODULE_LOGGER, "LOGFILE_SIZE", strTmp);
}

// Vide le fichier de logs
void Logger::viderFichierCarteSd() {
  if(fichier) {
    fichier.close();
  }
  SD.remove(NOM_FICHIER_LOGS);
  fichier = SD.open(NOM_FICHIER_LOGS, FILE_WRITE);
}

// Fonctions d'écriture des logs
void Logger::log(const char module[], const char message[], const char details[]) {
  if (logSerieActif || logCarteSdActif || logUdpActif) {
    delay(1); // Attente minimale pour éviter d'envoyer plein de logs à la suite (risque de perte)
    formaterLog(strLog, module, message, details);

    if(logSerieActif) Serial.println(strLog);
    if(logUdpActif) wifi->ecrireUdp(strLog);
    if(logCarteSdActif) fichier.println(strLog);
  }
}




