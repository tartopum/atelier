#ifndef Light_h
#define Light_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "Arduino.h"
#include "WebServer.h" // https://github.com/sirleech/Webduino
#include "Time.h"

class TimeRange
{
    public:
        TimeRange(byte, byte, byte, byte);
        bool set(byte, byte, byte, byte);
        bool entering();
        bool leaving();
        bool isNow();
        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        byte _bh; // 0-23
        byte _bm; // 0-59
        byte _eh;
        byte _em;
        bool _wasIn = false;
        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
