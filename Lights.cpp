#include "Lights.h"
#include "TimeRange.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Lights::Lights(int lightPins[3], int pinBtn1, int pinBtn2) : sleep(21, 30, 6, 30), buttons(pinBtn1, pinBtn2)
{
    _pins = lightPins;
    for (int i = 0; i < _N_PINS; i++) {
        pinMode(_pins[i], OUTPUT);
    }
}

void Lights::cmdLight(int n, bool on)
{
    if (n < 0 || n >= _N_PINS) return;
    digitalWrite(_pins[n], on ? HIGH : LOW);
}

void Lights::_commandFromBtn()
{
    two_btn_state_t state = buttons.state(); 
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
        bool cur = digitalRead(_pins[pinIndex]) == HIGH;
        cmdLight(pinIndex, !cur);
    }
}

void Lights::control()
{
    if (sleep.isNow()) {
        for (int i = 0; i < _N_PINS; i++) {
            cmdLight(i, false); 
        }
    }
    _commandFromBtn();
}

void Lights::httpRouteState(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type != WebServer::GET) {
        server.httpUnauthorized();
        return;
    }
    server.httpSuccess("application/json");
    server << "{ ";

    for (int i = 0; i < _N_PINS; i++) {
        server << "\"" << i << "\": " << (digitalRead(_pins[i]) == HIGH);
        if (i < (_N_PINS - 1)) server << ", ";
    }
    server << " }";
}

void Lights::httpRouteCmd(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type != WebServer::POST) {
        server.httpUnauthorized();
        return;
    }
    
    const byte keyLen = 2;
    const byte valueLen = 1;
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
