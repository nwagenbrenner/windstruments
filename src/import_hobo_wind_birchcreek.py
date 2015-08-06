import os, sqlite3, datetime, logging

def import_hobo(dbfile, path):
    '''
    Import csv files from hobo wind sensors.  Import all records in all csv
    files in the path provided.  Tailored to hobo loggers.
    '''
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
    cursor.execute('PRAGMA journal_mode=off')
    cursor.fetchone()
    csv_files = [csv for csv in os.listdir(path) if os.path.splitext(csv)[1] == '.csv']
    csv_files = [os.path.join(path, csv) for csv in csv_files]
    if not csv_files:
        logging.error('No csv files in directory')
        return None
    for csv in csv_files:
        fin = open(csv)
        plot = os.path.splitext(os.path.basename(csv))[0].upper()
        #cursor.execute('INSERT INTO plot_location(plot_id) VALUES(?)',
        #                    (plot,))
        #header = 0
        for i, line in enumerate(fin):
            #if header < 2:
                #header += 1
                #continue
            line = line.split(',')
            if len(line) != 5:
			    pass
                    #logging.error('Could not parse csv file properly, not'
                    #              'enough records.  Check file: %s' % csv)
                    #continue
            plot_id = line[0]
            date = datetime.datetime.strptime(line[1], '%m/%d/%Y %H:%M')
            date.replace(second=0)

            spd = float(line[2])
            gust = float(line[3])
            dir = float(line[4])
            quality = 'OK'
            if spd < 0.0:
                logging.error('Invalid speed (%f) for plot:%s' % (spd, plot))
                quality = 'SUSPECT'
            if gust < 0.0:
                logging.error('Invalid gust (%f) for plot:%s' % (gust, plot))
                quality = 'SUSPECT'
            if dir < 0.0 or dir > 360.0:
                logging.error('Invalid dir (%f) for plot:%s' % (dir, plot))
                quality = 'SUSPECT'
            try:
                cursor.execute('''INSERT INTO mean_flow_obs(plot_id,
                   		          date_time, wind_speed, wind_gust,
                           		  wind_dir, quality)
                          	  	VALUES(?, ?, ?, ?, ?, ?)''',
                               	(plot, date, spd, gust, dir, quality))
            except:
			    try:
				    cursor.execute('''INSERT INTO mean_flow_obs(plot_id,
                        	          date_time, wind_speed, wind_gust,
                               		  wind_dir, quality)
                              	  	VALUES(?, ?, ?, ?, ?, ?)''',
                                    	(plot, date.replace(second=30), spd, gust, dir, quality))
			    except:
				    print(plot, date, spd, gust, dir, quality)
				    print(csv, line, i)
            db.commit()

#path_to_csv = '/home/natalie/birch_creek/data/'
#dbfile = 'birch.sqlite'
#import_hobo(dbfile, path_to_csv)


