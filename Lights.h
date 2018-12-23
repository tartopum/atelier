#ifndef Lights_h
#define Lights_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "Arduino.h"
#include "WebServer.h" // https://github.com/sirleech/Webduino
#include "Time.h"
#include "TimeRange.h"

typedef enum {
    OUTSIDE = 0,
    INSIDE1 = 1,
    INSIDE2 = 2,
} light_t;

class Lights
{
    public:
        Lights(int, int, int);
        bool isOn(light_t light);
        void cmdLight(light_t light, bool on);
        void cmdInside(bool on);
        void cmdOutside(bool on);
        void command();
        TimeRange sleep;

        void httpRouteState(WebServer &server, WebServer::ConnectionType type, char *, bool);
        void httpRouteCmd(WebServer &server, WebServer::ConnectionType type, char *, bool);

    private:
        int _lightToPin(light_t);
        int _pinInside1;
        int _pinInside2;
        int _pinOutside;
};

#endif
