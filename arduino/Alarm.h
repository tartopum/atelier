#ifndef Alarm_h
#define Alarm_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "Arduino.h"
#include "WebServer.h" // https://github.com/sirleech/Webduino
#include "Alert.h"
#include "AlertLight.h"

class Alarm
{
    public:
        Alarm(
            int,
            int,
            int,
            int,
            int,
            AlertLight *alertLight,
            void (*sendAlert)(const char *, const char *)
        );
        // The movement detector stays active ~ 8 seconds after we leave the room
        unsigned long millisBeforeAlert = 15000;

        void loop();
        bool listening();
        bool breachDetected();
        bool movementDetected();
        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        int _pinDetector;
        int _pinBuzzer;
        int _pinListening;
        int _pinNotListening;
        int _pinListenSwitch;
        Alert _alert;

        bool _breachDetected = false;
        bool _listening = false;
        uint8_t _oldListenSwitchState; 
        unsigned long _breachTime = 0;

        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
