#include "Atelier.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Atelier::Atelier(int pinStopPower, unsigned long inactivityDelay_, int pinsAlarm[5], int pinsLigth[3], int pinsLightBtn[2], int pinsFence[2], TimeRange *lunch_, TimeRange *night_) :
    alarm(pinsAlarm[0], pinsAlarm[1], pinsAlarm[2], pinsAlarm[3], pinsAlarm[4], pinsAlarm[5], lunch_, night_),
    lights(pinsLigth, pinsLightBtn[0], pinsLightBtn[1], night_),
    fence(pinsFence[0], pinsFence[1])
{
    lunch = lunch_;
    night = night_;
    _pinStopPower = pinStopPower;
    inactivityDelay = inactivityDelay_;
    pinMode(_pinStopPower, OUTPUT);
}

void Atelier::cmdPower(bool on)
{
    digitalWrite(_pinStopPower, on ? HIGH : LOW);
}

void Atelier::control()
{
    if (millis() - _lastActivityTime > inactivityDelay) {
        lights.cmdAll(false);
    }

    fence.control();
    alarm.control();
    lights.control();

    if (alarm.movementDetected()) {
        _lastActivityTime = millis();
    }

    if (alarm.breachDetected()) {
        lights.cmdLight(0, true);
    }

    cmdPower(!night->isNow());
}

void Atelier::_httpRouteGet(WebServer &server)
{
    server.httpSuccess("application/json");
    server << "{ ";
    server << "\"inactivity_delay\": " << inactivityDelay;
    server << " }";
}

void Atelier::_httpRouteSet(WebServer &server)
{
    const byte keyLen = 20;
    const byte valueLen = 5;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "inactivity_delay") == 0) {
            unsigned long delay = String(value).toInt();
            if (delay > 0) {
                inactivityDelay = delay;
            } else {
                server.httpServerError();
                return;
            }
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
