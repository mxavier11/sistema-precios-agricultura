import socket
import psycopg2

# Resolver manualmente la IP IPv4 del host
host = "db.hfcqmsxlbowncljhdqiy.supabase.co"
ipv4 = socket.gethostbyname(host)  # Esto fuerza IPv4
print("🟢 IP IPv4 resuelta:", ipv4)

conn_info = {
    "host": ipv4,
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin"
}

try:
    print("🔌 Intentando conectar con IPv4...")
    conn = psycopg2.connect(**conn_info)
    print("✅ Conexión exitosa")
    conn.close()
except Exception as e:
    print("❌ Error de conexión:", e)