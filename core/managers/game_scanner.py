import os
import json


class GameScanner:
    """Explora la carpeta de juegos y construye un catálogo con sus metadatos."""

    @staticmethod
    def scan_and_load_metadata(base_path: str):
        """
        Escanea el directorio de juegos, detecta proyectos que contienen un main.py
        y convierte su metadata.json en un diccionario listo para mostrar en el menú.
        """
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        catalog = []

        for folder in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder)

            # Un juego se considera válido si existe como carpeta y contiene un archivo main.py.
            if os.path.isdir(folder_path) and "main.py" in os.listdir(folder_path):
                json_path = os.path.join(folder_path, "metadata.json")

                metadata = {
                    "folder": folder,
                    "folder_path": folder_path,
                    "title": folder.replace("_", " "),
                    "description": "No se encontró descripción en metadata.json",
                    "authors": ["Desconocido"],
                    "group_number": "Desconocido",
                    "controls": "No fueron especificados los controles en metadata.json",
                }

                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r", encoding="utf-8") as f:
                            group_data = json.load(f)
                            metadata.update(group_data)
                    except Exception as e:
                        print(f"Error al leer el archivo metadata.json en la carpeta '{folder}': {e}")

                folder_parts = folder.split('_')
                if len(folder_parts) >= 2 and folder_parts[0].capitalize() in ["Lunes", "Jueves"]:
                    metadata["group_number"] = f"{folder_parts[0].capitalize()} {folder_parts[1]}"

                catalog.append(metadata)

        def sort_key(game_meta):
            folder_name = game_meta.get("folder", "")
            parts = folder_name.split("_")
            
            day_val = 2 
            num_val = 999
            
            if len(parts) >= 2:
                day_str = parts[0].capitalize()
                
                if day_str == "Lunes":
                    day_val = 0
                elif day_str == "Jueves":
                    day_val = 1
                
                try:
                    num_val = int(parts[1])
                except ValueError:
                    pass
                    
            return (num_val, day_val)

        catalog.sort(key=sort_key)

        return catalog