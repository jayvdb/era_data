CREATE TABLE conference (
	eraid integer not null,
	title nvarchar2(500) not null,
	acronym nvarchar2(50),
	rank char(1) check (rank in ('A', 'B', 'C')),
	multidisciplinary_ind char(1) default 'N' check (multidisciplinary_ind in ('Y', 'N')),
	CONSTRAINT conference_pk PRIMARY KEY (eraid)
);

CREATE TABLE conference_for (
	eraid integer not null,
	-- a discipline of two or four digits, padded to six like those of journal_for
	discipline char(6) not null check (SUBSTR(discipline,5,2) = '00'),
	column_id integer not null check (column_id > 0),
	CONSTRAINT conference_for_pk PRIMARY KEY (eraid, discipline),
	CONSTRAINT conference_for_fk FOREIGN KEY (eraid) REFERENCES conference (eraid)
);
