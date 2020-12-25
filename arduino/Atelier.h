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
            Lights *lights,
            bool (*sendAlert)(const char *, const char *, byte)
        );
        unsigned long inactivityDelay;
        unsigned long powerManualModeReminderDelay = 86400000;

        void loop();
        void cmdPowerSupply(bool on);
        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        Alarm *_alarm;
        Lights *_lights;
        Alert _powerManualModeAlert;

        int _pinPowerSupply;
        bool _breach = false;
        bool _isInsideLightOn = false;
        bool _isAlarmListening = false;
        unsigned long _lastActivityTime = 0;
        unsigned long _powerManualModeTime = 0;
        bool _powerManualMode = false;

        void _setManualMode(bool);
        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
