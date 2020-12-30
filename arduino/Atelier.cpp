#include "Atelier.h"

#define LIGHT_OUT 0
#define LIGHT_IN1 1
#define LIGHT_IN2 2

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Atelier::Atelier(
    int pinPowerSupply,
    unsigned long inactivityDelay_,
    Alarm *alarm,
    Lights *lights,
    bool (*sendAlert)(const char *, const char *, byte)
) :
    _powerManualModeAlert(
        "workshop",
        "L'alimentation est en manuel depuis longtemps.",
        sendAlert,
        NULL,
        MID_ALERT,
        NO_ALERT_REMINDER
    )
{
    _alarm = alarm;
    _lights = lights;
    _pinPowerSupply = pinPowerSupply;
    inactivityDelay = inactivityDelay_;
    pinMode(_pinPowerSupply, OUTPUT);
    cmdPowerSupply(true);
}

void Atelier::cmdPowerSupply(bool on)
{
    digitalWrite(_pinPowerSupply, on ? HIGH : LOW);
}

void Atelier::_setManualMode(bool manualMode)
{
    _powerManualMode = manualMode;
    if (_powerManualMode) _powerManualModeTime = millis();
}

void Atelier::loop()
{
    _alarm->loop();
    _lights->loop();

    // Power
    if (!_powerManualMode && _alarm->listening()) {
        cmdPowerSupply(false);
    }
    if (_isAlarmListening && !_alarm->listening()) { // The alarm was just turned off
        cmdPowerSupply(true);
    }
    // Send reminder when power supply has been in manual mode for long
    if (_powerManualMode && millis() - _powerManualModeTime > powerManualModeReminderDelay) {
        _powerManualModeAlert.raise(true);
        _powerManualModeTime = millis();
    } else {
        _powerManualModeAlert.raise(false);
    }

    // The light inside was just turned on
    // We need this to be able to turn lights on through the web interface
    // after a long inactivity delay. Otherwise, no movement is detected
    // and the light is turned off immediatly.
    if ((_lights->isOn(LIGHT_IN1) || _lights->isOn(LIGHT_IN2)) && !_isInsideLightOn) {
        _lastActivityTime = millis();
        _isInsideLightOn = true;
    } else if (!_lights->isOn(LIGHT_IN1) && !_lights->isOn(LIGHT_IN2)) {
        _isInsideLightOn = false;
    }

    if (_alarm->movementDetected()) {
        _lastActivityTime = millis();
    }

    if (millis() - _lastActivityTime > inactivityDelay) {
        _lights->cmdLight(LIGHT_IN1, false);
        _lights->cmdLight(LIGHT_IN2, false);
    }

    if (!_isAlarmListening && _alarm->listening()) { // The alarm was just turned on
        _lights->cmdAll(false);
    }

    if (_alarm->breachDetected()) {
        _lights->cmdLight(LIGHT_OUT, true);
        _breach = true;
    } else {
        if (_breach) _lights->cmdLight(LIGHT_OUT, false); // The alarm was just stopped
        _breach = false;
    }

    _isAlarmListening = _alarm->listening();
}

void Atelier::_httpRouteGet(WebServer &server)
{
    server.httpSuccess("application/json");
    server << "{ ";
    server << "\"power_supply\": " << (digitalRead(_pinPowerSupply) == HIGH) << ",";
    server << "\"power_reminder_delay\": " << powerManualModeReminderDelay << ",";
    server << "\"power_manual_mode\": " << _powerManualMode << ",";
    server << "\"inactivity_delay\": " << inactivityDelay;
    server << " }";
}

void Atelier::_httpRouteSet(WebServer &server)
{
    const byte keyLen = 50;
    const byte valueLen = 50;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "inactivity_delay") == 0) {
            unsigned long delay = atol(value);
            if (delay > 0) {
                inactivityDelay = delay;
            } else {
                server.httpServerError();
                return;
            }
        }
        if (strcmp(key, "power_supply") == 0) {
            (strcmp(value, "1") == 0) ? cmdPowerSupply(true) : cmdPowerSupply(false);
        }
        if (strcmp(key, "power_manual_mode") == 0) {
            _setManualMode(strcmp(value, "1") == 0);
        }
        if (strcmp(key, "power_reminder_delay") == 0) {
            powerManualModeReminderDelay = atol(value);
        }
    }
    server.httpSuccess();
}

void Atelier::httpRoute(WebServer &server, WebServer::ConnectionType type)
{
    if (type == WebServer::POST) {
        _httpRouteSet(server);
        return;
    }
    _httpRouteGet(server);
}
