#ifndef Tank_h
#define Tank_h
#define WEBDUINO_NO_IMPLEMENTATION

#include <Arduino.h>
#include <WebServer.h>
#include "Alert.h"

class Tank
{
    public:
        Tank(
            byte pinPumpIn,
            byte pinPumpOut,
            byte pinUrbanNetwork,
            byte pinFlowIn,
            byte pinFlowOut,
            byte pinWaterLimitLow,
            byte pinWaterLimitHigh,
            byte pinFilterInBlocked,
            byte pinMotorInBlocked,
            byte pinMotorOutBlocked,
            byte pinOverpressure,
            byte pinFilterCleaning,
            byte pinLightWarning,
            byte pinLightFatal,
            void (*sendAlert)(const char *, const char *)
        );
        byte minFlowIn = 10; // L/min
        unsigned long timeToFillUp = 1800000; // ms
        unsigned long flowCheckPeriod = 30000; // ms
        unsigned long filterCleaningPeriod = 3600000; // ms
        unsigned long filterCleaningDuration = 30000; // ms

        void attachFlowInterrupts();
        void (*flowInInterrupt)();
        void (*flowOutInterrupt)();
        void flowInPulsed();
        void flowOutPulsed();

        void loop();
        bool isMotorInBlocked();
        bool isMotorOutBlocked();
        bool isFilterInBlocked();
        bool isOverpressured();
        bool isTankFull();
        bool isTankEmpty();
        bool isWellFull();
        bool isWellEmpty();
        bool canCleanFilter();

        void httpRoute(WebServer &server, WebServer::ConnectionType type);

    private:
        byte _pinPumpIn;
        byte _pinPumpOut;
        byte _pinUrbanNetwork;
        byte _pinFlowIn;
        byte _pinFlowOut;
        byte _pinWaterLimitLow;
        byte _pinWaterLimitHigh;
        byte _pinFilterInBlocked;
        byte _pinMotorInBlocked;
        byte _pinMotorOutBlocked;
        byte _pinOverpressure;
        byte _pinFilterCleaning;
        byte _pinLightWarning;
        byte _pinLightFatal;

        bool _manualMode = true;
        float _flowIn = 0.0; // L/min
        float _flowOut = 0.0; // L/min
        unsigned long _oldTimeFlow = 0;
        unsigned long _lastTimePumpInOff = 0; // ms
        unsigned long _timePumpInStarted = 0; // ms
        unsigned long _pumpInStartDuration = 60000; // ms
        volatile byte _flowInPulses = 0; // L
        volatile byte _flowOutPulses = 0; // L
        unsigned int _volumeBeforePumpOut = 500; // L
        unsigned int _volumeCollectedSinceEmpty = 0; // L
        bool _canEnablePumpOut = true;
        unsigned long _lastFilterCleaningTime = 0; // ms

        void _dettachFlowInterrupts();
        void _computeFlowRates();
        void _cmdPumpIn(bool);
        void _enablePumpOut(bool);
        void _cmdUrbanNetwork(bool);
        void _cmdFilterCleaning(bool);

        Alert _motorInBlockedAlert;
        Alert _motorOutBlockedAlert;
        Alert _filterInBlockedAlert;
        Alert _overpressureAlert;
        Alert _tankEmptyAlert;
        Alert _manualModeAlert;
        void _alertWarning(bool);
        void _alertFatal(bool);

        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
