#include "Alert.h"

Alert::Alert(
    const char *name,
    const char *msg,
    void (*send)(const char *, const char *),
    unsigned int reminderDelay
)
{
    strcpy(_name, name);
    strcpy(_msg, msg);
    _send = send;
    _reminderDelay = (unsigned long)reminderDelay * 60 * 1000;
}

void Alert::raise(bool problemDetected)
{
    if (!problemDetected) {
        _sent = false;
        return;
    }
    if (_sent && (millis() - _lastTimeSent) < _reminderDelay) return;

    _sent = true;
    _lastTimeSent = millis();
    _send(_name, _msg);
}
