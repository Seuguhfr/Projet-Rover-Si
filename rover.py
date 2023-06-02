from machine import Pin, PWM, reset_cause
from time import sleep, time as actual_time
from math import sin, cos, radians, pi

class Rover:
    def __init__(self, *moteurs):
        self.moteurs = list(moteurs)
        self.methodes = {
            'allez-retour': self.go_and_back,
            'flip': self.rotation,
            'carre': self.carre,
            'losange': self.losange,
            'cercle': self.cercle
        }

    def __call__(self):
        return self.moteurs
    
    def calibrage(self):
        dutys: list = []
        vitesse_calibrage: int = 2**12
        for moteur in self.moteurs:
            diametre: str = input(f'MOTEUR {moteur.position}, quel est le diametre (en m)')
            try:
                diametre: float = float(diametre)
            except ValueError:
                break
            while True:
                input(f'Appuyez sur <Entrer> pour lancer la roue {moteur.position} (attendez 5 tours)')
                ancien_temps: float = actual_time()
                moteur.regler_vitesse(vitesse_calibrage)
                input('Appuyez sur <Entrer> pour stopper la roue')
                moteur.regler_vitesse(0)
                difference_temps: float = actual_time() - ancien_temps
                if input('Est-ce bien arrêté ?') == 'oui':
                    break
            dutys.append(vitesse_calibrage / (diametre * 5 / difference_temps))
        for index, duty in enumerate(dutys):
            print(f'moteur {index} : {duty}')
        input()

    def calculer_mouvement(self, angle: float) -> tuple:
        return cos(radians(45 + angle)), sin(radians(45 + angle))
    
    def stop(self):
        for moteur in self.moteurs:
            moteur.regler_vitesse(0)
        print('stop')

    def deplacer(self, distance: float = .1, angle: float = 0, temps: float = 1):
        for moteur in self.moteurs:
            mouvement: float = self.calculer_mouvement(angle)[moteur.position % 2]
            moteur.regler_vitesse(mouvement * distance / temps * moteur.efficacite * moteur.sens)
        sleep(temps)
        self.stop()
    
    def polygone(self, angle_initial: float = 0, angle_rotation: float = 120, rayon: float = .5, temps: float = 4):
        cote: float = 2 * rayon * sin(2 * pi * (pi/angle_rotation))
        for angle in range(angle_initial, angle_initial + 360, angle_rotation):
            self.deplacer(cote, angle, temps * angle_rotation / 360)
            sleep(.1)

    def rotation(self, vitesse: float = 1, direction: int = 1):
        for moteur in self.moteurs:
            moteur.regler_vitesse(vitesse * moteur.efficacite * direction * moteur.sens * -1 if moteur.position%3 else 1)
        sleep(1)
        self.stop()

    def go_and_back(self, distance: float = 1, temps: float = 4):
        self.polygone(0, 180, distance, temps)
        
    def carre(self, distance: float = 1, temps: float = 4):
        self.polygone(0, 90, distance, temps)

    def losange(self, distance: float = 1, temps: float = 4):
        self.polygone(-45, 90, distance, temps)

    def cercle(self, vitesse: float = .1, temps: float = 4):
        for angle in range(360):
            for index, moteur in enumerate(self.moteurs):
                mouvement: float = self.calculer_mouvement(angle)[index % 2]
                moteur.regler_vitesse(mouvement * vitesse * moteur.efficacite * moteur.sens)
                sleep(temps/360)
        self.stop()
            
class Moteur:
    def __init__(self, pin_vitesse, pin_direction, sens, position, efficacite):
        self.vitesse: PWM = PWM(Pin(pin_vitesse, mode=Pin.OUT))
        self.direction: Pin = Pin(pin_direction, mode=Pin.OUT)
        self.sens: int = sens
        self.position: int = position
        self.efficacite: float = efficacite
        
    def regler_vitesse(self, vitesse: float):
        self.vitesse.duty_u16(int(abs(vitesse)))
        self.direction.value(1 if vitesse > 0 else 0)