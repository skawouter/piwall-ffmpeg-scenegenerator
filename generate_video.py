import os
import sys
import yaml
import getopt
import subprocess
import generatescene
def main(argv):
#    try:
        totalscenes = 0
       
        optlist, args = getopt.getopt(argv, 'pen:o:b:c:')

        outputfile = ''
        basepath = configpath = './'
        execflag = False
        for opt, arg in optlist:
            if opt == '-n':
                totalscenes = arg
            if opt == '-o':
                outputfile = arg
            if opt == '-b':
                basepath = arg
            if opt == '-c':
                configpath = arg
            if opt == '-e':
                execflag = True

        with open(configpath + 'screenconfig.yaml') as f:
            screenconfig = yaml.safe_load(f)
        with open(configpath + 'scenes.yaml') as f:
            sceneconfig = yaml.safe_load(f)

        if args:
            sceneconfig['scenes'] = [ scene for scene in sceneconfig['scenes']
                if scene['scene'] == ' '.join(args) ]
            if not sceneconfig['scenes']:
                raise Exception("No available scenes")
        if not outputfile:
            print 'no outputfile specified can not continue (use -o filename)'
            return -1

        if not totalscenes:
            totalscenes = len(sceneconfig['scenes'])

        inputstr, complexfilter, endstr = generatescene.generate_scene(
             sceneconfig['scenes'][0], screenconfig, basepath)

        arglist = ['ffmpeg'] + inputstr.split(' ')[1:]
        arglist.append(complexfilter[0] +  '; '.join(complexfilter[1:-1])
            + complexfilter[-1])
        arglist += endstr 

        #limit file size to 40Mb
        arglist.append(' -fs 41943040 ')
        arglist.append(outputfile)

        arglist = [ x for x in arglist if x ]
        print ' '.join(arglist)

        print 'Start generating'
        if execflag:
            if os.path.exists(outputfile):
                os.remove(outputfile)
            with open('/dev/null', 'wb') as f:
                proc = subprocess.Popen([' '.join(arglist)], shell=True,
                    stdout=f, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            if not proc.returncode:
                print "Video generated"
            else:
                print "FAIL"
                print err
                print "FAIL"


#except Exception as e:
#        raise e

if __name__ == "__main__":
    main(sys.argv[1:])
