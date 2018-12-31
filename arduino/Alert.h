#ifndef Alert_h
#define Alert_h

#include <Arduino.h>

class Alert
{
    public:
        Alert(
            const char *name,
            const char *msg,
            void (*send)(const char *, const char *),
            unsigned int reminderDelay = 24 * 60 // min
        );
        void raise(bool);

    private:
        char _name[40];
        char _msg[100];
        unsigned long _reminderDelay;
        bool _sent = false;
        unsigned long _lastTimeSent = 0;
        void (*_send)(const char *, const char *);
};

#endif
