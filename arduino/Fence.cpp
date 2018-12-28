#include "Fence.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Fence::Fence(int pinControl, int pinDisplay)
{
  _pinControl = pinControl;
  _pinDisplay = pinDisplay;
  pinMode(_pinControl, OUTPUT);
  pinMode(_pinDisplay, OUTPUT);
  on();
}

void Fence::on()
{
  digitalWrite(_pinControl, HIGH);
  digitalWrite(_pinDisplay, LOW);
}

void Fence::off()
{
  digitalWrite(_pinControl, LOW);
  digitalWrite(_pinDisplay, HIGH);
}

bool Fence::isOn()
{
  return digitalRead(_pinControl) == HIGH;
}

void Fence::loop() {
    if (isOn()) return;

    // Make light blink
    if (millis() - _lightStateChangeTime > 500) {
        bool isLightOn = (digitalRead(_pinDisplay) == HIGH);
        digitalWrite(_pinDisplay, isLightOn ? LOW : HIGH);
        _lightStateChangeTime = millis();
    }
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
    const byte keyLen = 10;
    const byte valueLen = 5;
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
