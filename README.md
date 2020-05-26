# Webplotter ✍🔌
A plotter that works over the network. Follows the keep it fucking stupidly simple principle. (KIFSS) 

Webplotter is **very simple, easy to use and efficient. It doesn't consume hundreds of MB of RAM just idling**.
You need one docker call to run it. 
The whole code is less than a hundred lines. 

Unlike Grafana and the whole stack it needs, you can **understand and manage its complexity.** 
Webplotter is meant **not to be a black box**.

I built Webplotter because I couldn't make sure other solutions were not risky to run on my servers.

<sub><sup> Precisely, cAdvisor which is advised for monitoring Docker Swarms with Grafana needs the docker 
--privileged flag, to dangerously mount folders on the host and to be available from the 
outside. It consumed more CPU than the app it monitored when I tested it. </sup></sub> 

 
![a superb screenshot of webplotter](https://raw.githubusercontent.com/Kaktana/webplotter/master/webplotter.png)    


### Wtf we already have Grafana 
Yes, but the tutorial on how to add a custom datasource has seven fucking tabs and is 3x longer than webplotter's source code.

Compare it to how easy it is to send points to Webplotter:
```python
import request
requests.post("supersecretaddress.com" + "/addPoints", json={[
  {"key": "grandma's beer stock", "value": 1337,  "timestamp": 1010361600},
  {"key": "CPU1-temp", "value": 69}, # No timestamp here, the server will put the current timestamp
  {"key": "RAM_2", "value": 42e9}, # All keys with the same prefix 
  {"key": "RAM_1", "value": 3.14}  # before the underscore will be on the same chart
]})
```    


### How It Works
- When you send a point, it appends your point in a file in the ```data/``` folder
- When you ask for the homepage, it calls gnuplot through a subprocess and returns the .png image.    


### How to deploy it
#### Docker
```
docker run -d --name=webplotter -p 8080:8000 --mount source=webplotter-data,destination=/app/data kaktana/webplotter:latest
```
#### Without Docker:
```
Reproduce the steps in the Dockerfile but on your system.
```   

### How to Monitor CPU
cf. https://github.com/Kaktana/webplotter-cpu-monitor 

Haven't put a readme yet but the 28 lines of code are self-explanatory. Run it with docker with the needed env variables.   


### Security
- The code runs as an unpriviledged user. That's why the default port binded to is 8080
- There's no authentication mechanism. 
To secure you data (if needed!) put a reverse-proxy with Basic Auth in front of Webplotter. 
Traefik works well for that.  


### Contribute 
If you add a feature for yourself, share it back with us! 
I don't have time to implement them but here are a few cool things I want to build:
- A program like ```cat``` in a compiled language that filters the data by timestamp (checking bounds and sampling rate)
before sending it to gnuplot. 
It's currently done in Python and is the main bottleneck.
- Showing only the current value of a metric (like in a car speed meter).
- An alterting thing integrated could be cool, as long as it stays simple.

I'll be happy to review and include your pull requests :-)  


### Why do I need to push data to webplotter, rather than have Webplotter pull it?
Because having the plotter pull the data requires this data to be accessible from the outside.
It is sometimes impractical and unsafe.
 
There's an alternative architecture: ```plotter =PULL=> DB <=PUSH= app``` but I like simple things.  





### Can I host it on a RPI/exotic SBC?
I haven't been able to configure docker hub to build arm images automatically. 

I personally host webplotter on my Odroid SBC. 
To do the same, clone the repository on your SBC and build the docker image yourself.    

### Sponsors
This program was initially made for [Kaktana](https://kaktana.com), 
a tool that lets traders create their own trading bots without knowing how to code.
