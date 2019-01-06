#include "AlertLight.h"

AlertLight::AlertLight(byte pin)
{
    _pin = pin;
    pinMode(_pin, OUTPUT);
}

void AlertLight::setLevel(alert_level_t level)
{
    if (level > _level) _level = level;
}

void AlertLight::unsetLevel(alert_level_t level)
{
    if (_level == level) _level = NO_ALERT;
}

void AlertLight::_blink()
{
    unsigned int period = (_level == MID_ALERT) ? midLevelBlinkPeriod : highLevelBlinkPeriod;

    if (millis() - _lastBlinkTime < period) return;
    digitalWrite(_pin, (digitalRead(_pin) == HIGH) ? LOW : HIGH);
    _lastBlinkTime = millis();
}

void AlertLight::loop()
{
    switch (_level) {
        case NO_ALERT:
            digitalWrite(_pin, LOW);
            break;
        case LOW_ALERT:
            digitalWrite(_pin, HIGH);
            break;
        default:
            _blink();
    }
}
