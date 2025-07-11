import pandas as pd
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# 1️⃣ Cargar variables del .env
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

CSV_URL = "https://datosabiertos.gob.ec/dataset/6bc34498-caaa-4eb9-b75e-322347cb0e85/resource/3d30ad84-965a-45fc-a2b0-1d940ec4f748/download/mag_preciosproductor_2025mayo.csv"

# 2️⃣ Descargar el CSV
def fetch_csv_data():
    print("🔄 Descargando CSV...")
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    print("✅ Datos cargados:", df.shape)
    return df

# 3️⃣ Procesar y limpiar
def process_data(df):
    df = df.dropna(subset=['pp_anio', 'pp_mes', 'pp_producto', 'pp_unidad', 'pp_ponderado_usd'])

    df['pp_ponderado_usd'] = pd.to_numeric(df['pp_ponderado_usd'], errors='coerce')
    df['pp_ponderado_usd_kg'] = pd.to_numeric(df['pp_ponderado_usd_kg'], errors='coerce')

    productos = df[['pp_producto', 'pp_unidad']].drop_duplicates().reset_index(drop=True)
    precios = df[['pp_anio', 'pp_mes', 'pp_producto', 'pp_ponderado_usd', 'pp_ponderado_usd_kg']]

    return productos, precios

# 4️⃣ Insertar a la DB
def load_to_db(products, prices, usuario_simulado="backend_script"):
    print("🔄 Conectando a la base de datos...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # Insertar productos
        for _, row in products.iterrows():
            call_stored_procedure(
                cursor,
                "insertar_producto",
                (row['pp_producto'], row['pp_unidad'], usuario_simulado)
            )

        # Insertar precios
        for _, row in prices.iterrows():
            call_stored_procedure(
                cursor,
                "insertar_precio_productor",
                (
                    row['pp_anio'],
                    row['pp_mes'],
                    row['pp_producto'],
                    row['pp_ponderado_usd'],
                    row['pp_ponderado_usd_kg'],
                    usuario_simulado
                )
            )

        conn.commit()
        print("✅ Datos insertados con éxito")
    except Exception as e:
        conn.rollback()
        print("❌ Error:", e)
    finally:
        cursor.close()
        conn.close()

# 5️⃣ Llamar al procedimiento almacenado
def call_stored_procedure(cursor, proc_name, params):
    query = sql.SQL("CALL {}({})").format(
        sql.Identifier(proc_name),
        sql.SQL(', ').join(sql.Placeholder() * len(params))
    )
    cursor.execute(query, params)

# 6️⃣ MAIN
def main():
    df = fetch_csv_data()
    products, prices = process_data(df)
    load_to_db(products, prices)

if __name__ == "__main__":
    main()