#include "Atelier.h"

#define LIGHT_OUT 0
#define LIGHT_IN1 1
#define LIGHT_IN2 2

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Atelier::Atelier(
    int pinPowerSupply,
    unsigned long inactivityDelay_,
    Alarm *alarm,
    Lights *lights
)
{
    _alarm = alarm;
    _lights = lights;
    _pinPowerSupply = pinPowerSupply;
    inactivityDelay = inactivityDelay_;
    pinMode(_pinPowerSupply, OUTPUT);
    cmdPowerSupply(true);
}

void Atelier::cmdPowerSupply(bool on)
{
    digitalWrite(_pinPowerSupply, on ? HIGH : LOW);
}

void Atelier::loop()
{
    _alarm->loop();
    _lights->loop();

    // The light inside was just turned on
    // We need this to be able to turn lights on through the web interface
    // after a long inactivity delay. Otherwise, no movement is detected
    // and the light is turned off immediatly.
    if ((_lights->isOn(LIGHT_IN1) || _lights->isOn(LIGHT_IN2)) && !_isInsideLightOn) {
        _lastActivityTime = millis();
        _isInsideLightOn = true;
    } else if (!_lights->isOn(LIGHT_IN1) && !_lights->isOn(LIGHT_IN2)) {
        _isInsideLightOn = false;
    }

    if (_alarm->movementDetected()) {
        _lastActivityTime = millis();
    }

    if (millis() - _lastActivityTime > inactivityDelay) {
        _lights->cmdLight(LIGHT_IN1, false);
        _lights->cmdLight(LIGHT_IN2, false);
    }

    if (_alarm->breachDetected()) {
        _lights->cmdLight(LIGHT_OUT, true);
        _breach = true;
    } else {
        if (_breach) _lights->cmdLight(LIGHT_OUT, false); // The alarm was just stopped
        _breach = false;
    }
}

void Atelier::_httpRouteGet(WebServer &server)
{
    server.httpSuccess("application/json");
    server << "{ ";
    server << "\"power_supply\": " << (digitalRead(_pinPowerSupply) == HIGH) << ",";
    server << "\"inactivity_delay\": " << inactivityDelay;
    server << " }";
}

void Atelier::_httpRouteSet(WebServer &server)
{
    const byte keyLen = 50;
    const byte valueLen = 50;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "inactivity_delay") == 0) {
            unsigned long delay = atol(value);
            if (delay > 0) {
                inactivityDelay = delay;
            } else {
                server.httpServerError();
                return;
            }
        }
        if (strcmp(key, "power_supply") == 0) {
            (strcmp(value, "1") == 0) ? cmdPowerSupply(true) : cmdPowerSupply(false);
        }
    }
    server.httpSuccess();
}

void Atelier::httpRoute(WebServer &server, WebServer::ConnectionType type)
{
    if (type == WebServer::POST) {
        _httpRouteSet(server);
        return;
    }
    _httpRouteGet(server);
}
