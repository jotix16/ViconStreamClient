# vicon_transformer
Read frames provided by a Vicon system and transform them into a usable form for your project.

This package was initiated in [intelligent-soft-robots/vicon_transformer](https://github.com/intelligent-soft-robots/vicon_transformer/tree/addWandIndependentOrigin). Here, we remove any project related dependencies and add some documentation.

This package allows for a wand independent representation of the measurement. It realizes that by saving the relative transformation between the Vicon-origin(different every time) and the origin-structure. We then use this transformation to transform any measurements to the reference frame given by the origin-structure.

For this reason, the package puts a requirement on the setup. 
The origin-structure should be present in the view-field of the Vicon system when starting the package.


### Installation and setting up the Vicon system

Ensure that you have installed, activated, and calibrated the Vicon Tracker software according to the tutorial videos shown [here](https://youtube.com/playlist?list=PLxtdgDam3USXt3RxvklaNCHxxvBpAUXtA). 

For this package to work, the [Viconstreamsdk](https://www.vicon.com/software/datastream-sdk/) should be additionally installed on the computer.

For the network communication, we use the [zeromq](https://zeromq.org/languages/python/) package, which can be installed via
```
pip install pyzmq
```


### Starting the streaming
``` python
# 1. We first start the 'Vicon Tracker' software and use the magic-wand to 
#    calibrate cameras and set the origin.

# 2. Start the streaming service on the host side by copying the script `StartStream.py`
#    and starting it via
python StartStream.py
#    make sure that the IP parameter is set according to the IP of the host machine.


# 3. Create `ViconJson` from `vicon_transformer.py` and start it on the client computer.
#    An example is shown in `TestSettingOrigin.py`
python TestSettingOrigin.py
```
