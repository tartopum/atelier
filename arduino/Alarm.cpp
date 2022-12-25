#include "Alarm.h"

template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

Alarm::Alarm(
    int pinDetector,
    int pinBuzzer,
    int pinBuzzerStart,
    int pinListening,
    int pinNotListening,
    int pinListenSwitch,
    AlertLight *alertLight,
    bool (*sendAlert)(const char *, const char *, byte)
) :
    _alert(
        "alarm",
        "Une intrusion a été détectée.",
        sendAlert,
        alertLight,
        HIGH_ALERT,
        60
    )
{
    _pinDetector = pinDetector;
    _pinBuzzer = pinBuzzer;
    _pinBuzzerStart = pinBuzzerStart;
    _pinListening = pinListening;
    _pinNotListening = pinNotListening;
    _pinListenSwitch = pinListenSwitch;

    pinMode(_pinDetector, INPUT);
    pinMode(_pinListenSwitch, INPUT);

    pinMode(_pinBuzzer, OUTPUT);
    pinMode(_pinBuzzerStart, OUTPUT);
    pinMode(_pinListening, OUTPUT);
    pinMode(_pinNotListening, OUTPUT);

    digitalWrite(_pinBuzzer, LOW);
    digitalWrite(_pinBuzzerStart, LOW);

    _curSwitchState = digitalRead(_pinListenSwitch);
}

bool Alarm::breachDetected()
{
    return _breachDetected;
}

void Alarm::enable(bool enabled)
{
    if (!enabled) {
        _state = DISABLED;
    } else if (_state == DISABLED) { // When we are listening, we don't go back to the STARTING state
      _state = STARTING;
      _enabledTime = millis();
    }
}

bool Alarm::listening()
{
    return _state == LISTENING;
}

bool Alarm::movementDetected()
{
    return digitalRead(_pinDetector) == HIGH;
}

void Alarm::_handleSwitch()
{
    uint8_t switchState = digitalRead(_pinListenSwitch);
    if (switchState == _curSwitchState) return;
    // The key was turned
    // We don't want to make the warning buzzer ring because the user already
    // knows if the alarm is starting and would trigger the buzzer when leaving
    // the building.
    _warnStarting = false;
    _curSwitchState = switchState;
    enable(_state == DISABLED);
}

void Alarm::_updateState()
{
    if (_state != STARTING) return;
    if (millis() - _enabledTime < delayBeforeListening) return;
    _state = LISTENING;
}

void Alarm::loop()
{
    _handleSwitch();
    _updateState();

    _alert.raise(_breachDetected);

    if (_state == DISABLED) {
        digitalWrite(_pinBuzzer, LOW);
        digitalWrite(_pinBuzzerStart, LOW);
        digitalWrite(_pinListening, LOW);
        digitalWrite(_pinNotListening, HIGH);
        _breachTime = 0;
        _breachDetected = false;
        return;
    }
    if (_state == STARTING) {
        digitalWrite(_pinBuzzer, LOW);
        // Show orange light
        digitalWrite(_pinListening, HIGH);
        digitalWrite(_pinNotListening, HIGH);
        if (movementDetected() && _warnStarting) {
            digitalWrite(_pinBuzzerStart, HIGH);
        }
        return;
    }
    // Show red light
    digitalWrite(_pinListening, HIGH);
    digitalWrite(_pinNotListening, LOW);

    // At power startup, the movement detector is turned on. We wait a bit to let it
    // turn off. Otherwise, the alarm would automatically be raised at startup.
    if (millis() < delayBeforeListening) {
        return;
    }

    if (!movementDetected()) {
        _breachTime = 0;
        return;
    }

    // Breach detected!
    // We save the time it was detected at
    if (_breachTime == 0) {
        _breachTime = millis();
        return;
    }

    // We wait a bit before raising the alert
    if (millis() - _breachTime < delayBeforeAlert) {
        return;
    }

    // We raise the alert
    _breachDetected = true;
    digitalWrite(_pinBuzzer, HIGH);
    digitalWrite(_pinBuzzerStart, HIGH);
}

void Alarm::_httpRouteGet(WebServer &server)
{
    server.httpSuccess("application/json");
    server << "{ ";
    server << "\"listen\": " << (_state != DISABLED) << ", ";
    server << "\"starting\": " << (_state == STARTING) << ", ";
    server << "\"breach\": " << breachDetected() << ", ";
    server << "\"delay_before_alert\": " << delayBeforeAlert << ", ";
    server << "\"delay_before_listening\": " << delayBeforeListening << ", ";
    server << "\"movement\": " << movementDetected();
    server << " }";
}

void Alarm::_httpRouteSet(WebServer &server)
{
    const byte keyLen = 50;
    const byte valueLen = 50;
    char key[keyLen];
    char value[valueLen];
    while (server.readPOSTparam(key, keyLen, value, valueLen)) {
        if (strcmp(key, "listen") == 0) {
            _warnStarting = true;
            enable(strcmp(value, "1") == 0);
        }
        if (strcmp(key, "delay_before_alert") == 0) {
            delayBeforeAlert = atol(value);
        }
        if (strcmp(key, "delay_before_listening") == 0) {
            delayBeforeListening = atol(value);
        }
    }
    server.httpSuccess();
}

void Alarm::httpRoute(WebServer &server, WebServer::ConnectionType type)
{
    if (type == WebServer::POST) {
        _httpRouteSet(server);
        return;
    }
    _httpRouteGet(server);
}
