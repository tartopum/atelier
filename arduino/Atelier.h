#ifndef Atelier_h
#define Atelier_h

#include "Alarm.h"
#include "Lights.h"
#include "Fence.h"

class Atelier
{
    public:
        Atelier(int pinStopPower, unsigned long inactivityDelay_, int pinsAlarm[6], int pinsLight[3], int pinsLightBtn[2], int pinsFence[2], TimeRange *lunch, TimeRange *night);
        // Need to be public to access HTTP routes
        TimeRange *lunch;
        TimeRange *night;
        Alarm alarm;
        Lights lights;
        Fence fence;
        unsigned long inactivityDelay;
        void control();
        void cmdPower(bool on);
        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        int _pinStopPower;
        unsigned long _lastInactivityTime = 0;
        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
