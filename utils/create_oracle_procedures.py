from extensions import db

def crear_procediments_oracle():
    """
    Funció per crear seqüències, triggers i procediments PL/SQL a la base de dades
    Oracle per gestionar els IDs de les taules `grups_oracle` i `cicles_oracle`.
    """
    sql_procediments = [
        # Seqüència per a grups
        """
        BEGIN
          EXECUTE IMMEDIATE 'CREATE SEQUENCE grups_seq START WITH 1 INCREMENT BY 1';
        EXCEPTION
          WHEN OTHERS THEN
            IF SQLCODE != -955 THEN
              RAISE;
            END IF;
        END;
        """,

        # Seqüència per a cicles
        """
        BEGIN
          EXECUTE IMMEDIATE 'CREATE SEQUENCE cicles_seq START WITH 1 INCREMENT BY 1';
        EXCEPTION
          WHEN OTHERS THEN
            IF SQLCODE != -955 THEN
              RAISE;
            END IF;
        END;
        """,

        # Trigger per a grups: auto-incrementa `id` abans d’inserir
        """
        BEGIN
          EXECUTE IMMEDIATE q'[
            CREATE OR REPLACE TRIGGER trg_grups_id
            BEFORE INSERT ON grups_oracle
            FOR EACH ROW
            BEGIN
              SELECT grups_seq.NEXTVAL INTO :NEW.id FROM dual;
            END;
          ]';
        EXCEPTION
          WHEN OTHERS THEN
            NULL;
        END;
        """,

        # Trigger per a cicles: auto-incrementa `id` abans d’inserir
        """
        BEGIN
          EXECUTE IMMEDIATE q'[
            CREATE OR REPLACE TRIGGER trg_cicles_id
            BEFORE INSERT ON cicles_oracle
            FOR EACH ROW
            BEGIN
              SELECT cicles_seq.NEXTVAL INTO :NEW.id FROM dual;
            END;
          ]';
        EXCEPTION
          WHEN OTHERS THEN
            NULL;
        END;
        """,

        # Procediment per inserir un grup passant només el nom
        """
        BEGIN
          EXECUTE IMMEDIATE q'[
            CREATE OR REPLACE PROCEDURE inserir_grup(p_nom IN VARCHAR2) AS
            BEGIN
              INSERT INTO grups_oracle (id, nom)
              VALUES (grups_seq.NEXTVAL, p_nom);
            END inserir_grup;
          ]';
        EXCEPTION
          WHEN OTHERS THEN
            NULL;
        END;
        """,

        # Procediment per inserir un cicle passant només el nom
        """
        BEGIN
          EXECUTE IMMEDIATE q'[
            CREATE OR REPLACE PROCEDURE inserir_cicle(p_nom IN VARCHAR2) AS
            BEGIN
              INSERT INTO cicles_oracle (id, nom)
              VALUES (cicles_seq.NEXTVAL, p_nom);
            END inserir_cicle;
          ]';
        EXCEPTION
          WHEN OTHERS THEN
            NULL;
        END;
        """
    ]

    # Executem tots els blocs PL/SQL
    with db.engine.begin() as conn:
        for bloc in sql_procediments:
            # Si prefereixes usar el cursor directament:
            conn.connection.cursor().execute(bloc)
            # També és vàlid fer:
            # conn.execute(bloc)
