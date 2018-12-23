#ifndef Lights_h
#define Lights_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "Arduino.h"
#include "WebServer.h" // https://github.com/sirleech/Webduino
#include "Time.h"
#include "TimeRange.h"
#include "TwoButtons.h"

class Lights
{
    public:
        Lights(int lightPins[3], int, int);
        void cmdLight(int n, bool on);
        void command();
        TimeRange sleep;
        TwoButtons buttons;

        void httpRouteState(WebServer &server, WebServer::ConnectionType type, char *, bool);
        void httpRouteCmd(WebServer &server, WebServer::ConnectionType type, char *, bool);

    private:
        byte _N_PINS = 3;
        int* _pins;
        void _commandFromBtn();
};

#endif
