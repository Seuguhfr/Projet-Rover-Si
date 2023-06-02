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
        for moteur in self.moteurs:
            diametre = input(f"MOTEUR {moteur.position}, quel est le diametre (en m)")
            try:
                diametre = float(diametre)
            except ValueError:
                break
            while True:
                input(f"Appuyez sur <Entrer> pour lancer la roue {moteur.position} (attendez 5 tours)")
                ancien_temps = actual_time()
                moteur.regler_vitesse(vitesse_calibrage)
                input("Appuyez sur <Entrer> pour stopper la roue")
                moteur.regler_vitesse(0)
                difference_temps = actual_time() - ancien_temps
                if input("Est-ce bien arrêté ?") == "oui":
                    break
            dutys.append(vitesse_calibrage / (diametre * 5 / difference_temps))
        for index, duty in enumerate(dutys):
            print(f'moteur {index} : {duty}')
        input()

    def calculer_mouvement(self, angle):
        return cos(radians(45 + angle)), sin(radians(45 + angle))
    
    def stop(self):
        for moteur in self.moteurs:
            moteur.regler_vitesse(0)

    def deplacer(self, distance, angle, temps):
        for moteur in self.moteurs:
            mouvement = self.calculer_mouvement(angle)[moteur.position % 2]
            moteur.regler_vitesse(mouvement * distance / temps * moteur.efficacite * moteur.sens)
        sleep(temps)
        self.stop()
    
    def polygone(self, angle_initial, angle_rotation, rayon, temps):
        cote = 2 * rayon * sin(2 * pi * (pi/angle_rotation))
        for angle in range(angle_initial, angle_initial + 360, angle_rotation):
            self.deplacer(cote, angle, temps * angle_rotation / 360)
            sleep(.1)

    def rotation(self, vitesse=1, direction=1):
        for moteur in self.moteurs:
            moteur.regler_vitesse(vitesse * moteur.efficacite * direction * moteur.sens * -1 if moteur.position%3 else 1)
        sleep(1)
        self.stop()

    def go_and_back(self, distance=1, temps=4):
        self.polygone(0, 180, distance, temps)
        
    def carre(self, distance=1, temps=4):
        self.polygone(0, 90, distance, temps)

    def losange(self, distance=1, temps=4):
        self.polygone(-45, 90, distance, temps)

    def cercle(self, vitesse=.1, temps=4):
        for angle in range(360):
            for index, moteur in enumerate(self.moteurs):
                mouvement = self.calculer_mouvement(angle)[index % 2]
                moteur.regler_vitesse(mouvement * vitesse * moteur.efficacite * moteur.sens)
                sleep(temps/360)
        self.stop()
            
class Moteur:
    def __init__(self, pin_vitesse, pin_direction, sens, position, efficacite):
        self.vitesse = PWM(Pin(pin_vitesse, mode=Pin.OUT))
        self.direction = Pin(pin_direction, mode=Pin.OUT)
        self.sens = sens
        self.position = position
        self.efficacite = efficacite
        
    def regler_vitesse(self, vitesse):
        self.vitesse.duty_u16(int(abs(vitesse)))
        self.direction.value(1 if vitesse > 0 else 0)