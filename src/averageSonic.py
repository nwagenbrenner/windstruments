import csv
import datetime

import numpy
import scipy.stats as stats
import math

import fnmatch

## 
#  Class that calculates and averages CSAT3 data.
#  @param Vaz sonic angle, Vaz = azimuth + 90 degrees
#  @param f path to sonic file
#  @param avgMinutes Averaging period in minutes.
#         options are 1, 5, 10, 15, and 30.
#         default is 15.
#

class csat3:

    def __init__(self, Vaz, f, avgMinutes=15):
        self.Vaz = Vaz
        self.f = f
        self.avgMinutes = avgMinutes
        self.end_file = False

    ## 
    #  extract sonic data from file
    #
    #  @return datetime, temp, ux, uy, uz
    #
    def extract(self, loop):
        self.end_file = False
        dt = list()
        T = list()
        ux = list()
        uy = list()
        uz = list()
        
        try: #see if we are end of file before we enter loop
            row = self.f.next()
        except:
            print 'Reached end of csv file'
            self.end_file = True
            return None
            
        if '.' not in row[4]:
            row[4] = row[4] + '.0'
        
        for i in range(20000): #9000 rows = 15 min of data
            if len(row[3]) == 4: #check for different H:M formats
                dateTime = datetime.datetime.strptime(row[1]+'/'+row[2]+'/'+row[3][:2]+'/'+row[3][2:]+'/'+row[4][:-2]+'/'+row[4][-1:], "%Y/%j/%H/%M/%S/%f")
            if len(row[3]) == 3:
                dateTime = datetime.datetime.strptime(row[1]+'/'+row[2]+'/'+'0'+row[3][0]+'/'+row[3][1:]+'/'+row[4][:-2]+'/'+row[4][-1:], "%Y/%j/%H/%M/%S/%f")

            theTime = dateTime.strftime("%M:%S.%f")[:-5]
        
            if(self.avgMinutes == 1):
                if (fnmatch.fnmatch(theTime, '?1:00.1')):
                    if i == 0:
                        return None
                    break
            elif(self.avgMinutes == 5):
                if (fnmatch.fnmatch(theTime, '?5:00.1')):
                    if i == 0:
                        return None
                    break
            elif(self.avgMinutes == 10):
                if (fnmatch.fnmatch(theTime, '?0:00.1')):
                    if i == 0:
                        return None                    
                    break
            elif(self.avgMinutes == 15):
                if (theTime == '00:00.1' or theTime == '15:00.1' \
                    or theTime == '30:00.1' or theTime == '45:00.1'):
                    if i == 0:
                        return None
                    break
            elif(self.avgMinutes == 30):
                if (theTime == '00:00.1' or theTime == '30:00.1'):
                    if i == 0:
                        return None
                    break
                    
            dt.append(dateTime)
            T.append(float(row[5]))
            ux.append(float(row[6]))
            uy.append(float(row[7]))
            uz.append(float(row[8]))
            
            tdelta = dateTime - dt[0]
            
            try: #continue reading data if not EOF and tdelta < avg time
                row = self.f.next()
            except:
                print 'Reached end of csv file'
                self.end_file = True
                break
            
            if '.' not in row[4]:
                row[4] = row[4] + '.0'
            
            if tdelta > datetime.timedelta(minutes = self.avgMinutes, seconds = 0):
                break

        return dt, T, ux, uy, uz, tdelta

    ## 
    #  10 Hz calculations (direction, speed, u', v', ustar, U, V, w'T')
    #
    #  return dt, T, U, V, speed, direction, ustar, wprime_Tprime

    def calcs(self, loop):
        data = self.extract(loop)
        if data == None:
            return None
        tdelta = data[5]
        dt = list()
        ux = list() #Usonic
        uy = list() #Vsonic
        wprime = list()
        T = list()
        speed = list()
        direction = list()
        U = list() #U in geographic coords
        V = list() #V in geographic coords
        for i in xrange(len(data[0])):
            dt.append(data[0][i])
            ux.append(data[2][i])
            uy.append(data[3][i])
            wprime.append(data[4][i])
            T.append(data[1][i])
            direction.append(math.atan2(-ux[i],-uy[i])*180/math.pi + self.Vaz)
            speed.append((ux[i]*ux[i]+uy[i]*uy[i])**0.5)
            U.append(ux[i]*math.cos(self.Vaz*math.pi/180) + uy[i]*math.sin(self.Vaz*math.pi/180))
            V.append(-ux[i]*math.sin(self.Vaz*math.pi/180) + uy[i]*math.cos(self.Vaz*math.pi/180))

        #calculate moving average with 1 min window, all observations equally weighted
        weights = numpy.repeat(1.0, 600)/600
        Tmoving_avg = numpy.convolve(T, weights, 'valid')
        Umoving_avg = numpy.convolve(U, weights, 'valid')
        Vmoving_avg = numpy.convolve(V, weights, 'valid')

        #populate lists of primes
        Uprime = list()
        Vprime = list()
        Tprime = list()
        for i in range(300): #no moving avg for upper boundary
            Uprime.append(U[i] - numpy.mean(U[0:299]))
            Vprime.append(V[i] - numpy.mean(V[0:299]))
            Tprime.append(T[i] - numpy.mean(T[0:299]))
        U_index = len(Uprime) - 1

        for i in range(len(Umoving_avg)-1): #use moving avg for central values
            Uprime.append(U[i+299] - Umoving_avg[i])
            Vprime.append(V[i+299] - Vmoving_avg[i])
            Tprime.append(T[i+299] - Tmoving_avg[i])

        U_index = len(Uprime) - 1
        V_index = len(Vprime) - 1
        T_index = len(Tprime) - 1

        for i in range(300): #no moving avg for lower boundary
            Uprime.append(U[i+U_index] - numpy.mean(U[((len(U)-1)-299):(len(U)-1)]))
            Vprime.append(V[i+V_index] - numpy.mean(V[299+V_index:(len(V)-1)]))
            Tprime.append(T[i+T_index] - numpy.mean(T[299+T_index:(len(T)-1)]))

        ustar = list()
        wprime_Tprime = list()
        for i in xrange(len(data[0])): 
            ustar.append(((Uprime[i]*wprime[i])**2*(Vprime[i]*wprime[i])**2)**0.25)
            wprime_Tprime.append(wprime[i]*Tprime[i])

        return dt, T, U, V, speed, direction, ustar, wprime_Tprime         

    ## 
    #  Calculate 15-min averages to write out
    #
    #  return average U, V, T, speed, direction, ustar, wprime_Tprime 

    def averages(self, loop):
        data = self.calcs(loop)
        if data == None:
            return None
        time = list()
        T = list()
        U = list()
        V = list()
        speed = list()
        direction = list()
        ustar = list()
        wprime_Tprime = list()

        for i in xrange(len(data[0])):
            time.append(data[0][i])
            T.append(data[1][i])
            U.append(data[2][i])
            V.append(data[3][i])
            speed.append(data[4][i])
            direction.append(data[5][i])
            ustar.append(data[6][i])
            wprime_Tprime.append(data[7][i])

        time_begin = time[0].strftime("%Y-%m-%d %H:%M")
        time_end = time[(len(time)-1)].strftime("%Y-%m-%d %H:%M")
        print 'start time = %s\n' % time[0].strftime("%Y-%m-%d %H:%M:%S.%f")
        print 'end time = %s\n' % time[(len(time)-1)].strftime("%Y-%m-%d %H:%M:%S.%f")
        #use masked arrays to get around NANs
        samples = numpy.ma.masked_array(U, numpy.isnan(U))  
        U_avg = numpy.mean(samples)
        samples = numpy.ma.masked_array(V, numpy.isnan(V))
        V_avg = numpy.mean(samples)
        samples = numpy.ma.masked_array(T, numpy.isnan(T))
        T_avg = numpy.mean(samples)
        samples = numpy.ma.masked_array(speed, numpy.isnan(speed))
        speed_avg = numpy.mean(samples)
        samples = numpy.ma.masked_array(direction, numpy.isnan(direction))
        direction_avg = stats.morestats.circmean(samples, 360, 0)
        samples = numpy.ma.masked_array(ustar, numpy.isnan(ustar))
        ustar_avg = numpy.mean(samples)
        samples = numpy.ma.masked_array(wprime_Tprime, numpy.isnan(wprime_Tprime))
        wprime_Tprime_avg = numpy.mean(samples)
        
        return time_end, U_avg, V_avg, T_avg, speed_avg, direction_avg, \
               ustar_avg, wprime_Tprime_avg
    ## 
    #  @Write output file with averages 
    #
    #  @return filename

    def write_file(self, filename = ''):
        if filename == '':
            filename = 'sonic_summary_' + self.Vaz + '_csat3'
        if filename[-4:] != '.txt':
            filename = filename + '.txt'

        fout = open(filename, 'w')
        fout.write('Time, U, V, T, speed, direction, ustar, wprimeTprime\n')
        
        #loop over 15-min intervals in sonic file
        self.end_file = False
        loop = 0
        while self.end_file == False:
            data = self.averages(loop)
            if data == None:
                continue
            fout.write('%s, %.2f, %.2f, %.2f, %.2f, %.1f, %.2f, %.4f\n' % \
                (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]))
            loop = loop + 1
        fout.close()
        return filename

