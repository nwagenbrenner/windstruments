require(ggplot2)

#function to pad the time variable with 0's
padDt<-function(x){
    if( nchar(as.character(x)) == 1)
    {
        x<-paste0('000',x)
    }
    else if( nchar(as.character(x)) == 2)
    {
        x<-paste0('00',x)
    }
    else if( nchar(as.character(x)) == 3)
    {
        x<-paste0('0',x)
    }
    return(x)
}

#function to pad the day/month variables with 0's
padDayMonth<-function(x){
    if( nchar(as.character(x)) == 1)
    {
        x<-paste0('0',x)
    }
    return(x)
}

#read in mesonet data
#5-min data
setwd('/home/natalie/src/wind_obs/trunk/data/bsb/mesonet/Mesonet')
d<-read.table('JUL2010.CSV', header=FALSE, skip=1, sep=",")

#first four variables are year, month, day, and hhmm
dt<-d[,1:4]
colnames(dt)<-c('year','month','day','hhmm')

#pad time variable with 0's
dt$hhmm<-mapply(padDt,dt$hhmm)
dt$month<-mapply(padDayMonth,dt$month)
dt$day<-mapply(padDayMonth,dt$day)

time_string<-paste0(dt$year,"-",dt$month,"-",dt$day," ",dt$hhmm)
t<-as.POSIXct(strptime(time_string, '%Y-%m-%d %H%M'), "MST")


#SUM data is 651-666 (see Mesonet_readme.txt)
sum<-d[,651:666]
big<-d[,107:122]
los<-d[,409:428]

colnames(sum)<-c('mean_dir_6m','mean_dir_6m_flag','stddev_dir_6m',
'stddev_dir_6m_flag','mean_speed_6m','mean_speed_6m_flag',
'peak_speed_6m','peak_speed_6m_flag','mean_temp_2m',
'mean_temp_2m_flag','mean_rh_2m','mean_rh_2m_flag',
'mean_solar_rad','mean_solar_rad_flag','mean_pressure',
'mean_pressure_flag')

colnames(big)<-c('mean_dir_6m','mean_dir_6m_flag','stddev_dir_6m',
'stddev_dir_6m_flag','mean_speed_6m','mean_speed_6m_flag',
'peak_speed_6m','peak_speed_6m_flag','mean_temp_2m',
'mean_temp_2m_flag','mean_rh_2m','mean_rh_2m_flag',
'mean_solar_rad','mean_solar_rad_flag','mean_pressure',
'mean_pressure_flag')

colnames(los)<-c('mean_dir_15m','mean_dir_15m_flag','stddev_dir_15m',
'stddev_dir_15m_flag','mean_speed_15m','mean_speed_15m_flag',
'peak_speed_15m','peak_speed_15m_flag','mean_temp_2m',
'mean_temp_2m_flag','mean_temp_15m','mean_temp_15m_flag','mean_rh_2m','mean_rh_2m_flag',
'mean_solar_rad','mean_solar_rad_flag','mean_pressure',
'mean_pressure_flag','total_precip_inches','total_precip_flag')

#combine data and time
sum<-cbind(t,sum)
big<-cbind(t,big)
los<-cbind(t,los)

#subset on 5-day period
t1<-as.POSIXct(strptime("2010-07-15 0000", '%Y-%m-%d %H%M'), "MST")
t2<-as.POSIXct(strptime("2010-07-19 2300", '%Y-%m-%d %H%M'), "MST")
s <- subset(sum, subset=(t<t2 & t>t1))

p<-ggplot(sum, aes(x=t, y=mean_speed_6m)) +
    geom_point(shape=19, size=1.5, alpha = 1.0, colour='black') +
    xlab("Time") + ylab("Speed")











