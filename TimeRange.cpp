#include "TimeRange.h"

TimeRange::TimeRange(byte bh, byte bm, byte eh, byte em)
{
    set(bh, bm, eh, em);
}

bool TimeRange::set(byte bh, byte bm, byte eh, byte em)
{
    if (bh < 0 || bh > 23) return false; 
    if (eh < 0 || eh > 23) return false; 
    if (bm < 0 || bm > 59) return false; 
    if (em < 0 || em > 59) return false; 
    beginHour = bh;
    beginMinute = bm;
    endHour = eh;
    endMinute = em;
    return true;
}

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

void TimeRange::httpRoute(WebServer &server, WebServer::ConnectionType type)
{
    if (type != WebServer::POST) {
        server.httpUnauthorized();
        return;
    }
    byte bh = 255;
    byte bm = 255;
    byte eh = 255;
    byte em = 255;

    const byte keyLen = 2;
    const byte valueLen = 2;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "bh") == 0) {
            bh = _parseBound(value);
        }
        if (strcmp(key, "bm") == 0) {
            bm = _parseBound(value);
        }
        if (strcmp(key, "eh") == 0) {
            eh = _parseBound(value);
        }
        if (strcmp(key, "em") == 0) {
            em = _parseBound(value);
        }
    }

    if (!set(bh, bm, eh, em)) {
        server.httpServerError();
        return;
    }
    server.httpSuccess();
}
