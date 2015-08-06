import os
import datetime

import sqlite3 as lite

import numpy
import scipy.stats as stats

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import zipfile
import math

## Class representing a single point plot on Big Butte.
#  Contains a start and end time for subsetting.  Requires a plot id to extract
#  data.
#
#  @todo Implement stats stuff for fewer dependencies
#
class mean_flow_point:

    ## Plot id to extract data from.
    plot = ""
    ## Start time for time subset.
    start = ""
    ## End time for time subset
    end = ""
    ## Should we ignore 'suspect' results?
    ignoresuspect = False

    ##
    #  @brief Initialize class with plot name, start and end time
    #
    #  @param plot_id Plot to extract data from.
    #  @param start_time time to start time subset as an ISO Date/Time string
    #  @param end_time time to end time subset as an ISO Date/Time string
    #  @param ignoresuspect ignore suspect data where:
    #  @code Quality != 'OK' @endcode
    #  or
    #  @code Sensor_qual != 'OK' @endcode
    #  @note ISO Format:
    #  @code YYYY-MM-DDTHH:MM:SS @endcode
    #  where the T delimits date and time
    #
    def __init__(self, plot_id, start_time, end_time, ignoresuspect = False):
        self.plot = plot_id
        self.start = datetime.datetime.strptime(start_time, 
                                                "%Y-%m-%dT%H:%M:%S")
        self.end = datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")
        self.ignoresuspect = ignoresuspect

    ## 
    #  @brief Fetch the location of a point.
    #
    #  @return the longitude and latitude of the point/plot
    #
    def location(self):
        con = lite.connect('/home/natalie/birch_creek/birch.sqlite')
        if con is None:
                if __debug__:
                    print 'Failed to connect to sqlite database'
                return None
        cur = con.cursor()
        sql = """SELECT geometry
                FROM plot_location
                WHERE plot_id='%s'""" % self.plot
        cur.execute(sql)
        result = cur.fetchone()
        result[0]
        r = result[0].split(",")
        print(r)
        print(r[0])
        print(r[0][:r[0].find(' ')])
        print(r[0][r[0].find(' ') + 1:])
        lat = float(r[0][:r[0].find(' ')])
        lon = float(r[0][r[0].find(' ') + 1:])
        con.close()
        return lat, lon

    ## 
    #  @brief Extract the point data from the database.
    #
    #  This data is bounded by the start and end time
    #
    #  @param ignoresuspect Ignore readings with questionable reading, 
    #         definitely the no data values (-888.0) Quality='CAUTION', 
    #         but later on stuck sensors, Sensor_qual='CAUTION'
    #  @return tuple(s) of data on success, None on failure
    #
    def extract(self):
        con = lite.connect('/home/natalie/birch_creek/birch.sqlite')
        cur = con.cursor()
        sql = """SELECT * FROM mean_flow_obs
                  WHERE Plot_id='%s'
                  AND Date_time BETWEEN '%s' AND '%s'
                  AND Quality='OK'""" \
                  % (self.plot,
                  self.start.strftime('%Y-%m-%d %H:%M:%S'),
                  self.end.strftime('%Y-%m-%d %H:%M:%S'))
        cur.execute(sql)
        data = cur.fetchall()
        if __debug__:
            print 'Query fetched %i result(s)' % len(data)
        if len(data) == 0:
            print 'Query fetched no data for plot %s.' % self.plot
            return None
        if self.ignoresuspect:
            sql = sql + "AND Quality='OK'"
        cur.execute(sql)
        data = cur.fetchall()
        if __debug__:
            print 'Query fetched %i result(s)' % len(data)
        con.close()
        return data

    ## 
    #  @brief Extract the point data and average the speed and direction
    #
    #  Average the speed and direction, use the max gust.  Also return stats
    #  on the speed and direction
    #
    #  @return ((average speed, speed standard deviation),
    #           (max gust),
    #           (average direction, direction standard deviation))
    #
    def extract_average(self):
        data = self.extract()
        if data == None:
            return None
        speed = list()
        gust = list()
        direction = list()

        for i in xrange(len(data)):
            speed.append((data[i][2])*0.447) # convert to m/s
            gust.append((data[i][3])*0.447) # convert to m/s
            direction.append(data[i][4])

        if len(speed) < 1 or len(gust) < 1 or len(direction) < 1:
            return None

        samples = numpy.array(speed)
        spd_mean = numpy.mean(samples)
        spd_stddev = numpy.std(samples)
        samples = numpy.array(gust)
        gust_max = numpy.max(samples)
        samples = numpy.array(direction)
        direction_mean = stats.morestats.circmean(samples, 360, 0)
        direction_stddev = stats.morestats.circstd(samples, 360, 0)

        return (spd_mean, spd_stddev), (gust_max), (direction_mean, direction_stddev)

    ## 
    #  @brief Create an image for a point time series.
    #
    #  Create a time series image from a point object with data > 1
    #  @param filename to write image to, if ommitted, just display plot.
    #  @return None on failure, image name on success
    #
    def create_time_series_image(self, filename = ''):
        data = self.extract()
        if data == None:
            return None
        if len(data) < 1:
            if __debug__:
                print 'Insufficient data to create a plot'
            return None

        speed = list()
        gust = list()
        direction = list()
        time = list()

        #create lists for matplotlib
        for i in xrange(len(data)):
            speed.append((data[i][2])*0.447) # convert to m/s
            gust.append((data[i][3])*0.447) # convert to m/s
            direction.append(data[i][4])
            time.append(datetime.datetime.strptime(data[i][1], "%Y-%m-%d %H:%M:%S"))

        if len(data) >= 1:
            fig = plt.figure()

            ax1 = fig.add_subplot(211)
            ##ax1a = ax1.twinx()

            ax1.plot(time, speed, 'b-')
            #ax1.plot(time, gust, 'g-')
            ax1.set_xlabel('Time (s)')
            #ax1.set_ylabel('Speed(m/s)', color = 'b')
            ax1.set_ylabel('Speed(m/s)', color = 'b')
                       
            ax2 = fig.add_subplot(212)
            ax2.plot(time, direction, 'r.')
            ax2.set_ylabel('Direction', color='r')

            fig.autofmt_xdate()

            plt.suptitle('Plot %s from %s to %s' % (self.plot, 
                         self.start.strftime('%Y-%m-%d %H:%M:%S'),
                         self.end.strftime('%Y-%m-%d %H:%M:%S')))

            if filename == '':
                plt.show()
            else:
                fout = open(filename, 'w')
                plt.savefig(fout)

            return filename
        else:
            if __debug__:
                print 'Unknown failure in src.create_image()'
            return None

    ## 
    #  @brief Create kml string for a plot.
    #
    #  Data includes:
    #  - an optional image of a time series
    #  - optional images of plot pictures 
    #  - average statistics for the time series
    #  If writevector is true, draw a vector using LineString using:
    #
    #  @param imagefile file to be embedded in the placemark.
    #         This can be a photo or a graph of the time series
    #  @param calcstats write the stats to the CDATA
    #  @param writevector write a vector representation of the placemark.
    #  @return a string representation of kml
    #
    def create_kml(self, imagefile = '',  calcstats = True, begin = '', end = '', direc = ''):
        lon, lat = self.location()
        lon = float(lon)
        lat = float(lat)
        stats = self.extract_average()
        if stats is None:
            return ''
        d = stats[2][0]
        if d < 0:
            d = d + 360.0
        kml =               '  <Placemark>\n'\
                            '    <Style>\n' \
                            '      <IconStyle>\n' \
                            '        <Icon>\n' \
                            '          <href>http://maps.google.com/mapfiles/kml/shapes/arrow.png</href>\n' \
                            '        </Icon>\n' \
                            '        <heading>%s</heading>\n' \
                            '      </IconStyle>\n' \
                            '    </Style>\n'\
                            '    <Point>\n' \
                            '      <coordinates>%.9f,%.9f,0</coordinates>\n' \
                            '    </Point>\n' % (d, lon, lat)
        kml = kml +         '    <name>%s</name>\n' \
                            '    <description>\n' \
                            '      <![CDATA[\n' % self.plot
        if(imagefile != ''):
            kml = kml +     '        <img src = "%s"/>\n'  % imagefile
	if(calcstats == True):
            kml = kml +     '        <table border="1">' \
                            '          <tr>\n' \
                            '            <th>Stats</th>\n' \
                            '          </tr>\n' \
                            '          <tr>\n' \
                            '            <td>Average Speed</td>\n' \
                            '            <td>%.2f</td>\n' \
                            '          </tr>\n' \
                            '          <tr>\n' \
                            '            <td>STDDEV Speed</td>\n' \
                            '            <td>%.2f</td>\n' \
                            '          </tr>\n' \
                            '          <tr>\n' \
                            '            <td>Max Gust</td>\n' \
                            '            <td>%.2f</td>\n' \
                            '          </tr>\n' \
                            '          <tr>\n' \
                            '            <td>Circular Avg Direction</td>\n' \
                            '            <td>%.2f</td>\n' \
                            '          </tr>\n' \
                            '          <tr>\n' \
                            '            <td>STDDEV Direction</td>\n' \
                            '            <td>%.2f</td>\n' \
                            '          </tr>\n' \
                            '        </table>\n' % (stats[0][0], stats[0][1],
                                                   stats[1], stats[2][0],
                                                   stats[2][1])
        kml = kml +         '        Additional information at: https://collab.firelab.org/software/projects/big-butte\n' \
                            '      ]]>\n' \
                            '    </description>\n' \
                            '  </Placemark>\n'
        return kml    

    ## 
    #  @brief Create a kmz for a point with a time series plot.
    #
    #  @param filename to write.  If the extension is not .kmz, it will be
    #  appended.  If no file name is given, the plot id is used.
    #
    def create_kmz(self, filename = ''):
        if filename == '':
            filename = self.plot
        if filename[-4:] != '.kmz':
            filename = filename + '.kmz'

        pngfile = self.create_time_series_image(self.plot + '.png')
        kml = self.create_kml(pngfile)
        
        kmlfile = 'doc.kml'
        fout = open(kmlfile, 'w')
        fout.write(kml)
        fout.close()
        kmz = zipfile.ZipFile( filename, 'w', 0, False)
        kmz.write(kmlfile)
        kmz.write(pngfile)
        kmz.close()
        os.remove(kmlfile)
        os.remove(pngfile)
        return filename

    def create_csv(self, filename):
        data = self.extract()
        if len(data) < 1:
            if __debug__:
                print 'Insufficient data to create a plot'
            return None
        if filename == '':
            filename = self.plot
        if filename[-4:] != '.csv':
            filename = filename + '.csv'
        lon, lat = self.location()
        lon = float(lon)
        lat = float(lat)
        fout = open(filename, 'w')
        for i in xrange(len(data)):
            time = data[i][1]
            speed = data[i][2]
            gust = data[i][3]
            direction = data[i][4]
            fout.write('%.6f,%.6f,%s,%s,%.2f,%.2f,%.1f\n' % (lon, lat,
                       self.plot, time,
                       #time.strftime('%Y-%m-%d %H:%M:%S'),
                       speed, gust, direction))
        fout.close()
        return filename


