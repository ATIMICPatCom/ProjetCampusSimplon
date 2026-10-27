import plotly.express as px
import pandas as pd
import urllib.request
import csv
from string import Template

# 7. trouver le produit le plus vendu et le moins vendu en nombre d’unités vendues. 
def obtenir_extremes_ventes(url):
    reponse = urllib.request.urlopen(url)
    lignes = [ligne.decode('utf-8') for ligne in reponse.readlines()]
    lecteur_csv = csv.DictReader(lignes)

    ventes_produits = {}
    # on parcours le fichier afin d'alimenter la collection
    for ligne in lecteur_csv:
        produit = ligne['produit']
        ventes_produits[produit] = ventes_produits.get(produit, 0) + int(ligne['qte'])

    # on interroge la collection, ici les max & min pour trouver le produit le plus vendu et le moins vendu en nombre d’unités vendues
    plus_vendu = max(ventes_produits, key=ventes_produits.get)
    moins_vendu = min(ventes_produits, key=ventes_produits.get)

    return (
        f"Le produit le plus vendu est : {plus_vendu} ({ventes_produits[plus_vendu]} unités).",
        f"Le produit le moins vendu est : {moins_vendu} ({ventes_produits[moins_vendu]} unités)."
    )

def generer_rapport():
    url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSC4KusfFzvOsr8WJRgozzsCxrELW4G4PopUkiDbvrrV2lg0S19-zeryp02MC9WYSVBuzGCUtn8ucZW/pub?output=csv'
    
    # 1. Calculs natifs pour la question 7
    texte_plus, texte_moins = obtenir_extremes_ventes(url)

    # 2. Préparation Pandas
    donnees = pd.read_csv(url)
    donnees['chiffre_affaires'] = donnees['prix'] * donnees['qte']

    # 3. Graphiques Plotly
    fig_region = px.pie(donnees, values='qte', names='region', title='Quantité vendue par région')
    # 8.a. Graphique pour les ventes par produit
    fig_vol_prod = px.pie(donnees, values='qte', names='produit', title='Volume des ventes par produit')
    # 8.b. Graphique pour le chiffre d'affaires par produit.
    fig_ca_prod = px.pie(donnees, values='chiffre_affaires', names='produit', title="Chiffre d'affaires")

    # 4. Tableaux Pandas, les formatters appliqués (pour avoir les quantités sans virgules et les autres valeurs à 2 chiffres après la virgule)
    format_mixte = {"chiffre_affaires": lambda x: f"{x:.2f}", "qte": lambda x: f"{x:.0f}"}
    format_entier = {"Ecart-type Quantité": lambda x: f"{x:.0f}", "Variance Quantité": lambda x: f"{x:.0f}"}

    # 5. Lecture du fichier HTML externe
    with open('modele.html', 'r', encoding='utf-8') as f:
        modele = Template(f.read())

    # 6. Injection des données dans le modèle
    page_finale = modele.safe_substitute(
        texte_plus_vendu=texte_plus,
        texte_moins_vendu=texte_moins,
        html_fig_region=fig_region.to_html(full_html=False, include_plotlyjs='cdn'),
        html_fig_vol_prod=fig_vol_prod.to_html(full_html=False, include_plotlyjs=False),
        html_fig_ca_prod=fig_ca_prod.to_html(full_html=False, include_plotlyjs=False),

        # question 6. a. i. la moyenne
        html_moyenne=donnees.groupby('produit')[['chiffre_affaires', 'qte']].mean().reset_index().to_html(formatters=format_mixte),
        # question 6. a. ii. la médiane
        html_mediane=donnees.groupby('produit')[['chiffre_affaires', 'qte']].median().reset_index().to_html(formatters=format_mixte),
        # question 6. b. i. l'écart-type 
        html_ecart=donnees.groupby('produit')['qte'].std().to_frame(name='Ecart-type Quantité').reset_index().to_html(formatters=format_entier),
        # question 6. b. ii. la variance
        html_var=donnees.groupby('produit')['qte'].var().to_frame(name='Variance Quantité').reset_index().to_html(formatters=format_entier)
    )

    # 7. Sauvegarde du résultat
    with open('rapport-ventes.html', 'w', encoding='utf-8') as f:
        f.write(page_finale)
    
    print("Rapport professionnel généré avec succès !")

# Exécution du programme
if __name__ == '__main__':
    generer_rapport()