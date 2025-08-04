import os
import pandas as pd
import joblib
from django.conf import settings

# Chemins vers les fichiers modèles
MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml', 'model_panne.pkl')
ENCODER_PATH = os.path.join(settings.BASE_DIR, 'ml', 'type_encoder.pkl')

# Chargement unique
model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

def predire_panne(age_days, type_equipement, nb_maintenances, nb_alertes_actives):
    # Préparation des données d'entrée
    input_df = pd.DataFrame([{
        "age_days": age_days,
        "type_equipement": type_equipement,
        "nb_maintenances": nb_maintenances,
        "nb_alertes_actives": nb_alertes_actives
    }])

    # Encodage du type
    encoded_type = encoder.transform(input_df[["type_equipement"]])
    encoded_df = pd.DataFrame(encoded_type, columns=encoder.get_feature_names_out(["type_equipement"]))

    # Fusion des colonnes
    input_final = pd.concat([input_df.drop(columns=["type_equipement"]), encoded_df], axis=1)

    # Prédiction
    prediction = model.predict(input_final)

    return prediction[0]  # 1 = en panne, 0 = pas en panne
