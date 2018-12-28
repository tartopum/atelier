#ifndef Atelier_h
#define Atelier_h

#include "Alarm.h"
#include "Lights.h"
#include "Fence.h"

class Atelier
{
    public:
        Atelier(int pinPowerSupply, unsigned long inactivityDelay_, int pinsAlarm[6], int pinsLight[3], int pinsLightBtn[2], int pinsFence[2]);
        // Need to be public to access HTTP routes
        Alarm alarm;
        Lights lights;
        Fence fence;
        unsigned long inactivityDelay;
        void loop();
        void cmdPowerSupply(bool on);
        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        int _pinPowerSupply;
        unsigned long _lastActivityTime = 0;
        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
