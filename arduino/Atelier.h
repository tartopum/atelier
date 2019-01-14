#ifndef Atelier_h
#define Atelier_h

#include "Alarm.h"
#include "Lights.h"
#include "Fence.h"
#include "AlertLight.h"

class Atelier
{
    public:
        Atelier(
            int pinPowerSupply,
            unsigned long inactivityDelay_,
            Alarm *alarm,
            Lights *lights
        );
        unsigned long inactivityDelay;
        void loop();
        void cmdPowerSupply(bool on);
        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        Alarm *_alarm;
        Lights *_lights;
        int _pinPowerSupply;
        bool _breach = false;
        bool _isInsideLightOn = false;
        unsigned long _lastActivityTime = 0;
        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
