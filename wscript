# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-

VERSION='0.1'
APPNAME='template'

from waflib import Build, Logs, Options, TaskGen
import subprocess
import os

def options(opt):
    opt.load(['compiler_c', 'compiler_cxx'])
    opt.load(['default-compiler-flags',
              'boost', 'ns3'],
             tooldir=['.waf-tools'])

    opt.add_option('--logging',action='store_true',default=True,dest='logging',help='''enable logging in simulation scripts''')
    opt.add_option('--run',
                   help=('Run a locally built program; argument can be a program name,'
                         ' or a command starting with the program name.'),
                   type="string", default='', dest='run')
    opt.add_option('--visualize',
                   help=('Modify --run arguments to enable the visualizer'),
                   action="store_true", default=False, dest='visualize')
    opt.add_option('--mpi',
                   help=('Run in MPI mode'),
                   type="string", default="", dest="mpi")
    opt.add_option('--time',
                   help=('Enable time for the executed command'),
                   action="store_true", default=False, dest='time')
    opt.add_option('--with-brite',
                   help=('Use BRITE integration support, given by the indicated path,'
                         ' to allow the use of the BRITE topology generator'),
                   default=False, dest='with_brite')


MANDATORY_NS3_MODULES = ['core', 'network', 'point-to-point', 'applications', 'mobility', 'ndnSIM']
OTHER_NS3_MODULES = ['antenna', 'aodv', 'bridge', 'brite', 'buildings', 'click', 'config-store', 'csma', 'csma-layout', 'dsdv', 'dsr', 'emu', 'energy', 'fd-net-device', 'flow-monitor', 'internet', 'lte', 'mesh', 'mpi', 'netanim', 'nix-vector-routing', 'olsr', 'openflow', 'point-to-point-layout', 'propagation', 'spectrum', 'stats', 'tap-bridge', 'topology-read', 'uan', 'virtual-net-device', 'visualizer', 'wifi', 'wimax']

def configure(conf):
    conf.load(['compiler_c', 'compiler_cxx',
               'default-compiler-flags',
               'boost', 'ns3'])

    if not os.environ.has_key('PKG_CONFIG_PATH'):
        os.environ['PKG_CONFIG_PATH'] = ':'.join([
            '/usr/local/lib/pkgconfig',
            '/opt/local/lib/pkgconfig'])
    conf.check_cfg(package='libndn-cxx', args=['--cflags', '--libs'],
                   uselib_store='NDN_CXX', mandatory=True)

    test_code = '''
#include "libdash.h"

int main()
{
  return 0;
}
'''

    conf.env.append_value('INCLUDES', os.path.abspath(os.path.join("../libdash/libdash/libdash/include/", ".")))

    conf.check(args=["--cflags", "--libs"], fragment=test_code, package='libdash', lib='dash', mandatory=True, define_name='DASH', 
                                                    uselib_store='DASH',libpath=os.path.abspath(os.path.join("../libdash/libdash/build/bin/", ".")))

    conf.env['INCLUDES_DASH'] = os.path.abspath(os.path.join("../libdash/libdash/build/bin/", "."))

    conf.env.append_value('NS3_MODULE_PATH',os.path.abspath(os.path.join("../libdash/libdash/build/bin/", ".")))
    OTHER_NS3_MODULES.append('DASH')

    # check for brite
    conf.env['ENABLE_BRITE'] = False

    lib_to_check = 'libbrite.so'
    if Options.options.with_brite:
        conf.msg("Checking BRITE location", ("%s (given)" % Options.options.with_brite))
        brite_dir = Options.options.with_brite
        if os.path.exists(os.path.join(brite_dir, lib_to_check)):
            conf.env['WITH_BRITE'] = os.path.abspath(Options.options.with_brite)
        else:
            # Add this module to the list of modules that won't be built
            # if they are enabled.
            conf.env['MODULES_NOT_BUILT'].append('brite')
            return
    else:
        # No user specified '--with-brite' option, try to guess
        # bake.py uses ../../build, while ns-3-dev uses ../click
        brite_dir = os.path.join('..','BRITE')
        brite_bake_build_dir = os.path.join('..', '..', 'build') 
        brite_bake_lib_dir = os.path.join(brite_bake_build_dir, 'lib')
        if os.path.exists(os.path.join(brite_dir, lib_to_check)):
            conf.msg("Checking for BRITE location", ("%s (guessed)" % brite_dir))
            conf.env['WITH_BRITE'] = os.path.abspath(brite_dir)
