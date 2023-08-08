class Pheromone:
    """
    Assuming:
    - start intensity = 1
    - tick = 1s 
    """

    def __init__(self):
        self.__intensity = 1                # intensity of the pheromone (1 when released)
        self.__center_x = None              # X coord. of the matrix where it will be released
        self.__center_y = None              # Y coord. of the matrix where it will be released
        self.__radius_top = 1               # top radius indicating where intensity(r, k) = intensity(0, k)
        self.__radius_down = 1              # down radius indicating where intensity decreases gradually between top radius and down radius, and drops to 0 after down radius
        self.__deltaEvaporate = None        # delta(r) = evapRate * intensity(r,0)
        self.__evapRate = 0.1               # rate for the evaporation: in 10 sec the pheromone vanishes (because intensity(0, 0) = 1 -> intensity(0, 10) = 0)
        self.__olfactory_habituation = 5    # 5sec

    def tick(self) -> bool:
        """
        Updates intensity value as time goes by.
        Called by `Stigmergy` parent class.
        
        Returns: 
        - True if Pheromone is still active
        - False if Pheromone has reached 0 `intensity` value
        """
        self.__deltaEvaporate = self.__evapRate * 1
        self.__intensity -= self.__deltaEvaporate
        return self.__intensity > 0
    
    @property
    def get_intensity(self) -> float:
        return self.__intensity