#include <util/atomic.h>
#include "Tank.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Tank::Tank(
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
    void (*sendAlert)(const char *, const char *, byte)
) :
    _motorInBlockedAlert(
        "tank",
        "Le moteur de la pompe du puits est en panne.",
        sendAlert,
        lightFatal,
        MID_ALERT,
        120
    ),
    _motorOutBlockedAlert(
        "tank",
        "Le moteur de la pompe du surpresseur est en panne.",
        sendAlert,
        lightFatal,
        MID_ALERT,
        120
    ),
    _filterInBlockedAlert(
        "tank",
        "Le filtre est encrassé.",
        sendAlert,
        lightWarning,
        HIGH_ALERT,
        120
    ),
    _overpressureAlert(
        "tank",
        "Le système est en surpression.",
        sendAlert,
        lightFatal,
        HIGH_ALERT,
        15
    ),
    _urbanNetworkUsedAlert(
        "",
        "",
        sendAlert,
        lightWarning,
        LOW_ALERT,
        120
    ),
    _manualModeAlert(
        "tank",
        "La cuve est en mode manuel.",
        sendAlert,
        lightFatal,
        LOW_ALERT,
        1440
    ),
    _pumpOutRunningForTooLongAlert(
        "tank",
        "La pompe du surpresseur a fonctionné trop longtemps.",
        sendAlert,
        lightFatal,
        MID_ALERT,
        240
    ),
    _noFlowInAlert(
        "tank",
        "La pompe du puits n'a pas remonté d'eau durant le cycle de remplissage.",
        sendAlert,
        lightFatal,
        MID_ALERT
    ),
    _noFlowOutAlert(
        "tank",
        "Il n'y a pas eu de consommation détectée depuis trop longtemps.",
        sendAlert,
        lightFatal,
        MID_ALERT
    ),
    _pumpInDisabledAlert(
        "",
        "",
        sendAlert,
        lightFatal,
        HIGH_ALERT
    ),
    _pumpOutDisabledAlert(
        "",
        "",
        sendAlert,
        lightFatal,
        HIGH_ALERT
    )
{
    _pinPumpIn = pinPumpIn;
    _pinPumpOut = pinPumpOut;
    _pinPumpOutCanRun = pinPumpOutCanRun;
    _pinUrbanNetwork = pinUrbanNetwork;
    _pinFlowIn = pinFlowIn;
    _pinFlowOut = pinFlowOut;
    _pinWaterLimitLow = pinWaterLimitLow;
    _pinWaterLimitHigh = pinWaterLimitHigh;
    _pinFilterInBlocked = pinFilterInBlocked;
    _pinMotorInBlocked = pinMotorInBlocked;
    _pinMotorOutBlocked = pinMotorOutBlocked;
    _pinOverpressure = pinOverpressure;
    _pinFilterCleaning = pinFilterCleaning;

    pinMode(_pinFlowIn, INPUT);
    pinMode(_pinFlowOut, INPUT);
    pinMode(_pinWaterLimitLow, INPUT);
    pinMode(_pinWaterLimitHigh, INPUT);
    pinMode(_pinFilterInBlocked, INPUT);
    pinMode(_pinMotorInBlocked, INPUT);
    pinMode(_pinMotorOutBlocked, INPUT);
    pinMode(_pinOverpressure, INPUT);
    pinMode(_pinPumpOutCanRun, INPUT);

    pinMode(_pinPumpIn, OUTPUT);
    pinMode(_pinPumpOut, OUTPUT);
    pinMode(_pinUrbanNetwork, OUTPUT);
    pinMode(_pinFilterCleaning, OUTPUT);

    _cmdPumpIn(false);
    _cmdPumpOut(false);
    _cmdUrbanNetwork(false);
}

bool isOn(int pin)
{
    return digitalRead(pin) == HIGH;
}

bool isOff(int pin)
{
    return digitalRead(pin) == LOW;
}

/*
 * Input
 */
bool Tank::isMotorInBlocked()
{
    return isOn(_pinMotorInBlocked);
}

bool Tank::isMotorOutBlocked()
{
    return isOn(_pinMotorOutBlocked);
}

bool Tank::isOverpressured()
{
    return isOn(_pinOverpressure);
}

bool Tank::isFilterInBlocked()
{
    return isOn(_pinFilterInBlocked);
}

