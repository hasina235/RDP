# petri_streamlit_animated_full.py
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from snakes.nets import *
import time
import random

# -------------------
# 1. Définition du réseau de Petri
# -------------------
net = PetriNet('Commande_Restaurant')

# Places
net.add_place(Place('Client_arrive', [1]))
net.add_place(Place('Commande', []))
net.add_place(Place('Cuisine', []))
net.add_place(Place('Plat_servi', []))
net.add_place(Place('Paiement', []))

# Transitions
net.add_transition(Transition('Prendre_commande'))
net.add_transition(Transition('Preparer_plat'))
net.add_transition(Transition('Servir_plat'))
net.add_transition(Transition('Encaisser'))

# Arcs
net.add_input('Client_arrive', 'Prendre_commande', Value(1))
net.add_output('Commande', 'Prendre_commande', Value(1))

net.add_input('Commande', 'Preparer_plat', Value(1))
net.add_output('Cuisine', 'Preparer_plat', Value(1))

net.add_input('Cuisine', 'Servir_plat', Value(1))
net.add_output('Plat_servi', 'Servir_plat', Value(1))

net.add_input('Plat_servi', 'Encaisser', Value(1))
net.add_output('Paiement', 'Encaisser', Value(1))

# -------------------
# 2. Fonction pour dessiner le réseau
# -------------------
def dessiner_reseau(container):
    G = nx.DiGraph()

    # Déterminer les transitions activables
    enabled_transitions = [t.name for t in net.transition() if t.enabled(Substitution())]

    # Places
    for place_obj in net.place():
        place_name = place_obj.name
        label = f"{place_name} ({len(place_obj.tokens)})"
        G.add_node(place_name, label=label, shape='circle', color='lightblue')

    # Transitions
    for t_obj in net.transition():
        t_name = t_obj.name
        color = 'green' if t_name in enabled_transitions else 'orange'
        G.add_node(t_name, label=t_name, shape='square', color=color)

    # Arcs
    for place_obj in net.place():
        place_name = place_obj.name
        for t_name in net.post(place_name):
            G.add_edge(place_name, t_name)
        for t_name in net.pre(place_name):
            G.add_edge(t_name, place_name)

    # Positionnement et dessin
    pos = nx.spring_layout(G, seed=42)
    node_labels = {node: data['label'] for node, data in G.nodes(data=True)}
    node_colors = [data['color'] for _, data in G.nodes(data=True)]

    plt.figure(figsize=(8, 5))
    nx.draw(G, pos, labels=node_labels, with_labels=True, node_color=node_colors,
            node_size=2000, font_size=9, arrowsize=20)
    container.pyplot(plt)
    plt.clf()

# -------------------
# 3. Interface Streamlit
# -------------------
st.title("Réseau de Petri - Gestion d'un restaurant 🍽️")
st.subheader("Simulation pas à pas ou automatique avec animation")

graph_container = st.empty()
dessiner_reseau(graph_container)

# Initialisation du nombre de tirages
if 'tirages' not in st.session_state:
    st.session_state.tirages = 0

# Boutons de simulation
col1, col2 = st.columns(2)
with col1:
    sim_step = st.button("Tirer une transition")
with col2:
    sim_auto = st.button("Simuler automatiquement")

# Simulation pas à pas
if sim_step:
    tirable = [t for t in net.transition() if t.enabled(Substitution())]
    if tirable:
        t = random.choice(tirable)
        t.fire(Substitution())
        st.session_state.tirages += 1
        dessiner_reseau(graph_container)
        st.success(f"Tirage {st.session_state.tirages}: {t.name} exécutée")
        st.info(f"Transitions possibles: {[t.name for t in tirable]}")
    else:
        st.warning("Aucune transition possible, simulation terminée.")

# Simulation automatique
if sim_auto:
    tirages_auto = 0
    while True:
        tirable = [t for t in net.transition() if t.enabled(Substitution())]
        if not tirable:
            st.warning("Aucune transition possible, simulation terminée.")
            break
        t = random.choice(tirable)
        t.fire(Substitution())
        tirages_auto += 1
        st.session_state.tirages += 1
        dessiner_reseau(graph_container)
        st.write(f"Tirage {st.session_state.tirages}: {t.name} exécutée")
        time.sleep(1)
    st.success(f"Simulation automatique terminée après {tirages_auto} tirages.")

# Affichage du statut des places
st.subheader("État actuel des places")
for place_obj in net.place():
    st.write(f"{place_obj.name}: {len(place_obj.tokens)} jeton(s)")

st.info("Les transitions vertes sont activables, les oranges sont inactives. "
        "Le nombre de jetons est indiqué entre parenthèses dans le graphe.")
