#include "Atelier.h"

Atelier::Atelier(int pinStopPower, int pinsAlarm[5], int pinsLigths[3], int pinsLightBtns[2]) :
    alarm(pinsAlarm[0], pinsAlarm[1], pinsAlarm[2], pinsAlarm[3], pinsAlarm[4]),
    lights(pinsLigths, pinsLightBtns[0], pinsLightBtns[1])
{
    _pinStopPower = pinStopPower;
    pinMode(_pinStopPower, OUTPUT);
}

void Atelier::cmdPower(bool on)
{
    digitalWrite(_pinStopPower, on ? HIGH : LOW);
}

void Atelier::control()
{
    alarm.control();
    lights.control();
    cmdPower(!lights.sleep.isNow());
}
