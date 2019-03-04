CREATE TABLE odds (
	country character varying(20),
    season character varying(50),
    date date,
    home_team character varying(40),
    guest_team character varying(40),
    score character varying(10),
    home_score integer,
    guest_score integer,
    odds_1 real,
    odds_x real,
    odds_2 real,
    ftr character varying(5),
    explore_id character varying(150)
);