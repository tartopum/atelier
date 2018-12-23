#ifndef Atelier_h
#define Atelier_h

#include "Alarm.h"
#include "Lights.h"
#include "Fence.h"

class Atelier
{
    public:
        Atelier(int pinStopPower, int pinsAlarm[5], int pinsLight[3], int pinsLightBtn[2], int pinsFence[2]);
        Alarm alarm;
        Lights lights;
        Fence fence;
        void control();
        void cmdPower(bool on);

    private:
        int _pinStopPower;
};

#endif
