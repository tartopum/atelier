#include <Ethernet.h> // Make sure to use Controllino's Ethernet module (see compilation logs)
#include <WebServer.h> // https://github.com/sirleech/Webduino
#include <Controllino.h>
#include <Atelier.h>

byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
IPAddress ip(192, 168, 168, 100);
WebServer webserver("", 80);

int pinStopPower = CONTROLLINO_RELAY_05;
int pinsAlarm[5] = {
    CONTROLLINO_AI6,
    CONTROLLINO_DO5,
    CONTROLLINO_DO4,
    CONTROLLINO_DO1,
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

Atelier atelier(
    pinStopPower,
    pinsAlarm,
    pinsLight,
    pinsLightBtn
);


void alarmRoute(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    atelier.alarm.httpRoute(server, type);
}

void lightsRoute(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    atelier.lights.httpRoute(server, type);
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
}

void loop()
{
    handleHTTP();
    atelier.control();
}
