#ifndef AlertLight_h
#define AlertLight_h

#include "Arduino.h"

typedef enum {
    NO_ALERT = 0,
    LOW_ALERT = 1,
    MID_ALERT = 2,
    HIGH_ALERT = 3
} alert_level_t;

class AlertLight
{
    public:
        AlertLight(byte pin);
        void setLevel(alert_level_t);
        void unsetLevel(alert_level_t);
        void loop();

        unsigned int midLevelBlinkPeriod = 1000;
        unsigned int highLevelBlinkPeriod = 500;

    private:
        byte _pin;
        alert_level_t _level = NO_ALERT;
        unsigned long _lastBlinkTime = 0;
        void _blink();
};

#endif
