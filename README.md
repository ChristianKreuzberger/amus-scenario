Description
===========

This is the scenario template for the adaptive multimedia streaming ndnSIM (with BRITE and DASH). Please have a look
at [amus-ndnSIM github repository](https://github.com/ChristianKreuzberger/amus-ndnSIM) before continuing here.

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

To configure in debug mode with all logging enabled

    ./waf configure --debug --with-brite=/home/$USER/ndnSIM/BRITE

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


Running
=======

Very important: As we extended ndnSIM with DASH and BRITE, we need to define LD_LIBRARY_PATH so the programs find
the shared objects libdash and libbrite. To do this, write the following either in your .bashrc or everytime after 
you start a new terminal window:

    export LD_LIBRARY_PATH=/home/$USER/ndnSIM/libdash/libdash/build/bin/:/home/$USER/ndnSIM/BRITE/:$LD_LIBRARY_PATH

Now you can run scenarios either directly

    ./build/<scenario_name>

or using waf

    ./waf --run <scenario_name>

If NS-3 is installed in a non-standard location, on some platforms (e.g., Linux) you need to specify ``LD_LIBRARY_PATH`` variable:

    LD_LIBRARY_PATH=/usr/local/lib ./build/<scenario_name>

or

    LD_LIBRARY_PATH=/usr/local/lib ./waf --run <scenario_name>

To run scenario using debugger, use the following command:

    gdb --args ./build/<scenario_name>

We have several example scenarios available for testing:

    ./waf --run hello # test if the compiling/linking did work
    ./waf --run ndn-mysimple # test if ndn stuff works (this does not print much output though)
    ./waf --run ndn-mysimple --vis # test if visualizer works (this should show you packets being processed)

