#ifndef Lights_h
#define Lights_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "Arduino.h"
#include "WebServer.h" // https://github.com/sirleech/Webduino
#include "Time.h"
#include "TimeRange.h"

class Lights
{
    public:
        Lights(int pinsInside[2], int pinsOutside[1], int pinsBtn[2]);
        unsigned long pressDelay = 2000;
        void cmdInside(bool on, int n = -1);
        void cmdOutside(bool on, int n = -1);
        void command();
        TimeRange sleep;

        void httpRouteState(WebServer &server, WebServer::ConnectionType type, char *, bool);
        void httpRouteCmdInside(WebServer &server, WebServer::ConnectionType type, char *, bool);
        void httpRouteCmdOutside(WebServer &server, WebServer::ConnectionType type, char *, bool);

    private:
        int* _pinsInside;
        int* _pinsOutside;
        int* _pinsBtn;
        unsigned long _lastDebounceTime = 0;
        unsigned long _debounceDelay = 1000;
        void _commandFromBtn();
};

#endif