bool Tank::isTankFull()
{
    return isOn(_pinWaterLimitHigh);
}

bool Tank::isTankEmpty()
{
    return isOn(_pinWaterLimitLow);
}

bool Tank::isWellFull()
{
    return (millis() - _lastTimePumpInOff) > timeToFillUp;
}

bool Tank::isWellEmpty()
{
    // Wait a bit for the pump to start
    // We need to wait for two checking periods to avoid this:
    // 1. Flow rate = 0
    // 2. At (flowCheckPeriod - delta), start pump
    // 3. At flowCheckPeriod, compute flowIn: 0
    // 4. At (2*flowCheckPeriod - delta), read flowIn below: still 0
    if ((millis() - _timePumpInStarted) < (_pumpInStartDuration + flowCheckPeriod)) return false;
    return _flowIn < minFlowIn;
}

bool Tank::canCleanFilter()
{
    return isOn(_pinPumpIn) && (millis() - _timePumpInStarted > _pumpInStartDuration) && (
        (!_filterFirstCleaningDone && millis() - _lastFilterCleaningTime > filterCleaningPeriod) ||
        (_filterFirstCleaningDone && millis() - _lastFilterCleaningTime > filterCleaningConsecutiveDelay)
    );
}

bool Tank::pumpOutRunningForTooLong()
{
    return isOn(_pinPumpOut) && (millis() - _lastTimePumpOutOff > maxPumpOutRunningDuration);
}

bool Tank::canPumpOutRun()
{
    return digitalRead(_pinPumpOutCanRun) == HIGH;
}

bool Tank::isFillingCycleEmpty()
{
    int volumeInCurCycle;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        volumeInCurCycle = _volumeInCurCycle;
    }
    return (
        isOn(_pinPumpIn) &&
        isOff(_pinFilterCleaning) &&
        (millis() - _timePumpInStarted > _pumpInStartDuration) &&
        volumeInCurCycle == 0
    );
}

bool Tank::isConsumptionMissing()
{
    unsigned long lastTimeFlowOut;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        lastTimeFlowOut = _lastTimeFlowOut;
    }
    return millis() - lastTimeFlowOut > maxDurationWithoutFlowOut;
}

/*
 * Output
 */
void Tank::_cmdPumpIn(bool on)
{
    if (isOverpressured()) on = false;
    if (isMotorInBlocked()) on = false;
    if (isTankFull()) on = false;
    if (!_pumpInActivated) on = false;

    if (!on && isOn(_pinPumpIn)) {
        _lastTimePumpInOff = millis();
        _pumpInRunningDuration += (millis() - _pumpInRunningDurationStart) / 1000;
    }
    if (on && !isOn(_pinPumpIn)) {
        _timePumpInStarted = millis();
        _pumpInRunningDurationStart = millis();
    }

    if (on) {
        ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
            _volumeInCurCycle = 0;
        }
    }

    digitalWrite(_pinPumpIn, on ? HIGH : LOW); 
}

void Tank::_cmdPumpOut(bool on)
{
    if (isOverpressured()) on = false;
    if (isMotorOutBlocked()) on = false;
    if (!_manualMode && !canPumpOutRun()) on = false;
    if (!_pumpOutActivated) on = false;

    if (on && !isOn(_pinPumpOut)) _pumpOutRunningDurationStart = millis();
    if (!on && isOn(_pinPumpOut)) {
        _pumpOutRunningDuration += (millis() - _pumpOutRunningDurationStart) / 1000;
    }

    digitalWrite(_pinPumpOut, on ? HIGH : LOW); 
}

void Tank::_cmdUrbanNetwork(bool on)
{
    if (!_urbanNetworkActivated) on = false;
    if (on && !isOn(_pinUrbanNetwork)) _urbanNetworkRunningDurationStart = millis();
    if (!on && isOn(_pinUrbanNetwork)) {
        _urbanNetworkRunningDuration += (millis() - _urbanNetworkRunningDurationStart) / 1000;
    }
    digitalWrite(_pinUrbanNetwork, on ? HIGH : LOW); 
}

void Tank::_cmdFilterCleaning(bool on)
{
    if (on) {
        _lastFilterCleaningTime = millis();
        _filterFirstCleaningDone = !_filterFirstCleaningDone; 
    }
    digitalWrite(_pinFilterCleaning, on ? HIGH : LOW); 
}

