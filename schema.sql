CREATE TABLE Vector (
	ID integer PRIMARY KEY AUTOINCREMENT,
	RSSI1 decimal not null,
	RSSI2 decimal not null,
	RSSI3 decimal not null
);
CREATE TABLE Fingerprint (
	ID integer PRIMARY KEY AUTOINCREMENT,
    Vector_ID integer not null,
    X decimal not null,
	Y decimal not null,
	Z decimal not null,
	foreign key(Vector_ID) references Vector(ID)
);
CREATE TABLE AP (
	ID integer PRIMARY KEY,
	X decimal not null,
	Y decimal not null,
	Z decimal not null
);

.save fp.db