##
#  Class for representing an entire wind field for a snapshot in time, or
#  an average of time.
#
class mean_flow_field:
    ## Start date to pass to the point instances
    start = ''
    ## End date to pass to the point instances
    end = ''
    ## Flag for supressing bad data, passed to point instances.
    ignoresuspect = True

    ## Construct a field object
    #  @param start_time start time for subset
    #  @param end_time end time for subset
    #  @param ignoresuspect ignore bad values in averaging

    def __init__(self, start_time, end_time, ignore = True):
        self.start = start_time
        self.end = end_time
        self.ignoresuspect = ignore

    def fetch_plot_list(self):
        con = lite.connect('/home/natalie/birch_creek/birch.sqlite')
        if con is None:
            if __debug__:
                print 'Failed to connect to sqlite database'
            return None
        cur = con.cursor()
        sql = "SELECT Plot_id FROM plot_location"
        cur.execute(sql)
        data = cur.fetchall()
        if data == None:
            if __debug__:
                print 'Failed to extract plot list from the database'
            return None
        plots = list()
        for i in xrange(len(data)):
            plots.append(data[i][0])

        return tuple(plots)

    ## 
    #  @brief Create a plot kmz to show the entire field with no data.
    #
    #  @param filename file to open and write to
    #  @return filename if successfully written, otherwise, None
    #
    def create_plot_kmz(self, filename = ''):
        print filename

    ## 
    #  @brief Create a kmz with a vector field representing the data.
    #
    #  Write a kmz and all pertinent data.  The kmz will hold a placemark for 
    #  all valid plots during the time period.  An optional time series graph
    #  may also be included, as well as optional statistics.
    #
    #  @param filename to write data to.
    #  @param timeseries write the time series graph to the placemarks
    #  @return filename on success, None on failure.
    #
    def create_kmz(self, filename = '', timeseries=False):
        plots = self.fetch_plot_list()
        if len(plots) == 0:
            return None
        kmlfile = 'doc.kml'
        fout = open(kmlfile, 'w')
        fout.write('<Document>\n')
        kmz = zipfile.ZipFile( filename, 'w', 0, False)
        for plot in plots:
            p = mean_flow_point(plot, self.start, self.end, self.ignoresuspect)
            if timeseries:
                image = plot + '.png'
                if p.create_time_series_image(image) != None:
                    kmz.write(image)
                    os.remove(image)
            else:
                image = ''
            kml = p.create_kml(image)
            fout.write(kml)
        fout.write('</Document>\n')
        fout.close()
        kmz.write(kmlfile)
        kmz.close()
        os.remove(kmlfile)
        return filename     


