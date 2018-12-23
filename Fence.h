#ifndef Fence_h
#define Fence_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "Arduino.h"
#include "WebServer.h"

class Fence
{
    public:
        Fence(int pinControl, int pinDisplay);
        void on();
        void off();
        bool isOn();
        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        int _pinControl;
        int _pinDisplay;
        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
