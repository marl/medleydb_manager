CREATE TABLE tickets
  (ticket_number varchar(20) PRIMARY KEY,
  status varchar(20),
  ticket_name varchar(20),
  date_opened datetime,
  date_updated datetime,
  number_of_tracks varchar(20),
  genre varchar(20),
  session_date date,
  creator_name varchar(20),
  creator_email varchar(20),
  engineer_name varchar(20),
  engineer_email varchar(20),
  assignee_name varchar(20),
  assignee_email varchar(20),
  mixer_name varchar(20),
  mixer_email varchar(20),
  bouncer_name varchar(20),
  bouncer_email varchar(20),
  comments varchar(100));


CREATE TABLE ticket_history
( ticket_number varchar(20),
  ticket_revision_id varchar(20) PRIMARY KEY,
  status varchar(20),
  ticket_name varchar(20),
  date_opened datetime,
  date_updated datetime,
  number_of_tracks varchar(20),
  genre varchar(20),
  session_date datetime,
  creator_name varchar(20),
  creator_email varchar(20),
  engineer_name varchar(20),
  engineer_email varchar(20),
  assignee_name varchar(20),
  assignee_email varchar(20),
  mixer_name varchar(20),
  mixer_email varchar(20),
  bouncer_name varchar(20),
  bouncer_email varchar(20),
  comments varchar(100));


CREATE TABLE multitracks
( ticket_number varchar(20),
  multitrack_id varchar(20) PRIMARY KEY,
  date_added datetime,
  title varchar(20),
  artist varchar(20),
  genre varchar(20),
  start_time time,
  end_time time,
  number_of_instruments varchar(20)
);
