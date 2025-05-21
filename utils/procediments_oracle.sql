CREATE SEQUENCE grups_seq START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE PROCEDURE inserir_grup(p_nom IN VARCHAR2) AS
BEGIN
  INSERT INTO grups_oracle (id, nom)
  VALUES (grups_seq.NEXTVAL, p_nom);
END;
/

CREATE SEQUENCE cicles_seq START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE PROCEDURE inserir_cicle(p_nom IN VARCHAR2) AS
BEGIN
  INSERT INTO cicles_oracle (id, nom)
  VALUES (cicles_seq.NEXTVAL, p_nom);
END;
/
