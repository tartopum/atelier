#include "Tank.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Tank::Tank(
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
) :
    _motorInBlockedAlert("tank", "Le moteur de la pompe est en panne.", sendAlert),
    _motorOutBlockedAlert("tank", "Le moteur du surpresseur est en panne.", sendAlert),
    _filterInBlockedAlert("tank", "Le filtre est encrassé.", sendAlert, 60),
    _overpressureAlert("tank", "Le système est en surpression.", sendAlert),
    _tankEmptyAlert("tank", "La cuve est vide.", sendAlert, 120),
    _manualModeAlert("tank", "La cuve est en mode manuel.", sendAlert)
{
    _pinPumpIn = pinPumpIn;
    _pinPumpOut = pinPumpOut;
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
    _pinLightWarning = pinLightWarning;
    _pinLightFatal = pinLightFatal;

    pinMode(_pinFlowIn, INPUT);
    pinMode(_pinFlowOut, INPUT);
    pinMode(_pinWaterLimitLow, INPUT);
    pinMode(_pinWaterLimitHigh, INPUT);
    pinMode(_pinFilterInBlocked, INPUT);
    pinMode(_pinMotorInBlocked, INPUT);
    pinMode(_pinMotorOutBlocked, INPUT);
    pinMode(_pinOverpressure, INPUT);

    pinMode(_pinPumpIn, OUTPUT);
    pinMode(_pinPumpOut, OUTPUT);
    pinMode(_pinUrbanNetwork, OUTPUT);
    pinMode(_pinLightWarning, OUTPUT);
    pinMode(_pinLightFatal, OUTPUT);
    pinMode(_pinFilterCleaning, OUTPUT);

    _cmdPumpIn(false);
    _enablePumpOut(false);
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
    if ((millis() - _timePumpInStarted) < (2 * flowCheckPeriod)) return false;
    return _flowIn < minFlowIn;
}

bool Tank::canCleanFilter()
{
    return (
        (millis() - _lastFilterCleaningTime > filterCleaningPeriod) &&
        isOn(_pinPumpIn)
    );
}

/*
 * Output
 */
void Tank::_alertWarning(bool on)
{
    digitalWrite(_pinLightWarning, on ? HIGH : LOW); 
}

void Tank::_alertFatal(bool on)
{
    digitalWrite(_pinLightFatal, on ? HIGH : LOW); 
}

void Tank::_cmdPumpIn(bool on)
{
    if (isOverpressured()) on = false;
    if (isMotorInBlocked()) on = false;
    if (isTankFull()) on = false;

    if (!on && isOn(_pinPumpIn)) _lastTimePumpInOff = millis();
    if (on && !isOn(_pinPumpIn)) _timePumpInStarted = millis();

    digitalWrite(_pinPumpIn, on ? HIGH : LOW); 
}

void Tank::_enablePumpOut(bool on)
{
    if (isOverpressured()) on = false;
    if (isMotorOutBlocked()) on = false;

    digitalWrite(_pinPumpOut, on ? HIGH : LOW); 
    if (!_manualMode) {
        _cmdUrbanNetwork(!on);
    }
}

void Tank::_cmdUrbanNetwork(bool on)
{
    digitalWrite(_pinUrbanNetwork, on ? HIGH : LOW); 
}

void Tank::_cmdFilterCleaning(bool on)
{
    if (on) _lastFilterCleaningTime = millis();
    digitalWrite(_pinFilterCleaning, on ? HIGH : LOW); 
}

