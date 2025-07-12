import pandas as pd

from dotenv import load_dotenv
import os
from supabase import create_client

# ==== CONFIGURACIÓN Y CARGA ====
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

CSV_URL = "https://datosabiertos.gob.ec/dataset/6bc34498-caaa-4eb9-b75e-322347cb0e85/resource/3d30ad84-965a-45fc-a2b0-1d940ec4f748/download/mag_preciosproductor_2025mayo.csv"
CSV_LOCAL = "datos.csv"

# ==== FUNCIONES ====

def fetch_csv_data():
    print("🔄 Descargando CSV...")
    df = pd.read_csv(CSV_URL, delimiter=";")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    print("✅ Datos cargados:", df.shape)
    print("Columnas del DataFrame:", df.columns.tolist())
    return df

def guardar_csv_local(df):
    df.to_csv(CSV_LOCAL, index=False, encoding='utf-8')
    print(f"💾 CSV procesado guardado como '{CSV_LOCAL}'")

def limpiar_dataframe(df):
    df = df.rename(columns={
        'pp_anio': 'anio',
        'pp_mes': 'mes',
        'pp_producto': 'producto',
        'pp_unidad': 'unidad',
        'pp_ponderado_usd': 'usd',
        'pp_ponderado_usd_kg': 'usd_kg'
    })

    # Convertir a numérico y reemplazar errores por NaN
    df['usd'] = pd.to_numeric(df['usd'], errors='coerce')
    df['usd_kg'] = pd.to_numeric(df['usd_kg'], errors='coerce')

    df = df.dropna(subset=['producto', 'anio'])  # eliminar filas con datos clave nulos
    return df

def insertar_productos(df):
    productos_unicos = df[['producto', 'unidad']].drop_duplicates()
    print(f"📦 Insertando {len(productos_unicos)} productos únicos...")

    for _, row in productos_unicos.iterrows():
        nombre, unidad = row['producto'], row['unidad']
        existe = supabase.table("producto").select("id").eq("nombre", nombre).execute()
        
        if not existe.data:
            supabase.table("producto").insert({"nombre": nombre, "unidad": unidad}).execute()

def insertar_precios(df):
    print(f"💰 Insertando {len(df)} registros en 'precio_productor'...")
    errores = []
    
    for idx, row in df.iterrows():
        resp = supabase.table("producto").select("id").eq("nombre", row['producto']).execute()
        if resp.data:
            producto_id = resp.data[0]['id']
            data = {
                "anio": int(row['anio']),
                "mes": row['mes'],
                "producto_id": producto_id,
                "ponderado_usd": row['usd'] if pd.notnull(row['usd']) else None,
                "ponderado_usd_kg": row['usd_kg'] if pd.notnull(row['usd_kg']) else None,
            }
            try:
                supabase.table("precio_productor").insert(data).execute()
            except Exception as e:
                errores.append((idx, str(e)))
    
    print(f"✅ Inserción completada con {len(errores)} errores.")
    if errores:
        print("⚠️ Errores en las filas:")
        for i, err in errores[:5]:
            print(f"Fila {i}: {err}")

# ==== EJECUCIÓN ====

df = fetch_csv_data()
df = limpiar_dataframe(df)
guardar_csv_local(df)

input("\n🟡 Revisa los datos procesados en 'datos.csv'. Presiona Enter para insertar en la base de datos...")

insertar_productos(df)
insertar_precios(df)
