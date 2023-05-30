try:
    from machine import Pin, PWM, reset_cause
    carte_branche = True
except ModuleNotFoundError:
    from my_machine import Pin, PWM
    carte_branche = False
from time import sleep, time as actual_time
from math import sin, cos, radians, pi

class Rover:
    def __init__(self, *moteurs):
        self.moteurs = list(moteurs)
        self.methodes = {
            "allez-retour": self.go_and_back,
            "flip": self.rotation,
            "carre": self.carre,
            "losange": self.losange,
            "cercle": self.cercle
        }

    def __call__(self):
        return self.moteurs
    
    def calibrage(self):
        dutys = []
        vitesse_calibrage = 2**12
        for index, moteur in enumerate(self.moteurs) :
            moteur.regler_direction(1)
            diametre = float(input(f"MOTEUR {index}, quel est le diametre (en m)"))
            while True:
                input("Appuyez sur <Entrer> pour lancer la roue (attendez 5 tours)")
                ancien_temps = actual_time()
                moteur.regler_vitesse(vitesse_calibrage)
                input("Appuyez sur <Entrer> pour stopper la roue")
                moteur.regler_vitesse(0)
                if input("Est-ce bien arrêté ?") == "oui":
                    break
            dutys.append(vitesse_calibrage / (diametre * 5 / (actual_time() - ancien_temps)))
        for index, value in enumerate(dutys):
            print(f'moteur {index} : {value}')
        input()

    def calculer_mouvement(self, angle):
        """Calcule les deux vecteurs de poussée en fonction de l'angle donné."""
        return cos(radians(45 + angle)), sin(radians(45 + angle))
    
    def stop(self):
        for index, moteur in enumerate(self.moteurs):
            moteur.regler_vitesse(0)

    def deplacer(self, distance, angle, temps):
        """Déplace le rover en fonction de la distance et de l'angle donnés."""
        sens_moteurs = []
        for index, moteur in enumerate(self.moteurs):
            mouvement = self.calculer_mouvement(angle)[index % 2]
            moteur.regler_vitesse(mouvement * distance / temps * moteur.efficacite * moteur.sens)
        sleep(temps)
        self.stop()
    
    def polygone(self, angle_initial, angle_rotation, rayon, temps):
        """Déplace le rover en forme de polygone en fonction des angles et du temps donnés."""
        cote = 2 * rayon * sin(2 * pi * (pi/angle_rotation))
        for angle in range(angle_initial, angle_initial + 360, angle_rotation):
            self.deplacer(cote, angle, temps * angle_rotation / 360)
            sleep(.1)

    def rotation(self, vitesse=1, direction=1):
        for index, moteur in enumerate(self.moteurs):
            moteur.regler_vitesse(vitesse * moteur.efficacite * direction * moteur.sens * -1 if index%3 else 1)
        sleep(1)
        self.stop()

    def go_and_back(self, distance=1, temps=4):
        self.polygone(0, 180, distance, temps)
        
    def carre(self, distance=1, temps=4):
        self.polygone(0, 90, distance, temps)

    def losange(self, distance=1, temps=4):
        self.polygone(-45, 90, distance, temps)

    def cercle(self, vitesse=1, temps=4):
        for angle in range(360):
            for index, moteur in enumerate(self.moteurs):
                mouvement = self.calculer_mouvement(angle)[index % 2]
                moteur.regler_vitesse(mouvement * vitesse * moteur.efficacite * moteur.sens)
                sleep(temps/360)
        self.stop()
            

class Moteur:
    def __init__(self, pin_vitesse, pin_direction, sens, efficacite):
        self.vitesse = PWM(Pin(pin_vitesse, mode=Pin.OUT))
        self.direction = Pin(pin_direction, mode=Pin.OUT)
        self.sens = sens
        self.efficacite = efficacite
        
    def regler_vitesse(self, vitesse):
        self.vitesse.duty_u16(int(abs(vitesse)))
        self.direction.value(1 if vitesse > 0 else 0)

rover = Rover(
    Moteur(14, 15, -1, 2**16),
    Moteur(2, 3, 1, 2**16),
    Moteur(12, 13, 1, 2**16),
    Moteur(16, 17, -1, 2**16)
)

if carte_branche:
    if not reset_cause():
        sleep(3)
        rover.carre()
        sleep(1)
        rover.losange()
        sleep(1)
        rover.rotation(direction=1)
        sleep(1)
        rover.rotation(direction=-1)
        exit()

rover.calibrage()
while True:
    methodes = list(rover.methodes.keys())
    print("\n\nVoici les déplacements que vous pouvez faire :")
    for methode in methodes:
        print(f' - {methode}')
    choix = input("\nQuel déplacement voulez-vous faire ?\n   > ")
    if choix in rover.methodes:
        try:
            rover.methodes[choix]()
        except KeyboardInterrupt:
            rover.stop()
            exit()
    else:
        print("Méthode inconnue. Veuillez choisir une méthode valide.")
sleep(1)