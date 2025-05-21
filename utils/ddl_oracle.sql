CREATE TABLE grups_oracle (
  id   INTEGER PRIMARY KEY,
  nom  VARCHAR2(50) NOT NULL
);

CREATE TABLE cicles_oracle (
  id          INTEGER PRIMARY KEY,
  nom         VARCHAR2(100) NOT NULL,
  descripcio  VARCHAR2(200)
);

CREATE TABLE assignatures_oracle (
  id         INTEGER PRIMARY KEY,
  nom        VARCHAR2(100) NOT NULL,
  cicle_id   INTEGER NOT NULL REFERENCES cicles_oracle(id)
);

CREATE TABLE alumnes_oracle (
  id         INTEGER PRIMARY KEY,
  nom        VARCHAR2(50) NOT NULL,
  cognoms    VARCHAR2(100) NOT NULL,
  email      VARCHAR2(100),
  grup_id    INTEGER REFERENCES grups_oracle(id),
  cicle_id   INTEGER REFERENCES cicles_oracle(id),
  curs       VARCHAR2(10)
);
