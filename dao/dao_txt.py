# dao/dao_txt.py
import json
from dao.base_dao import BaseDAO

class TXTDAO(BaseDAO):

    def __init__(self, file_path):
        self.file = file_path

    def _read(self):
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def _write(self, data):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def get_all_products(self):
        return self._read()

    def get_product_by_id(self, producto_id):
        productos = self._read()
        for p in productos:
            if p["id"] == producto_id:
                return p
        return None

    def add_product(self, nombre, precio, imagen):
        productos = self._read()
        new_id = max([p["id"] for p in productos], default=0) + 1

        productos.append({
            "id": new_id,
            "nombre": nombre,
            "precio": precio,
            "imagen": imagen
        })

        self._write(productos)
        return new_id
