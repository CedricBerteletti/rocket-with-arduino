/*
 * --------------------------------------------------------------------------
 * Gestion de la centrale inertielle de l'Arduino Nano 33 IoT
 * --------------------------------------------------------------------------
 * @author Cédric Berteletti
 */

#include "CentraleInertielle.hpp"

const char CentraleInertielle::MODULE_IMU[] = "IMU";
const char CentraleInertielle::SOUS_MODULE_IMU_DATA[] = "IMU_DATA";
const char CentraleInertielle::SOUS_MODULE_IMU_BUFFER[] = "IMU_BUFFER";
const char CentraleInertielle::ENTETE_DATA[] = "t, accX, accY, accZ, vAlpha, vBeta, vGamma";
const char CentraleInertielle::SEPARATEUR_DATA[] = ", ";


CentraleInertielle::CentraleInertielle(Logger &logger):logger(logger) {
}

void CentraleInertielle::init()
{
  if (!IMU.begin()) {
    logger.log(MODULE_IMU, "ERROR_INIT", "Erreur d'initialisation");
    while (true); // Blocage du programme
  }
  
  logger.log(MODULE_IMU, "INITIALIZED", "Centrale inertielle initialisée");
  itoa(IMU.accelerationSampleRate(), strLog, 10);
  logger.log(MODULE_IMU, "ACCELEROMETER_FREQUENCY", strLog);
  itoa(IMU.gyroscopeSampleRate(), strLog, 10);
  logger.log(MODULE_IMU, "GYRO_FREQUENCY", strLog);

  index = 0;
}

void CentraleInertielle::lire() {
  if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
    donneesInertiellesFrenetCourantes.t = millis();
    donneesInertiellesFrenetPrecedentes = donneesInertiellesFrenetCourantes;
    // Adaptation à la position de montage de l'Arduino dans la fusée
    IMU.readAcceleration(donneesInertiellesFrenetCourantes.accZ, donneesInertiellesFrenetCourantes.accY, donneesInertiellesFrenetCourantes.accX);
    IMU.readGyroscope(donneesInertiellesFrenetCourantes.vGamma, donneesInertiellesFrenetCourantes.vBeta, donneesInertiellesFrenetCourantes.vAlpha);

    //On calibre et on filtre les valeurs
    donneesInertiellesFrenetCourantes.accX += offsetAccX;
    donneesInertiellesFrenetCourantes.accY += offsetAccY;
    donneesInertiellesFrenetCourantes.accZ += offsetAccZ;
    donneesInertiellesFrenetCourantes.vAlpha += offsetVAlpha;
    donneesInertiellesFrenetCourantes.vBeta += offsetVBeta;
    donneesInertiellesFrenetCourantes.vGamma += offsetVGamma;

    if (abs(donneesInertiellesFrenetCourantes.accX-donneesInertiellesFrenetPrecedentes.accX) <= minAccX) {
      donneesInertiellesFrenetCourantes.accX = donneesInertiellesFrenetPrecedentes.accX;
    }

    if (abs(donneesInertiellesFrenetCourantes.accY-donneesInertiellesFrenetPrecedentes.accY) <= minAccY) {
      donneesInertiellesFrenetCourantes.accY = donneesInertiellesFrenetPrecedentes.accY;
    }

    if (abs(donneesInertiellesFrenetCourantes.accZ-donneesInertiellesFrenetPrecedentes.accZ) <= minAccZ) {
      donneesInertiellesFrenetCourantes.accZ = donneesInertiellesFrenetPrecedentes.accZ;
    }

    if (abs(donneesInertiellesFrenetCourantes.vAlpha-donneesInertiellesFrenetPrecedentes.vAlpha) <= minVAlpha) {
      donneesInertiellesFrenetCourantes.vAlpha = donneesInertiellesFrenetPrecedentes.vAlpha;
    }

    if (abs(donneesInertiellesFrenetCourantes.vBeta-donneesInertiellesFrenetPrecedentes.vBeta) <= minVBeta) {
      donneesInertiellesFrenetCourantes.vBeta = donneesInertiellesFrenetPrecedentes.vBeta;
    }

    if (abs(donneesInertiellesFrenetCourantes.vGamma-donneesInertiellesFrenetPrecedentes.vGamma) <= minVGamma) {
      donneesInertiellesFrenetCourantes.vGamma = donneesInertiellesFrenetPrecedentes.vGamma;
    }
    // On sauvegarde les valeurs courantes dans le buffer des données inertielles
    donneesInertiellesFrenet[index] = donneesInertiellesFrenetCourantes;

    // Intégration et changement de référentiel
    integration();

    // La prochaine fois, on stockera la valeur lue dans la "case" suivante du buffer
    index++;
    if(index == TAILLE_BUFFER_DONNEES_INERTIELLES) {
      index = 0;
    }
    
    if (loggingData) {
      log(donneesInertiellesFrenetCourantes, SOUS_MODULE_IMU_DATA, ENTETE_DATA);
    }
  }
}

void CentraleInertielle::setFiltreMinAcceleration(float minAcc) {
  minAccX = minAcc;
  minAccY = minAcc;
  minAccZ = minAcc;
}

