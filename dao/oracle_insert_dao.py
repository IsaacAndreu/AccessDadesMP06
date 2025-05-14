import cx_Oracle
from extensions import oracle_connection

# Afegeix un nou grup utilitzant un procediment PL/SQL
def inserir_grup_oracle(nom):
    nom = nom.strip()
    with oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc("inserir_grup", [nom])
        conn.commit()

# Afegeix un nou cicle utilitzant un procediment PL/SQL
def inserir_cicle_oracle(nom):
    nom = nom.strip()
    with oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc("inserir_cicle", [nom])
        conn.commit()
