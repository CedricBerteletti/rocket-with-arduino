/*
 * --------------------------------------------------------------------------
 * Gestion d'un servomoteur
 * --------------------------------------------------------------------------
 * @author Cédric Berteletti
 */

#ifndef Servomoteur_h
#define Servomoteur_h

#include <Arduino.h>
#include "Logger.hpp"
#include <Servo.h>

inline constexpr int SERVO_DECALAGE_PAR_DEFAUT = 90;
inline constexpr float SERVO_PENTE_PAR_DEFAUT = 0.9f;
inline constexpr float SERVO_POSITION_MIN = -100;
inline constexpr float SERVO_POSITION_MAX = 100;

class Servomoteur
{
  public:
    Servomoteur();
    void init(int id, int broche, Logger *logger);
    void setDecalage(int decalage);
    void setPente(float pente);
    void angle(int angle);
    void position(int position);
    void logStatut();
  
  private:
    static const char MODULE_SERVO[];
    char strTmp[LONGUEUR_MAX_CHAINE_CARACTERES];
    Logger *logger;
    Servo servo;
    int id;
    int broche;
    int decalage = SERVO_DECALAGE_PAR_DEFAUT;
    float pente = SERVO_PENTE_PAR_DEFAUT;    
};

#endif