#ifndef Atelier_h
#define Atelier_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "WebServer.h"

class Atelier
{
    public:
        Atelier(int);
        //Alarm alarm;
        //Lights lights;

    private:
        int _pinStopPower;
};

#endif