void Tank::loop()
{
    _manualModeAlert.raise(_manualMode);
    _motorInBlockedAlert.raise(isMotorInBlocked());
    _motorOutBlockedAlert.raise(isMotorOutBlocked());
    _filterInBlockedAlert.raise(isFilterInBlocked());
    _overpressureAlert.raise(isOverpressured());
    _tankEmptyAlert.raise(isTankEmpty());

    // TODO: different signals based on the problem
    // e.g. constant light vs blinking
    _alertFatal(isMotorInBlocked() || isMotorOutBlocked() || isOverpressured() || _manualMode);
    _alertWarning(isFilterInBlocked() || isOn(_pinUrbanNetwork));

    _computeFlowRates();

    if (isMotorInBlocked()) {
        _cmdPumpIn(false);
    }
    if (isMotorOutBlocked()) {
        _enablePumpOut(false);
    }
    if (isOverpressured()) {
        _cmdPumpIn(false);
        _enablePumpOut(false);
    }

    if (isTankFull()) {
        _cmdPumpIn(false);
        _enablePumpOut(true);
        return;
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
    if (isTankEmpty()) {
        _enablePumpOut(false);
        _volumeCollectedSinceEmpty = 0;
    } else if (_volumeCollectedSinceEmpty > _volumeBeforeTankReady) {
        _enablePumpOut(true);
    } else {
        _enablePumpOut(false);
        _volumeCollectedSinceEmpty += _flowIn * (flowCheckPeriod / 60000.0);
    }

    // Command pump-in
    if (isWellFull()) {
        _cmdPumpIn(true);
    } else if (isWellEmpty()) {
        _cmdPumpIn(false);
    }
}

/*
 * Interrupts
 */
void Tank::flowInPulsed()
{
    _flowInPulses++;
}

void Tank::flowOutPulsed()
{
    _flowOutPulses++;
}

void Tank::attachFlowInterrupts()
{
    attachInterrupt(digitalPinToInterrupt(_pinFlowIn), flowInInterrupt, RISING);
    attachInterrupt(digitalPinToInterrupt(_pinFlowOut), flowOutInterrupt, RISING);
}

void Tank::_dettachFlowInterrupts()
{
    detachInterrupt(digitalPinToInterrupt(_pinFlowIn));
    detachInterrupt(digitalPinToInterrupt(_pinFlowOut));
}

void Tank::_computeFlowRates()
{
    if((millis() - _oldTimeFlow) < flowCheckPeriod) return;
    // We detach interrupts to avoid editing millis() and _flowInPulses during
    // the computations
    _dettachFlowInterrupts();

    // 1 pulse = 1L
    // L/min
    _flowIn = 60000.0 / (millis() - _oldTimeFlow) * _flowInPulses;
    _flowOut = 60000.0 / (millis() - _oldTimeFlow) * _flowOutPulses;

    _oldTimeFlow = millis();
    _flowInPulses = 0;
    _flowOutPulses = 0;

    attachFlowInterrupts();
}

/*
 * HTTP
 */
void Tank::_httpRouteGet(WebServer &server)
{
    server.httpSuccess("application/json");
    server << "{ ";
    server << "\"manual_mode\": " << _manualMode << ", ";
    server << "\"pump_in\": " << isOn(_pinPumpIn) << ", ";
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
    server << "\"volume_before_tank_ready\": " << _volumeBeforeTankReady << ", ";
    server << "\"volume_collected_since_empty \": " << _volumeCollectedSinceEmpty << ", ";
    server << "\"filter_cleaning_period\": " << filterCleaningPeriod << ", ";
    server << "\"filter_cleaning_duration\": " << filterCleaningDuration << ", ";
    server << "\"time_to_fill_up\": " << timeToFillUp << ", ";
    server << "\"flow_check_period\": " << flowCheckPeriod << ", ";
    server << "\"flow_in\": " << _flowIn << ", ";
    server << "\"flow_out\": " << _flowOut;
    server << " }";
}

void Tank::_httpRouteSet(WebServer &server)
{
    const byte keyLen = 20;
    const byte valueLen = 5;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "manual_mode") == 0) {
            _manualMode = (strcmp(value, "1") == 0);
        }
        if (strcmp(key, "min_flow_in") == 0) {
            minFlowIn = atoi(value);
        }
        if (strcmp(key, "time_to_fill_up") == 0) {
            timeToFillUp = atol(value);
        }
        if (strcmp(key, "flow_check_period") == 0) {
            flowCheckPeriod = atol(value);
        }
        if (strcmp(key, "volume_before_tank_ready") == 0) {
            _volumeBeforeTankReady = atoi(value);
        }
        if (strcmp(key, "pump_in") == 0) {
            _cmdPumpIn(strcmp(value, "1") == 0);
        }
        if (strcmp(key, "pump_out") == 0) {
            _enablePumpOut(strcmp(value, "1") == 0);
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
