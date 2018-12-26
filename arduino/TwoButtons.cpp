#include "TwoButtons.h"

TwoButtons::TwoButtons(int pin1, int pin2)
{
    _pin1 = pin1;
    _pin2 = pin2;

    pinMode(_pin1, INPUT_PULLUP);
    pinMode(_pin2, INPUT_PULLUP);

    _oldState1 = digitalRead(_pin1);
    _oldState2 = digitalRead(_pin2);
}

two_btn_state_t TwoButtons::state()
{
    uint16_t state1 = digitalRead(_pin1);
    uint16_t state2 = digitalRead(_pin2);

    if (state1 != _oldState1 || state2 != _oldState2) {
        _oldState1 = state1;
        _oldState2 = state2;
        _lastChangeTime = millis();
        changed = true;
        return UNKNOWN;
    }
    if (!changed) {
        return UNKNOWN;
    }
    if (millis() - _lastChangeTime < pressDelay) {
        return UNKNOWN;
    }
    changed = false;

    if (state1 == LOW && state2 == LOW) return BOTH;
    if (state1 == LOW && state2 == HIGH ) return BTN1;
    if (state1 == HIGH && state2 == LOW) return BTN2;
    return NONE;
}
