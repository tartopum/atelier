#include "Alarm.h"
#include "TimeRange.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Alarm::Alarm(int pinDetector, int pinBuzzer, int pinLightAlert, int pinListening, int pinNotListening, int pinListenSwitch) : listeningPeriod(21, 30, 6, 30)
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
    digitalWrite(_pinBuzzer, LOW);
    digitalWrite(_pinLightAlert, LOW);
    digitalWrite(_pinListening, LOW);
    digitalWrite(_pinNotListening, LOW);

    _oldListenSwitchState = digitalRead(_pinListenSwitch);
}

void Alarm::_updateListeningFromSwitch() 
{
    uint8_t curState = digitalRead(_pinListenSwitch);
    if (curState == _oldListenSwitchState) return;
    // The key was turned
    _oldListenSwitchState = curState;
    _listening = !_listening;
}

bool Alarm::listening()
{
    // _listening may have been set manually through the web
    // interface or the switch.
    _updateListeningFromSwitch();

    // If we enter or quit the listening period, we update it.
    // Otherwise, we don't change its value.
    if (listeningPeriod.isNow() && !_wasInListeningPeriod) {
        _listening = true;
        _wasInListeningPeriod = true;
    }
    else if (!listeningPeriod.isNow() && _wasInListeningPeriod) {
        _listening = false;
        _wasInListeningPeriod = false;
    }
    return _listening;
}

bool Alarm::breachDetected()
{
    return digitalRead(_pinDetector);
}

bool Alarm::control()
{
    if (!listening()) {
        digitalWrite(_pinBuzzer, LOW);
        digitalWrite(_pinLightAlert, LOW);
        digitalWrite(_pinListening, LOW);
        digitalWrite(_pinNotListening, HIGH);
        _breachTime = 0;
        return false;
    }
    digitalWrite(_pinListening, HIGH);
    digitalWrite(_pinNotListening, LOW);

    if (!breachDetected()) {
        _breachTime = 0;
        return false;
    }

    // Breach detected!
    // We save the time it was detected at
    if (_breachTime == 0) {
        _breachTime = millis();
        return false;
    }

    // We wait a bit before raising the alert
    if (millis() - _breachTime < millisBeforeAlert) {
        return false;
    }

    // We raise the alert
    digitalWrite(_pinBuzzer, HIGH);
    digitalWrite(_pinLightAlert, HIGH);
    return true;
}

void Alarm::_httpRouteGet(WebServer &server)
{
    server.httpSuccess("application/json");
    server << "{ ";
    server << "\"listen\": " << listening() << ", ";
    server << "\"breach\": " << breachDetected();
    server << " }";
}

void Alarm::_httpRouteSet(WebServer &server)
{
    const byte keyLen = 6;
    const byte valueLen = 1;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "listen") != 0) continue;
        _listening = (strcmp(value, "1") == 0);
        server.httpSuccess();
        return;
    }
    server.httpFail();
}

void Alarm::httpRoute(WebServer &server, WebServer::ConnectionType type)
{
    if (type == WebServer::POST) {
        _httpRouteSet(server);
        return;
    }
    _httpRouteGet(server);
}
