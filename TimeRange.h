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
        byte endHour = 0; // 0-23
        byte endMinute = 0; // 0-59
        byte beginHour = 0;
        byte beginMinute = 0;
        bool set(byte, byte, byte, byte);
        bool isNow();
        void httpRouteSet(WebServer &server, WebServer::ConnectionType type, char *, bool);
};

#endif
