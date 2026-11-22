CREATE TABLE anzsrc (
	-- the code padded with zeros to six digits, as journal_for.discipline is, so the two join directly:
	-- a division such as 08 is 080000, and a group such as 0801 is 080100
	code char(6) not null,
	-- as the ABS publishes it, so ANZSRC 2020 has its division names in capitals
	name nvarchar2(200) not null,
	-- the division a group is in, or the group a field or objective is in; null for a division
	parent char(6),
	CONSTRAINT anzsrc_pk PRIMARY KEY (code),
	CONSTRAINT anzsrc_fk FOREIGN KEY (parent) REFERENCES anzsrc (code)
);