void Tank::loop()
{
    _manualModeAlert.raise(_manualMode);
    _motorInBlockedAlert.raise(isMotorInBlocked());
    _motorOutBlockedAlert.raise(isMotorOutBlocked());
    _filterInBlockedAlert.raise(isFilterInBlocked());
    _overpressureAlert.raise(isOverpressured());
    _pumpOutRunningForTooLongAlert.raise(pumpOutRunningForTooLong());
    _urbanNetworkUsedAlert.raise(isOn(_pinUrbanNetwork));
    _noFlowInAlert.raise(isFillingCycleEmpty());
    _noFlowOutAlert.raise(isConsumptionMissing());
    _pumpInDisabledAlert.raise(!_pumpInActivated);
    _pumpOutDisabledAlert.raise(!_pumpOutActivated);

    if (isMotorInBlocked() || isFilterInBlocked() || isFillingCycleEmpty()) {
        _cmdPumpIn(false);
        _pumpInActivated = false;
    }
    if (isMotorOutBlocked() || isOverpressured() || pumpOutRunningForTooLong()) {
        _cmdPumpOut(false);
        _cmdUrbanNetwork(true);
        _pumpOutActivated = false;
    }

    _computeFlowRates();

    if (isOff(_pinPumpOut)) {
        _lastTimePumpOutOff = millis();
    }

    if (isTankFull()) {
        _cmdPumpIn(false);
    }

    if (_manualMode) {
        return;
    }

    // Clean filter
    if (canCleanFilter()) {
        _cmdFilterCleaning(true);
    }
    if (millis() - _lastFilterCleaningTime > filterCleaningDuration) {
        _cmdFilterCleaning(false);
    }

    // Command pump-out and urban network
    unsigned int volumeCollectedSinceEmpty;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        volumeCollectedSinceEmpty = _volumeCollectedSinceEmpty;
    }
    if (!_pumpOutActivated) {
        _cmdUrbanNetwork(true);
    }
    if (isTankEmpty()) {
        _tankFullEnough = false;
        _cmdPumpOut(false);
        _cmdUrbanNetwork(true);
        ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
            _volumeCollectedSinceEmpty = 0;
        }
    } else if (_tankFullEnough && _pumpOutActivated) {
        _cmdPumpOut(isOn(_pinPumpOutCanRun));
        _cmdUrbanNetwork(false);
    } else if (volumeCollectedSinceEmpty > _volumeBeforePumpOut) {
        // We need this state because the tank could stay always full and
        // _volumeCollectedSinceEmpty could loop back to 0. So we can only rely on
        // it when it's "low".
        _tankFullEnough = true;
    }

    // Command pump-in
    if (_pumpInActivated && isOff(_pinPumpIn) && isWellFull() && !isTankFull()) {
        _cmdPumpIn(true);
    }
    if (isOn(_pinPumpIn) && (isWellEmpty() || isTankFull())) {
        _cmdPumpIn(false);
    }
}

/*
 * Interrupts
 */
void Tank::flowInPulsed()
{
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        _flowInPulses++;
    }
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        _volumeCollectedSinceEmpty++;
    }
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        _volumeIn++;
    }
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        _volumeInCurCycle++;
    }
}

void Tank::flowOutPulsed()
{
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        _flowOutPulses++;
    }
    if (isOn(_pinUrbanNetwork)) {
        ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
            _volumeOutUrbanNetwork++;
        }
    } else {
        ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
            _volumeOutTank++;
        }
    }
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        _lastTimeFlowOut = millis();
    }
}

void Tank::attachFlowInterrupts()
{
    attachInterrupt(digitalPinToInterrupt(_pinFlowIn), flowInInterrupt, RISING);
    attachInterrupt(digitalPinToInterrupt(_pinFlowOut), flowOutInterrupt, RISING);
}

void Tank::_computeFlowRates()
{
    if((millis() - _oldTimeFlow) < flowCheckPeriod) return;
    unsigned int flowInPulses = 0;
    unsigned int flowOutPulses = 0;
    unsigned long time;

    // We detach interrupts to avoid editing millis() and _flowInPulses during
    // the computations
    // https://www.arduino.cc/reference/en/language/variables/variable-scope--qualifiers/volatile/
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        flowInPulses = _flowInPulses;
        flowOutPulses = _flowOutPulses;
        time = millis();
        _flowInPulses = 0;
        _flowOutPulses = 0;
    }

    // 1 pulse = 1L
    // flow rates in L/min
    _flowIn = 60000.0 / (time - _oldTimeFlow) * flowInPulses;
    _flowOut = 60000.0 / (time - _oldTimeFlow) * flowOutPulses;
    _oldTimeFlow = time;
}

