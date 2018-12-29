#include "Alarm.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Alarm::Alarm(int pinDetector, int pinBuzzer, int pinLightAlert, int pinListening, int pinNotListening, int pinListenSwitch)
{
    _pinDetector = pinDetector;
    _pinBuzzer = pinBuzzer;
    _pinLightAlert = pinLightAlert;
    _pinListening = pinListening;
    _pinNotListening = pinNotListening;
    _pinListenSwitch = pinListenSwitch;

    pinMode(_pinDetector, INPUT);
    pinMode(_pinListenSwitch, INPUT);

    pinMode(_pinBuzzer, OUTPUT);
    pinMode(_pinLightAlert, OUTPUT);
    pinMode(_pinListening, OUTPUT);
    pinMode(_pinNotListening, OUTPUT);

    _oldListenSwitchState = digitalRead(_pinListenSwitch);
    _listening = false;
}

bool Alarm::breachDetected()
{
    return _breachDetected;
}

bool Alarm::listening()
{
    uint8_t curState = digitalRead(_pinListenSwitch);
    if (curState != _oldListenSwitchState) { // The key was turned
        _oldListenSwitchState = curState;
        _listening = !_listening;
    }
    return _listening;
}

bool Alarm::movementDetected()
{
    return digitalRead(_pinDetector);
}

void Alarm::loop()
{
    if (!listening()) {
        digitalWrite(_pinBuzzer, LOW);
        digitalWrite(_pinLightAlert, LOW);
        digitalWrite(_pinListening, LOW);
        digitalWrite(_pinNotListening, HIGH);
        _breachTime = 0;
        _breachDetected = false;
        return;
    }
    digitalWrite(_pinListening, HIGH);
    digitalWrite(_pinNotListening, LOW);

    if (!movementDetected()) {
        _breachTime = 0;
        return;
    }

    // Breach detected!
    // We save the time it was detected at
    if (_breachTime == 0) {
        _breachTime = millis();
        return;
    }

    // We wait a bit before raising the alert
    if (millis() - _breachTime < millisBeforeAlert) {
        return;
    }

    _breachDetected = true;
    // We raise the alert
    digitalWrite(_pinBuzzer, HIGH);
    // Make light blink
    if (millis() - _lightStateChangeTime > 500) {
        bool isLightOn = (digitalRead(_pinLightAlert) == HIGH);
        digitalWrite(_pinLightAlert, isLightOn ? LOW : HIGH);
        _lightStateChangeTime = millis();
    }
}

void Alarm::_httpRouteGet(WebServer &server)
{
    server.httpSuccess("application/json");
    server << "{ ";
    server << "\"listen\": " << listening() << ", ";
    server << "\"ms_before_alert\": " << millisBeforeAlert << ", ";
    server << "\"movement\": " << movementDetected();
    server << " }";
}

void Alarm::_httpRouteSet(WebServer &server)
{
    const byte keyLen = 20;
    const byte valueLen = 5;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "listen") == 0) {
            _listening = (strcmp(value, "1") == 0);
        }
        if (strcmp(key, "ms_before_alert") == 0) {
            millisBeforeAlert = atol(value);
        }
    }
    server.httpSuccess();
}

void Alarm::httpRoute(WebServer &server, WebServer::ConnectionType type)
{
    if (type == WebServer::POST) {
        _httpRouteSet(server);
        return;
    }
    _httpRouteGet(server);
}
