import cx_Oracle
from extensions import oracle_connection  # assegura’t que tens aquesta connexió definida

def inserir_grup_oracle(nom):
    with oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc("inserir_grup", [nom])
        conn.commit()

def inserir_cicle_oracle(nom):
    with oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc("inserir_cicle", [nom])
        conn.commit()
