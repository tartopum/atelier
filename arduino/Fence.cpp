#include "Fence.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Fence::Fence(int pinControl, AlertLight *light)
{
    _light = light;
    _pinControl = pinControl;
    pinMode(_pinControl, OUTPUT);
    on();
}

void Fence::on()
{
    digitalWrite(_pinControl, HIGH);
    _light->unsetLevel(MID_ALERT);
}

void Fence::off()
{
    digitalWrite(_pinControl, LOW);
    _light->setLevel(MID_ALERT);
}

bool Fence::isOn()
{
    return digitalRead(_pinControl) == HIGH;
}

void Fence::loop() {
}

void Fence::_httpRouteGet(WebServer &server)
{
    server.httpSuccess("application/json");
    server << "{ ";
    server << "\"state\": " << isOn();
    server << " }";
}

void Fence::_httpRouteSet(WebServer &server)
{
    const byte keyLen = 50;
    const byte valueLen = 50;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "state") == 0) {
            (strcmp(value, "1") == 0) ? on() : off();
            server.httpSuccess();
            return;
        }
    }
    server.httpFail();
}

void Fence::httpRoute(WebServer &server, WebServer::ConnectionType type)
{
    if (type == WebServer::POST) {
        _httpRouteSet(server);
        return;
    }
    _httpRouteGet(server);
}