void CentraleInertielle::setFiltreMinVitesseAngulaire(float minV) {
  minVAlpha = minV;
  minVBeta = minV;
  minVGamma = minV;
}

void CentraleInertielle::setRcsServoX(Servomoteur *servo) {
  rcsServoX = servo;
}

void CentraleInertielle::setRcsServoY(Servomoteur *servo) {
  rcsServoY = servo;
}

void CentraleInertielle::setWcsServoX(Servomoteur *servo) {
  wcsServoX = servo;
}

void CentraleInertielle::setWcsServoY(Servomoteur *servo) {
  wcsServoY = servo;
}

void CentraleInertielle::calibrer(float ax, float ay, float az, float valpha, float vbeta, float vgamma) {
  float axSum = 0;
  float aySum = 0;
  float azSum = 0;
  float valphaSum = 0;
  float vbetaSum = 0;
  float vgammaSum = 0;

  for(int i = 0; i < TAILLE_BUFFER_DONNEES_INERTIELLES; i++) {
    axSum += donneesInertiellesFrenet[i].accX;
    aySum += donneesInertiellesFrenet[i].accY;
    azSum += donneesInertiellesFrenet[i].accZ;
    valphaSum += donneesInertiellesFrenet[i].vAlpha;
    vbetaSum += donneesInertiellesFrenet[i].vBeta;
    vgammaSum += donneesInertiellesFrenet[i].vGamma;
  }
  offsetAccX = ax - axSum/TAILLE_BUFFER_DONNEES_INERTIELLES;
  offsetAccY = ay - aySum/TAILLE_BUFFER_DONNEES_INERTIELLES;
  offsetAccZ = az - azSum/TAILLE_BUFFER_DONNEES_INERTIELLES;
  offsetVAlpha = valpha - valphaSum/TAILLE_BUFFER_DONNEES_INERTIELLES; 
  offsetVBeta = vbeta - vbetaSum/TAILLE_BUFFER_DONNEES_INERTIELLES;
  offsetVGamma = vgamma - vgammaSum/TAILLE_BUFFER_DONNEES_INERTIELLES;  
}

void CentraleInertielle::logDonneesCalibration() {
  logger.log(SOUS_MODULE_IMU_BUFFER, "BUFFER_BEGIN", "Début des données dans le cache de calibration");
  delay(DELAI_ENVOI_UDP);
  for (unsigned int i = 0; i < TAILLE_BUFFER_DONNEES_INERTIELLES; i++)  
  {
    log(donneesInertiellesFrenet[i], SOUS_MODULE_IMU_BUFFER, ENTETE_DATA);
    delay(DELAI_ENVOI_UDP);
  }
  delay(DELAI_ENVOI_UDP);
  logger.log(SOUS_MODULE_IMU_BUFFER, "BUFFER_END", "Fin des données dans le cache de calibration");
}

void CentraleInertielle::log(DonneesInertielles &data, const char module[], const char message[]) {
  int longueur = 5 + decimales;
  itoa(data.t, strLog, 10);
  strcat(strLog, SEPARATEUR_DATA);

  dtostrf(data.accX, longueur, decimales, strNumber);
  strcat(strLog, strNumber);
  strcat(strLog, SEPARATEUR_DATA);
  
  dtostrf(data.accY, longueur, decimales, strNumber);
  strcat(strLog, strNumber);
  strcat(strLog, SEPARATEUR_DATA);
  
  dtostrf(data.accZ, longueur, decimales, strNumber);
  strcat(strLog, strNumber);
  strcat(strLog, SEPARATEUR_DATA);
  
  dtostrf(data.vAlpha, longueur, decimales, strNumber);
  strcat(strLog, strNumber);
  strcat(strLog, SEPARATEUR_DATA);
  
  dtostrf(data.vBeta, longueur, decimales, strNumber);
  strcat(strLog, strNumber);
  strcat(strLog, SEPARATEUR_DATA);
  
  dtostrf(data.vGamma, longueur, decimales, strNumber);
  strcat(strLog, strNumber);

  logger.log(module, message, strLog);
}

void CentraleInertielle::integration() {
  // TODO
}

void CentraleInertielle::stabiliser() {
  if(rcsActif) {
    stabiliserParTuyere();
  }
  if(wcsActif) {
    stabiliserParAilerons();
  }
}

float CentraleInertielle::funcCorrection(float var){
  return a*pow(var,3) + b*pow(var,2) + c*var + d;

}

void CentraleInertielle::stabiliserParAilerons() {
  float xCorrection = funcCorrection(donneesInertiellesFrenet[index].accX);
  float yCorrection = funcCorrection(donneesInertiellesFrenet[index].accY);
  
  wcsServoX->position(xCorrection);
  wcsServoY->position(yCorrection);
}

void CentraleInertielle::stabiliserParTuyere() {
  // TODO
}

void CentraleInertielle::setCorrectionFunctionParameters(float a2, float b2, float c2, float d2) {
  a = a2;
  b = b2;
  c = c2;
  d = d2;
}