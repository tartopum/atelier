#include "Lights.h"
#include "TimeRange.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Lights::Lights(int lightPins[3], int pinBtn1, int pinBtn2, TimeRange *sleep) : _buttons(pinBtn1, pinBtn2)
{
    _pins = lightPins;
    _sleep = sleep;
    for (int i = 0; i < _N_PINS; i++) {
        pinMode(_pins[i], OUTPUT);
    }
}

void Lights::cmdAll(bool on)
{
    for (int i = 0; i < _N_PINS; i++) {
        cmdLight(i, on);
    }
}

void Lights::cmdLight(int n, bool on)
{
    if (n < 0 || n >= _N_PINS) return;
    digitalWrite(_pins[n], on ? HIGH : LOW);
}

void Lights::_commandFromBtn()
{
    two_btn_state_t state = _buttons.state(); 
    int pinIndex = -1;
    if (state == BOTH) {
        pinIndex = 0;
    }
    if (state == BTN1) {
        pinIndex = 1;
    }
    if (state == BTN2) {
        pinIndex = 2;
    }
    if (pinIndex != -1) {
        bool curState = (digitalRead(_pins[pinIndex]) == HIGH);
        cmdLight(pinIndex, !curState);
    }
}

void Lights::control()
{
    if (_sleep->isNow()) {
        for (int i = 0; i < _N_PINS; i++) {
            cmdLight(i, false); 
        }
    }
    _commandFromBtn();
}

void Lights::_httpRouteGet(WebServer &server)
{
    server.httpSuccess("application/json");
    server << "{ ";

    for (int i = 0; i < _N_PINS; i++) {
        server << "\"" << i << "\": " << (digitalRead(_pins[i]) == HIGH);
        if (i < (_N_PINS - 1)) server << ", ";
    }
    server << " }";
}

void Lights::_httpRouteSet(WebServer &server)
{
    const byte keyLen = 10;
    const byte valueLen = 5;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        for (int i = 0; i < _N_PINS; i++) {
            if (strcmp(key, String(i).c_str()) == 0) {
                cmdLight(i, (strcmp(value, "1") == 0)); 
            }
        }
    }
    server.httpSuccess();
}

void Lights::httpRoute(WebServer &server, WebServer::ConnectionType type)
{
    if (type == WebServer::POST) {
        _httpRouteSet(server);
        return;
    }
    _httpRouteGet(server);
}