/*
 * HTTP
 */
void Tank::_httpRouteGet(WebServer &server)
{
    server.httpSuccess("application/json");
    server << "{ ";
    server << "\"manual_mode\": " << _manualMode << ", ";
    server << "\"pump_in_activated\": " << _pumpInActivated << ", ";
    server << "\"pump_in_running_duration\": " << _pumpInRunningDuration << ", ";
    server << "\"pump_in_running_duration_start\": " << _pumpInRunningDurationStart << ", ";
    server << "\"pump_out_activated\": " << _pumpOutActivated << ", ";
    server << "\"pump_out_running_duration\": " << _pumpOutRunningDuration << ", ";
    server << "\"pump_out_running_duration_start\": " << _pumpOutRunningDurationStart << ", ";
    server << "\"urban_network_activated\": " << _urbanNetworkActivated << ", ";
    server << "\"urban_network_running_duration\": " << _urbanNetworkRunningDuration << ", ";
    server << "\"urban_network_running_duration_start\": " << _urbanNetworkRunningDurationStart << ", ";
    server << "\"pump_in\": " << isOn(_pinPumpIn) << ", ";
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        server << "\"volume_in\": " << _volumeIn << ", ";
    }
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        server << "\"volume_out_tank\": " << _volumeOutTank << ", ";
    }
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        server << "\"volume_out_urban_network\": " << _volumeOutUrbanNetwork << ", ";
    }
    server << "\"millis\": " << millis() << ", ";
    server << "\"last_time_pump_in_off\": " << _lastTimePumpInOff << ", ";
    server << "\"last_time_pump_in_started\": " << _timePumpInStarted << ", ";
    server << "\"pump_in_start_duration\": " << _pumpInStartDuration << ", ";
    server << "\"pump_out\": " << isOn(_pinPumpOut) << ", ";
    server << "\"urban_network\": " << isOn(_pinUrbanNetwork) << ", ";
    server << "\"is_tank_full\": " << isTankFull() << ", ";
    server << "\"is_tank_empty\": " << isTankEmpty() << ", ";
    server << "\"is_well_full\": " << isWellFull() << ", ";
    server << "\"is_well_empty\": " << isWellEmpty() << ", ";
    server << "\"is_motor_in_blocked\": " << isMotorInBlocked() << ", ";
    server << "\"is_motor_out_blocked\": " << isMotorOutBlocked() << ", ";
    server << "\"is_overpressured\": " << isOverpressured() << ", ";
    server << "\"is_filter_in_blocked\": " << isFilterInBlocked() << ", ";
    server << "\"min_flow_in\": " << minFlowIn << ", ";
    server << "\"volume_before_pump_out\": " << _volumeBeforePumpOut << ", ";
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        server << "\"volume_collected_since_empty \": " << _volumeCollectedSinceEmpty << ", ";
    }
    server << "\"filter_cleaning\": " << isOn(_pinFilterCleaning) << ", ";
    server << "\"filter_cleaning_period\": " << filterCleaningPeriod << ", ";
    server << "\"filter_cleaning_duration\": " << filterCleaningDuration << ", ";
    server << "\"filter_cleaning_consecutive_delay\": " << filterCleaningConsecutiveDelay << ", ";
    server << "\"time_to_fill_up\": " << timeToFillUp << ", ";
    server << "\"max_pump_out_running_time\": " << maxPumpOutRunningDuration << ", ";
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        server << "\"last_time_flow_out\": " << _lastTimeFlowOut << ", ";
    }
    server << "\"max_duration_without_flow_out\": " << maxDurationWithoutFlowOut << ", ";
    server << "\"flow_check_period\": " << flowCheckPeriod << ", ";
    server << "\"flow_in\": " << _flowIn << ", ";
    server << "\"flow_out\": " << _flowOut;
    server << " }";
}

