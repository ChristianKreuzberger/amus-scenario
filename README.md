Description
===========

This is the scenario template for the adaptive multimedia streaming ndnSIM (with BRITE and DASH). Please have a look
at [amus-ndnSIM github repository](https://github.com/ChristianKreuzberger/amus-ndnSIM) before continuing here.

In addition, this template is based on [ndnSIM-scenario-template](https://github.com/cawka/ndnSIM-scenario-template),
with some additions. If you run into problems, this is the place to go to for further documentation.

---------------------------------------------

Prerequisites
=============

You need to compile [amus-ndnSIM](https://github.com/ChristianKreuzberger/amus-ndnSIM) and install all of its 
dependencies, including the custom version of NS-3. Please follow the instructions on 
[amus-ndnSIM](https://github.com/ChristianKreuzberger/amus-ndnSIM) and then come back here!


Switch to the ~/ndnSIM directory, then perform the following operations:
    
    git clone https://github.com/ChristianKreuzberger/amus-scenario.git amus-scenario
    cd amus-scenario

Compiling
=========

To configure in optimized mode without logging **(default)**:

    ./waf configure --with-brite=/home/$USER/ndnSIM/BRITE

To configure in optimized mode with scenario logging enabled (logging in NS-3 and ndnSIM modules will still be disabled,
but you can see output from NS_LOG* calls from your scenarios and extensions):

    ./waf configure --logging --with-brite=/home/$USER/ndnSIM/BRITE

To configure in debug mode with all logging enabled by adding the ``--debug`` statement:

    ./waf configure --debug --with-brite=/home/$USER/ndnSIM/BRITE
    
If you have libdash installed to a non-default location, you will need to specify it by using the ``--with-dash`` option:

    ./waf configure --with-dash=/path/to/libdash

If you have installed NS-3 in a non-standard location, you may need to set up ``PKG_CONFIG_PATH`` variable.

You can now proceed and compile the example code provided in the scenario subfolder, by using the ./waf command:

    ./waf
    
This should successfully compile all examples, printing the following to console:

    Waf: Entering directory `/home/$USER/ndnSIM/amus-scenario/build'
    [1/6] Compiling scenarios/hello.cpp
    [2/6] Compiling scenarios/ndn-file-simple.cpp
    [3/6] Compiling scenarios/ndn-mysimple.cpp
    [4/6] Linking build/hello
    [5/6] Linking build/ndn-file-simple
    [6/6] Linking build/ndn-mysimple
    Waf: Leaving directory `/home/$USER/ndnSIM/amus-scenario/build'
    'build' finished successfully (15.609s)


---------------------------------------------

Running
=======



Now you can run scenarios either directly

    ./build/<scenario_name>

or using waf

    ./waf --run <scenario_name>

If NS-3/amus-ndnSIM is installed in a non-standard location, on some platforms (e.g., Linux) you need to specify ``LD_LIBRARY_PATH`` variable:

    LD_LIBRARY_PATH=/usr/local/lib ./build/<scenario_name>

or

    LD_LIBRARY_PATH=/usr/local/lib ./waf --run <scenario_name>


We have several example scenarios available for testing:

    ./waf --run hello # test if the compiling/linking did work
    ./waf --run ndn-mysimple # test if ndn stuff works (this does not print much output though)
    ./waf --run ndn-mysimple --vis # test if visualizer works (this should show you packets being processed)



---------------------------------------------

Debugging
=========
To run a scenario using debugger, use the following command:

    gdb --args ./build/<scenario_name>

or use the command template:

    ./waf --run <scenario_name> --command-template="gdb %s"

In the same way, you can also run valgrind:

    ./waf --run <scenario_name> --command-template="valgrind --leak-check=full --show-reachable=yes %s"

Note: If you need to debug amus-ndnSIM, we recommend compiling amus-ndnSIM without the -d optimized flag.

---------------------------------------------


Troubleshooting with Libraries
==============================

In case you are having issues with libdash or BRITE, make sure that the LD_LIBRARY_PATH is set properly
To do this, adapt the following command and write it either to your .bashrc or everytime after 
you start a new terminal window:

    export LD_LIBRARY_PATH=/home/$USER/ndnSIM/libdash/libdash/build/bin/:/home/$USER/ndnSIM/BRITE/:$LD_LIBRARY_PATH


---------------------------------------------


Acknowledgements
================
This work was partially funded by the Austrian Science Fund (FWF) under the CHIST-ERA project [CONCERT](http://www.concert-project.org/) 
(A Context-Adaptive Content Ecosystem Under Uncertainty), project number I1402.



