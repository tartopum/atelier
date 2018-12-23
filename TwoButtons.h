#ifndef TwoButtons_h
#define TwoButtons_h

#include "Arduino.h"

typedef enum {
    BTN1,
    BTN2,
    BOTH,
    NONE,
    UNKNOWN,
} two_btn_state_t;

class TwoButtons
{
    public:
        TwoButtons(int, int);
        two_btn_state_t state();
        unsigned long pressDelay = 2000;

    private:
        int _pin1;
        int _pin2;
        uint16_t _oldState1;
        uint16_t _oldState2;
        unsigned long _lastChangeTime = 0;
};

#endif
