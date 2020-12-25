#ifndef Alert_h
#define Alert_h

#include <Arduino.h>
#include "AlertLight.h"

class Alert
{
    public:
        Alert(
            const char *name,
            const char *msg,
            bool (*send)(const char *, const char *, byte),
            AlertLight *light,
            alert_level_t level,
            unsigned int reminderDelay = 60 // min
        );
        void raise(bool);

    private:
        char _name[40];
        char _msg[100];
        AlertLight *_light;
        alert_level_t _level;
        unsigned long _reminderDelay;
        bool _sent = false;
        bool _raised = false;
        unsigned long _lastTimeSent = 0;
        bool (*_send)(const char *, const char *, byte);
};

#endif
