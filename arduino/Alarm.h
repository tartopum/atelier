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
        Alarm(int, int, int, int, int, int, TimeRange *lunch, TimeRange *night);
        unsigned long millisBeforeAlert = 15000;

        bool control();
        bool listening();
        bool movementDetected();
        bool breachDetected();
        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        int _pinDetector;
        int _pinBuzzer;
        int _pinLightAlert;
        int _pinListening;
        int _pinNotListening;
        int _pinListenSwitch;

        TimeRange *_lunch;
        TimeRange *_night;
        bool _listening = false;
        uint8_t _oldListenSwitchState; 
        unsigned long _breachTime = 0;
        unsigned long _lightStateChangeTime = 0;

        void _updateListeningFromSwitch(); 
        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
