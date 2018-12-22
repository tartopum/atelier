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

bool Alarm::inListeningPeriod()
{
    bool beforeBegin = hour() <= listeningPeriodBeginHour && minute() <= listeningPeriodBeginMinute;
    bool afterEnd = hour() >= listeningPeriodEndHour && listeningPeriodEndMinute;
    return beforeBegin || afterEnd;
}

bool Alarm::listening()
{
    // _listening may have been set manually through the web
    // interface or the switch.
    _updateListeningFromSwitch();

    // If we enter or quit the listening period, we update it.
    // Otherwise, we don't change its value.
    if (inListeningPeriod() && !_wasInListeningPeriod) {
        _listening = true;
        _wasInListeningPeriod = true;
    }
    else if (!inListeningPeriod() && _wasInListeningPeriod) {
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

byte _parseListeningPeriodBound(char value[2])
{
    byte tens = value[0] - '0';
    byte units = value[1] - '0';
    if (tens < 0 || tens > 9 || units < 0 || units > 9) {
        return 255; // Error
    }
    return 10 * tens + units;
}

void Alarm::httpRouteSetListeningPeriod(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type != WebServer::POST) {
        server.httpUnauthorized();
        return;
    }
    byte bHour = 255;
    byte bMinute = 255;
    byte eHour = 255;
    byte eMinute = 255;

    const byte keyLen = 2;
    const byte valueLen = 2;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "bh") == 0) {
            bHour = _parseListeningPeriodBound(value);
        }
        if (strcmp(key, "bm") == 0) {
            bMinute = _parseListeningPeriodBound(value);
        }
        if (strcmp(key, "eh") == 0) {
            eHour = _parseListeningPeriodBound(value);
        }
        if (strcmp(key, "eh") == 0) {
            eMinute = _parseListeningPeriodBound(value);
        }
    }

    if (bHour == 255 || bMinute == 255 || eHour == 255 || eMinute == 255) {
        server.httpServerError();
        return;
    }
    server.httpSuccess();
    listeningPeriodBeginHour = bHour;
    listeningPeriodBeginMinute = bMinute;
    listeningPeriodEndHour = eHour;
    listeningPeriodEndMinute = eMinute;
}
