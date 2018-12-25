#include "Alarm.h"
#include "TimeRange.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Alarm::Alarm(int pinDetector, int pinBuzzer, int pinLightAlert, int pinListening, int pinNotListening, int pinListenSwitch, TimeRange *lunch, TimeRange *night)
{
    _pinDetector = pinDetector;
    _pinBuzzer = pinBuzzer;
    _pinLightAlert = pinLightAlert;
    _pinListening = pinListening;
    _pinNotListening = pinNotListening;
    _pinListenSwitch = pinListenSwitch;

    _lunch = lunch;
    _night = night;

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

bool Alarm::breachDetected()
{
    return listening() && movementDetected();
}

bool Alarm::listening()
{
    // _listening may have been set manually through the web
    // interface or the switch.
    _updateListeningFromSwitch();

    // If we enter or quit the listening period, we update it.
    // Otherwise, we don't change its value.
    if (_lunch->entering() || _night->entering()) {
        _listening = true;
    }
    else if (_lunch->leaving() || _night->leaving()) {
        _listening = false;
    }
    return _listening;
}

bool Alarm::movementDetected()
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

    if (!movementDetected()) {
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
    // Make light blink
    if (millis() - _lightStateChangeTime > 500) {
        bool isLightOn = (digitalRead(_pinLightAlert) == HIGH);
        digitalWrite(_pinLightAlert, isLightOn ? LOW : HIGH);
        _lightStateChangeTime = millis();
    }
    return true;
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
            millisBeforeAlert = String(value).toInt();
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
