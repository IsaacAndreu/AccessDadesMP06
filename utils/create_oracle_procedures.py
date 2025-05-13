from extensions import db


def crear_procediments_oracle():
    sql_procediments = [
        # Sequence GRUPS
        "BEGIN EXECUTE IMMEDIATE 'CREATE SEQUENCE grups_seq START WITH 1 INCREMENT BY 1'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -955 THEN RAISE; END IF; END;",

        # Trigger GRUPS (no utilitzem :NEW com a placeholder!)
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
        EXCEPTION WHEN OTHERS THEN
          NULL;
        END;
        """,

        # Sequence CICLES
        "BEGIN EXECUTE IMMEDIATE 'CREATE SEQUENCE cicles_seq START WITH 1 INCREMENT BY 1'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -955 THEN RAISE; END IF; END;",

        # Trigger CICLES
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
        EXCEPTION WHEN OTHERS THEN
          NULL;
        END;
        """
    ]

    with db.engine.begin() as conn:
        for sql in sql_procediments:
            conn.connection.cursor().execute(sql)
