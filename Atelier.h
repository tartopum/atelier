#ifndef Atelier_h
#define Atelier_h

#include "Alarm.h"
#include "Lights.h"

class Atelier
{
    public:
        Atelier(int pinStopPower, int pinsAlarm[5], int pinsLight[3], int pinsLightBtn[2]);
        Alarm alarm;
        Lights lights;
        void control();
        void cmdPower(bool on);

    private:
        int _pinStopPower;
};

#endif
