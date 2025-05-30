"""
Superhero Network Analysis Script

This script analyzes a network of superheroes and their connections. It processes data from two CSV files:
- superheroes.csv: Contains information about individual superheroes
- links.csv: Contains the connections between superheroes

The script performs several analyses:
1. Counts total number of superheroes
2. Counts total number of connections
3. Identifies superheroes added in the last 3 days
4. Finds the top 3 most connected superheroes
5. Analyzes information about the 'dataiskole' superhero
6. BONUS: Shows a visual graph of the network
7. BONUS: Allows adding new superheroes and connections
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from collections import Counter
import networkx as nx
import matplotlib.pyplot as plt

# Setup file paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, 'data')

# Define paths to data files
superheroes_path = os.path.join(data_dir, 'superheroes.csv')
links_path = os.path.join(data_dir, 'links.csv')


def load_data():
    """
    Load and preprocess the superhero and connection data from CSV files.
    
    Returns:
        tuple: A tuple containing two pandas DataFrames:
            - superheroes: DataFrame with superhero information
            - links: DataFrame with connection information
    """
    superheroes = pd.read_csv(superheroes_path)
    links = pd.read_csv(links_path)
    superheroes['created_at'] = pd.to_datetime(superheroes['created_at']).dt.date
    return superheroes, links


def basic_stats(superheroes, links):
    """
    Display basic statistics about the superhero network.
    
    Args:
        superheroes (pd.DataFrame): DataFrame containing superhero information
        links (pd.DataFrame): DataFrame containing connection information
    
    Displays:
        - Total number of superheroes
        - Total number of connections
        - Recently added superheroes (last 3 days)
        - Top 3 most connected superheroes
    """
    print(f"\n🦸 Total Superheroes: {superheroes['id'].nunique()}")
    print(f"🔗 Total Connections: {len(links)}")

    # Find superheroes added in the last 3 days
    today = datetime.today().date()
    recent_heroes = superheroes[superheroes['created_at'] >= today - timedelta(days=3)]

    print("\n🕒 Superheroes added in the last 3 days:")
    if recent_heroes.empty:
        print("No superheroes added in the last 3 days.")
    else:
        for _, row in recent_heroes.iterrows():
            print(f"- {row['name']} (added on {row['created_at']})")

    # Calculate and display top 3 most connected superheroes
    connection_counts = Counter(links['source'].tolist() + links['target'].tolist())
    top_3 = connection_counts.most_common(3)

    print("\n🏆 Top 3 Most Connected Superheroes:")
    for hero_id, count in top_3:
        name = superheroes.loc[superheroes['id'] == hero_id, 'name'].values[0]
        print(f"- {name} with {count} connections")


def analyze_dataiskole(superheroes, links):
    """
    Analyze information about the 'dataiskole' superhero.
    
    Args:
        superheroes (pd.DataFrame): DataFrame containing superhero information
        links (pd.DataFrame): DataFrame containing connection information
    
    Displays:
        - When dataiskole was added
        - List of dataiskole's connections (friends)
    """
    print("\n📋 Info about 'dataiskole':")
    dataiskole_row = superheroes[superheroes['name'] == 'dataiskole']
    if not dataiskole_row.empty:
        dataiskole_id = dataiskole_row.iloc[0]['id']
        added_date = dataiskole_row.iloc[0]['created_at']
        print(f"✔️ Added on: {added_date}")

        # Find all connections by checking both source and target columns
        is_source = links[links['source'] == dataiskole_id]['target']
        is_target = links[links['target'] == dataiskole_id]['source']
        friend_ids = pd.concat([is_source, is_target]).unique()

        if len(friend_ids) == 0:
            print("❌ No friends found.")
        else:
            friend_names = superheroes[superheroes['id'].isin(friend_ids)]['name'].tolist()
            print(f"👥 Friends: {', '.join(friend_names)}")
    else:
        print("❌ dataiskole not found in superhero list.")


def draw_graph(superheroes, links):
    """
    Create and display a visual representation of the superhero network.
    
    Args:
        superheroes (pd.DataFrame): DataFrame containing superhero information
        links (pd.DataFrame): DataFrame containing connection information
    
    Creates:
        A matplotlib figure showing the network graph with:
        - Nodes representing superheroes
        - Edges representing connections
        - Labels showing superhero names
    """
    print("\n📊 Visualizing superhero network...")
    G = nx.Graph()

    # Add nodes (superheroes) to the graph
    for _, row in superheroes.iterrows():
        G.add_node(row['id'], label=row['name'])

    # Add edges (connections) to the graph
    for _, row in links.iterrows():
        G.add_edge(row['source'], row['target'])

    # Calculate node positions using spring layout
    pos = nx.spring_layout(G, seed=42)
    labels = {row['id']: row['name'] for _, row in superheroes.iterrows()}

    # Create and display the graph
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=2000, 
            node_color="lightblue", font_size=9, font_weight="bold")
    plt.title("Superhero Network Graph")
    plt.show()


def add_superhero():
    """
    Add a new superhero to the network.
    
    Prompts the user for:
        - New superhero name
    
    Updates:
        - superheroes.csv with the new superhero entry
    """
    name = input("Enter new superhero name: ")
    superheroes = pd.read_csv(superheroes_path)
    new_id = superheroes['id'].max() + 1
    today = datetime.today().date()
    new_row = pd.DataFrame([{'id': new_id, 'name': name, 'created_at': today}])
    superheroes = pd.concat([superheroes, new_row], ignore_index=True)
    superheroes.to_csv(superheroes_path, index=False)
    print(f"✅ Superhero '{name}' added with ID {new_id}.")


def add_connection():
    """
    Add a new connection between two superheroes.
    
    Prompts the user for:
        - First superhero name
        - Second superhero name
    
    Updates:
        - links.csv with the new connection
    """
    superheroes = pd.read_csv(superheroes_path)
    name1 = input("Enter first superhero name: ")
    name2 = input("Enter second superhero name: ")

    # Find superhero IDs
    id1 = superheroes[superheroes['name'] == name1]['id']
    id2 = superheroes[superheroes['name'] == name2]['id']

    if id1.empty or id2.empty:
        print("❌ One or both superheroes not found.")
        return

    # Add new connection to links file
    new_link = pd.DataFrame([{'source': int(id1), 'target': int(id2)}])
    links = pd.read_csv(links_path)
    links = pd.concat([links, new_link], ignore_index=True)
    links.to_csv(links_path, index=False)
    print(f"✅ Connection added between {name1} and {name2}.")


def menu():
    """
    Display and handle the main menu interface.
    
    Provides options to:
        1. Show basic stats
        2. Analyze 'dataiskole'
        3. Show network graph
        4. Add new superhero
        5. Add new connection
        6. Exit
    
    Continuously runs until the user chooses to exit.
    """
    while True:
        print("\n==== Superhero Network Menu ====")
        print("1. Show basic stats")
        print("2. Analyze 'dataiskole'")
        print("3. Show network graph")
        print("4. Add new superhero")
        print("5. Add new connection")
        print("6. Exit")

        choice = input("Choose an option (1–6): ")

        superheroes, links = load_data()

        if choice == '1':
            basic_stats(superheroes, links)
        elif choice == '2':
            analyze_dataiskole(superheroes, links)
        elif choice == '3':
            draw_graph(superheroes, links)
        elif choice == '4':
            add_superhero()
        elif choice == '5':
            add_connection()
        elif choice == '6':
            print("👋 Exiting.")
            break
        else:
            print("❗ Invalid choice. Please try again.")


if __name__ == "__main__":
    menu()
