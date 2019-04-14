CREATE DATABASE IF NOT EXISTS pynet_db;
USE pynet_db;
CREATE TABLE IF NOT EXISTS device_data (
    device_id INT NOT NULL,
    time_stamp INT NOT NULL,
    chan_0 FLOAT,
    chan_1 FLOAT,
    chan_2 FLOAT,
    chan_3 FLOAT
)  ENGINE=INNODB;