#include <Ethernet.h> // Make sure to use Controllino's Ethernet module (see compilation logs)
#include <WebServer.h> // https://github.com/sirleech/Webduino
#include <Controllino.h>
#include "Atelier.h"
#include "Tank.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
IPAddress ip(192, 168, 167, 100);
int port = 80;
WebServer webserver("", port);

// To be sent by the server
char apiIp[] = "192.168.167.101";
char apiAuthHeader[100] = "";
int apiPort = 5000;

void sendAlert(const char *name, const char *message)
{
    EthernetClient client;
    if (client.connect(apiIp, apiPort) != 1) {
        return;
    }

    const char *start = "{\"name\": \"";
    const char *messageKey = "\", \"message\": \"";
    const char *end = "\"}";
    unsigned int len = strlen(start) + strlen(name) + strlen(messageKey) + strlen(message) + strlen(end);
    client.println("POST /alert HTTP/1.1");
    client.print("Host: ");
    client.print(apiIp);
    client.print(":");
    client.println(apiPort);
    client.println("Content-Type: application/json");
    client.println("Connection: close");
    if (strlen(apiAuthHeader) > 0) {
        client.println(apiAuthHeader);
    }
    client.print("Content-Length: ");
    client.println(len);
    client.println();

    client.print(start);
    client.print(name);
    client.print(messageKey);
    client.print(message);
    client.println(end);

    delay(20);
    client.stop();
}

unsigned long inactivityDelay = 15000 * (long) 60;
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
    pinsFence,
    &sendAlert
);

Tank tank(
    CONTROLLINO_RELAY_02,
    CONTROLLINO_RELAY_03,
    CONTROLLINO_AI10,
    CONTROLLINO_RELAY_00,
    CONTROLLINO_IN0,
    CONTROLLINO_IN1,
    CONTROLLINO_AI1,
    CONTROLLINO_AI0,
    CONTROLLINO_AI2,
    CONTROLLINO_AI7,
    CONTROLLINO_AI8,
    CONTROLLINO_AI9,
    CONTROLLINO_RELAY_01,
    CONTROLLINO_DO2,
    CONTROLLINO_DO4,
    &sendAlert
);

void flowInInterrupt()
{
  tank.flowInPulsed();
}

void flowOutInterrupt()
{
  tank.flowOutPulsed();
}

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

void tankRoute(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    tank.httpRoute(server, type);
}

void tankStatsRoute(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    tank.httpRouteStats(server, type);
}

void configApiRoute(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type == WebServer::GET) {
        server.httpSuccess("application/json");
        server << "{ ";
        server << "\"ip\": \"" << apiIp[0] << "." << apiIp[1] << "." << apiIp[2] << "." << apiIp[3] << "\",";
        server << "\"port\": " << apiPort << ",";
        server << "\"auth_header\": \"" << apiAuthHeader << "\"";
        server << " }";
        return;
    }

    const byte keyLen = 20;
    const byte valueLen = 100;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "ip") == 0) {
            strcpy(apiIp, value);
        }
        if (strcmp(key, "port") == 0) {
            apiPort = atoi(value);
        }
        if (strcmp(key, "auth_header") == 0) {
            strcpy(apiAuthHeader, value);
        }
    }
    server.httpSuccess();
}

void handleHTTP()
{
    char buff[64];
    int len = 64;
    webserver.processConnection(buff, &len);
}

void setup()
{
    Serial.begin(9600); // TODO

    sei(); // Enable interrupts

    tank.flowInInterrupt = &flowInInterrupt;
    tank.flowOutInterrupt = &flowOutInterrupt;
    tank.attachFlowInterrupts();

    Ethernet.begin(mac, ip);
    webserver.addCommand("config_api", &configApiRoute);
    webserver.addCommand("alarm", &alarmRoute);
    webserver.addCommand("lights", &lightsRoute);
    webserver.addCommand("fence", &fenceRoute);
    webserver.addCommand("workshop", &atelierRoute);
    webserver.addCommand("tank", &tankRoute);
    webserver.addCommand("tank_stats", &tankStatsRoute);
}

void loop()
{
    handleHTTP();
    atelier.loop();
    tank.loop();
}
