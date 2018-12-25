#include "Atelier.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Atelier::Atelier(int pinStopPower, unsigned long inactivityDelay, int pinsAlarm[5], int pinsLigth[3], int pinsLightBtn[2], int pinsFence[2], TimeRange *lunch_, TimeRange *night_) :
    alarm(pinsAlarm[0], pinsAlarm[1], pinsAlarm[2], pinsAlarm[3], pinsAlarm[4], pinsAlarm[5], lunch_, night_),
    lights(pinsLigth, pinsLightBtn[0], pinsLightBtn[1], night_),
    fence(pinsFence[0], pinsFence[1])
{
    lunch = lunch_;
    night = night_;
    _pinStopPower = pinStopPower;
    _inactivityDelay = inactivityDelay;
    pinMode(_pinStopPower, OUTPUT);
}

void Atelier::cmdPower(bool on)
{
    digitalWrite(_pinStopPower, on ? HIGH : LOW);
}

void Atelier::control()
{
    if (millis() - _lastInactivityTime > _inactivityDelay) {
        lights.cmdAll(false);
        _lastInactivityTime = millis();
    }

    alarm.control();
    lights.control();
    cmdPower(!night->isNow());
}

void Atelier::_httpRouteGet(WebServer &server)
{
    server.httpSuccess("application/json");
    server << "{ ";
    server << "\"inactivity_delay\": " << _inactivityDelay;
    server << " }";
}

void Atelier::_httpRouteSet(WebServer &server)
{
    unsigned long delayMinutes = 0;

    const byte keyLen = 20;
    const byte valueLen = 3;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "inactivity_delay") == 0) {
            String delay = String(value);
            delayMinutes = delay.toInt();
        }
    }
    if (delayMinutes == 0) {
        server.httpServerError();
        return;
    }

    _inactivityDelay = 1000 * 60 * delayMinutes;
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
