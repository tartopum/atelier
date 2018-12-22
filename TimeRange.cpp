#include "TimeRange.h"

bool TimeRange::isNow()
{
    int h = hour();
    int m = minute();
    bool afterBegin = (h > beginHour) || (h == beginHour && m > beginMinute);
    bool beforeEnd = (h < endHour) || (h == endHour && m < endMinute);
    return afterBegin && beforeEnd;
}

byte _parseBound(char value[2])
{
    byte tens = value[0] - '0';
    byte units = value[1] - '0';
    if (tens < 0 || tens > 9 || units < 0 || units > 9) {
        return 255; // Error
    }
    return 10 * tens + units;
}

void TimeRange::httpRouteSet(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
    if (type != WebServer::POST) {
        server.httpUnauthorized();
        return;
    }
    byte bHour = 255;
    byte bMinute = 255;
    byte eHour = 255;
    byte eMinute = 255;

    const byte keyLen = 2;
    const byte valueLen = 2;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "bh") == 0) {
            bHour = _parseBound(value);
        }
        if (strcmp(key, "bm") == 0) {
            bMinute = _parseBound(value);
        }
        if (strcmp(key, "eh") == 0) {
            eHour = _parseBound(value);
        }
        if (strcmp(key, "eh") == 0) {
            eMinute = _parseBound(value);
        }
    }

    if (bHour > 23 || bMinute > 59 || eHour > 23 || eMinute > 59) {
        server.httpServerError();
        return;
    }
    server.httpSuccess();
    beginHour = bHour;
    beginMinute = bMinute;
    endHour = eHour;
    endMinute = eMinute;
}
