#!/usr/bin/python

def Usage():
    print '\n    writeSonic.py azimuth fin [-a avgMinutes]'
    print '\n    azimuth: sonic azimuth in degrees'
    print '\n    fin: input filename.'
    print '\n    avgMinutes: optional averaging period in minutes. Default is 15.'
    print '                options are 1, 5, 10, 15, or 30.'
    print '\n    Processes 10 Hz sonic data with averageSonic.py'
    print '    Returns 15-min averages of U, V, T, speed, direction, ustar, and w\'T\'\n'   
    sys.exit(0)

#=============================================================================
#             Set some initial values.
#=============================================================================
import averageSonic
import csv
import sys

azimuth = None
fin = None
avgMinutes = 15

#=============================================================================
#             Parse command line options.
#=============================================================================

if __name__ == '__main__':
    argv = sys.argv
    if argv is None:
        sys.exit(0)   

    i = 1

    while i < len(argv):
        arg = argv[i]
        if arg == '-a':
            i = i + 1
            avgMinutes = int(argv[i])
        elif azimuth is None:
            azimuth = argv[i] 
        elif fin is None:
            fin = argv[i] 
        else:
            Usage()

        i = i + 1

    if len(argv) < 3:
        print "\n    Not enough args..."
        Usage()

Vaz = int(azimuth) + 90 #Vaz is sonic azimuth + 90 degrees 
if Vaz > 360:
    Vaz = Vaz - 360 
fout = fin[:-4] + '_%dmin_avg.txt' % avgMinutes

f = csv.reader(open(fin, 'rU'))
data = averageSonic.csat3(Vaz, f, avgMinutes)
fileout = data.write_file(fout)




