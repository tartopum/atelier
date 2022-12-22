#ifndef Tank_h
#define Tank_h
#define WEBDUINO_NO_IMPLEMENTATION

#include <Arduino.h>
#include <WebServer.h>
#include "Alert.h"
#include "AlertLight.h"

class Tank
{
    public:
        // Voir le detail des pins dans le constructeur Tank() dans Tank.cpp
        Tank(
            byte pinPumpIn,
            byte pinPumpOut,
            byte pinPumpOutCanRun,
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
            AlertLight *lightWarning,
            AlertLight *lightFatal,
            bool (*sendAlert)(const char *, const char *, byte)
        );

        // Ces variables sont configurables depuis l'interface web
        byte minFlowIn = 10; // L/min
        unsigned long timeToFillUp = 30 * 60 * 1000; // ms
        unsigned long flowCheckPeriod = 30 * 1000; // ms
        unsigned long filterCleaningPeriod = 60 * 60 * 1000; // ms
        unsigned long filterCleaningDuration = 30 * 1000; // ms
        unsigned long filterCleaningConsecutiveDelay = 5 * 1000; // ms
        unsigned long maxPumpOutRunningDuration = 5 * 60 * 1000; // ms
        unsigned long minPumpOutStopDuration = 60 * 1000; // ms
        unsigned long maxDurationWithoutFlowOut = 60 * 60 * 1000; // ms

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
        bool pumpOutRunningForTooLong();
        bool canPumpOutRun();
        bool isFillingCycleEmpty();
        bool isConsumptionMissing();

        void httpRoute(WebServer &server, WebServer::ConnectionType type);
        void httpRouteStats(WebServer &server, WebServer::ConnectionType type);

    private:
        byte _pinPumpIn;
        byte _pinPumpOut;
        byte _pinPumpOutCanRun;
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

        bool _manualMode = true;

        float _flowIn = 0.0; // L/min
        float _flowOut = 0.0; // L/min
        unsigned long _oldTimeFlow = 0;
        volatile byte _flowInPulses = 0; // L
        volatile byte _flowOutPulses = 0; // L

        bool _pumpInActivated = true;
        unsigned long _lastTimePumpInOff = 0; // ms
        unsigned long _timePumpInStarted = 0; // ms
        unsigned long _pumpInStartDuration = 60000; // ms
        volatile int _volumeInCurCycle = -1;
        unsigned int _pumpInRunningDuration = 0; // s
        unsigned long _pumpInRunningDurationStart = 0; // ms

        bool _pumpOutActivated = true;
        unsigned int _volumeBeforePumpOut = 500; // L
        volatile unsigned int _volumeCollectedSinceEmpty = 0; // L
        bool _tankFullEnough = true;
        unsigned long _lastTimePumpOutOff = 0; // ms
        unsigned long _pumpOutRunningDurationStart = 0; // ms
        unsigned int _pumpOutRunningDuration = 0; // s
        volatile unsigned long _lastTimeFlowOut = 0; // ms

        unsigned long _lastFilterCleaningTime = 0; // ms
        bool _filterFirstCleaningDone = false;

        bool _urbanNetworkActivated = true;
        unsigned long _urbanNetworkRunningDurationStart = 0; // ms
        unsigned int _urbanNetworkRunningDuration = 0; // s

        // Stats
        volatile unsigned long _volumeIn = 0; // L
        volatile unsigned long _volumeOutTank = 0; // L
        volatile unsigned long _volumeOutUrbanNetwork = 0; // L

        void _computeFlowRates();
        void _cmdPumpIn(bool);
        void _cmdPumpOut(bool);
        void _cmdUrbanNetwork(bool);
        void _cmdFilterCleaning(bool);

        Alert _motorInBlockedAlert;
        Alert _motorOutBlockedAlert;
        Alert _filterInBlockedAlert;
        Alert _overpressureAlert;
        Alert _urbanNetworkUsedAlert;
        Alert _manualModeAlert;
        Alert _pumpOutRunningForTooLongAlert;
        Alert _noFlowInAlert;
        Alert _noFlowOutAlert;
        Alert _pumpInDisabledAlert;
        Alert _pumpOutDisabledAlert;

        void _httpRouteGet(WebServer &server);
        void _httpRouteSet(WebServer &server);
};

#endif