# Below is not yet ready (bake does not install BRITE yet, just builds it)
#        elif os.path.exists(os.path.join(brite_bake_lib_dir, lib_to_check)):
#            conf.msg("Checking for BRITE location", ("%s (guessed)" % brite_bake_lib_dir))
#            conf.env['WITH_BRITE'] = os.path.abspath(brite_bake_lib_dir)
        else:
            # Add this module to the list of modules that won't be built
            # if they are enabled.
            conf.env['MODULES_NOT_BUILT'].append('brite')
            return

    test_code = '''
#include "Brite.h"

int main()
{
  return 0;
}
'''

    conf.env['DL'] = conf.check(mandatory=True, lib='dl', define_name='DL', uselib='DL')

    conf.env.append_value('NS3_MODULE_PATH',os.path.abspath(os.path.join(conf.env['WITH_BRITE'], '.')))

    conf.env['INCLUDES_BRITE'] = os.path.abspath(os.path.join(conf.env['WITH_BRITE'],'.'))

    conf.env['CPPPATH_BRITE'] = [
            os.path.abspath(os.path.join(conf.env['WITH_BRITE'],'.')),
            os.path.abspath(os.path.join(conf.env['WITH_BRITE'],'Models'))
            ]
    conf.env['LIBPATH_BRITE'] = [os.path.abspath(os.path.join(conf.env['WITH_BRITE'], '.'))]

    conf.env.append_value('CXXDEFINES', 'NS3_BRITE')
    conf.env.append_value('CPPPATH', conf.env['CPPPATH_BRITE'])

    conf.env['BRITE'] = conf.check(fragment=test_code, lib='brite', libpath=conf.env['LIBPATH_BRITE'], use='BRITE DL')

    if conf.env['BRITE']:
        conf.env['ENABLE_BRITE'] = True
        conf.env.append_value('CXXDEFINES', 'NS3_BRITE')
        conf.env.append_value('CPPPATH', conf.env['CPPPATH_BRITE'])
        OTHER_NS3_MODULES.append('BRITE')

    try:
        conf.check_ns3_modules(MANDATORY_NS3_MODULES)
        for module in OTHER_NS3_MODULES:
            conf.check_ns3_modules(module, mandatory = False)
    except:
        Logs.error ("NS-3 or one of the required NS-3 modules not found")
        Logs.error ("NS-3 needs to be compiled and installed somewhere.  You may need also to set PKG_CONFIG_PATH variable in order for configure find installed NS-3.")
        Logs.error ("For example:")
        Logs.error ("    PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH ./waf configure")
        conf.fatal ("")

    if conf.options.debug:
        conf.define ('NS3_LOG_ENABLE', 1)
        conf.define ('NS3_ASSERT_ENABLE', 1)

    if conf.env.DEST_BINFMT == 'elf':
        # All ELF platforms are impacted but only the gcc compiler has a flag to fix it.
        if 'gcc' in (conf.env.CXX_NAME, conf.env.CC_NAME):
            conf.env.append_value('SHLIB_MARKER', '-Wl,--no-as-needed')

    if conf.options.logging:
        conf.define('NS3_LOG_ENABLE', 1)
        conf.define('NS3_ASSERT_ENABLE', 1)

def build (bld):
    deps = 'NDN_CXX ' + ' '.join (['ns3_'+dep for dep in MANDATORY_NS3_MODULES + OTHER_NS3_MODULES]).upper ()

    common = bld.objects (
        target = "extensions",
        features = ["cxx"],
        source = bld.path.ant_glob(['extensions/**/*.cc', 'extensions/**/*.cpp']),
        use = deps,
        )

    for scenario in bld.path.ant_glob (['scenarios/*.cc']):
        name = str(scenario)[:-len(".cc")]
        app = bld.program (
            target = name,
            features = ['cxx'],
            source = [scenario],
            use = deps + " extensions DASH BRITE",
            includes = ' '.join (["extensions", bld.env['INCLUDES_BRITE'], bld.env['INCLUDES_DASH']])
            )

    for scenario in bld.path.ant_glob (['scenarios/*.cpp']):
        name = str(scenario)[:-len(".cpp")]
        app = bld.program (
            target = name,
            features = ['cxx'],
            source = [scenario],
            use = deps + " extensions DASH BRITE",
            includes = ' '.join (["extensions", bld.env['INCLUDES_BRITE'], bld.env['INCLUDES_DASH']])
            )

def shutdown (ctx):
    if Options.options.run:
        visualize=Options.options.visualize
        mpi = Options.options.mpi

        if mpi and visualize:
            Logs.error ("You cannot specify --mpi and --visualize options at the same time!!!")
            return

        argv = Options.options.run.split (' ');
        argv[0] = "build/%s" % argv[0]

        if visualize:
            argv.append ("--SimulatorImplementationType=ns3::VisualSimulatorImpl")

        if mpi:
            argv.append ("--SimulatorImplementationType=ns3::DistributedSimulatorImpl")
            argv.append ("--mpi=1")
            argv = ["openmpirun", "-np", mpi] + argv
            Logs.error (argv)

        if Options.options.time:
            argv = ["time"] + argv
        
        return subprocess.call (argv)
