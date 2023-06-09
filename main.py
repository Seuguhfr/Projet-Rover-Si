from roverr import *

rover = Rover(
    Moteur(14, 15, -1, 0, 34773.25),
    Moteur(2, 3, 1, 1, 34773.25),
    Moteur(12, 13, 1, 2, 23182.17),
    Moteur(16, 17, -1, 3, 34773.25)
)


if not reset_cause():
    sleep(3)
    rover.carre()
    sleep(1)
    rover.losange()
    sleep(1)
    rover.rotation(direction=1)
    sleep(1)
    rover.rotation(direction=-1)
    sleep(1)
    rover.cercle()
    exit()

try:
    while True:
        methodes = list(rover.methodes.keys())
        print('\n\nVoici les déplacements que vous pouvez faire :')
        for methode in methodes:
            print(f' - {methode}')
        choix = input('\nQuel déplacement voulez-vous faire ?\n   > ')
        if choix in rover.methodes:
            rover.methodes[choix]()
        else:
            print('Méthode inconnue. Veuillez choisir une méthode valide.')
except KeyboardInterrupt:
    rover.stop()
    print("Arrêt d'urgence. Fin du programme.")
    exit()