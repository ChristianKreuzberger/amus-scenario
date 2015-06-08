# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-

VERSION='0.1'
APPNAME='template'

from waflib import Build, Logs, Options, TaskGen
import wutils
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
    opt.add_option('--with-dash',
                   help=('libdash path - assuming ../libdash/libdash/ if not provided'
                         '  - should contain the following subfolders: libdash/include/, build/bin/ '
                         '  - should contain the following files: header files, shared object (libdash.so)'),
                   default=False, dest='with_dash')
    opt.add_option('--command-template',
                   help=('Template of the command used to run the program given by --run;'
                         ' It should be a shell command string containing %s inside,'
                         ' which will be replaced by the actual program.'),
                   type="string", default=None, dest='command_template')


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
    conf.check_boost(lib='system iostreams')
    boost_version = conf.env.BOOST_VERSION.split('_')
    if int(boost_version[0]) < 1 or int(boost_version[1]) < 53:
        Logs.error ("ndnSIM requires at least boost version 1.53")
        Logs.error ("Please upgrade your distribution or install custom boost libraries (http://ndnsim.net/faq.html#boost-libraries)")
        exit (1)

    conf.check_cfg(package='libndn-cxx', args=['--cflags', '--libs'],
                   uselib_store='NDN_CXX', mandatory=True)



    # check for libdash
    conf.env['ENABLE_DASH'] = False
    lib_to_check = 'libdash.so'
    libdash_default_dir = "../libdash/libdash/" # according to tutorial

    if Options.options.with_dash:
        conf.msg("Checking LIBDASH location", ("%s (given)" % Options.options.with_dash))
        libdash_dir = os.path.abspath(os.path.join(Options.options.with_dash, "build/bin/"))
        if os.path.exists(os.path.join(libdash_dir, lib_to_check)):
            conf.env['WITH_DASH'] = os.path.abspath(Options.options.with_dash)
        else:
            # Add this module to the list of modules that won't be built
            # if they are enabled.
            conf.env['MODULES_NOT_BUILT'].append('dash')
            return
    else:
        # No user specified '--with-dash' option, try to guess
        # we have built it, so it should be in ../libdash/libdash/
        libdash_dir = os.path.abspath(os.path.join(libdash_default_dir, "build/bin/"))
        if os.path.exists(os.path.join(libdash_dir, lib_to_check)):
            conf.msg("Checking for LIBDASH location", ("%s (guessed)" % libdash_default_dir))
            conf.env['WITH_DASH'] = os.path.abspath(libdash_default_dir)
        else:
            # Add this module to the list of modules that won't be built
            # if they are enabled.
            conf.env['MODULES_NOT_BUILT'].append('dash')
            return
    # end if - libdash should be found now


    test_code = '''
#include "libdash.h"

int main()
{
  return 0;
}
'''

    conf.env.append_value('NS3_MODULE_PATH',os.path.abspath(os.path.join(conf.env['WITH_DASH'], 'build/bin/')))

    conf.env['INCLUDES_DASH'] = os.path.join(conf.env['WITH_DASH'], "libdash/include/")
    conf.env['LIBPATH_DASH'] = [ os.path.join(conf.env['WITH_DASH'], "build/bin/") ]

    conf.env['DASH'] = conf.check(fragment=test_code, lib='dash', libpath=conf.env['LIBPATH_DASH'], use='DASH')

    if conf.env['DASH']:
        conf.env['ENABLE_DASH'] = True
        conf.env.append_value('CXXDEFINES', 'NS3_LIBDASH')
        #OTHER_NS3_MODULES.append('DASH')



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
        #OTHER_NS3_MODULES.append('BRITE')

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
    deps = 'BOOST BOOST_IOSTREAMS ' + ' '.join (['ns3_'+dep for dep in MANDATORY_NS3_MODULES + OTHER_NS3_MODULES]).upper ()

    bld.all_task_gen = []

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
            )
        bld.all_task_gen.append(app)

    for scenario in bld.path.ant_glob (['scenarios/*.cpp']):
        name = str(scenario)[:-len(".cpp")]
        app = bld.program (
            target = name,
            features = ['cxx'],
            source = [scenario],
            use = deps + " extensions DASH BRITE",
            )
        bld.all_task_gen.append(app)
    wutils.bld = bld

def shutdown (ctx):
    bld = wutils.bld
    if wutils.bld is None:
        return
    env = bld.env

    if Options.options.run:
        wutils.run_program(Options.options.run, env, wutils.get_command_template(env),
                           visualize=Options.options.visualize,cwd='./')
        raise SystemExit(0)



