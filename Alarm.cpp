#include "Alarm.h"

Alarm::Alarm(int pinDetector, int pinBuzzer, int pinLightAlert, int pinListening, int pinListenSwitch)
{
    _pinDetector = pinDetector;
    _pinBuzzer = pinBuzzer;
    _pinLightAlert = pinLightAlert;
    _pinListening = pinListening;
    _pinListenSwitch = pinListenSwitch;

    pinMode(_pinDetector, INPUT);
    pinMode(_pinListenSwitch, INPUT);

    pinMode(_pinBuzzer, OUTPUT);
    pinMode(_pinLightAlert, OUTPUT);
    pinMode(_pinListening, OUTPUT);
    digitalWrite(_pinBuzzer, LOW);
    digitalWrite(_pinLightAlert, LOW);
    digitalWrite(_pinListening, LOW);

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
        _breachTime = 0;
        return false;
    }
    digitalWrite(_pinListening, HIGH);

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

void Alarm::httpRouteState(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type != WebServer::GET) {
        server.httpUnauthorized();
        return;
    }
    server.httpSuccess();
    server.println("HTTP/1.1 200 OK");
    server.println("Content-Type: application/json");
    server.println();
    server.println("{");

    server.print("\"listening\": ");
    server.print(listening());
    server.println(",");

    server.print("\"breach\": ");
    server.println(breachDetected());

    server.println("}");
}

void Alarm::httpRouteListeningOn(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type != WebServer::POST) {
        server.httpUnauthorized();
        return;
    }
    server.httpSuccess();
    _listening = true;
}

void Alarm::httpRouteListeningOff(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type != WebServer::POST) {
        server.httpUnauthorized();
        return;
    }
    server.httpSuccess();
    _listening = false;
}
