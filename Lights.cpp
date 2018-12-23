#include "Lights.h"
#include "TimeRange.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Lights::Lights(int pinInside1, int pinInside2, int pinOutside) : sleep(21, 30, 6, 30)
{
    _pinInside1 = pinInside1;
    _pinInside2 = pinInside2;
    _pinOutside = pinOutside;

    pinMode(_pinInside1, OUTPUT);
    pinMode(_pinInside2, OUTPUT);
    pinMode(_pinOutside, OUTPUT);
}

int Lights::_lightToPin(light_t light)
{
    if (light == INSIDE1) return _pinInside1;
    if (light == INSIDE2) return _pinInside2;
    return _pinOutside;
}

bool Lights::isOn(light_t light)
{
    return digitalRead(_lightToPin(light)) == HIGH;
}

void Lights::cmdLight(light_t light, bool on)
{
    digitalWrite(_lightToPin(light), on ? HIGH : LOW);
}

void Lights::cmdInside(bool on)
{
    cmdLight(INSIDE1, on);
    cmdLight(INSIDE2, on);
}

void Lights::cmdOutside(bool on)
{
    cmdLight(OUTSIDE, on);
}

void Lights::command()
{
    if (sleep.isNow()) {
        cmdInside(false); 
        cmdOutside(false); 
    }
}

void Lights::httpRouteState(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type != WebServer::GET) {
        server.httpUnauthorized();
        return;
    }
    server.httpSuccess("application/json");
    server << "{ ";
    server << "\"inside1\": " << isOn(INSIDE1) << ", ";
    server << "\"inside2\": " << isOn(INSIDE2) << ", ";
    server << "\"outside\": " << isOn(OUTSIDE);
    server << " }";
}

void Lights::httpRouteCmd(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type != WebServer::POST) {
        server.httpUnauthorized();
        return;
    }
    
    const byte keyLen = 3;
    const byte valueLen = 1;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "in1") == 0) {
            cmdLight(INSIDE1, (strcmp(value, "1") == 0)); 
        }
        if (strcmp(key, "in2") == 0) {
            cmdLight(INSIDE2, (strcmp(value, "1") == 0)); 
        }
        if (strcmp(key, "out") == 0) {
            cmdLight(OUTSIDE, (strcmp(value, "1") == 0)); 
        }
    }
    server.httpSuccess();
}
