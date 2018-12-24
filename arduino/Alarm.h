#ifndef Alarm_h
#define Alarm_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "Arduino.h"
#include "WebServer.h" // https://github.com/sirleech/Webduino
#include "Time.h"
#include "TimeRange.h"

class Alarm
{
    public:
        Alarm(int, int, int, int, int);
        unsigned long millisBeforeAlert = 5000;
        TimeRange listeningPeriod;

        bool control();
        bool listening();
        bool breachDetected();
        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        int _pinDetector;
        int _pinBuzzer;
        int _pinLightAlert;
        int _pinListening;
        int _pinListenSwitch;

        bool _listening = false;
        bool _wasInListeningPeriod = false;
        uint8_t _oldListenSwitchState; 
        unsigned long _breachTime = 0;

        void _updateListeningFromSwitch(); 
        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
