#include "Alert.h"

Alert::Alert(
    const char *name,
    const char *msg,
    void (*send)(const char *, const char *),
    AlertLight *light,
    alert_level_t level,
    unsigned int reminderDelay
)
{
    strcpy(_name, name);
    strcpy(_msg, msg);
    _send = send;
    _reminderDelay = (unsigned long)reminderDelay * 60 * 1000;
    _level = level;
    _light = light;
}

void Alert::raise(bool problemDetected)
{
    if (!problemDetected) {
        if (_sent) {
            _light->unsetLevel(_level);
        }
        _sent = false;
        return;
    }

    _light->setLevel(_level);
    if (_sent && (millis() - _lastTimeSent) < _reminderDelay) return;

    _sent = true;
    _lastTimeSent = millis();
    _send(_name, _msg);
}
