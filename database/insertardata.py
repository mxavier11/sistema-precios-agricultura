import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os


CSV_URL = "https://datosabiertos.gob.ec/dataset/6bc34498-caaa-4eb9-b75e-322347cb0e85/resource/3d30ad84-965a-45fc-a2b0-1d940ec4f748/download/mag_preciosproductor_2025mayo.csv"
CSV_LOCAL = "datos.csv" #el nombre para descargar el dataset limopio


#SELECT setval('public.producto_id_seq', 1,true);
#select setval('precio_productor_id_seq',1,true);


# Cargar variables de entorno
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----Leer CSV------


DESCARGAR_API = True #esto es para que ya no vuelva a descargar desde api si esta localmente, al principio es true


if DESCARGAR_API:

    print("🔄 Descargando CSV...")
    df = pd.read_csv(CSV_URL, delimiter=";")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    print("✅ Datos cargados:", df.shape)
    print("Columnas del DataFrame:", df.columns.tolist())
# renombramos 
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

# aqui le estoy guardando localmente, pero medio xd porque luego le vuelvo a cargar, esto solo es para que pueda visualizar, solo sirve la primera vez, luego mejor desactivar el descargaer desde api
    df.to_csv(CSV_LOCAL, index=False, encoding='utf-8')
    print(f"💾 CSV procesado guardado como '{CSV_LOCAL}'")


df = pd.read_csv("datos.csv")
df['producto'] = df['producto'].str.strip()


print(f"[+] Registros listos para insertar: {df.shape}")
df = df.drop_duplicates(subset=['anio', 'mes', 'producto'], keep='first')
print(f"[+] Registros listos para insertar: {df.shape}")


#En esta seccion inserto los productos

df2 = df.copy()
df2 = df2.drop('anio', axis=1)
df2 = df2.drop('mes', axis=1)
df2 = df2.drop('usd', axis=1)
df2 = df2.drop('usd_kg', axis=1)

df2 = df2.drop_duplicates(subset=['producto'])
df2 = df2.rename(columns={'producto':'nombre'})

print("forma es" , df2.shape)

batchproductos = df2.to_dict(orient='records')

supabase.table('producto').insert(batchproductos).execute()

# Obtener productos existentes
producto_resp = supabase.table("producto").select("id,nombre").execute()
producto_data = producto_resp.data
producto_map = {p['nombre']: p['id'] for p in producto_data}






# Preparar registros
registros = []
nuevos_productos = {}
for i, row in df.iterrows():
    nombre_producto = row['producto']
    
    # Si no existe, agregarlo
    if nombre_producto not in producto_map:
        nuevos_productos[nombre_producto] = row['unidad']

    # Guardamos los datos igual, asignando el producto_id más adelante

    


    registros.append({
        "anio": int(row['anio']),
        "mes": row['mes'],
        "producto_nombre": nombre_producto,  # temporal
        "unidad": row['unidad'],            # para crear si no existe
        "ponderado_usd": float(row['usd']),
        "ponderado_usd_kg": float(row['usd_kg'])
    })

# Insertar nuevos productos en batch
if nuevos_productos:
    print(f"[+] Insertando {len(nuevos_productos)} productos nuevos...")
    nuevos = [{"nombre": nombre, "unidad": unidad} for nombre, unidad in nuevos_productos.items()]
    inserted = supabase.table("producto").insert(nuevos).execute().data
    for p in inserted:
        producto_map[p['nombre']] = p['id']
    print("[✔] Nuevos productos insertados")

# Asignar IDs y limpiar registros para inserción
datos_finales = []
for r in registros:
    nombre = r["producto_nombre"]
    producto_id = producto_map.get(nombre)
    if producto_id is None:
        print(f"[!] No se pudo asignar ID para: {nombre}")
        continue


    if pd.isna(r["ponderado_usd"]):
        print(f"SE ACABO TODO SEÑORES {r}")
        continue
    
    if pd.isna(r["ponderado_usd_kg"]):
        r["ponderado_usd_kg"] = 0
        print(f"[!] Saltando fila con NaN: {r}")
        

    datos_finales.append({
        "anio": r["anio"],
        "mes": r["mes"],
        "producto_id": producto_id,
        "ponderado_usd": float(r["ponderado_usd"]),
        "ponderado_usd_kg": float(r["ponderado_usd_kg"])
    })

print(f"[+] Registros listos para insertar: {len(datos_finales)}")
input("... presiona enter para continuar")
# Insertar en batches
batch_size = 100
total = len(datos_finales)
for i in range(0, total, batch_size):
    batch = datos_finales[i:i+batch_size]
    supabase.table("precio_productor").insert(batch).execute()
    print(f"[✔] Insertados {i + len(batch)} / {total}")
