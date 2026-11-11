-- SPM-420 monitoring database (PostgreSQL 14+).
-- Generated from SOFTWARE/BACKEND/app/models.py - the application also creates these tables at start-up.
-- psql -U spm -d spm -f schema.sql

CREATE TABLE batches (
	id SERIAL NOT NULL, 
	batch_no VARCHAR(40) NOT NULL, 
	product VARCHAR(60) NOT NULL, 
	target_weight_g FLOAT NOT NULL, 
	planned_bags INTEGER NOT NULL, 
	film_lot VARCHAR(40) NOT NULL, 
	operator VARCHAR(40) NOT NULL, 
	started_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	closed_at TIMESTAMP WITH TIME ZONE, 
	bags_at_start INTEGER NOT NULL, 
	bags_at_close INTEGER, 
	notes TEXT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (batch_no)
);

CREATE TABLE maintenance_tasks (
	id SERIAL NOT NULL, 
	name VARCHAR(80) NOT NULL, 
	interval_cycles INTEGER, 
	interval_days INTEGER, 
	instructions TEXT NOT NULL, 
	active BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE TABLE alarm_events (
	id SERIAL NOT NULL, 
	alarm_id INTEGER NOT NULL, 
	alarm_class VARCHAR(1) NOT NULL, 
	text VARCHAR(120) NOT NULL, 
	raised_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	cleared_at TIMESTAMP WITH TIME ZONE, 
	batch_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(batch_id) REFERENCES batches (id)
);

CREATE INDEX ix_alarm_open ON alarm_events (alarm_id, cleared_at);

CREATE INDEX ix_alarm_events_raised_at ON alarm_events (raised_at);

CREATE INDEX ix_alarm_events_alarm_id ON alarm_events (alarm_id);

CREATE TABLE maintenance_records (
	id SERIAL NOT NULL, 
	task_id INTEGER, 
	done_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	done_by VARCHAR(40) NOT NULL, 
	bags_total_at INTEGER NOT NULL, 
	kind VARCHAR(20) NOT NULL, 
	description TEXT NOT NULL, 
	downtime_min FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(task_id) REFERENCES maintenance_tasks (id)
);

CREATE TABLE samples (
	id SERIAL NOT NULL, 
	ts TIMESTAMP WITH TIME ZONE NOT NULL, 
	state INTEGER NOT NULL, 
	mode INTEGER NOT NULL, 
	speed_bpm FLOAT NOT NULL, 
	bags_total INTEGER NOT NULL, 
	empty_cycles INTEGER NOT NULL, 
	temp_z1 FLOAT NOT NULL, 
	temp_z2 FLOAT NOT NULL, 
	temp_z3 FLOAT NOT NULL, 
	recipe VARCHAR(32) NOT NULL, 
	batch_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(batch_id) REFERENCES batches (id)
);

CREATE INDEX ix_samples_ts ON samples (ts);

-- convenience views for reports
CREATE VIEW v_batch_summary AS
SELECT b.id, b.batch_no, b.product, b.target_weight_g, b.started_at, b.closed_at,
       COALESCE(b.bags_at_close, b.bags_at_start) - b.bags_at_start AS bags,
       (COALESCE(b.bags_at_close, b.bags_at_start) - b.bags_at_start) * b.target_weight_g / 1000.0 AS nominal_kg,
       (SELECT count(*) FROM alarm_events a WHERE a.batch_id = b.id AND a.alarm_class IN ('A','B')) AS stops
FROM batches b;

CREATE VIEW v_alarm_pareto_30d AS
SELECT alarm_id, max(text) AS text, count(*) AS occurrences,
       round(sum(extract(epoch FROM COALESCE(cleared_at, now()) - raised_at)) / 60.0, 1) AS minutes
FROM alarm_events WHERE raised_at > now() - interval '30 days'
GROUP BY alarm_id ORDER BY minutes DESC;

-- retention: samples older than 400 days can be dropped by a scheduled job
-- DELETE FROM samples WHERE ts < now() - interval '400 days';
