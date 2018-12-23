#include "Atelier.h"

Atelier::Atelier(int pinStopPower)
{
    _pinStopPower = pinStopPower;

    pinMode(_pinStopPower, OUTPUT);
}
