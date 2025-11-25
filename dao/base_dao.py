# dao/base_dao.py

class BaseDAO:
    # PRODUCTOS 
    def get_all_products(self):
        raise NotImplementedError

    def get_product_by_id(self, producto_id: int):
        raise NotImplementedError

    def create_product(self, nombre: str, precio: float, imagen: str):
        raise NotImplementedError

    def update_product(self, producto_id: int, nombre: str, precio: float, imagen: str):
        raise NotImplementedError

    def delete_product(self, producto_id: int):
        raise NotImplementedError

    # USUARIOS 
    def get_user_by_email(self, email: str):
        raise NotImplementedError

    def get_user_by_id(self, user_id: int):
        raise NotImplementedError

    #  ORDENES
    def create_order(self, usuario_id: int, total: float):
        raise NotImplementedError

    def add_order_detail(self, orden_id: int, producto_id: int,
                         cantidad: int, precio_unitario: float):
        raise NotImplementedError

    def get_all_orders(self):
        raise NotImplementedError

    def get_order_details(self, orden_id: int):
        raise NotImplementedError
