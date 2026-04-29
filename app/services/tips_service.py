import random

TIPS_SALUDABLES = [
    "Bebe al menos 8 vasos de agua al día para mantenerte hidratado.",
    "Incluye frutas y verduras frescas en cada comida.",
    "Realiza al menos 30 minutos de actividad física diaria.",
    "Evita el consumo excesivo de azúcares y bebidas procesadas.",
    "Duerme entre 7 y 8 horas cada noche para una buena recuperación.",
    "Tómate un momento para respirar profundo y reducir el estrés.",
    "Prefiere alimentos integrales sobre los refinados.",
    "Desayuna todos los días para activar tu metabolismo.",
    "Lava tus manos antes de comer y después de ir al baño.",
    "Mantén una actitud positiva y agradece cada día."
]

def obtener_tip_saludable():
    return random.choice(TIPS_SALUDABLES)
