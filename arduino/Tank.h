#ifndef Tank_h
#define Tank_h
#define WEBDUINO_NO_IMPLEMENTATION

#include "Arduino.h"
#include "WebServer.h"

class Tank
{
    public:
        Tank(int pinPumpIn, int pinPumpOut, int pinUrbanNetwork, int pinFlowIn, int pinFlowOut, int pinWaterLimitLow, int pinWaterLimitHigh, int pinFilterInBlocked, int pinMotorInBlocked, int pinLightWater, int pinLightMotor, void (*sendAlert_)(const char *, const char *));
        byte minFlowIn = 6; // mL/s
        unsigned int timeToFillUp = 30; // m

        void (*sendAlert)(const char *, const char *);
        void attachFlowInterrupts();
        void (*flowInInterrupt)();
        void (*flowOutInterrupt)();
        void flowInPulsed();
        void flowOutPulsed();

        void loop();
        bool isMotorInBlocked();
        bool isFilterInBlocked();
        bool isTankFull();
        bool isTankEmpty();
        bool isWellFull();
        bool isWellEmpty();

        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        int _pinPumpIn;
        int _pinPumpOut;
        int _pinUrbanNetwork;
        int _pinFlowIn;
        int _pinFlowOut;
        int _pinWaterLimitLow;
        int _pinWaterLimitHigh;
        int _pinFilterInBlocked;
        int _pinMotorInBlocked;
        int _pinLightWater;
        int _pinLightMotor;

        unsigned int _flowIn = 0; // mL/s
        unsigned int _flowOut = 0; // mL/s
        unsigned long _oldTimeFlow = 0;
        unsigned long _lastTimePumpInOff = 0;
        volatile byte _flowInPulses = 0;
        volatile byte _flowOutPulses = 0;

        void _dettachFlowInterrupts();
        void _computeFlowRates();
        void _alertWater(bool);
        void _alertMotor(bool);
        void _cmdPumpIn(bool);
        void _cmdPumpOut(bool);
        void _cmdUrbanNetwork(bool);

        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
