from backend.db.connection import supabase

def testar_conexao():
    usuarios = supabase.table("PBL - usuarios").select("*").limit(1).execute()
    print("Conexão bem-sucedida!")
    print(usuarios.data)

if __name__ == "__main__":
    testar_conexao()
