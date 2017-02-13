#!/usr/bin/env python3

####################################################################################
### Copyright (C) 2015-2019 by ABLIFE
####################################################################################





####################################################################################

####################################################################################
# Date           Version       Author            ChangeLog

#
#
#
#
#####################################################################################

"""



"""


# import subprocess
# import threading
# from ablib.resource import nodes
# from ablib.resource import assignment
# from ablib.utils import filesplit
from ablib.utils.tools import *


# if sys.version_info < (3, 0):
#     print("Python Version error: please use phthon3")
#     sys.exit(-1)


_version = 'v1.0'


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
# def configOpt():
#     """Init for option
#     """
#     usage = 'Usage: %prog [-c] [other option] [-h]'
#     p = OptionParser(usage)
#     ##basic options
#     p.add_option('--showtools', dest='showtools', default=False, action='store_true', help='showtools')
#     ##preset options
#     group = OptionGroup(p, "Preset options")
#     group.add_option('-O', '--outDir', dest='outDir', default='./', action='store', type='string', help='output directory,default is ./', metavar="DIR")
#     group.add_option('-L', '--logDir', dest='logDir', default='', action='store', type='string', help='log dir ,default is outDir/log')
#     group.add_option('-P', '--logPrefix', dest='logPrefix', default='', action='store', type='string', help='log file prefix')
#     group.add_option('-E', '--email', dest='email', default='none', action='store', type='string', help='email address, if you want get a email when this job is finished,default is no email', metavar="EMAIL")
#     group.add_option('-Q', '--quiet', dest='quiet', default=False, action='store_true', help='do not print messages to stdout')
#     group.add_option('-K', '--keepTemp', dest='keepTemp', default=True, action='store_false', help='keep temp dir')
#     group.add_option('-T', '--test', dest='isTest', default=False, action='store_true', help='run this program for test')
#     p.add_option_group(group)
#
#     opt, args = p.parse_args()
#     return (p, opt, args)


def listToString(x):
    """
    """
    rVal = ''
    for a in x:
        rVal += a + ' '
    return rVal



# opt_parser, opt, args = configOpt()



# if opt.logDir == "":
#     opt.logDir = opt.outDir + '/logs/'
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


scriptPath = os.path.abspath(os.path.dirname(__file__))  # absolute script path


# binPath = scriptPath + '/bin'  # absolute bin path
# outPath = os.path.abspath(opt.outDir)  # absolute output path
# os.system("mkdir -p " + outPath)
# tempPath = outPath + '/temp/'  # absolute bin path
# os.system("mkdir -p " + tempPath)
# resultPath = outPath + '/result/'
# os.system("mkdir -p " + resultPath)
# logPath = os.path.abspath(opt.logDir)
# os.system("mkdir -p " + logPath)


# srcpath = scriptPath if not opt.srcDir else os.path.abspath(opt.srcDir)


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
# def initLogging(logFilename):
#     """Init for logging
#     """
#     logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s : %(levelname)s] %(message)s', datefmt='%y-%m-%d %H:%M', filename=logFilename, filemode='w')

#         # define a Handler which writes INFO messages or higher to the sys.stderr
#         console = logging.StreamHandler()
#         console.setLevel(logging.INFO)
#         # set a format which is simpler for console use
#         formatter = logging.Formatter('[%(asctime)s : %(levelname)s] %(message)s', datefmt='%y-%m-%d %H:%M')
#         # tell the handler to use this format
#         console.setFormatter(formatter)
#         logging.getLogger('').addHandler(console)
#
#
# dt = datetime.datetime.now()
# logFile = logPath + '/' + opt.logPrefix + 'log.' + str(dt.strftime('%Y%m%d.%H%M%S.%f')) + '.txt'
# initLogging(logFile)

#
# os.system('rm -rf ' + opt.outDir + '/log && ln -s ' + logFile + ' ' + opt.outDir + '/log')
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
# logging.debug('Program version: %s' % _version)
# logging.debug('Start the program with [ python3 %s ]\n', listToString(sys.argv))
# startTime = datetime.datetime.now()



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------
def print_tools(tools_dict):
    for key in tools_dict:
        print("##" + key + "\t\t" + tools_dict[key]["info"])
        for t in tools_dict[key]["modules"]:
            print("\t" + t[0] + "\t\t" + t[1])