void Tank::_httpRouteSet(WebServer &server)
{
    const byte keyLen = 50;
    const byte valueLen = 50;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "manual_mode") == 0) {
            _manualMode = (strcmp(value, "1") == 0);
        }
        if (strcmp(key, "min_flow_in") == 0) {
            minFlowIn = atoi(value);
        }
        if (strcmp(key, "max_pump_out_running_time") == 0) {
            maxPumpOutRunningDuration = atol(value);
        }
        if (strcmp(key, "max_duration_without_flow_out") == 0) {
            maxDurationWithoutFlowOut = atol(value);
        }
        if (strcmp(key, "time_to_fill_up") == 0) {
            timeToFillUp = atol(value);
        }
        if (strcmp(key, "pump_in_start_duration") == 0) {
            _pumpInStartDuration = atol(value);
        }
        if (strcmp(key, "flow_check_period") == 0) {
            flowCheckPeriod = atol(value);
        }
        if (strcmp(key, "volume_before_pump_out") == 0) {
            _volumeBeforePumpOut = atoi(value);
        }
        if (strcmp(key, "pump_in") == 0) {
            _cmdPumpIn(strcmp(value, "1") == 0);
        }
        if (strcmp(key, "pump_in_activated") == 0) {
            _pumpInActivated = (strcmp(value, "1") == 0);
        }
        if (strcmp(key, "pump_out") == 0) {
            _cmdPumpOut(strcmp(value, "1") == 0);
        }
        if (strcmp(key, "pump_out_activated") == 0) {
            _pumpOutActivated = (strcmp(value, "1") == 0);
        }
        if (strcmp(key, "filter_cleaning") == 0) {
            _cmdFilterCleaning(strcmp(value, "1") == 0);
        }
        if (strcmp(key, "filter_cleaning_period") == 0) {
            filterCleaningPeriod = atol(value);
        }
        if (strcmp(key, "filter_cleaning_duration") == 0) {
            filterCleaningDuration = atol(value);
        }
        if (strcmp(key, "filter_cleaning_consecutive_delay") == 0) {
            filterCleaningConsecutiveDelay = atol(value);
        }
        if (strcmp(key, "urban_network") == 0) {
            _cmdUrbanNetwork(strcmp(value, "1") == 0);
        }
    }
    server.httpSuccess();
}

void Tank::httpRoute(WebServer &server, WebServer::ConnectionType type)
{
    if (type == WebServer::POST) {
        _httpRouteSet(server);
        return;
    }
    _httpRouteGet(server);
}

void Tank::httpRouteStats(WebServer &server, WebServer::ConnectionType type)
{
    if (type == WebServer::POST) {
        server.httpUnauthorized();
        return;
    }
    
    server.httpSuccess("application/json");
    server << "{ ";
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        server << "\"volume_in\": " << _volumeIn << ", ";
        _volumeIn = 0;
    }

    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        server << "\"volume_out_tank\": " << _volumeOutTank << ", ";
        _volumeOutTank = 0;
    }

    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        server << "\"volume_out_urban_network\": " << _volumeOutUrbanNetwork << ", ";
        _volumeOutUrbanNetwork = 0;
    }

    if (isOn(_pinPumpIn)) {
        _pumpInRunningDuration += (millis() - _pumpInRunningDurationStart) / 1000;
        _pumpInRunningDurationStart = millis();
    }
    server << "\"pump_in_running_duration\": " << _pumpInRunningDuration << ", ";
    _pumpInRunningDuration = 0;

    if (isOn(_pinPumpOut)) {
        _pumpOutRunningDuration += (millis() - _pumpOutRunningDurationStart) / 1000;
        _pumpOutRunningDurationStart = millis();
    }
    server << "\"pump_out_running_duration\": " << _pumpOutRunningDuration << ", ";
    _pumpOutRunningDuration = 0;

    if (isOn(_pinUrbanNetwork)) {
        _urbanNetworkRunningDuration += (millis() - _urbanNetworkRunningDurationStart) / 1000;
        _urbanNetworkRunningDurationStart = millis();
    }
    server << "\"urban_network_running_duration\": " << _urbanNetworkRunningDuration << ", ";
    _urbanNetworkRunningDuration = 0;

    server << "\"is_tank_full\": " << isTankFull() << ", ";
    server << "\"is_tank_empty\": " << isTankEmpty();
    server << " }";
}
