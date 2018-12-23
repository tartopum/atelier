#include "Fence.h"

Fence::Fence(int pinControl, int pinDisplay)
{
  pinMode(pinControl, OUTPUT);
  pinMode(pinDisplay, OUTPUT);
  _pinControl = pinControl;
  _pinDisplay = pinDisplay;
}

void Fence::on()
{
  digitalWrite(_pinControl, HIGH);
  digitalWrite(_pinDisplay, HIGH);
}

void Fence::off()
{
  digitalWrite(_pinControl, LOW);
  digitalWrite(_pinDisplay, LOW);
}

bool Fence::isOn()
{
  return digitalRead(_pinControl) == HIGH;
}

void Fence::_httpRouteGet(WebServer &server)
{
    server.httpSuccess();
    server.print(isOn() ? "1" : "0");
}

void Fence::_httpRouteSet(WebServer &server)
{
    const byte keyLen = 2;
    const byte valueLen = 1;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "on") != 0) continue;
        if (strcmp(value, "1") == 0) on();
        else off();
        server.httpSuccess();
        return;
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
