#include "Lights.h"
#include "TimeRange.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Lights::Lights(int pinsInside[2], int pinsOutside[1], int pinsBtn[2]) : sleep(21, 30, 6, 30)
{
    _pinsInside = pinsInside;
    _pinsOutside = pinsOutside;
    _pinsBtn = pinsBtn;

    pinMode(_pinsInside[0], OUTPUT);
    pinMode(_pinsInside[1], OUTPUT);
    pinMode(_pinsOutside[0], OUTPUT);

    pinMode(_pinsBtn[0], INPUT);
    pinMode(_pinsBtn[1], INPUT);
}

void Lights::cmdInside(bool on, int n = -1)
{
    uint16_t state = on ? HIGH : LOW;
    if (n == -1) {
        digitalWrite(_pinsInside[0], state);
        digitalWrite(_pinsInside[1], state);
        return;
    }
    digitalWrite(_pinsInside[n], state);
}

void Lights::cmdOutside(bool on, int n = -1)
{
    uint16_t state = on ? HIGH : LOW;
    digitalWrite(_pinsOutside[0], state);
}

void Lights::_commandFromBtn()
{
    int btn1State = digitalRead(_pinsBtn[0]);
    int btn2State = digitalRead(_pinsBtn[1]);
    unsigned long now = millis();
}

void Lights::command()
{
    if (sleep.isNow()) {
        cmdInside(false); 
        cmdOutside(false); 
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

    for (int i = 0; i < 2; i++) {
        server << "\"in" << i << "\": " << (digitalRead(_pinsInside[i]) == HIGH) << ", ";
    }
    server << "\"out0\": " << (digitalRead(_pinsOutside[0]) == HIGH);
    server << " }";
}

void Lights::httpRouteCmdInside(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type != WebServer::POST) {
        server.httpUnauthorized();
        return;
    }
    
    const byte keyLen = 1;
    const byte valueLen = 1;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "0") == 0) {
            cmdInside((strcmp(value, "1") == 0), 0); 
        }
        if (strcmp(key, "1") == 0) {
            cmdInside((strcmp(value, "1") == 0), 1); 
        }
    }
    server.httpSuccess();
}

void Lights::httpRouteCmdOutside(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type != WebServer::POST) {
        server.httpUnauthorized();
        return;
    }
    
    const byte keyLen = 1;
    const byte valueLen = 1;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "0") == 0) {
            cmdOutside((strcmp(value, "1") == 0), 0); 
        }
    }
    server.httpSuccess();
}
