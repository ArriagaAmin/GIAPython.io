from uuid import UUID
from typing import List, Tuple, Dict
from src.GameObject import GameObject

class CollisionHandler:
    """
        Se encarga de manejar las colisiones entre los objetos del juego.
    """
    def __init__(self):
        self.objects = {}
        self.tiles : Dict[Tuple[int, int], Dict[UUID, GameObject]]= {}

    def add(self, obj: GameObject):
        """
            Agrega un objeto a las casillas correspondientes
        """
        # Verificamos cuantas casillas ocupa el objeto
        tiles = obj.tiles()

        # Agregamos referencias tile -> object
        for tile in tiles: 
            if tile in self.tiles:
                self.tiles[tile][obj.id] = obj
            else:
                self.tiles[tile] = {obj.id: obj}

        # Agregamos la referencia object -> tiles
        self.objects[obj.id] = tiles

    def delete(self, obj: GameObject):
        """
            Elimina un objeto
        """
        # Si no esta en el manejador, no se hace nada
        if obj.id not in self.objects: 
            print('?')
            return 
        
        for tile in self.objects[obj.id]:
            self.tiles[tile].pop(obj.id)

        # Verificamos si el tile queda vacio:
        if len(self.tiles[tile]) == 0:
            self.tiles.pop(tile)

        self.objects.pop(obj.id)

    def collision_with(self, obj: GameObject, obj_class: str) -> List[GameObject]:
        """
            Verificamos cuales son los objetos de una determinada clase con los 
            que choca un objeto especificado
        """
        tiles = obj.tiles()

        # Obtenemos los objetos de la clase especificada que se encuentran en
        # las mismas casillas que el objeto
        target_obj = set()
        for tile in tiles:
            if tile in self.tiles:
                for obj_id in self.tiles[tile]:
                    obj_t = self.tiles[tile][obj_id]
                    if obj_t.NAME == obj_class:
                        target_obj.add(obj_t)

        # Retornamos aquellos objetos que verdaderamente colisionan
        return [obj_t for obj_t in target_obj if obj.collision(obj_t)]


