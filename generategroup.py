import subprocess
import yaml
import os
from generatescene import generate_scene

def generate(scenecfg, screencfg, basepath, groupname):
    with open('groupsceneconfig.yaml') as fh:
        config  = yaml.safe_load(fh)
    for k,v in config.iteritems():
        if k == groupname:
            return generate_group(v, scenecfg, screencfg, basepath)
    print "No group found!"

def generate_group(groupcfg, scenecfg, screencfg, basepath='./'):
    for scenedesc in groupcfg['scenes']:
        scene = [ scene for scene in scenecfg['scenes']
            if scene['scene'] == scenedesc['scene'] ]
        if not scene:
            print scene
            raise Exception("No available scenes")
        print '------------\n'
        print scene
        inputstr, complexfilter, endstr = generate_scene(
            scene[0], screencfg, basepath)

        arglist = ['ffmpeg'] + inputstr.split(' ')[1:]
        arglist.append(complexfilter[0] +  '; '.join(complexfilter[1:-1])
            + complexfilter[-1])
        arglist += endstr

        outputfile = scenedesc['scene'].replace(' ', '_') + '.mp4'

        arglist.append(outputfile)

        arglist = [ x for x in arglist if x ]
        print ' '.join(arglist)
        print '----------------------\n'

        print 'Start generating'
        continue

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
            return
    print 'Combining videos'
    with open('./fil.txt', 'w') as fh:
        for scenedesc in groupcfg['scenes']:
            fh.write("file '{0}/{1}'\n".format(os.getcwd(),
                scenedesc['scene'].replace(' ', '_') + '.mp4'))

    return ['ffmpeg', '-f concat -i {0}/fil.txt'.format(os.getcwd())]