def nextvalue(list, value):
    index = list.index(value)
    return list[index + 1]


def argv2config(tool_name, tool_argv):
    filename = tool_name + '.%s.config' % os.getpid()
    with open(filename, 'w') as o:
        o.writelines('[gc]' + "\n")
        for id in tool_argv:
            if id == "-genomeid":
                value = nextvalue(tool_argv, id)
                o.writelines("GenomeID = " + value + "\n\n")
        o.writelines('[sample]' + "\n\n")
        for id in tool_argv:
            if re.search(r'-sample\d+$', id):
                input_id = re.sub(r'^-', "", id)
                value = nextvalue(tool_argv, id)
                o.writelines(input_id + " = " + value + "\n")
        for id in tool_argv:
            if re.search(r'-list\d+$', id):
                input_id = re.sub(r'^-', "", id)
                value = nextvalue(tool_argv, id)
                o.writelines(input_id + " = " + value + "\n")
        o.writelines('[module:' + tool_name + ']' + "\n")
        o.writelines("order = 1 \n")
        for id in tool_argv:
            if id == "-genomeid":
                continue
            elif re.search(r'-sample\d+$', id):
                continue
            elif re.search(r'-list\d+$', id):
                continue
            elif id.startswith("-"):
                input_id = re.sub(r'^-', "", id)
                value = nextvalue(tool_argv, id)
                o.writelines(input_id + " = " + value + "\n")
    return filename


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def main():



    modules_dict, tools_dict = register()
    if len(sys.argv) == 1:
        print_tools(tools_dict)
        sys.exit(1)


    if sys.argv[1] not in modules_dict:
        print("Hello！You have select a tools that not exist！")
        print_tools(tools_dict)
        sys.exit(1)


    if len(sys.argv) == 2 or "-h" in sys.argv:
        Thistool = modules_dict[sys.argv[1]]
        print("\n  ：" + Thistool.__doc__ + "\n")
        m = Thistool()
        m.print_help(scriptPath)
        sys.exit(1)

    if len(sys.argv) >= 3:
        tool_argv = sys.argv[2:]
        tool_name = sys.argv[1]
        temp_config_file = argv2config(tool_name, tool_argv)
        os.system("python3 " + scriptPath + "/Pipeline.py -c " + temp_config_file)
        os.system("rm -rf flowchart.png flowchart.dot temp finished_modules.txt ")


        # logging.info("Main procedure start...")


        # configfile = os.path.abspath(opt.configfile)
        # config = Config()
        # config.readConfigFile(configfile)

        #
        # if os.path.exists(scriptPath + '/__VERSION__'):
        #     logging.info('Version:')
        #     ver = ''
        #     for line in open(scriptPath + '/__VERSION__'):
        #         line = line.strip()
        #         ver += line + ' '
        #     logging.info(ver)
        # else:
        #     logging.info('Version: [dev]')
        #
        # if opt.makecmd:
        #     config.gc["make-cmd-only"] = True
        # if to_bool(config.gc["make-cmd-only"]):
        #     logging.info("make-cmd-only modle")
        #
        # logging.info("Load config file successfully")
        #
        # ##################################

        # ##################################
        #

        # for order in sorted(config.switchorder, key=int):
        #     fi = open('finished_modules.txt', "a")
        #     if len(config.switchorder[order]) == 0:
        #         continue
        #     runThem(config.switchorder[order], config, fi)
        #     fi.close()


if __name__ == '__main__':

    main()


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
# if not opt.keepTemp:
#     os.system('rm -rf ' + tempPath)
#     logging.debug("Temp folder is deleted..")
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
# logging.debug("Program ended")
# currentTime = datetime.datetime.now()
# runningTime = (currentTime - startTime).seconds  # in seconds



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
# if opt.email != "none":
#     run_cmd = listToString(sys.argv)
#     sendEmail(opt.email, str(startTime), str(currentTime), run_cmd, outPath)



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def countProgram(programName, startT, runT, isTest):
    countProgramFile = open('/users/ablife/ablifepy/countProgram.txt', 'a')
    countProgramFile.write(programName + '\t' + str(startT) + '\t' + str(runT) + 's\t' + isTest + '\n')
    countProgramFile.close()

# testStr = 'P'
# if opt.isTest:
#     testStr = 'T'
# countProgram(sys.argv[0], startTime, runningTime, testStr)
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
