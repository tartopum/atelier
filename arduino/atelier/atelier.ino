#include <Ethernet.h> // Make sure to use Controllino's Ethernet module (see compilation logs)
#include <WebServer.h> // https://github.com/sirleech/Webduino
#include <Controllino.h>
#include <Atelier.h>

byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
IPAddress ip(192, 168, 167, 100);
WebServer webserver("", 80);

unsigned long inactivityDelay = 15000 * 60;
int pinPower = CONTROLLINO_RELAY_05;
int pinsAlarm[6] = {
    CONTROLLINO_AI6,
    CONTROLLINO_DO5,
    CONTROLLINO_DO4,
    CONTROLLINO_DO1,
    CONTROLLINO_DO0,
    CONTROLLINO_AI5,
};
int pinsLight[3] = {
    CONTROLLINO_RELAY_09,
    CONTROLLINO_RELAY_08,
    CONTROLLINO_RELAY_07,
};
int pinsLightBtn[2] = {
    CONTROLLINO_AI3,
    CONTROLLINO_AI4,
};
int pinsFence[2] = {
    CONTROLLINO_RELAY_04,
    CONTROLLINO_DO3,
};

Atelier atelier(
    pinPower,
    inactivityDelay,
    pinsAlarm,
    pinsLight,
    pinsLightBtn,
    pinsFence
);


void alarmRoute(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    atelier.alarm.httpRoute(server, type);
}

void lightsRoute(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    atelier.lights.httpRoute(server, type);
}

void fenceRoute(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    atelier.fence.httpRoute(server, type);
}

void atelierRoute(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    atelier.httpRoute(server, type);
}

void handleHTTP()
{
    char buff[64];
    int len = 64;
    webserver.processConnection(buff, &len);
}

void setup()
{
    Ethernet.begin(mac, ip);
    webserver.addCommand("alarm", &alarmRoute);
    webserver.addCommand("lights", &lightsRoute);
    webserver.addCommand("fence", &fenceRoute);
    webserver.addCommand("workshop", &atelierRoute);
}

void loop()
{
    handleHTTP();
    atelier.control();
}
