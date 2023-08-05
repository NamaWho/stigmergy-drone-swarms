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
        self.__deltaEvaporate = 0.1         # delta value for the evaporation: in 10 sec the pheromone vanishes (because intensity(0, 0) = 1 -> intensity(0, 10) = 0)
        self.__evapRate = None              # 
        self.__olfactory_habituation = 5    # 5sec

    def tick(self) -> bool:
        """
        Updates intensity value as time goes by.
        Called by Stigmergy parent class.
        
        Returns: 
        - True if Pheromone is still active
        - False if Pheromone has reached 0 `intensity` value
        """
        self.__intensity -= self.__deltaEvaporate
        return self.__intensity > 0