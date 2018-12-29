#include "Lights.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Lights::Lights(int lightPins[3], int pinBtn1, int pinBtn2) : _buttons(pinBtn1, pinBtn2)
{
    _pins = lightPins;
    for (int i = 0; i < _N_PINS; i++) {
        pinMode(_pins[i], OUTPUT);
    }
    cmdAll(false);
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

void Lights::loop()
{
    two_btn_state_t state = _buttons.state(); 
    if (state == UNKNOWN || state == NONE) return;

    int pinIndex = 0;
    if (state == BOTH) {
        pinIndex = 0;
    }
    if (state == BTN1) {
        pinIndex = 1;
    }
    if (state == BTN2) {
        pinIndex = 2;
    }
    bool curState = (digitalRead(_pins[pinIndex]) == HIGH);
    cmdLight(pinIndex, !curState);
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
    const byte keyLen = 15;
    const byte valueLen = 5;
    char key[keyLen];
    char value[valueLen];
    char strIndex[3];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        for (int i = 0; i < _N_PINS; i++) {
            sprintf(strIndex, "%i", i);
            if (strcmp(key, strIndex) == 0) {
                cmdLight(i, (strcmp(value, "1") == 0)); 
            }
            if (strcmp(key, "press_delay") == 0) {
                _buttons.pressDelay = atol(value);
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
