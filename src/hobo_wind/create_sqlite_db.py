import sqlite3
def create_tables(dbfile):
        '''
        Create a new database and tables for mean flow.  Two tables are created,
        one for plot locations, another for the measured data.  These are made
        under the assumption of similar set up for big butte.
        '''
        db = sqlite3.connect(dbfile)
        curs = db.cursor()
        sql = '''CREATE TABLE plot_location(plot_id       TEXT     NOT NULL,
                                            datalogger_id TEXT,
                                            geometry      TEXT,
                                            constraint plt_loc_pk
                                            primary key(plot_id))'''
        curs.execute(sql)
        sql = ''' create table mean_flow_obs(plot_id       text     not null,
                                             date_time     datetime not null,
                                             wind_speed    double,
                                             wind_gust     double,
                                             wind_dir      double,
                                             quality       text,
                                             sensor_qual   text,
                                             constraint mean_obs_pk
                                             primary key(plot_id,date_time))'''                                    
        curs.execute(sql)
        db.commit()
        db.close()


create_tables('birch.db')
