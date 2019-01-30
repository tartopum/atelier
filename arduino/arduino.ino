#include <Ethernet.h> // Make sure to use Controllino's Ethernet module (see compilation logs)
#include <WebServer.h> // https://github.com/sirleech/Webduino
#include <Controllino.h>
#include "Atelier.h"
#include "Tank.h"
#include "Fence.h"
#include "Lights.h"
#include "Alarm.h"
#include "AlertLight.h"

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

void sendAlert(const char *name, const char *message, byte level)
{
    EthernetClient client;
    if (client.connect(apiIp, apiPort) != 1) {
        return;
    }

    const char *start = "{\"name\": \"";
    const char *messageKey = "\", \"message\": \"";
    const char *levelKey = "\", \"level\": ";
    const char *end = "}";
    unsigned int len = (
        strlen(start) + strlen(name) + strlen(messageKey) + strlen(message) +
        strlen(levelKey) + 1 + strlen(end)
    );

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
    client.print(levelKey);
    client.print(level);
    client.println(end);

    delay(20);
    client.stop();
}

AlertLight redLight(CONTROLLINO_DO4);
AlertLight greenLight(CONTROLLINO_DO3);
AlertLight blueLight(CONTROLLINO_DO2);

Fence fence(CONTROLLINO_RELAY_04, &greenLight);

Alarm alarm(
    CONTROLLINO_AI6,
    CONTROLLINO_DO6,
    CONTROLLINO_DO5,
    CONTROLLINO_DO1,
    CONTROLLINO_DO0,
    CONTROLLINO_AI5,
    &redLight,
    &sendAlert
);

int pinsLight[3] = {
    CONTROLLINO_RELAY_09,
    CONTROLLINO_RELAY_08,
    CONTROLLINO_RELAY_07,
};
Lights lights(
    pinsLight,
    CONTROLLINO_AI3,
    CONTROLLINO_AI4
);

Atelier atelier(
    CONTROLLINO_RELAY_05,
    15000 * (long)60,
    &alarm,
    &lights
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
    &blueLight,
    &redLight,
    &sendAlert
);

/*
 * Interrupts
 */
void flowInInterrupt()
{
  tank.flowInPulsed();
}

void flowOutInterrupt()
{
  tank.flowOutPulsed();
}

/*
 * HTTP
 */
void askForConfig()
{
    EthernetClient client;
    if (client.connect(apiIp, apiPort) != 1) {
        return;
    }

    client.println("GET /send_config HTTP/1.1");
    client.print("Host: ");
    client.print(apiIp);
    client.print(":");
    client.println(apiPort);
    client.println("Connection: close");
    client.println("Content-Length: 0");
    delay(20);
    client.stop();
}

void alarmRoute(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    alarm.httpRoute(server, type);
}

void lightsRoute(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    lights.httpRoute(server, type);
}

void fenceRoute(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    fence.httpRoute(server, type);
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
        server << "\"ip\": \"" << apiIp << "\",";
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

    askForConfig();
}

void loop()
{
    handleHTTP();
    fence.loop();
    atelier.loop();
    tank.loop();
    redLight.loop();
    greenLight.loop();
    blueLight.loop();
}
