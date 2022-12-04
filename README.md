# Minescaner
Python Minecraft Scanning Tool

## HELP

Can someone help me with rsa encryption.
(the public key (PEM-ENCODED) to the X.509 encoded.)

i dont know encryption.

## Data Sructure

I want to use sqlite3 so i thought of a datastructure...


   ** PING TABLE **
          name;   type;             exampel; info
          time;    INT; 1670072676534401627; unix ns time.time_ns()
            ip; STRING;             8.8.8.8; The pinged ip
  protocolvers;    INT;                 760; [Protocol version](https://wiki.vg/Protocol_version_numbers)
    maxplayers;    INT;                  20; max players
   description; STRING;         rpg anarchy; VERY striped down string(anti sql and short is good) (:
   isdescolord;    INT;                   1; is colored (if it contains color: or \u00a7) 1 if it is 0 if not
       version; STRING;        Paper 1.19.2; Server version string (also striped down)
      ismodded;    INT;                   0; if server gives forgedata
    
   ** PING PLAYERS TABLE **
          name;   type;                          exampel; info
        pingid;    INT;                               42; the ping id (sqlite automaticly adds id to every thing)
          name; STRING;                          Example; the name given in ping
          UUID; STRING; c823834bac564d079203217e5070c76e; the uuid given in ping

   (in the sense of the ingame serverlist...)

   ** PING PLAYER TABLE **

   ** PLAYER TABLE **
