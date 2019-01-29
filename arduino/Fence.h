#ifndef Fence_h
#define Fence_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "Arduino.h"
#include "WebServer.h"
#include "AlertLight.h"

class Fence
{
    public:
        Fence(int pinControl, AlertLight *light);
        void on();
        void off();
        bool isOn();
        void loop();
        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        int _pinControl;
        AlertLight *_light;
        bool _activated = true;
        unsigned long _lightStateChangeTime = 0;
        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
