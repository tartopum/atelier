#ifndef Light_h
#define Light_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "Arduino.h"
#include "WebServer.h" // https://github.com/sirleech/Webduino
#include "Time.h"
#include "TimeRange.h"

class Light
{
    public:
        Light(int, int);
        bool isInsideOn();
        bool isOutsideOn();
        void cmdInside(bool on);
        void cmdOutside(bool on);
        void command();
        TimeRange sleep;

        void httpRouteState(WebServer &server, WebServer::ConnectionType type, char *, bool);
        void httpRouteInsideOn(WebServer &server, WebServer::ConnectionType type, char *, bool);
        void httpRouteInsideOff(WebServer &server, WebServer::ConnectionType type, char *, bool);
        void httpRouteOutsideOn(WebServer &server, WebServer::ConnectionType type, char *, bool);
        void httpRouteOutsideOff(WebServer &server, WebServer::ConnectionType type, char *, bool);

    private:
        int _pinInside;
        int _pinOutside;
};

#endif
