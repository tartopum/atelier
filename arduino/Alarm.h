#ifndef Alarm_h
#define Alarm_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "Arduino.h"
#include "WebServer.h" // https://github.com/sirleech/Webduino
#include "Alert.h"
#include "AlertLight.h"

typedef enum {
    DISABLED,
    STARTING,
    LISTENING,
} alarm_state_t;

class Alarm
{
    public:
        Alarm(
            int,
            int,
            int,
            int,
            int,
            int,
            AlertLight *alertLight,
            bool (*sendAlert)(const char *, const char *, byte)
        );
        unsigned long delayBeforeAlert = 3000;
        // The movement detector stays active ~ 8 seconds after we leave the room
        unsigned long delayBeforeListening = 20000;

        void loop();
        bool listening();
        bool breachDetected();
        bool movementDetected();
        void enable(bool);
        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        int _pinDetector;
        int _pinBuzzer;
        int _pinBuzzerStart;
        int _pinListening;
        int _pinNotListening;
        int _pinListenSwitch;
        Alert _alert;

        bool _breachDetected = false;
        alarm_state_t _state = LISTENING;
        uint8_t _curSwitchState; 
        unsigned long _breachTime = 0;
        unsigned long _enabledTime = 0;
        bool _warnStarting = true;

        void _handleSwitch();
        void _updateState();

        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
