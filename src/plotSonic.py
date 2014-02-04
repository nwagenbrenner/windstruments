#!/usr/bin/env python

import sys
import os

import matplotlib.pyplot as plt
import datetime
import zipfile

def Usage():
    print '\nplotSonic.py start_time end_time d'
    print '\n    start_time, end_time: start/end hour for simulation.'
    print '                 2010-07-16T23:00:00 2010-07-18T00:00:00 (for one day)'
    print '\n    d: directory containing (only) averaged sonic data'
    print '\n    Plots available sonic data and writes a txt file (sonic.txt) for the'
    print '    specified time period.\n' 
    sys.exit(0)

start_time = None
end_time = None
d = None

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
        if start_time is None:
            start_time = argv[i] 
        elif end_time is None:
	        end_time = argv[i]
        elif d is None:
            d = argv[i] 
        else:
            Usage()

        i = i + 1

    if len(argv) < 3:
        print "Not enough args..."
        Usage()

start = datetime.datetime.strptime(start_time,"%Y-%m-%dT%H:%M:%S")
end = datetime.datetime.strptime(end_time,"%Y-%m-%dT%H:%M:%S")

#=============================================================================
#      Read the data and write a txt file for requested time period.
#=============================================================================

files = list()
speed = list()
direction = list()
T = list()
wptp = list()
ustar = list()
time = list()
moLength = list()

os.listdir(d)

for f in os.listdir(d):
    files.append(d + '/' + f)

def setAlpha(moLength):
    iMoLength = 1/moLength
    if iMoLength < -0.13:
        pStb = 'A'
        alpha = 5.0
        stb = 'unstable'
    elif iMoLength < -0.08:
        pStb = 'AB'
        alpha = 4.25
        stb = 'unstable'
    elif iMoLength < -0.06:
        pStb = 'B'
        alpha = 3.5
        stb = 'unstable'
    elif iMoLength < -0.035:
        pStb = 'BC'
        alpha = 2.75
        stb = 'unstable'
    elif iMoLength < -0.015:
        pStb = 'C'
        alpha = 2.0
        stb = 'unstable'
    elif iMoLength < 0.0:
        pStb = 'CD'
        alpha = 1.5
        stb = 'unstable'
    elif iMoLength < 0.015:
        pStb = 'D'
        alpha = 1.0
        stb = 'neutral'
    elif iMoLength < 0.07:
        pStb = 'E'
        alpha = 0.5 #TESTING!
        stb = 'stable'
    else:
        pStb = 'F'
        alpha = 0.2 #TESTING!
        stb = 'stable'
    return pStb, alpha, stb


fout = open("sonic.txt", 'w')
fout.write('time,speed,T,direction,wptp,ustar,L,pstability,alpha,stability\n')

for sonicFile in files:
    fin = open(sonicFile, 'r')
    line = fin.readline()

    while True:
        line = fin.readline()
        if len(line) == 0:
            print "Reached end of file. %d lines read." % len(time)
            break #EOF
        line = line.split(",")
        if line[0] != '':
            try:
                time.append(datetime.datetime.strptime(line[0], "%m/%d/%Y %H:%M")) #wsu format
            except:
                time.append(datetime.datetime.strptime(line[0], "%Y-%m-%d %H:%M")) #jefferson format
            speed.append(float(line[4]))
            T.append(float(line[3]))
            direction.append(float(line[5]))
            wptp.append(float(line[7]))
            ustar.append(float(line[6]))
            try:
                length = (-(T[-1] + 273.15) * (ustar[-1]**3)) / (0.4 * 9.81 * wptp[-1]) 
                moLength.append(length)
            except ZeroDivisionError:
                moLength.append(None)
                print 'Divsion by zero or nan...'
            try:
                pStb, alpha, stb = setAlpha(length)
            except:
                print 'Not calculating alpha...'
            if(time[-1] > start and time[-1] < end and 
              (time[-1].minute == 0 or time[-1].minute == 59)): #only write hourly avgs
                new_time = time[-1]
                if(time[-1].minute == 59): #stupid wsu thing
                    tomorrow = time[-1] + datetime.timedelta(days = 1)
                    new_time = time[-1].replace(minute = 0, hour = 0, day = tomorrow.day)
                try:
                    fout.write('%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.4f,%s,%.2f,%s\n' % (new_time.strftime('%Y-%b-%d %H:%M:%S'),
                        speed[-1], T[-1], direction[-1], wptp[-1], ustar[-1], moLength[-1], pStb,
                        alpha, stb)) #write to file
                except TypeError:
                    print 'NoneType detected for L...appending NA'
                    fout.write('%s,%.2f,%.2f,%.2f,%.2f,%.2f,NA,NA,2.0,stable\n' % (new_time.strftime('%Y-%b-%d %H:%M:%S'), 
                    speed[-1], T[-1], direction[-1], wptp[-1], ustar[-1]))#write to file
fout.close()
print 'sonic.txt written.'
fin.close()

#print "length time = ", len(time) 
#print "length ustar = ", len(ustar)
#print "length moLength =", len(moLength)


#=============================================================================
#             Plot data for requested time period.
#=============================================================================

fig = plt.figure()

fig.subplots_adjust(left=0.15)   # <--

ax1 = fig.add_subplot(211,)
ax1.plot(time, T, 'r-')
plt.xlim(start, end)
ax1.set_ylabel('T (C)', color = 'r')
ax1.xaxis.grid(color='gray', linestyle='dashed')
plt.setp(ax1.get_xticklabels(), visible=False)

ax2 = fig.add_subplot(212)
ax2.plot(time, direction, 'r.')
ax2.set_ylabel('Direction', color='r')
ax2.xaxis.grid(color='gray', linestyle='dashed')
#plt.xticks(rotation=-90)
fig.autofmt_xdate() #has to come before twinx()

ax2a = ax2.twinx()
ax2a.plot(time, speed, '-b')
ax2a.set_ylabel('speed (m/s)', color = 'b')
ax2a.yaxis.grid(color='gray', linestyle='dashed')
plt.xlim(start, end)

ax1a = ax1.twinx()
ax1a.plot(time, wptp, 'g-')
ax1a.set_ylabel('w\'T\'', color = 'g')
ax1a.yaxis.grid(color='gray', linestyle='dashed')
plt.xlim(start, end)


##add a new y-axis at left
newax = fig.add_axes(ax1.get_position())
newax.spines['left'].set_position(('outward', 50))
newax.patch.set_visible(False)
newax.yaxis.set_label_position('left')
newax.yaxis.set_ticks_position('left')
newax.plot(time, moLength, 'b-')
newax.set_ylabel('L (m)', color='blue')
plt.ylim((-50,50))
plt.xlim(start, end)
plt.setp(newax.get_xticklabels(), visible=False)

newax = fig.add_axes(ax2.get_position())
newax.spines['left'].set_position(('outward', 50))
newax.patch.set_visible(False)
newax.yaxis.set_label_position('left')
newax.yaxis.set_ticks_position('left')
newax.plot(time, ustar, 'g-')
newax.set_ylabel('ustar (m/s)', color='green')
plt.setp(newax.get_xticklabels(), visible=False)
plt.xlim(start, end)

plt.suptitle('Jefferson sonic 15-min Averages from %s to %s' % (start, end))
plt.show()
 













