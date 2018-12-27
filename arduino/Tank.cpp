#include "Tank.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Tank::Tank(int pinPumpIn, int pinPumpOut, int pinUrbanNetwork, int pinFlowIn, int pinFlowOut, int pinWaterLimitLow, int pinWaterLimitHigh, int pinFilterInBlocked, int pinMotorInBlocked, int pinLightWater, int pinLightMotor)
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
    _pinLightWater = pinLightWater;
    _pinLightMotor = pinLightMotor;

    pinMode(_pinFlowIn, INPUT);
    pinMode(_pinFlowOut, INPUT);
    pinMode(_pinWaterLimitLow, INPUT);
    pinMode(_pinWaterLimitHigh, INPUT);
    pinMode(_pinFilterInBlocked, INPUT);
    pinMode(_pinMotorInBlocked, INPUT);

    pinMode(_pinPumpIn, OUTPUT);
    pinMode(_pinPumpOut, OUTPUT);
    pinMode(_pinUrbanNetwork, OUTPUT);
    pinMode(_pinLightWater, OUTPUT);
    pinMode(_pinLightMotor, OUTPUT);

    _cmdPumpIn(false);
    _cmdPumpOut(true);
    _cmdUrbanNetwork(false);
    _alertWater(false);
    _alertMotor(false);
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
  return isOff(_pinWaterLimitLow);
}

bool Tank::isWellFull()
{
  return (millis() - _oldTimePumpInOff) > timeToFillUp;
}

bool Tank::isWellEmpty()
{
  return _flowIn < minFlowIn;
}

/*
 * Output
 */
void Tank::_alertWater(bool on)
{
    digitalWrite(_pinLightWater, on ? HIGH : LOW); 
}

void Tank::_alertMotor(bool on)
{
    digitalWrite(_pinLightWater, on ? HIGH : LOW); 
}

void Tank::_cmdPumpIn(bool on)
{
    if (isTankFull() and on) return;
    if (!on && isOn(_pinPumpIn)) _oldTimePumpInOff = millis();
    digitalWrite(_pinPumpIn, on ? HIGH : LOW); 
}

void Tank::_cmdPumpOut(bool on)
{
    digitalWrite(_pinPumpIn, on ? HIGH : LOW); 
}

void Tank::_cmdUrbanNetwork(bool on)
{
    digitalWrite(_pinUrbanNetwork, on ? HIGH : LOW); 
}

void Tank::control()
{
    if (isMotorInBlocked()) {
        _alertMotor(true);
        _cmdPumpIn(false);
        _cmdPumpOut(false);
        _cmdUrbanNetwork(true);
        return;
    }
    // TODO: alertWater

    _alertMotor(false);
    _alertWater(false);

    if (isTankFull()) {
        _cmdPumpIn(false);
        return;
    }

    _computeFlowRates();
    _cmdUrbanNetwork(isTankEmpty());
    if (isOff(_pinPumpIn) && isWellFull()) {
        _cmdPumpIn(true);
    }
    else if (isOn(_pinPumpIn) && isWellEmpty()) {
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
    if((millis() - _oldTimeFlow) < 1000) return;
    _dettachFlowInterrupts();

    _flowIn = 1000.0 / (millis() - _oldTimeFlow) * _flowInPulses;
    _flowOut = 1000.0 / (millis() - _oldTimeFlow) * _flowOutPulses;

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
    //server << "\"ms_before_alert\": " << millisBeforeAlert << ", ";
    server << " }";
}

void Tank::_httpRouteSet(WebServer &server)
{
    const byte keyLen = 20;
    const byte valueLen = 5;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "TODO") == 0) {
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
