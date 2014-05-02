-- Database Creation Queries

-- Entities
-- Table 1:  Course Schedule
CREATE TABLE `course_schedule` (
	id int(11) NOT NULL AUTO_INCREMENT,
	department varchar(4) NOT NULL,
	course_id int(11) NOT NULL,
	section_id int(11) NOT NULL,
	instructor varchar(40) NOT NULL,
	Monday boolean default 0,
	Tuesday boolean default 0,
	Wednesday boolean default 0,
	Thursday boolean default 0,
	Friday boolean default 0,
	TBA boolean default 0,
	start_time time default '00:00:00',
	end_time time default '00:00:00',
	PRIMARY KEY (id),
	UNIQUE KEY (department, course_id, section_id)
) ENGINE = InnoDB;

CREATE INDEX `department_tla_schedule` on `course_schedule` (department);

CREATE TABLE `departments` (
	id int(11) NOT NULL AUTO_INCREMENT,
	department varchar(40) NOT NULL,
	department_tla varchar(4) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY (department_tla),
	CONSTRAINT ScheduleTLA FOREIGN KEY (department_tla) REFERENCES course_schedule (department) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE INDEX `instructor_name_schedule` on `course_schedule` (instructor);

CREATE TABLE `instructors` (
	id int(11) NOT NULL AUTO_INCREMENT,
	name_schedule varchar(40) NOT NULL UNIQUE,
	first_name varchar(40),
	middle_name varchar(40),
	last_name varchar(40),
	onid_username varchar(40),
	PRIMARY KEY (id),
	UNIQUE KEY (onid_username),
	CONSTRAINT ScheduleName FOREIGN KEY (name_schedule) REFERENCES course_schedule (instructor) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

--Test
--INSERT INTO course_schedule (
--	department,	course_id, section_id, instructor, TBA)
--	VALUES ('ZZZ', 999, 000, 'Test, Name', 1);
