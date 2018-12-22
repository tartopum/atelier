#include "Light.h"
#include "TimeRange.h"

Light::Light(int pinInside, int pinOutside) : sleep(21, 30, 6, 30)
{
    _pinInside = pinInside;
    _pinOutside = pinOutside;

    pinMode(_pinInside, INPUT);
    pinMode(_pinOutside, INPUT);
}

bool Light::isInsideOn()
{
    return digitalRead(_pinInside) == HIGH;
}

bool Light::isOutsideOn()
{
    return digitalRead(_pinOutside) == HIGH;
}

void Light::cmdInside(bool on)
{
    digitalWrite(_pinInside, on ? HIGH : LOW);
}

void Light::cmdOutside(bool on)
{
    digitalWrite(_pinOutside, on ? HIGH : LOW);
}

void Light::command()
{
    if (sleep.isNow()) {
        cmdInside(false); 
        cmdOutside(false); 
    }
}

void Light::httpRouteState(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type != WebServer::GET) {
        server.httpUnauthorized();
        return;
    }
    server.httpSuccess();
    server.println("HTTP/1.1 200 OK");
    server.println("Content-Type: application/json");
    server.println();
    server.println("{");

    server.print("\"inside\": ");
    server.print(isInsideOn());
    server.println(",");

    server.print("\"outside\": ");
    server.println(isOutsideOn());

    server.println("}");
}

void httpRouteCmd(WebServer &server, WebServer::ConnectionType type)
{
    if (type != WebServer::POST) {
        server.httpUnauthorized();
        return;
    }
    server.httpSuccess();
}

void Light::httpRouteInsideOn(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    httpRouteCmd(server, type);
    cmdInside(true);
}

void Light::httpRouteInsideOff(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    httpRouteCmd(server, type);
    cmdInside(false);
}

void Light::httpRouteOutsideOn(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    httpRouteCmd(server, type);
    cmdOutside(true);
}

void Light::httpRouteOutsideOff(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    httpRouteCmd(server, type);
    cmdOutside(false);
}
