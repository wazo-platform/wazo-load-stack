# voipctl

voipctl is a tool that implements the logic used by load framework to perform
voip calls include signalling and media.

3 scenario have been implemented so far.

## RegistrationOnly
A simple use case involving SIP signalling only.
When wlapi get the load to run, it setup the proper environment
variables containing the SCENARIO, the LOGIN, the PASSWORD and the STACK that
are required to perform a SIP registration. Then wlapi run
voipctl that will trigger a registration.
You can bypass wlapi and run directly voicptl:


```
source /opt/venv/bin/activate
export SCENARIO=registration_only;
export LINE=1001;
export STACK=172.16.42.29;
export PASSWORD=tetetet;
export SCENARIO=simple_call;
export CALL_DURATION=300;
export GROUP_CALL=20000
voipctl
```
