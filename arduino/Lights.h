#ifndef Lights_h
#define Lights_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "Arduino.h"
#include "WebServer.h" // https://github.com/sirleech/Webduino
#include "TwoButtons.h"

class Lights
{
    public:
        Lights(int lightPins[3], int pinBtn1, int pinBtn2);
        void cmdAll(bool on);
        void cmdLight(int n, bool on);
        bool isOn(int n);
        void loop();
        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        byte _N_PINS = 3;
        int* _pins;
        TwoButtons _buttons;
        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
