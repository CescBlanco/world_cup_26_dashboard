import pandas as pd
import numpy as np
from mplsoccer import VerticalPitch
from mplsoccer import Pitch
import matplotlib.pyplot as plt
from matplotlib import patheffects
import matplotlib.patheffects as path_effects
from scipy.ndimage import gaussian_filter1d
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from io import BytesIO
from urllib.request import urlopen
from mplsoccer import Pitch, VerticalPitch, add_image
from PIL import Image
from highlight_text import ax_text, fig_text
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import patheffects
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import streamlit as st
from matplotlib.lines import Line2D

background_color = '#0C0D0E'
text_color = 'white'
line_color = 'white'
path_eff = [path_effects.Stroke(linewidth=1.5, foreground=line_color), 
                path_effects.Normal()]

@st.cache_data
def extract_formation_data(df, name_team, formation_mappings, players_dict):
    formationset = df[df['type']== 'FormationSet'].copy()

    team_home_formation = formationset[formationset['nameTeam'] == name_team].copy()

    qualifiers = team_home_formation['qualifiers'].iloc[0]

    player_ids = next( q['value'] for q in qualifiers if q['type']['displayName'] == 'InvolvedPlayers').split(',')

    formation_positions = next( q['value'] for q in qualifiers if q['type']['displayName'] == 'TeamPlayerFormation').split(',')

    jerseys = next( q['value'] for q in qualifiers if q['type']['displayName'] == 'JerseyNumber').split(',')

    lineup = pd.DataFrame({
                    'playerId': player_ids,
                    'opta_position': formation_positions,
                    'jersey': jerseys
                })

    lineup = lineup[lineup['opta_position'] != '0']
    lineup['playerName'] = lineup['playerId'].map(players_dict)
    lineup['opta_position'] = lineup['opta_position'].astype(int)

    formation_id = next( q['value'] for q in qualifiers if q['type']['displayName'] == 'TeamFormation')
    formation = formation_mappings[formation_id]

    pitch = VerticalPitch()
    formation_df = pitch.formations_dataframe

    coords = formation_df[ formation_df['formation'] == formation][['opta','x','y','x_flip','y_flip','x_half','y_half','x_half_flip','y_half_flip','name']]

    lineup = lineup.merge( coords, left_on='opta_position', right_on='opta', how='left')
    lineup['team'] = name_team
    return lineup


def plot_initial_formation(df, home_team, away_team, formation_mappings, players_dict,color_home,color_away ,nombre_jugador_partido=None,ax=None):
    pitch = Pitch( pitch_type='statsbomb', pitch_color=background_color, line_color='white', linewidth=2)

    # Si no existe eje, crear figura propia
    if ax is None:

        fig, ax = plt.subplots(figsize=(10, 7))
        
    else:
        fig = ax.figure
        ax.set_title("INITIAL FORMATIONS",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)

    pitch.draw(ax=ax)    
    fig.set_facecolor('none')
    ax.set_facecolor('none')
    
    #Extract formation data for both teams
    lineup_home = extract_formation_data(df, home_team, formation_mappings, players_dict)
    lineup_away = extract_formation_data(df, away_team, formation_mappings, players_dict)

    # =========================
    # HOME TEAM
    # =========================
    motm_home = lineup_home[lineup_home['playerName'] == nombre_jugador_partido]
    normal_home = lineup_home[lineup_home['playerName'] != nombre_jugador_partido]

    # jugadores normales
    pitch.scatter( normal_home['x_half'], normal_home['y_half'], s=950, color=color_home, edgecolors='white', linewidth=2, ax=ax, zorder=3)

    # MOTM estrella + dorsal negro
    if not motm_home.empty:
        x = motm_home['x_half'].values[0]
        y = motm_home['y_half'].values[0]
        jersey = motm_home['jersey'].values[0]

        pitch.scatter( x, y, s=2000, color='gold', marker='*', edgecolors='white', linewidth=2, ax=ax, zorder=4)

        ax.text( x, y, str(jersey), color='black', fontsize=12, fontweight='bold', ha='center', va='center', zorder=5 )
        ax.text( x, y + 6, motm_home['playerName'].values[0], color=text_color, fontsize=7, ha='center', va='center',
                         bbox=dict(facecolor='#1A1A1A', edgecolor='none', alpha=0.6, pad=0.3),zorder=5)

    # nombres + dorsales normales HOME
    for _, row in normal_home.iterrows():
       
        ax.text( row['x_half'], row['y_half'], str(row['jersey']), color='black', fontsize=12, fontweight='bold', ha='center', va='center', zorder=4)
        ax.text( row['x_half'], row['y_half'] + 6, row['playerName'], color=text_color, fontsize=7, ha='center', va='center',
                 bbox=dict(facecolor='#1A1A1A', edgecolor='none', alpha=0.6, pad=0.3), zorder=4)
    
    # =========================
    # AWAY TEAM
    # =========================
    motm_away = lineup_away[lineup_away['playerName'] == nombre_jugador_partido]
    normal_away = lineup_away[lineup_away['playerName'] != nombre_jugador_partido]

    # jugadores normales
    pitch.scatter( normal_away['x_half_flip'], normal_away['y_half_flip'], s=950, color=color_away, edgecolors='white', linewidth=2, ax=ax, zorder=3)

    # MOTM estrella + dorsal negro
    if not motm_away.empty:
        x = motm_away['x_half_flip'].values[0]
        y = motm_away['y_half_flip'].values[0]
        jersey = motm_away['jersey'].values[0]

        pitch.scatter(x, y, s=2000, color='gold', marker='*', edgecolors='white', linewidth=2, ax=ax, zorder=4)
        
        ax.text( x, y, str(jersey), color='black', fontsize=12, fontweight='bold', ha='center', va='center', zorder=5)
        ax.text( x, y + 6, motm_away['playerName'].values[0], color=text_color, fontsize=7, ha='center', va='center',
                     bbox=dict(facecolor='#1A1A1A', edgecolor='none', alpha=0.6, pad=0.3), zorder=5)
    
    for _, row in lineup_away.iterrows():
        # dorsal dentro
        ax.text(row['x_half_flip'],row['y_half_flip'],str(row['jersey']),color='black',fontsize=12,fontweight='bold',ha='center',va='center',zorder=4)

        # nombre debajo
        ax.text( row['x_half_flip'], row['y_half_flip'] +6, row['playerName'], color=text_color, fontsize=7, ha='center', va='center',
            bbox=dict( facecolor='#1A1A1A', edgecolor='none', alpha=0.6, pad=0.3),zorder=4)

    # ax.text( 30, -2,   f"{lineup_home['team'].iloc[0]} - Initial Formation", ha='center', va='center', fontsize=14, color='white', fontweight='bold' )# izquierda (home)

    # ax.text( 90,-2,  f"{lineup_away['team'].iloc[0]} - Initial Formation", ha='center', va='center', fontsize=14, color='White', fontweight='bold' ) # derecha (away)
    return fig, ax

#--------------------------------------SHOTS PREPARE-----------------------------

# Helper functions
def is_big_chance(qualifiers):
    return 'BigChance' in str(qualifiers)

def is_own_goal(qualifiers):
    return 'OwnGoal' in str(qualifiers)

@st.cache_data
# Calculate stats
def team_stats(df):
    goals = np.sum((df['eventType'] == 'Goal'))
    xg = np.round(df['expectedGoals'].sum(), 2)
    xgot = np.round(df['expectedGoalsOnTarget'].sum(), 2)
    shots = len(df)
    on_target = np.sum(df['isOnTarget'])
    big_chances = np.sum(df['is_big_chance'])
    big_chance_miss = np.sum((df['is_big_chance']) & (df['eventType'] != 'Goal'))
    xg_per_shot = np.round(xg / shots, 2) if shots > 0 else 0
    avg_dist = np.round(np.sqrt((df['x'] - 105)**2 + (df['y'] - 34)**2).mean(), 2)
    return [goals, xg, xgot, shots, on_target, big_chances, big_chance_miss, xg_per_shot, avg_dist]

@st.cache_data
def prepare_dataframe_shots(df, data,team_dict_fotmob,  name_home_fotmob , name_away_fotmob):
    shots_df= pd.DataFrame(data['content']['shotmap']['shots'])
    shots_df = shots_df[shots_df['period']!='PenaltyShootout']
    shots_df['teamName'] = shots_df['teamId'].map(team_dict_fotmob)

    #Dataframe eventos whoscored
    df_events_shots = df[ (df['isShot'] == True) & (df['period'] != 'PenaltyShootout')][['id', 'qualifiers', 'type']]
    df_events_shots

    shots_merged = pd.merge(shots_df, df_events_shots, left_on='id', right_on='id', how='left')

    # Add flags
    shots_merged['is_big_chance'] = shots_merged['qualifiers'].apply(is_big_chance)
    shots_merged['is_own_goal'] = shots_merged['qualifiers'].apply(is_own_goal)

    shots_merged['render_team'] = shots_merged['teamName']

    mask = shots_merged['isOwnGoal'].eq(True)

    home= name_home_fotmob
    away= name_away_fotmob
    
    team_swap = { home: away, away: home}

    shots_merged.loc[mask, 'render_team'] = ( shots_merged.loc[mask, 'teamName'].map(team_swap))
    
    # Split by team
    home_shots = shots_merged[shots_merged['render_team'] == name_home_fotmob]
    away_shots = shots_merged[shots_merged['render_team'] == name_away_fotmob]

    home_stats = team_stats(home_shots)
    away_stats = team_stats(away_shots)

    return shots_merged, home_stats, away_stats    


def plot_shot_map_with_stats(shots_merged, home_stats, away_stats, 
                           home_id, away_id, home_name, away_name, 
                           home_color, away_color, bg_color='#0C0D0E',
                           ax=None):
    """
    Plot shot map with stats bar using your data structure
    """
    
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color='white', linewidth=2, corner_arcs=True)
    if ax is None:
        fig, ax = pitch.draw(figsize=(10,7))
    else:
        fig = ax.figure
        pitch.draw(ax=ax)
        ax.set_title("SHOTMAP AND STATS",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)


    fig.set_facecolor('none')
    ax.set_facecolor('none')

    ax.set_ylim(-0.5, 68.5)
    ax.set_xlim(-0.5, 105.5)
    
    # Split shots by team
    home_shots = shots_merged[shots_merged['teamId'] == home_id]
    away_shots = shots_merged[shots_merged['teamId'] == away_id]
    
    # Helper function to plot shots with correct positioning
    def plot_shots(df, color, is_home_team=True, marker='o', s=200, edgecolor=None, fill=True, hatch=None, zorder=2):
        if len(df) > 0:
            face_color = color if fill else 'none'
            edge_color = edgecolor if edgecolor else color
            
            # Transform coordinates based on team
            if is_home_team:
                # Home team (left side): flip coordinates
                x_coords = 105 - df['x']
                y_coords = 68 - df['y']
            else:
                # Away team (right side): use original coordinates
                x_coords = df['x']
                y_coords = df['y']
                
            ax.scatter(x_coords, y_coords, s=s, c=face_color, marker=marker, 
                      edgecolors=edge_color, zorder=zorder, hatch=hatch, linewidth=1.5)
    
    # --- HOME TEAM SHOTS (LEFT SIDE) ---
    # Goals (green football marker)
    home_goals = home_shots[(home_shots['eventType'] == 'Goal') & (~home_shots['is_own_goal'])]
    plot_shots(home_goals, 'none', is_home_team=True, marker='o', s=350, edgecolor='green', zorder=3)
    
    # Own goals (orange football marker)
    home_own_goals = home_shots[home_shots['is_own_goal']]
    plot_shots(home_own_goals, 'none', is_home_team=True, marker='o', s=350, edgecolor='orange', zorder=3)
    
    # Regular shots (not big chances)
    home_misses = home_shots[(home_shots['eventType'] == 'Miss') & (~home_shots['is_big_chance'])]
    plot_shots(home_misses, 'none', is_home_team=True, edgecolor=home_color, fill=False)
    
    home_saves = home_shots[(home_shots['eventType'] == 'AttemptSaved') & (~home_shots['is_big_chance'])]
    plot_shots(home_saves, 'none', is_home_team=True, edgecolor=home_color, fill=False, hatch='///////')
    
    home_posts = home_shots[(home_shots['eventType'] == 'Post') & (~home_shots['is_big_chance'])]
    plot_shots(home_posts, home_color, is_home_team=True, edgecolor=home_color)
    
    # Big chances (bigger markers)
    home_big_misses = home_shots[(home_shots['eventType'] == 'Miss') & (home_shots['is_big_chance'])]
    plot_shots(home_big_misses, 'none', is_home_team=True, edgecolor=home_color, fill=False, s=500)
    
    home_big_saves = home_shots[(home_shots['eventType'] == 'AttemptSaved') & (home_shots['is_big_chance'])]
    plot_shots(home_big_saves, 'none', is_home_team=True, edgecolor=home_color, fill=False, hatch='///////', s=500)
    
    home_big_posts = home_shots[(home_shots['eventType'] == 'Post') & (home_shots['is_big_chance'])]
    plot_shots(home_big_posts, home_color, is_home_team=True, edgecolor=home_color, s=500)
    
    home_big_goals = home_shots[(home_shots['eventType'] == 'Goal') & (home_shots['is_big_chance']) & (~home_shots['is_own_goal'])]
    plot_shots(home_big_goals, 'none', is_home_team=True, marker='o', s=650, edgecolor='green', zorder=3)
    
    # --- AWAY TEAM SHOTS (RIGHT SIDE) ---
    # Goals (green football marker)
    away_goals = away_shots[(away_shots['eventType'] == 'Goal') & (~away_shots['is_own_goal'])]
    plot_shots(away_goals, 'none', is_home_team=False, marker='o', s=350, edgecolor='green', zorder=3)
    
    # Own goals (orange football marker)
    away_own_goals = away_shots[away_shots['is_own_goal']]
    plot_shots(away_own_goals, 'none', is_home_team=False, marker='o', s=350, edgecolor='orange', zorder=3)
    
    # Regular shots (not big chances)
    away_misses = away_shots[(away_shots['eventType'] == 'Miss') & (~away_shots['is_big_chance'])]
    plot_shots(away_misses, 'none', is_home_team=False, edgecolor=away_color, fill=False)
    
    away_saves = away_shots[(away_shots['eventType'] == 'AttemptSaved') & (~away_shots['is_big_chance'])]
    plot_shots(away_saves, 'none', is_home_team=False, edgecolor=away_color, fill=False, hatch='///////')
    
    away_posts = away_shots[(away_shots['eventType'] == 'Post') & (~away_shots['is_big_chance'])]
    plot_shots(away_posts, away_color, is_home_team=False, edgecolor=away_color)
    
    # Big chances (bigger markers)
    away_big_misses = away_shots[(away_shots['eventType'] == 'Miss') & (away_shots['is_big_chance'])]
    plot_shots(away_big_misses, 'none', is_home_team=False, edgecolor=away_color, fill=False, s=500)
    
    away_big_saves = away_shots[(away_shots['eventType'] == 'AttemptSaved') & (away_shots['is_big_chance'])]
    plot_shots(away_big_saves, 'none', is_home_team=False, edgecolor=away_color, fill=False, hatch='///////', s=500)
    
    away_big_posts = away_shots[(away_shots['eventType'] == 'Post') & (away_shots['is_big_chance'])]
    plot_shots(away_big_posts, away_color, is_home_team=False, edgecolor=away_color, s=500)
    
    away_big_goals = away_shots[(away_shots['eventType'] == 'Goal') & (away_shots['is_big_chance']) & (~away_shots['is_own_goal'])]
    plot_shots(away_big_goals, 'none', is_home_team=False, marker='o', s=650, edgecolor='green', zorder=3)
    
    # --- STATS BAR ---
    stats_labels = ["Goals", "xG", "xGOT", "Shots", "On Target", "BigChance", "BigC.Miss", "xG/Shot", "Avg.Dist"]
    y_positions = [62 - i * 7 for i in range(len(stats_labels))]
    
    # Normalize stats for bar visualization
    def safe_normalize(home_val, away_val, max_width=20):
        total = home_val + away_val
        if total == 0:
            return max_width / 2, max_width / 2
        home_norm = (home_val / total) * max_width
        away_norm = (away_val / total) * max_width
        return home_norm, away_norm
    
    # Draw bars for each stat
    start_x = 42.5
    for i, (y, label) in enumerate(zip(y_positions, stats_labels)):
        home_norm, away_norm = safe_normalize(home_stats[i], away_stats[i])
        
        # Draw bars
        ax.barh(y, home_norm, height=5, color=home_color, left=start_x, alpha=0.8)
        ax.barh(y, away_norm, height=5, color=away_color, left=start_x + home_norm, alpha=0.8)
        
        # Stat labels (center, WHITE text on colored background)
        ax.text(52.5, y, label, color='white', fontsize=16, ha='center', va='center', fontweight='bold')
        
        # Stat values (home on left, away on right)
        ax.text(41.5, y, str(home_stats[i]), color='white', fontsize=16, ha='right', va='center', fontweight='bold')
        ax.text(63.5, y, str(away_stats[i]), color='white', fontsize=16, ha='left', va='center', fontweight='bold')
    
    # Team names and direction indicators
    ax.text(0, 70, f"<- Shots", color=home_color, size=13, ha='left', fontweight='bold')
    ax.text(105, 70, f"Shots ->", color=away_color, size=13, ha='right', fontweight='bold')
    
    ax.text(1, -2, "This type of shotmap never includes penalty kicks", 
            fontsize=8, ha='left', va='top', color='white',
            bbox=dict(boxstyle="round,pad=0.3", facecolor=background_color, edgecolor='white', alpha=0.8))

    # Remove axis
    ax.axis('off')
    
    return fig, ax

@st.cache_data
def preparar_xg_flows(shots_df, name_home_fotmob):
    """
    Prepara los DataFrames necesarios para el flujo de xG acumulado de un partido.

    Args:
        df_tiros_completo (pd.DataFrame): DataFrame con todos los tiros del partido.
        color_local (str): Color del equipo local (para diferenciar los tiros).

    Returns:
        dict: Diccionario con los siguientes elementos:
            - local_xg (DataFrame): Tiros del equipo local con xG acumulado.
            - visit_xg (DataFrame): Tiros del equipo visitante con xG acumulado.
            - goles_local_xg (DataFrame): Goles del equipo local.
            - goles_visit_xg (DataFrame): Goles del equipo visitante.
            - a_total (str): xG total del equipo local.
            - h_total (str): xG total del equipo visitante.
    """
    # Separar tiros por equipo
    df_tiros_local = shots_df[shots_df['render_team'] == name_home_fotmob]
    df_tiros_visit = shots_df[shots_df['render_team'] != name_home_fotmob]


    # Seleccionar columnas relevantes
    cols = ['playerName', 'teamColor', 'eventType', 'expectedGoals', 'period', 'min', 'minAdded', 'isOwnGoal']
    df_xg_local = df_tiros_local[cols].copy()
    df_xg_visit = df_tiros_visit[cols].copy()

    # Rellenar valores faltantes
    for df in [df_xg_local, df_xg_visit]:
        df['expectedGoals'] = df['expectedGoals'].fillna(0)
        df['minAdded'] = df['minAdded'].fillna(0)
        df['mintotal'] = df['min'] + df['minAdded']

    # Ordenar por minuto total
    local_xg = df_xg_local.sort_values('mintotal').reset_index(drop=True)
    visit_xg = df_xg_visit.sort_values('mintotal').reset_index(drop=True)

    # Calcular xG acumulado
    local_xg['xg_cumsum'] = local_xg['expectedGoals'].cumsum()
    visit_xg['xg_cumsum'] = visit_xg['expectedGoals'].cumsum()

    # Calcular totales de xG
    h_total = str(round(local_xg['expectedGoals'].sum(), 2))
    a_total = str(round(visit_xg['expectedGoals'].sum(), 2))

    # Filtrar goles
    goles_local_xg = local_xg[local_xg['eventType'] == 'Goal'].copy()
    goles_visit_xg = visit_xg[visit_xg['eventType'] == 'Goal'].copy()

    # Ajustar periodos
    periodos = {'FirstHalf': '1P', 'SecondHalf': '2P'}
    goles_local_xg['period'] = goles_local_xg['period'].replace(periodos)
    goles_visit_xg['period'] = goles_visit_xg['period'].replace(periodos)

    # Crear columna "scorechart"
    goles_local_xg['scorechart'] = (
        goles_local_xg['mintotal'].astype(int).astype(str) + "'" + " " +
        goles_local_xg['playerName'] + " (" + goles_local_xg['period'] + ")"
    )
    goles_visit_xg['scorechart'] = (
        goles_visit_xg['mintotal'].astype(int).astype(str) + "'" + " " +
        goles_visit_xg['playerName'] + " (" + goles_visit_xg['period'] + ")"
    )

    return {
        'local_xg': local_xg,
        'visit_xg': visit_xg,
        'goles_local_xg': goles_local_xg,
        'goles_visit_xg': goles_visit_xg,
        'a_total': a_total,
        'h_total': h_total
    }

@st.cache_data
def get_data_xg(datos_xg):
    #Obtener los datos
    local_xg = datos_xg['local_xg']
    visit_xg = datos_xg['visit_xg']
    goles_local_xg = datos_xg['goles_local_xg']
    goles_visit_xg = datos_xg['goles_visit_xg']
    xg_home = datos_xg['h_total']
    xg_away= datos_xg['a_total']
    return local_xg,  visit_xg,   goles_local_xg,goles_visit_xg, xg_home,  xg_away

def plot_xg_flow_streamlit(
    local_xg,     visit_xg,     goles_local_xg,     goles_visit_xg,     nombre_local, 
    nombre_visitante,     color_local,     color_visit,    imagen_pelota_normal, imagen_pelota_roja,ax=None):
    """
    Función para graficar el flujo de xG acumulado y devolver la figura para Streamlit.

    Args:
        local_xg (pd.DataFrame): DataFrame con los datos de xG acumulado del equipo local.
        visit_xg (pd.DataFrame): DataFrame con los datos de xG acumulado del equipo visitante.
        goles_local_xg (pd.DataFrame): DataFrame con los goles del equipo local.
        goles_visit_xg (pd.DataFrame): DataFrame con los goles del equipo visitante.
        nombre_local (str): Nombre del equipo local.
        nombre_visitante (str): Nombre del equipo visitante.
        color_local (str): Color del equipo local.
        color_visit (str): Color del equipo visitante.
        imagen_pelota_normal: Imagen cargada (OffsetImage o similar) para usar como icono de gol.
    
    Returns:
        fig: Figura de Matplotlib lista para usar en Streamlit con st.pyplot(fig).
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(13, 6))
    else:
        fig = ax.figure
        ax.set_title("EVOLUTIVE EXPECTED GOAL (xG)",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)

    fig.patch.set_alpha(0.0)
    # Fondo del eje transparente
    ax.set_facecolor('none')
    fig.set_facecolor('none')


    # Graficar las líneas de xG acumulado
    ax.step(local_xg['min'], local_xg['xg_cumsum'], where='post', linewidth=4,
            label=f"{nombre_local} ({round(local_xg['xg_cumsum'].iloc[-1], 2)} xG)", color=color_local)
    ax.step(visit_xg['min'], visit_xg['xg_cumsum'], where='post', linewidth=4,
            label=f"{nombre_visitante} ({round(visit_xg['xg_cumsum'].iloc[-1], 2)} xG)", color=color_visit)

    # Agregar imágenes de goles como marcadores
    for _, row in goles_local_xg.iterrows():
        if row['isOwnGoal'] == True:
            imagebox = OffsetImage(imagen_pelota_roja, zoom=0.013)
        else:
            imagebox = OffsetImage(imagen_pelota_normal, zoom=0.02)
        ab = AnnotationBbox(imagebox, (row['min'], row['xg_cumsum']), frameon=False)
        ax.add_artist(ab)

    for _, row in goles_visit_xg.iterrows():
        if row['isOwnGoal'] == True:
            imagebox = OffsetImage(imagen_pelota_roja, zoom=0.013)
        else:
            imagebox = OffsetImage(imagen_pelota_normal, zoom=0.02)
        ab = AnnotationBbox(imagebox, (row['min'], row['xg_cumsum']), frameon=False)
        ax.add_artist(ab)

    # Agregar anotaciones para los goles con nombre y minuto
    for _, row in goles_local_xg.iterrows():
        # Minuto con añadido si corresponde
        if pd.notnull(row['minAdded']) and row['minAdded'] > 0:
            minuto_texto = f"{int(row['min'])}+{int(row['minAdded'])}"
        else:
            minuto_texto = f"{int(row['min'])}"
        
        ax.annotate(
            f"{row['playerName']} ({minuto_texto}){' OG' if row['isOwnGoal'] else ''}",
            (row['min'], row['xg_cumsum']),
            xytext=(-20, 20), textcoords='offset points', ha='center', fontsize=7, color='black',
            arrowprops=dict(arrowstyle="->", color='white'),
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=0.5, alpha=0.7)
        )

    for _, row in goles_visit_xg.iterrows():
        if pd.notnull(row['minAdded']) and row['minAdded'] > 0:
            minuto_texto = f"{int(row['min'])}+{int(row['minAdded'])}"
        else:
            minuto_texto = f"{int(row['min'])}"
        
        ax.annotate(
            f"{row['playerName']} ({minuto_texto}){' OG' if row['isOwnGoal'] else ''}",
            (row['min'], row['xg_cumsum']),
            xytext=(-20, 20), textcoords='offset points', ha='center', fontsize=9, color='black',
            arrowprops=dict(arrowstyle="->", color='white'),
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=0.5, alpha=0.7)
        )

    # Ocultar los bordes del gráfico
    spines = ['top', 'bottom', 'left', 'right']
    for x in spines:
        ax.spines[x].set_visible(True)

    # Personalizar el gráfico
    ax.set_xticks([0, 15, 30, 45, 60, 75, 90])
    ax.set_yticks([0, 0.5, 1, 1.5, 2])
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', labelsize=6, labelcolor='white')
    ax.tick_params(axis='y', labelsize=6,  labelcolor='white')
    ax.axvline(45, ls=':', color='white', lw=0.5)
    ax.set_xlabel("Minute", fontsize=10,  color='white',fontweight='bold')
    ax.set_ylabel("Acumulative xG", fontsize=10,  color='white', fontweight='bold')
    ax.legend()

    fig.tight_layout()
    return fig, ax

xT_grid = pd.read_csv('https://media.githubusercontent.com/media/ricardoherediaj/football-analytics-tutorials/refs/heads/main/data/xT_grid.csv', header=None)
xT_grid = xT_grid.values

def preparare_df_xt(df,name_home_fotmob,name_away_fotmob ):

    df['render_team'] = df['nameTeam']
    if 'isOwnGoal' not in df.columns:
        df['isOwnGoal'] = False
    mask = df['isOwnGoal'].eq(True)
    home= name_home_fotmob
    away= name_away_fotmob
    team_swap = {
        home: away,
        away: home
    }

    df.loc[mask, 'render_team'] = (
        df.loc[mask, 'nameTeam'].map(team_swap)
    )
    return df


def plot_xt_momentum(df_events: pd.DataFrame,xT_grid: np.ndarray,teams_dict_id_name: dict,home_team_id: int,away_team_id: int,window_size: int = 4,decay_rate: float = 0.25,
                    sigma: float = 1.0, home_color: str = '#43A1D5', away_color: str = '#FF4C4C', bg_color: str = '#0C0D0E', 
                    line_color: str = 'white', figsize: tuple = (12, 6), ax=None):
    """
    Plots match momentum using xT, adapted to your data schema and project style.
    """
    # 1. Scale coordinates if needed (my data is 0-100, grid expects 0-120/0-80)
    df = df_events.copy()
    df['x'] = df['x'] * 1.2
    df['y'] = df['y'] * 0.8
    df['endX'] = df['endX'] * 1.2
    df['endY'] = df['endY'] * 0.8

    n_rows, n_cols = xT_grid.shape

    # 2. Filter for successful passes and carries
    mask = (
        df['type'].isin(['Pass', 'Carry']) &
        (df['outcomeType'] == 'Successful')
    )
    df_xT = df[mask].copy()

    # 3. Bin start/end locations to xT grid
    def get_bin(val, max_val, n_bins):
        val = max(0, min(val, max_val))
        bin_idx = int(val / max_val * n_bins)
        return min(bin_idx, n_bins - 1)

    df_xT['start_x_bin'] = df_xT['x'].apply(lambda x: get_bin(x, 120, n_cols))
    df_xT['start_y_bin'] = df_xT['y'].apply(lambda y: get_bin(y, 80, n_rows))
    df_xT['end_x_bin'] = df_xT['endX'].apply(lambda x: get_bin(x, 120, n_cols))
    df_xT['end_y_bin'] = df_xT['endY'].apply(lambda y: get_bin(y, 80, n_rows))

    # 4. Calculate xT for each action
    df_xT['start_zone_value'] = df_xT.apply(lambda row: xT_grid[row['start_y_bin'], row['start_x_bin']], axis=1)
    df_xT['end_zone_value'] = df_xT.apply(lambda row: xT_grid[row['end_y_bin'], row['end_x_bin']], axis=1)
    df_xT['xT'] = df_xT['end_zone_value'] - df_xT['start_zone_value']

    # 5. Clip xT values (e.g., max 0.1)
    df_xT['xT_clipped'] = np.clip(df_xT['xT'], 0, 0.1)

    df_xT['team'] = df_xT['render_team']

    # ---------------------------
    # 6. TEAM ORDER (home/away)
    # ---------------------------
    
    
    home_team = teams_dict_id_name[home_team_id]
    away_team = teams_dict_id_name[away_team_id]

    teams = [home_team, away_team]

    # fallback safety
    if len(teams) < 2:
        teams = [df_events['render_team'].iloc[0], df_events['render_team'].iloc[-1]]

    # 7. For each team and minute, keep only the max xT (clipped)
    max_xT_per_minute = df_xT.groupby(['team', 'minute'])['xT_clipped'].max().reset_index()

    # 8. Calculate weighted sum of xT in rolling window for each minute/team
    minutes = sorted(max_xT_per_minute['minute'].unique())
    weighted_xT_sum = {team: [] for team in teams}
    momentum = []

    for current_minute in minutes:
        for team in teams:
            recent_xT = max_xT_per_minute[
                (max_xT_per_minute['team'] == team) &
                (max_xT_per_minute['minute'] <= current_minute) &
                (max_xT_per_minute['minute'] > current_minute - window_size)
            ]
            weights = np.exp(-decay_rate * (current_minute - recent_xT['minute'].values))
            weighted_sum = np.sum(weights * recent_xT['xT_clipped'].values)
            weighted_xT_sum[team].append(weighted_sum)
        # Home minus away for momentum
        momentum.append(weighted_xT_sum[teams[0]][-1] - weighted_xT_sum[teams[1]][-1])

    momentum_df = pd.DataFrame({
        'minute': minutes,
        'momentum': momentum
    })

    # 9. Plotting
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
        ax.set_title("xT MOMENTUM",  color=line_color, fontsize=25, fontweight='bold', path_effects=path_eff)

    fig.set_facecolor('none')
    ax.set_facecolor('none')

    # Smoothing
    full_minutes = np.arange(0, 99)
    momentum_df = momentum_df.set_index('minute').reindex(full_minutes)
    momentum_df['momentum'] = momentum_df['momentum'].fillna(0)
    momentum_df = momentum_df.reset_index().rename(columns={'index': 'minute'})

    momentum_df['smoothed_momentum'] = gaussian_filter1d(momentum_df['momentum'], sigma=sigma)
    ax.plot(momentum_df['minute'], momentum_df['smoothed_momentum'], color=line_color, linewidth=2)

    ax.axhline(0, color=line_color, linestyle='--', linewidth=1, alpha=0.7)
    ax.fill_between(momentum_df['minute'], momentum_df['smoothed_momentum'], where=(momentum_df['smoothed_momentum'] > 0), color=home_color, alpha=0.5, interpolate=True)
    ax.fill_between(momentum_df['minute'], momentum_df['smoothed_momentum'], where=(momentum_df['smoothed_momentum'] < 0), color=away_color, alpha=0.5, interpolate=True)

    # Team names and score
    # ax.text(2, 0.07, team_dict[home_team_id], fontsize=16, ha='left', va='center', color=home_color, fontweight='bold')
    # ax.text(2, -0.07, team_dict[away_team_id], fontsize=16, ha='left', va='center', color=away_color, fontweight='bold')

    # ---------------------------
    # GOALS + OWN GOALS (NO IMAGES)
    # ---------------------------

    for team, y in [(teams[0], 0.065), (teams[1], -0.065)]:

        goals = df_events[
            (df_events['render_team'] == team) &
            (df_events['type'] == 'Goal') &
            (~df_events['isOwnGoal'].fillna(False))
        ]['minute']

        for minute in goals:
            ax.axvline(minute, color=line_color, linestyle=':', linewidth=1, alpha=0.5)

            ax.scatter(
                minute,
                y,
                color='white',   # normal goal
                s=80,
                zorder=10,
                alpha=0.9,
                edgecolors='black'
            )

            ax.text(
                minute + 0.9,
                y,
                'Goal',
                fontsize=9,
                color=line_color
            )


    # ---------------------------
    # OWN GOALS (RED DOT)
    # ---------------------------

    own_goals = df_events[df_events['isOwnGoal'].eq(True)]

    for _, row in own_goals.iterrows():

        minute = row['minute']
        team = row['render_team']

        y = 0.065 if team == teams[0] else -0.065

        ax.axvline(minute, color='red', linestyle=':', linewidth=1, alpha=0.6)

        ax.scatter(
            minute,
            y,
            color='red',
            s=90,
            zorder=12,
            edgecolors='black'
        )

        ax.text(
            minute + 0.9,
            y,
            'Own Goal',
            fontsize=9,
            color='red'
        )


    # Aesthetics
    ax.set_xlabel('Minute', color=line_color, fontsize=15, fontweight='bold')
    ax.set_ylabel('Momentum', color=line_color, fontsize=15, fontweight='bold')
    ax.set_xticks([0,15,30,45,60,75,90])
    ax.tick_params(axis='x', colors=line_color)
    ax.tick_params(axis='y', left=False, right=False, labelleft=False)
    for spine in ['top', 'right', 'bottom', 'left']:
        ax.spines[spine].set_visible(False)
    ax.margins(x=0)
    ax.set_ylim(-0.08, 0.08)
    #ax.set_title('xT Momentum', color=line_color, fontsize=20, fontweight='bold', pad=-5)
    plt.tight_layout()
    return fig, ax

#----------------------------------------POSITION MEDIAN PLAYERS------------------------------------------
@st.cache_data
def prepare_positional_events(df, players_dict):
    df_pos= df[(df['x'] != 0) | (df['y'] != 0)].copy()
    avg_pos = (df_pos.groupby(['playerId', 'nameTeam']).agg(x=('x','mean'), y=('y','mean'), n=('type','count')).reset_index())
    avg_pos['playerName'] = avg_pos['playerId'].astype(int).astype(str).map(players_dict)
    return avg_pos

@st.cache_data
def create_dataframe_median_positions(df,avg_pos, home_team, away_team, teams_dict ,players_dict,is_home= True):
    
    if is_home ==True:

        av_players= avg_pos[avg_pos['nameTeam']==teams_dict[home_team['team_id']]].copy()

        # Create player info
        player_info = {}
        for player in home_team['players']:
            player_id = player['playerId']
            player_name = players_dict.get(str(player_id), player['name'])
            player_info[player_id] = {
                'shirtNo': player['shirtNo'],
                'position': player['position'],
                'isFirstEleven': player.get('isFirstEleven', False)
            }

    else:
        av_players= avg_pos[avg_pos['nameTeam']==teams_dict[away_team['team_id']]].copy()

        # Create player info
        player_info = {}
        for player in away_team['players']:
            player_id = player['playerId']
            player_name = players_dict.get(str(player_id), player['name'])
            player_info[player_id] = {
                'shirtNo': player['shirtNo'],
                'position': player['position'],
                'isFirstEleven': player.get('isFirstEleven', False)
            }

    player_df = pd.DataFrame.from_dict(player_info, orient='index')
    # Pasar el índice a columna
    player_df = player_df.reset_index().rename(columns={'index': 'playerId'})
    # Unir
    av_players = av_players.merge(player_df,on='playerId',how='left')
    return av_players

def plot_player_position_median(df, background_color, color, is_home= True, ax=None):

    df = df.copy()

    if not is_home:
        df['x'] = 100 - df['x']
        df['y'] = 100 - df['y']

    pitch = Pitch( pitch_type='opta', pitch_color=background_color, line_color='white', linewidth=2)

     # Crear figura sólo si no existe
    if ax is None:
        fig, ax = pitch.draw(figsize=(10, 7))
    else:
        fig = ax.figure
        pitch.draw(ax=ax)
        ax.set_title("PLAYERS AVERAGE POSITIONS",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)
    
    fig.set_facecolor('none')
    ax.set_facecolor('none')

    for _, row in df.iterrows():

        # # nombre debajo
        # ax.text( row['x'], row['y'] - 6, row['playerName'], color=text_color, fontsize=7, ha='center', va='center',
        #     bbox=dict( facecolor='#1A1A1A', edgecolor='none', alpha=0.6, pad=0.3),zorder=4)


        marker = 'o' if row['isFirstEleven'] else 's'

        pitch.scatter(row['x'], row['y'], s=1200, marker=marker,
                        color='white', edgecolors=color, linewidth=3, ax=ax, zorder=3)
        
        # Jersey numbers with better visibility
        ax.text(row['x'], row['y'], str(row['shirtNo']),
                ha='center', va='center', fontsize=14, color=color, weight='bold',
                path_effects=[patheffects.withStroke(linewidth=3, foreground='white')], zorder=4)
        

    # Away team - normal positioning (no axis inversion needed)
    ax.text(5, 95, "○ = starter\n□ = substitute", 
            fontsize=10, ha='left', va='top', color='white',
            bbox=dict(boxstyle="round,pad=0.3", facecolor=background_color, edgecolor='white', alpha=0.8))

    return fig, ax

#------------------------------------HEATMAP ACTIONS---------------------------------------

@st.cache_resource
def plot_heatmap_team(df, team_name , color_team, is_home= True):
    # Create KDE heatmap - 
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.colors import to_rgba
    
    df= df[df['nameTeam']== team_name].copy()
   
    color = np.array(to_rgba(color_team))
    flamingo_cmap = LinearSegmentedColormap.from_list( "Team colors", ['#0C0D0E', color], N=500)
    
    if not is_home:
        df['x'] = 100 - df['x']
        df['y'] = 100 - df['y']

    pitch = Pitch(pitch_type='opta' ,line_color="#FAFAFB", line_zorder=2)
    fig, ax = pitch.draw(figsize=(10, 7))

    kde = pitch.kdeplot(df.x, df.y, ax=ax,
                        # fill using 100 levels so it looks smooth
                        fill=True, levels=100,
                        # shade the lowest area so it looks smooth
                        # so even if there are no events it gets some color
                        thresh=0,
                        cut=4,  # extended the cut so it reaches the bottom edge
                        bw_adjust=0.3,
                        cmap=flamingo_cmap)
    
    fig.set_facecolor('none')
    ax.set_facecolor('none')

    if is_home:
        ax.text(0,  -3, 'Attacking Direction--->', color=color_team, fontsize=13, ha='left', va='center')

    if not is_home:
        ax.text(100,-3, '<---Attacking Direction', color=color_team, fontsize=13, ha='right', va='center')
    return fig

#------------------------------------HEATMAP TOUCHES---------------------------------------
def plot_heatmap_touches(df, team_name ,color_team, is_home= True, ax= None):
    # Create KDE heatmap - 
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.colors import to_rgba
    
    df_touches= df[df['isTouch']==True]
    df_team= df_touches[df_touches['nameTeam']== team_name].copy()

    color = np.array(to_rgba(color_team))
    flamingo_cmap = LinearSegmentedColormap.from_list( "Team colors", ['#0C0D0E', color], N=500)

    if not is_home:
        df_team['x'] = 100 - df_team['x']
        df_team['y'] = 100 - df_team['y']

  
    pitch = Pitch(pitch_type='opta' ,line_color="#FAFAFB", line_zorder=2)
    if ax is None:
        fig, ax = pitch.draw(figsize=(10, 7))
    else:
        fig = ax.figure
        pitch.draw(ax=ax)
        ax.set_title("HEATMAP TOUCHES",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)
    kde = pitch.kdeplot(df_team.x, df_team.y, ax=ax,
                        # fill using 100 levels so it looks smooth
                        fill=True, levels=200,
                        # shade the lowest area so it looks smooth
                        # so even if there are no events it gets some color
                        thresh=0,
                        cut=4,  # extended the cut so it reaches the bottom edge
                        bw_adjust=0.3,
                        cmap=flamingo_cmap)
    fig.set_facecolor('none')
    ax.set_facecolor('none')
    if is_home:
        ax.text(0,  -3, 'Attacking Direction--->', color=color_team, fontsize=13, ha='left', va='center')
    if not is_home:
        ax.text(100,-3, '<---Attacking Direction', color=color_team, fontsize=13, ha='right', va='center')
    return fig, ax

#-------------------------------------------NETWORK PASS-------------------------------------
@st.cache_data
def prepare_enhanced_passes(df_events):
    """Prepare passes with angle calculations"""
    passes = df_events[
        (df_events['type'] == 'Pass') & 
        (df_events['outcomeType'] == 'Successful')
    ].copy()
    
    # Convert coordinates (WhoScored 0-100 → StatsBomb 0-120x0-80)
    passes['x'] = passes['x'] * 1.2
    passes['y'] = passes['y'] * 0.8
    passes['endX'] = passes['endX'] * 1.2
    passes['endY'] = passes['endY'] * 0.8
    
    # Calculate pass angles
    passes['pass_angle'] = np.degrees(np.arctan2(
        passes['endY'] - passes['y'], 
        passes['endX'] - passes['x']
    ))
    passes['pass_angle_abs'] = np.abs(passes['pass_angle'])
    
    # Add receiver
    passes['receiver'] = passes['playerId'].shift(-1)
    
    return passes

@st.cache_data
def get_pass_combinations(passes_df, team_id):
    """Calculate bidirectional pass combinations"""
    team_passes = passes_df[passes_df['teamId'] == team_id].copy()
    
    # Create bidirectional pairs
    team_passes['pos_min'] = team_passes[['playerId', 'receiver']].min(axis=1)
    team_passes['pos_max'] = team_passes[['playerId', 'receiver']].max(axis=1)
    
    # Count passes between pairs
    pass_combinations = team_passes.groupby(['pos_min', 'pos_max']).size().reset_index(name='pass_count')
    
    return pass_combinations

@st.cache_data
def get_enhanced_positions(passes_df, team_id, team_players, player_names_dict):
    """Get average positions with player info"""
    team_passes = passes_df[passes_df['teamId'] == team_id]
    
    # Calculate average positions
    avg_locs = team_passes.groupby('playerId').agg({
        'x': 'median', 
        'y': 'median', 
        'playerId': 'count'
    })
    avg_locs.columns = ['x_avg', 'y_avg', 'pass_count']
    
    # Create player info
    player_info = {}
    for player in team_players:
        player_id = player['playerId']
        player_name = player_names_dict.get(str(player_id), player['name'])
        player_info[player_id] = {
            'name': player_name,
            'shirtNo': player['shirtNo'],
            'position': player['position'],
            'isFirstEleven': player.get('isFirstEleven', False)
        }
    
    # Join with player info
    player_df = pd.DataFrame.from_dict(player_info, orient='index')
    avg_locs = avg_locs.join(player_df)
    
    return avg_locs

@st.cache_data
def calculate_team_metrics(passes_df, avg_locs, team_id):
    """Calculate tactical metrics"""
    team_passes = passes_df[passes_df['teamId'] == team_id]
    
    # Verticality
    valid_passes = team_passes[
        (team_passes['pass_angle_abs'] >= 0) & 
        (team_passes['pass_angle_abs'] <= 90)
    ]
    median_angle = valid_passes['pass_angle_abs'].median()
    verticality = round((1 - median_angle/90) * 100, 2)
    
    # Defense line (center backs)
    center_backs = avg_locs[avg_locs['position'] == 'DC']
    defense_line = center_backs['x_avg'].median() if len(center_backs) > 0 else 30
    
    # Forward line (forwards and attacking mids)
    attackers = avg_locs[avg_locs['position'].isin(['FW', 'AMC'])]
    forward_line = attackers['x_avg'].mean() if len(attackers) > 0 else 90
    
    # Team median position
    team_median = avg_locs['x_avg'].median()
    
    return {
        'verticality': verticality,
        'defense_line': defense_line,
        'forward_line': forward_line,
        'team_median': team_median
    }

def plot_enhanced_network(passes_df, avg_locs, pass_combinations, team_metrics, 
                         team_name, color='blue', is_home=True, bg_color='#0C0D0E', ax=None, show_title=True):
    """Plot enhanced passing network with The Athletic styling"""
    
    # Setup pitch with dark theme
    pitch = Pitch(pitch_type='statsbomb', line_color='white', pitch_color=bg_color, linewidth=1)
    
    if ax is None:
        fig, ax = pitch.draw(figsize=(10,7))
    else:
        fig = ax.figure
        pitch.draw(ax=ax)
 
    if show_title:
        ax.set_title("PASSING NETWORK",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)

    ax.set_xlim(0, 120)
    ax.set_ylim(0, 80)
    ax.set_facecolor('none')  # Transparent background for subplot
    
    # Transform coordinates for away team instead of inverting axis
    if not is_home:
        # Transform BOTH X and Y coordinates to flip attack direction AND side positions
        avg_locs = avg_locs.copy()
        avg_locs['x_avg'] = 120 - avg_locs['x_avg']  # Flip attack direction
        avg_locs['y_avg'] = 80 - avg_locs['y_avg']   # Flip left/right sides
    
    # Add player info to combinations
    combinations = pass_combinations.merge(
        avg_locs[['x_avg', 'y_avg', 'name']], 
        left_on='pos_min', right_index=True
    ).merge(
        avg_locs[['x_avg', 'y_avg', 'name']], 
        left_on='pos_max', right_index=True, 
        suffixes=['', '_end']
    )
    
    # Pass lines with enhanced styling
    max_passes = combinations['pass_count'].max()
    combinations['line_width'] = (combinations['pass_count'] / max_passes) * 15
    combinations['alpha'] = 0.3 + (combinations['pass_count'] / max_passes) * 0.6
    
    # Draw pass lines FIRST (lower z-order)
    for _, row in combinations.iterrows():
        pitch.lines(row['x_avg'], row['y_avg'], row['x_avg_end'], row['y_avg_end'],
                   lw=row['line_width'], color=color, alpha=row['alpha'], ax=ax, zorder=1)
    
    # Tactical lines - also transform for away team
    defense_line = team_metrics['defense_line']
    forward_line = team_metrics['forward_line']
    team_median = team_metrics['team_median']
    
    if not is_home:
        defense_line = 120 - defense_line
        forward_line = 120 - forward_line
        team_median = 120 - team_median
    
    # Draw tactical lines (lighter gray for dark background)
    ax.axvline(x=defense_line, color='lightgray', linestyle='dotted', alpha=0.6, linewidth=2, zorder=2)
    ax.axvline(x=forward_line, color='lightgray', linestyle='dotted', alpha=0.6, linewidth=2, zorder=2)
    ax.axvline(x=team_median, color='lightgray', linestyle='--', alpha=0.8, linewidth=2, zorder=2)
    
    # Highlight middle zone
    min_line = min(defense_line, forward_line)
    max_line = max(defense_line, forward_line)
    ymid = [0, 0, 80, 80]
    xmid = [min_line, max_line, max_line, min_line]
    ax.fill(xmid, ymid, color, alpha=0.1, zorder=0)
    
    # Player nodes ON TOP (higher z-order)
    for player_id, row in avg_locs.iterrows():
        marker = 'o' if row['isFirstEleven'] else 's'
        pitch.scatter(row['x_avg'], row['y_avg'], s=1200, marker=marker,
                     color='white', edgecolors=color, linewidth=3, ax=ax, zorder=3)
        
        # Jersey numbers with better visibility
        ax.text(row['x_avg'], row['y_avg'], str(row['shirtNo']),
                ha='center', va='center', fontsize=14, color=color, weight='bold',
                path_effects=[patheffects.withStroke(linewidth=3, foreground='white')], zorder=4)
    
    # Text positioning based on team
    if is_home:
        # Home team - normal positioning
        ax.text(20, 75, "○ = starter\n□ = substitute", 
                fontsize=11, ha='right', va='top', color='white',
                bbox=dict(boxstyle="round,pad=0.3", facecolor=bg_color, edgecolor='white', alpha=0.8))
        ax.text(10, -3, f"Verticality: {team_metrics['verticality']}%", 
                fontsize=12, ha='left', color='white', weight='bold')
        ax.text(70, -3, f"Median: {team_metrics['team_median']:.1f}m", 
                fontsize=12, ha='left', color='white', weight='bold')
    else:
        # Away team - normal positioning (no axis inversion needed)
        ax.text(5, 75, "○ = starter\n□ = substitute", 
                fontsize=11, ha='left', va='top', color='white',
                bbox=dict(boxstyle="round,pad=0.3", facecolor=bg_color, edgecolor='white', alpha=0.8))
        ax.text(110, -3, f"Verticality: {team_metrics['verticality']}%", 
                fontsize=12, ha='right', color='white', weight='bold')
        ax.text(50, -3, f"Median: {team_metrics['team_median']:.1f}m", 
                fontsize=12, ha='right', color='white', weight='bold')
    
    #ax.set_title(f"{team_name} - Passing Network", fontsize=14, color='white')

#------------------------------------------------DEFENSIVE ACTIONS----------------------------------------------
def draw_progressive_pass_map(df, team_id, team_name, team_color, is_away_team=False, ax=None, show_title=True):
    """
    Draw progressive pass map with defensive block aesthetic
    """
    df1= df.copy()

    df1['prog_carry'] = np.where((df1['type'] == 'Carry'), 
                                np.sqrt((105 - df1['x'])**2 + (34 - df1['y'])**2) - np.sqrt((105 - df1['endX'])**2 + (34 - df1['endY'])**2), 0)
    df1['pass_or_carry_angle'] = np.degrees(np.arctan2(df1['endY'] - df1['y'], df1['endX'] - df1['x']))

    # Calculating passing distance, to find out progressive pass
    df1['prog_pass'] = np.where((df1['type'] == 'Pass'), 
                           np.sqrt((105 - df1['x'])**2 + (34 - df1['y'])**2) - np.sqrt((105 - df1['endX'])**2 + (34 - df1['endY'])**2), 0)


    # Filter progressive passes using prog_pass calculation
    dfpro = df1[
        (df1['teamId'] == team_id) & 
        (df1['type'] == 'Pass') &
        (df1['outcomeType'] == 'Successful') &
        (~df1['qualifiers'].astype(str).str.contains('CornerTaken|Freekick', na=False)) & 
        (df1['x'] >= 35) &
        (df1['prog_pass'] >= 9.11)  # Using prog_pass calculation
    ].copy()
    
    # Create pitch with defensive block aesthetic
    pitch = Pitch(  pitch_type='statsbomb',  pitch_color='#0C0D0E',  line_color='white',  linewidth=2,  line_zorder=2,  corner_arcs=True)
    if ax is None:
        fig, ax = pitch.draw(figsize=(10,7))
    else:
        fig = ax.figure
        pitch.draw(ax=ax)
    
    if show_title:
        ax.set_title("PROGRESSIVE PASSES",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)

    ax.set_facecolor('none')
    ax.set_xlim(-0.5, 120.5)
    ax.set_ylim(-0.5, 80.5)
    
    # Invert axes for away team
    if is_away_team:
        ax.invert_xaxis()
        ax.invert_yaxis()
    
    pro_count = len(dfpro)
    
    if pro_count > 0:
        # Calculate zone statistics (StatsBomb coordinates: 0-80 width)
        left_pro = len(dfpro[dfpro['y'] >= 53.33])    # Top third (53.33-80)
        mid_pro = len(dfpro[(dfpro['y'] >= 26.67) & (dfpro['y'] < 53.33)])  # Middle third
        right_pro = len(dfpro[dfpro['y'] < 26.67])    # Bottom third (0-26.67)
        
        left_percentage = round((left_pro/pro_count)*100) if pro_count > 0 else 0
        mid_percentage = round((mid_pro/pro_count)*100) if pro_count > 0 else 0
        right_percentage = round((right_pro/pro_count)*100) if pro_count > 0 else 0
        
        # Add zone dividing lines
        ax.hlines(26.67, xmin=0, xmax=120, colors='white', linestyle='dashed', alpha=0.35)
        ax.hlines(53.33, xmin=0, xmax=120, colors='white', linestyle='dashed', alpha=0.35)
        
        # Text styling matching defensive block
        bbox_props = dict(boxstyle="round,pad=0.3", edgecolor="None", facecolor='#0C0D0E', alpha=0.75)
        
        # Position text annotations
        ax.text(8, 13.335, f'{right_pro}\n({right_percentage}%)', color=team_color, fontsize=24, 
               va='center', ha='center', bbox=bbox_props, weight='bold')
        ax.text(8, 40, f'{mid_pro}\n({mid_percentage}%)', color=team_color, fontsize=24, 
               va='center', ha='center', bbox=bbox_props, weight='bold')
        ax.text(8, 66.67, f'{left_pro}\n({left_percentage}%)', color=team_color, fontsize=24, 
               va='center', ha='center', bbox=bbox_props, weight='bold')
        
        # Plot progressive passes with comet effect
        pitch.lines(dfpro['x'], dfpro['y'], dfpro['endX'], dfpro['endY'], 
                   lw=3.5, comet=True, color=team_color, ax=ax, alpha=0.5)
        
        # Add end points (matching inspirational code styling)
        pitch.scatter(dfpro['endX'], dfpro['endY'], s=35, edgecolor=team_color, 
                     linewidth=1, facecolor='#0C0D0E', zorder=2, ax=ax)
    
    else:
        left_pro = mid_pro = right_pro = 0
        left_percentage = mid_percentage = right_percentage = 0
    
    # Title color matching aesthetic
    counttext = f"Total: {pro_count}"

    if is_away_team:
        ax.text( 112, 4, counttext, color='black', fontsize=13, fontweight='bold', ha='left', va='top',
            bbox=dict( boxstyle='round,pad=0.4', facecolor=team_color, edgecolor='none', alpha=0.75))
    else:
        ax.text( 112, 76, counttext, color='black', fontsize=13, fontweight='bold', ha='right', va='top',
                 bbox=dict( boxstyle='round,pad=0.4', facecolor= team_color, edgecolor='none', alpha=0.75))
        
    return {
        'Team_Name': team_name,
        'Total_Progressive_Passes': pro_count,
        'Progressive_Passes_From_Left': left_pro,
        'Progressive_Passes_From_Center': mid_pro,
        'Progressive_Passes_From_Right': right_pro,
        'Left_Percentage': left_percentage,
        'Center_Percentage': mid_percentage,
        'Right_Percentage': right_percentage
    }

#-------------------------------------------MATCH STATS---------------------------------------
@st.cache_data
def calculate_match_stats(df, hteam_id, ateam_id):
    """
    Calculate match statistics from event data.
    
    Args:
        df: DataFrame containing match events
        hteam_id: Home team ID
        ateam_id: Away team ID
        
    Returns:
        Dictionary containing calculated statistics
    """
    stats = {}
    
    # Helper function to extract qualifiers
    def has_qualifier(event, qualifier_name):
        qualifiers = event.get('qualifiers', [])
        return any(
            q.get('type', {}).get('displayName') == qualifier_name 
            for q in qualifiers if isinstance(q, dict)
        )
    
    # Possession
    home_passes = df[(df['teamId'] == hteam_id) & (df['type'] == 'Pass')]
    away_passes = df[(df['teamId'] == ateam_id) & (df['type'] == 'Pass')]
    total_passes = len(home_passes) + len(away_passes)
    stats['Possession'] = {
        'home': round((len(home_passes) / total_passes) * 100, 2) if total_passes else 0,
        'away': round((len(away_passes) / total_passes) * 100, 2) if total_passes else 0
    }
    
    # Field Tilt
    home_touches = df[(df['teamId'] == hteam_id) & (df['isTouch'] == True) & (df['x'] >= 70)]
    away_touches = df[(df['teamId'] == ateam_id) & (df['isTouch'] == True) & (df['x'] >= 70)]
    total_touches = len(home_touches) + len(away_touches)
    stats['Field Tilt'] = {
        'home': round((len(home_touches) / total_touches) * 100, 2) if total_touches else 0,
        'away': round((len(away_touches) / total_touches) * 100, 2) if total_touches else 0
    }
    
    # Passes (Acc.)
    stats['Passes (Acc.)'] = {
        'home': len(home_passes[home_passes['outcomeType'] == 'Successful']),
        'away': len(away_passes[away_passes['outcomeType'] == 'Successful'])
    }
    
    # LongBalls (Acc.)
    stats['LongBalls (Acc.)'] = {
        'home': len([e for _, e in home_passes.iterrows() 
                    if e['outcomeType'] == 'Successful' and has_qualifier(e, 'Longball')]),
        'away': len([e for _, e in away_passes.iterrows() 
                    if e['outcomeType'] == 'Successful' and has_qualifier(e, 'Longball')])
    }
    
    # Tackles (Wins)
    stats['Tackles (Wins)'] = {
        'home': len(df[(df['teamId'] == hteam_id) & 
                      (df['type'] == 'Tackle') & 
                      (df['outcomeType'] == 'Successful')]),
        'away': len(df[(df['teamId'] == ateam_id) & 
                      (df['type'] == 'Tackle') & 
                      (df['outcomeType'] == 'Successful')])
    }
    
    # Interceptions
    stats['Interceptions'] = {
        'home': len(df[(df['teamId'] == hteam_id) & (df['type'] == 'Interception')]),
        'away': len(df[(df['teamId'] == ateam_id) & (df['type'] == 'Interception')])
    }
    
    # Clearances
    stats['Clearance'] = {
        'home': len(df[(df['teamId'] == hteam_id) & (df['type'] == 'Clearance')]),
        'away': len(df[(df['teamId'] == ateam_id) & (df['type'] == 'Clearance')])
    }
    
    # Aerials (Wins)
    stats['Aerials (Wins)'] = {
        'home': len(df[(df['teamId'] == hteam_id) & 
                      (df['type'] == 'Aerial') & 
                      (df['outcomeType'] == 'Successful')]),
        'away': len(df[(df['teamId'] == ateam_id) & 
                      (df['type'] == 'Aerial') & 
                      (df['outcomeType'] == 'Successful')])
    }
    
    # PPDA
    home_def_actions = df[(df['teamId'] == hteam_id) & 
                        (df['type'].isin(['Interception', 'Tackle', 'Foul', 'Challenge'])) &
                        (df['x'] > 35)]
    
    away_def_actions = df[(df['teamId'] == ateam_id) & 
                        (df['type'].isin(['Interception', 'Tackle', 'Foul', 'Challenge'])) &
                        (df['x'] > 35)]
    
    home_passes_ppda = df[(df['teamId'] == hteam_id) & 
                        (df['type'] == 'Pass') & 
                        (df['outcomeType'] == 'Successful') &
                        (df['x'] < 70)]
    
    away_passes_ppda = df[(df['teamId'] == ateam_id) & 
                        (df['type'] == 'Pass') & 
                        (df['outcomeType'] == 'Successful') &
                        (df['x'] < 70)]
    
    stats['PPDA'] = {
        'home': round(len(away_passes_ppda) / len(home_def_actions), 2) if len(home_def_actions) > 0 else 0,
        'away': round(len(home_passes_ppda) / len(away_def_actions), 2) if len(away_def_actions) > 0 else 0
    }
    
    return stats

def plot_match_stats_styled(stats, color_home, color_away, home_team_name="Home", away_team_name="Away", ax=None , show_title=False):
    """
    Plot match statistics with your signature dark aesthetic style
    """
    # Signature colors
    bg_color = 'none'  # Dark background
    line_color = 'white'  # White text/lines

    # Extract data from stats dictionary
    stat_names = list(stats.keys())
    home_values = [stats[stat]['home'] for stat in stat_names]
    away_values = [stats[stat]['away'] for stat in stat_names]
    
    # Calculate normalized values for bars
    normalized_home = []
    normalized_away = []
    
    for i, stat in enumerate(stat_names):
        home_val = home_values[i]
        away_val = away_values[i]
        total = home_val + away_val
        
        if total > 0:
            home_norm = -(home_val / total) * 50  # Negative for left side
            away_norm = (away_val / total) * 50   # Positive for right side
        else:
            home_norm = away_norm = 0
            
        normalized_home.append(home_norm)
        normalized_away.append(away_norm)
       
    # Draw pitch background 
    pitch = Pitch(pitch_type='uefa', corner_arcs=True, pitch_color=bg_color, 
                  line_color=bg_color, linewidth=2)
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10,7))
        fig.set_facecolor('none')
    else:
        pitch.draw(ax=ax)
        fig = ax.figure 

    if show_title:
        ax.set_title(
            "MATCH STATS COMPARISON",
            color='white',
            fontsize=25,
            fontweight='bold'
        )
    ax.set_facecolor('none')
    ax.set_xlim(-0.5, 105.5)
    ax.set_ylim(-5, 68.5)
    
    # Header box
    #head_y = [62, 68, 68, 62]
    #head_x = [0, 0, 105, 105]
    #ax.fill(head_x, head_y, 'orange')
    
    # Path effects for text
    path_eff = [path_effects.Stroke(linewidth=1.5, foreground=line_color), 
                path_effects.Normal()]
    path_eff1 = [path_effects.Stroke(linewidth=1.5, foreground=line_color), 
                 path_effects.Normal()]
    
    # ax.text(52.5, 64.5, "Match Stats Comparison", ha='center', va='center', 
    #         color=line_color, fontsize=25, fontweight='bold', path_effects=path_eff)
    
    # Y positions for stats 
    stats_y_positions = [58 - (i * 6) for i in range(len(stat_names))]
    
    # Draw bars
    start_x = 52.5
    ax.barh(stats_y_positions, normalized_home, height=4, color=color_home, left=start_x)
    ax.barh(stats_y_positions, normalized_away, height=4, left=start_x, color=color_away)
    
    # Clean up axis (remove all axis elements)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='both', which='both', bottom=False, top=False, 
                   left=False, right=False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add stat labels in center
    for i, (stat_name, y_pos) in enumerate(zip(stat_names, stats_y_positions)):
        ax.text(52.5, y_pos, stat_name, color='black', fontsize=17, 
                ha='center', va='center', fontweight='bold', path_effects=path_eff1)
    
    # Add values on left (home) and right (away)
    for i, (home_val, away_val, y_pos) in enumerate(zip(home_values, away_values, stats_y_positions)):
        # Format values based on stat type
        if 'Possession' in stat_names[i] or 'Field Tilt' in stat_names[i]:
            home_text = f"{round(home_val)}%"
            away_text = f"{round(away_val)}%"
        elif 'Passes' in stat_names[i] or 'LongBalls' in stat_names[i] or 'Tackles' in stat_names[i] or 'Aerials' in stat_names[i]:
            # Assuming format like "total(successful)" - you may need to adjust this
            home_text = f"{home_val}"
            away_text = f"{away_val}"
        else:
            home_text = f"{home_val}"
            away_text = f"{away_val}"
            
        # Home team values (left side)
        ax.text(0, y_pos, home_text, color=line_color, fontsize=20, 
                ha='right', va='center', fontweight='bold')
        # Away team values (right side)
        ax.text(105, y_pos, away_text, color=line_color, fontsize=20, 
                ha='left', va='center', fontweight='bold')
    
    return fig,  ax

#------------------------------------------------DEFESNIVE ACTIONS----------------------------------------------
@st.cache_data
def filter_defensive_actions(df_events: pd.DataFrame) -> pd.DataFrame:
    """
    Filter events to get only defensive actions using type.
    
    Args:
        df_events: DataFrame with match events
        
    Returns:
        DataFrame containing only defensive actions
    """
    # Use type (not type) and include all defensive actions from your data
    defensive_types = [
        'Tackle', 'Interception', 'BallRecovery', 'BlockedPass', 
        'Challenge', 'Clearance', 'Foul', 'Aerial'
    ]
    
    defensive_actions = df_events[
        df_events['type'].isin(defensive_types)
    ].copy()
    
    # Convert coordinates from WhoScored (0-100) to StatsBomb (0-120x0-80)
    defensive_actions['x_sb'] = defensive_actions['x'] * 1.2
    defensive_actions['y_sb'] = defensive_actions['y'] * 0.8
    
    return defensive_actions

@st.cache_data
def create_player_info(player: dict) -> dict:
    """Create standardized player info from team data."""
    return {
        'id': player['playerId'],
        'name': player['name'],
        'position': player['position'],
        'shirt_no': player['shirtNo'],
        'is_starter': player.get('isFirstEleven', False)
    }

@st.cache_data
def calculate_player_defensive_positions(defensive_actions: pd.DataFrame, 
                                       team_id: int, 
                                       team_players: list) -> dict:
    """
    Calculate average defensive positions and action counts for each player.
    """
    # Filter actions for this team
    team_actions = defensive_actions[defensive_actions['teamId'] == team_id]
    
    if len(team_actions) == 0:
        return {}
    
    # Create player info lookup
    player_info = {p['playerId']: create_player_info(p) for p in team_players}
    
    # Calculate player statistics
    player_stats = (
        team_actions.groupby('playerId')
        .agg({
            'x_sb': 'median',  # Use median like inspirational code
            'y_sb': 'median',
            'id': 'count'
        })
        .round(2)
        .rename(columns={'id': 'action_count'})
    )
    
    # Combine with player info
    positions = {}
    for player_id, stats in player_stats.iterrows():
        if player_id in player_info:
            positions[player_id] = {
                'x': stats['x_sb'],
                'y': stats['y_sb'],
                'action_count': stats['action_count'],
                'name': player_info[player_id]['name'],
                'position': player_info[player_id]['position'],
                'shirt_no': player_info[player_id]['shirt_no'],
                'is_starter': player_info[player_id]['is_starter']
            }
    
    return positions

def defensive_block(team_positions: dict, team_actions: pd.DataFrame, 
                   team_name: str, team_color: str, is_away_team: bool = False, ax=None, title=None):
    """
    Create defensive block visualization for one team - 
    """
    # Create pitch - following inspirational code exactly
    pitch = Pitch(
        pitch_type='statsbomb',  # Changed to statsbomb for my data
        pitch_color='none',
        line_color='white',
        linewidth=2,
        line_zorder=2,
        corner_arcs=True
    )
    if ax is None:
        fig, ax = pitch.draw(figsize=(10,7))
    else:
        fig = ax.figure
        pitch.draw(ax=ax)

    if title is None:
        ax.set_title(" ",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)
    else:
        ax.set_title("DEFENSIVE ACTIONS HEATMAP",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)

    ax.set_facecolor('none')
    ax.set_xlim(-0.5, 120.5)  # StatsBomb dimensions
    ax.set_ylim(-0.5, 80.5)
    
    if len(team_positions) == 0 or len(team_actions) == 0:
        ax.set_title(f"{team_name}\nDefensive Action Heatmap", 
                    color='white', fontsize=20, fontweight='bold')
        return {}
    
    # Convert positions to DataFrame for easier manipulation
    positions_df = pd.DataFrame.from_dict(team_positions, orient='index')
    
    # Variable marker size based on defensive actions - FAITHFUL TO INSPIRATIONAL
    MAX_MARKER_SIZE = 3500
    positions_df['marker_size'] = (
        positions_df['action_count'] / positions_df['action_count'].max() * MAX_MARKER_SIZE
    )
    
    # Create KDE heatmap - 
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.colors import to_rgba
    import numpy as np
    
    color = np.array(to_rgba(team_color))
    flamingo_cmap = LinearSegmentedColormap.from_list(
        "Team colors", ['#0C0D0E', team_color], N=500
    )
    
    # KDE plot 
    kde = pitch.kdeplot(
        team_actions['x_sb'], team_actions['y_sb'], 
        ax=ax, fill=True, levels=5000, thresh=0.02, cut=4, cmap=flamingo_cmap
    )
    
    # Plot player nodes 
    for idx, row in positions_df.iterrows():
        if row['is_starter']:
            marker = 'o'  # Circle for starters
        else:
            marker = 's'  # Square for substitutes
            
        pitch.scatter(
            row['x'], row['y'], 
            s=row['marker_size'] + 100,
            marker=marker, 
            color='#0C0D0E',
            edgecolor='white',
            linewidth=1,
            alpha=1, 
            zorder=3, 
            ax=ax
        )
    
    # Plot tiny scatter for defensive actions
    pitch.scatter(
        team_actions['x_sb'], team_actions['y_sb'],
        s=10, marker='x', color='yellow', alpha=0.2, ax=ax
    )
    
    # Add shirt numbers
    for idx, row in positions_df.iterrows():
        pitch.annotate(
            str(row['shirt_no']), 
            xy=(row['x'], row['y']),
            c='white', ha='center', va='center', size=14, ax=ax
        )
    
    # Calculate metrics
    dah = round(positions_df['x'].mean(), 2)  # Defensive Actions Height
    dah_show = round((dah * 1.05), 2)
    
    # Defense line height (center backs)
    center_backs = positions_df[positions_df['position'] == 'DC']
    if len(center_backs) > 0:
        def_line_h = round(center_backs['x'].median(), 2)
    else:
        def_line_h = dah
    
    # Forward line height (top 2 advanced players)
    starters = positions_df[positions_df['is_starter'] == True]
    if len(starters) >= 2:
        forwards = starters.nlargest(2, 'x')
        fwd_line_h = round(forwards['x'].mean(), 2)
    else:
        fwd_line_h = dah
    
    # Calculate compactness
    compactness = round((1 - ((fwd_line_h - def_line_h) / 120)) * 100, 2)
    
    # Add vertical lines 
    ax.axvline(x=dah, color='gray', linestyle='--', alpha=0.75, linewidth=2)
    ax.axvline(x=def_line_h, color='gray', linestyle='dotted', alpha=0.5, linewidth=2)
    ax.axvline(x=fwd_line_h, color='gray', linestyle='dotted', alpha=0.5, linewidth=2)
    
    # Invert axes for away team 
    if is_away_team:
        ax.invert_xaxis()
        ax.invert_yaxis()
        ax.text(dah-1, 83, f"{dah_show}m", fontsize=15, color='white', ha='left', va='center')
        ax.text(115, 83, f'Compact: {compactness}%', fontsize=15, color='white', ha='left', va='center')
        ax.text(2, 2, "circle = starter\nbox = sub", color='gray', size=12, ha='right', va='top')
    else:
        ax.text(dah-1, -3, f"{dah_show}m", fontsize=15, color='white', ha='right', va='center')
        ax.text(115, -3, f'Compact: {compactness}%', fontsize=15, color='white', ha='right', va='center')
        ax.text(2, 78, "circle = starter\nbox = sub", color='gray', size=12, ha='left', va='top')
    
    # Set title 
    # ax.set_title(f"{team_name}\nDefensive Action Heatmap", 
    #             color='white', fontsize=20, fontweight='bold')
    
    return {
        'Team_Name': team_name,
        'Average_Defensive_Action_Height': dah,
        'Forward_Line_Pressing_Height': fwd_line_h,
        'Compactness': compactness
    }

@st.cache_data
def create_defensive_heatmap_analysis(df_events: pd.DataFrame, home_team: dict,  away_team: dict) -> tuple:
    """
    Complete defensive heatmap analysis 
    """
    # Filter defensive actions
    defensive_actions = filter_defensive_actions(df_events)
    # print(f"Found {len(defensive_actions)} defensive actions")
    
    # Get player positions for both teams
    home_positions = calculate_player_defensive_positions(defensive_actions, home_team['team_id'], home_team['players'])
    away_positions = calculate_player_defensive_positions(defensive_actions, away_team['team_id'], away_team['players'])
    
    # Filter team actions
    home_actions = defensive_actions[defensive_actions['teamId'] == home_team['team_id']]
    away_actions = defensive_actions[defensive_actions['teamId'] == away_team['team_id']]
    
    return home_positions, away_positions, home_actions, away_actions
    


#----------------------------------------------------Team's Dominating Zone---------------------------------
def plot_congestion( df, home_team,away_team, color_home, color_away,  ax=None, show_title=False):
    bg_color= '#0C0D0E'

    pcmap = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",  [color_home, 'gray', color_away], N=20)

    df1 = df[(df['nameTeam']==home_team) & (df['isTouch']==1) & (~df['qualifiers'].str.contains('CornerTaken|Freekick|ThrowIn',na=False))]
    df2 = df[(df['nameTeam']==away_team) & (df['isTouch']==1) & (~df['qualifiers'].str.contains('CornerTaken|Freekick|ThrowIn',na=False))]
    df2['x'] = 105-df2['x']
    df2['y'] =  68-df2['y']
    pitch = Pitch(pitch_type='uefa', corner_arcs=True, pitch_color='none', line_color='white', linewidth=2, line_zorder=6)
    if ax is None:
        fig, ax = plt.subplots(figsize=(10,7))
    else:
        fig = ax.figure
    
    if show_title:
        ax.set_title("TEAM'S DOMINATING ZONE",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff,  y=1.075)
        
    pitch.draw(ax=ax)
    fig.set_facecolor('none')
    ax.set_facecolor('none')

    ax.set_ylim(-0.5,68.5)
    ax.set_xlim(-0.5,105.5)

    bin_statistic1 = pitch.bin_statistic(df1.x, df1.y, bins=(6,5), statistic='count', normalize=False)
    bin_statistic2 = pitch.bin_statistic(df2.x, df2.y, bins=(6,5), statistic='count', normalize=False)

    # Assuming 'cx' and 'cy' are as follows:
    cx = np.array([[ 8.75, 26.25, 43.75, 61.25, 78.75, 96.25],
               [ 8.75, 26.25, 43.75, 61.25, 78.75, 96.25],
               [ 8.75, 26.25, 43.75, 61.25, 78.75, 96.25],
               [ 8.75, 26.25, 43.75, 61.25, 78.75, 96.25],
               [ 8.75, 26.25, 43.75, 61.25, 78.75, 96.25]])

    cy = np.array([[61.2, 61.2, 61.2, 61.2, 61.2, 61.2],
               [47.6, 47.6, 47.6, 47.6, 47.6, 47.6],
               [34.0, 34.0, 34.0, 34.0, 34.0, 34.0],
               [20.4, 20.4, 20.4, 20.4, 20.4, 20.4],
               [ 6.8,  6.8,  6.8,  6.8,  6.8,  6.8]])

    # Flatten the arrays
    cx_flat = cx.flatten()
    cy_flat = cy.flatten()

    # Create a DataFrame
    df_cong = pd.DataFrame({'cx': cx_flat, 'cy': cy_flat})

    hd_values = []


    # Loop through the 2D arrays
    for i in range(bin_statistic1['statistic'].shape[0]):
        for j in range(bin_statistic1['statistic'].shape[1]):
            stat1 = bin_statistic1['statistic'][i, j]
            stat2 = bin_statistic2['statistic'][i, j]
        
            if (stat1 / (stat1 + stat2)) > 0.55:
                hd_values.append(1)
            elif (stat1 / (stat1 + stat2)) < 0.45:
                hd_values.append(0)
            else:
                hd_values.append(0.5)

    df_cong['hd']=hd_values
    bin_stat = pitch.bin_statistic(df_cong.cx, df_cong.cy, bins=(6,5), values=df_cong['hd'], statistic='sum', normalize=False)
    pitch.heatmap(bin_stat, ax=ax, cmap=pcmap, edgecolors='#000000', lw=0, zorder=3, alpha=0.85)

    ax_text(52.5, 71, s=f"<{home_team}>  |  Contested  |  <{away_team}>", highlight_textprops=[{'color':color_home}, {'color':color_away}],
            color='gray', fontsize=11, ha='center', va='center', ax=ax)
    #ax.set_title("Team's Dominating Zone", color='white', fontsize=30, fontweight='bold', y=1.075)
    ax.text(0,  -3, 'Attacking Direction--->', color=color_home, fontsize=9, ha='left', va='center')
    ax.text(105,-3, '<---Attacking Direction', color=color_away, fontsize=9, ha='right', va='center')

    ax.vlines(1*(105/6), ymin=0, ymax=68, color='black', lw=2, ls='--', zorder=5)
    ax.vlines(2*(105/6), ymin=0, ymax=68, color='black', lw=2, ls='--', zorder=5)
    ax.vlines(3*(105/6), ymin=0, ymax=68, color='black', lw=2, ls='--', zorder=5)
    ax.vlines(4*(105/6), ymin=0, ymax=68, color='black', lw=2, ls='--', zorder=5)
    ax.vlines(5*(105/6), ymin=0, ymax=68, color='black', lw=2, ls='--', zorder=5)

    ax.hlines(1*(68/5), xmin=0, xmax=105, color='black', lw=2, ls='--', zorder=5)
    ax.hlines(2*(68/5), xmin=0, xmax=105, color='black', lw=2, ls='--', zorder=5)
    ax.hlines(3*(68/5), xmin=0, xmax=105, color='black', lw=2, ls='--', zorder=5)
    ax.hlines(4*(68/5), xmin=0, xmax=105, color='black', lw=2, ls='--', zorder=5)
    
    return fig, ax


#-----------------------------PASS END ZONES------------------------------------------------
def Pass_end_zone( df,  team_name,  cm, ax=None,show_title=False):
    bg_color= '#0C0D0E'
    path_eff = [path_effects.Stroke(linewidth=3, foreground='white'), path_effects.Normal()]
    # setting the custom colormap
    pez = df[(df['nameTeam'] == team_name) & (df['type'] == 'Pass') & (df['outcomeType'] == 'Successful')].copy()

    pitch = Pitch(pitch_type='opta', line_color='white', goal_type='box', goal_alpha=.5, corner_arcs=True, line_zorder=2, pitch_color='none', linewidth=2)
    if ax is None:
        fig, ax = plt.subplots(figsize=(10,7))
    else:
        fig = ax.figure
        pitch.draw(ax=ax)

    if show_title:
        ax.set_title("PASS END ZONE",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)
        
    ax.set_xlim(-0.5, 105.5)
    if team_name == team_name:
      ax.invert_xaxis()
      ax.invert_yaxis()

    pearl_earring_cmap = cm
    # binning the data points

    bin_statistic = pitch.bin_statistic(pez.endX, pez.endY, bins=(6, 5), normalize=True)
    pitch.heatmap(bin_statistic, ax=ax, cmap=pearl_earring_cmap, edgecolors=bg_color)
    pitch.scatter(pez.endX, pez.endY, c='gray', alpha=0.5, s=5, ax=ax)
    labels = pitch.label_heatmap(bin_statistic, color='black', fontsize=25, ax=ax, ha='center', va='center', str_format='{:.0%}', path_effects=path_eff)
    
    # # Headings and other texts
    # if team_name ==  team_name:
    #   ax.set_title(f"{team_name}\nPass End Zone", color=color_home, fontsize=25, fontweight='bold')
    # else:
    #   ax.set_title(f"{team_name}\nPass End Zone", color=color_away, fontsize=25, fontweight='bold')

#------------------------------------------------zone14hs---------------------------------------------------------
def zone14hs(ax, df, team_name, col):
    bg_color= '#0C0D0E'
    dfhp = df[(df['nameTeam']==team_name) & (df['type']=='Pass') & (df['outcomeType']=='Successful') & 
              (~df['qualifiers'].str.contains('CornerTaken|Freekick', na=False))].copy()
    
    pitch = Pitch(pitch_type='uefa', pitch_color='none', line_color='white',  linewidth=2,
                          corner_arcs=True)
    pitch.draw(ax=ax)
    ax.set_xlim(-0.5, 105.5)
    ax.set_facecolor('none')
    if team_name == team_name:
      ax.invert_xaxis()
      ax.invert_yaxis()

    # setting the count varibale
    z14 = 0
    hs = 0
    lhs = 0
    rhs = 0

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]
    # iterating ecah pass and according to the conditions plotting only zone14 and half spaces passes
    for index, row in dfhp.iterrows():
        if row['endX'] >= 70 and row['endX'] <= 88.54 and row['endY'] >= 22.66 and row['endY'] <= 45.32:
            pitch.lines(row['x'], row['y'], row['endX'], row['endY'], color='orange', comet=True, lw=3, zorder=3, ax=ax, alpha=0.75)
            ax.scatter(row['endX'], row['endY'], s=35, linewidth=1, color=bg_color, edgecolor='orange', zorder=4)
            z14 += 1
        if row['endX'] >= 70 and row['endY'] >= 11.33 and row['endY'] <= 22.66:
            pitch.lines(row['x'], row['y'], row['endX'], row['endY'], color=col, comet=True, lw=3, zorder=3, ax=ax, alpha=0.75)
            ax.scatter(row['endX'], row['endY'], s=35, linewidth=1, color=bg_color, edgecolor=col, zorder=4)
            hs += 1
            rhs += 1
        if row['endX'] >= 70 and row['endY'] >= 45.32 and row['endY'] <= 56.95:
            pitch.lines(row['x'], row['y'], row['endX'], row['endY'], color=col, comet=True, lw=3, zorder=3, ax=ax, alpha=0.75)
            ax.scatter(row['endX'], row['endY'], s=35, linewidth=1, color=bg_color, edgecolor=col, zorder=4)
            hs += 1
            lhs += 1

    # coloring those zones in the pitch
    y_z14 = [22.66, 22.66, 45.32, 45.32]
    x_z14 = [70, 88.54, 88.54, 70]
    ax.fill(x_z14, y_z14, 'orange', alpha=0.2, label='Zone14')

    y_rhs = [11.33, 11.33, 22.66, 22.66]
    x_rhs = [70, 105, 105, 70]
    ax.fill(x_rhs, y_rhs, col, alpha=0.2, label='HalfSpaces')

    y_lhs = [45.32, 45.32, 56.95, 56.95]
    x_lhs = [70, 105, 105, 70]
    ax.fill(x_lhs, y_lhs, col, alpha=0.2, label='HalfSpaces')

    # showing the counts in an attractive way
    z14name = "Zone14"
    hsname = "HalfSp"
    z14count = f"{z14}"
    hscount = f"{hs}"
    ax.scatter(16.46, 13.85, color=col, s=15000, edgecolor='white', linewidth=2, alpha=1, marker='h')
    ax.scatter(16.46, 54.15, color='orange', s=15000, edgecolor='white', linewidth=2, alpha=1, marker='h')
    ax.text(16.46, 13.85-4, hsname, fontsize=20, color='white', ha='center', va='center', path_effects=path_eff)
    ax.text(16.46, 54.15-4, z14name, fontsize=20, color='white', ha='center', va='center', path_effects=path_eff)
    ax.text(16.46, 13.85+2, hscount, fontsize=40, color='white', ha='center', va='center', path_effects=path_eff)
    ax.text(16.46, 54.15+2, z14count, fontsize=40, color='white', ha='center', va='center', path_effects=path_eff)

    # Headings and other texts
    # if col == col:
    #   ax.set_title(f"{team_name}\nZone14 & Halfsp. Pass", color=col, fontsize=25, fontweight='bold')
    # else:
    #   ax.set_title(f"{team_name}\nZone14 & Halfsp. Pass", color=col, fontsize=25, fontweight='bold')

    return {
        'Team_Name': team_name,
        'Total_Passes_Into_Zone14': z14,
        'Passes_Into_Halfspaces': hs,
        'Passes_Into_Left_Halfspaces': lhs,
        'Passes_Into_Right_Halfspaces': rhs
    }

#-------------------------------------------GOALS POST (GK------------------------------------------------------
@st.cache_data
def prepare_df_shotsgoal(df, name_home , name_away):
    df['render_team'] = df['teamName']

    mask = df['isOwnGoal'].eq(True)

    home= name_home
    away = name_away
    team_swap = {
        home: away,
        away: home
    }

    df.loc[mask, 'render_team'] = (
        df.loc[mask, 'teamName'].map(team_swap)
    )
    hShotsdf = df[df['render_team']==name_home].reset_index(drop=True).copy()
    aShotsdf = df[df['render_team']==name_away].reset_index(drop=True).copy() 

    df_coords_h = hShotsdf['onGoalShot'].apply(pd.Series)

    df_coords_h = df_coords_h.rename(columns={
        'x': 'coord_x',
        'y': 'coord_y',
        'zoomRatio': 'coord_zoom'
    })
    df_tiros_coord_home = pd.concat([hShotsdf.drop(columns=['onGoalShot']), df_coords_h], axis=1)

    df_coordsa = aShotsdf['onGoalShot'].apply(pd.Series)

    df_coordsa = df_coordsa.rename(columns={
        'x': 'coord_x',
        'y': 'coord_y',
        'zoomRatio': 'coord_zoom'
    })
    df_tiros_coord_away = pd.concat([aShotsdf.drop(columns=['onGoalShot']), df_coordsa], axis=1)

    return df_tiros_coord_home, df_tiros_coord_away

def draw_goal( df, title, color, imagen_pelota_path, imagen_pelota_red_path, ax=None):
    

    ax.set_xlim(0, 2)
    ax.set_ylim(0, 0.68)
    ax.set_facecolor('black')
    ax.patch.set_alpha(0)
    ax.set_aspect("equal")
    ax.axis("off")

    # césped
    ax.fill_between([0, 2], 0, -0.06, color="green", alpha=0.3)

    # marco
    post_width = 0.03
    goal_height = 0.65
    goal_width = 1.99

    ax.add_patch(patches.Rectangle((0.01, 0), post_width, goal_height, color="white", zorder=1))
    ax.add_patch(patches.Rectangle((goal_width - post_width, 0), post_width, goal_height, color="white", zorder=1))
    ax.add_patch(patches.Rectangle((0.01, goal_height - 0.015), goal_width - 0.02, 0.015, color="white", zorder=1))

    # red
    num_lines = 6
    for i in range(1, num_lines):
        x = i * goal_width / num_lines
        ax.plot([x, x], [0, goal_height], color="lightgray", lw=0.5, zorder=0)

    for j in range(1, int(goal_height * 20)):
        y = j * goal_height / (goal_height * 20)
        ax.plot([0.01, goal_width - 0.01], [y, y], color="lightgray", lw=0.5, zorder=0)

    # tiros
    for _, row in df.iterrows():

        # ---------------------------
        # GOAL NORMAL vs OWN GOAL
        # ---------------------------
        if row["type"] == "Goal":

            # si es own goal → pelota roja
            if row.get("isOwnGoal", False):

                im = OffsetImage(imagen_pelota_red_path, zoom=0.02)

            # goal normal → pelota normal
            else:
                im = OffsetImage(imagen_pelota_path, zoom=0.03)

            ab = AnnotationBbox(
                im,
                (row["coord_x"], row["coord_y"]),
                frameon=False,
                zorder=10
            )

            ax.add_artist(ab)

        # ---------------------------
        # SAVED SHOT
        # ---------------------------
        elif row["type"] == "SavedShot" and not row["isBlocked"]:
            ax.scatter(
                row["coord_x"], row["coord_y"],
                s=350, alpha=0.6,
                color='red', edgecolors="white"
            )

        # ---------------------------
        # POST
        # ---------------------------
        elif row["type"] in ["Post", "ShotOnPost"]:
            ax.scatter(
                row["coord_x"], row["coord_y"],
                s=350, alpha=0.6,
                color='orange', edgecolors="white"
            )


    ax.set_title(title, fontsize=20, fontweight="bold", color=color, pad=8)


def plot_gk(df_home, df_away, color_home,color_away,  imagen_pelota_path, imagen_pelota_red_path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9), facecolor='none')

    draw_goal( df_away,  "HOME GK SAVES", color_home,imagen_pelota_path, imagen_pelota_red_path, ax=ax1)
    draw_goal( df_home, "AWAY GK SAVES", color_away, imagen_pelota_path, imagen_pelota_red_path, ax= ax2)

    return fig

#-------------------------------------CHANCE CREATING ZONE-----------------------------------------------------------------
def Chance_creating_zone( df, matchdict, team_name, cm, col , color_home, color_away, ax=None, title= False):
    bg_color= '#0C0D0E'
  
    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    pitch = Pitch(pitch_type='opta', line_color='white', corner_arcs=True, line_zorder=2, pitch_color='none', linewidth=2)
    if ax is None:
        fig, ax = plt.subplots(figsize=(10,7))
    else:
        fig = ax.figure
    pitch.draw(ax=ax)

    if title is False:
        ax.set_title(" ",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)
    else:
        ax.set_title("CHANCE CREATING ZONE",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)   
    fig.set_facecolor('none')
    ax.set_facecolor('none')
    ax.set_xlim(-0.5, 105.5)

    if team_name ==   matchdict['away']['name']:
            ax.invert_xaxis()
            ax.invert_yaxis()

    cc = 0
    pearl_earring_cmap = cm

    home_cross = df[df['nameTeam']==team_name]
    home_keypass= home_cross[home_cross['satisfiedEventsTypes'].apply(lambda x: 123 in x)].reset_index(drop=True)

    bin_statistic = pitch.bin_statistic(home_keypass.x, home_keypass.y, bins=(6,5), statistic='count', normalize=False)
    pitch.heatmap(bin_statistic, ax=ax, cmap=pearl_earring_cmap, edgecolors='grey')

    for index, row in home_keypass.iterrows():
        if 'IntentionalGoalAssist' in row['qualifiers']:
            pitch.lines(row['x'], row['y'], row['endX'], row['endY'], color='green', comet=True, lw=3, zorder=3, ax=ax)
            ax.scatter(row['endX'], row['endY'], s=35, linewidth=1, color='white', edgecolor='green', zorder=4)
            cc += 1
        else :
            pitch.lines(row['x'], row['y'], row['endX'], row['endY'], color='violet', comet=True, lw=3, zorder=3, ax=ax)
            ax.scatter(row['endX'], row['endY'], s=35, linewidth=1, color='white', edgecolor='violet', zorder=4)
            cc += 1
    labels = pitch.label_heatmap(bin_statistic, color='white', fontsize=25, ax=ax, ha='center', va='center', str_format='{:.0f}', path_effects=path_eff)

    if col == color_home:
        ax.text(100,-5.4, "violet = key pass\ngreen = assist", color=color_home, size=15, ha='right', va='center')
        ax.text(52.5,103, f"Total Chances Created = {cc}", color=color_home, fontsize=15, ha='center', va='center')
    else:
        ax.text(99,106, "violet = key pass\ngreen = assist", color=color_away, size=15, ha='left', va='center')
        ax.text(53,-2.5, f"Total Chances Created = {cc}", color=color_away, fontsize=15, ha='center', va='center')
    
    return fig, ax

#------------------------------------------CROSSES-------------------------------------------------------------------
def Crosses( df, matchdict, color_home, color_away, ax=None, show_title= False):
    pitch = Pitch(pitch_type='opta', corner_arcs=True, pitch_color='none', line_color='white', linewidth=2)
    if ax is None:
        fig, ax = pitch.draw(figsize=(10, 7))
    else:
        fig = ax.figure
        pitch.draw(ax=ax)
        
    if show_title:
        ax.set_title("CROSSES",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)

    

    fig.set_facecolor('none')
    ax.set_facecolor('none')
    mask_corner = df['qualifiers'].apply(
    lambda qs: any(q.get('type', {}).get('displayName') == 'CornerTaken'
                   for q in qs))
    home_cross_Unsuccessful= df[ df['satisfiedEventsTypes'].apply(lambda x: 126 in x)& (df['nameTeam'] == matchdict['home']['name'])& (~mask_corner)]
    home_cross_successful= df[df['satisfiedEventsTypes'].apply(lambda x: 125 in x)& (df['nameTeam'] == matchdict['home']['name'])& (~mask_corner)]

    away_cross_Unsuccessful= df[ df['satisfiedEventsTypes'].apply(lambda x: 126 in x)& (df['nameTeam'] == matchdict['away']['name'])& (~mask_corner)]
    away_cross_successful= df[df['satisfiedEventsTypes'].apply(lambda x: 125 in x)& (df['nameTeam'] == matchdict['away']['name'])& (~mask_corner)]

   
    hsuc = 0
    hunsuc = 0
    asuc = 0
    aunsuc = 0

    # iterating through each pass and coloring according to successful or not
    for index, row in home_cross_successful.iterrows():
        arrow = patches.FancyArrowPatch((100-row['x'], 100-row['y']), (100-row['endX'], 100-row['endY']), arrowstyle='->', mutation_scale=15, color=color_home, linewidth=1.5, zorder=3, alpha=1)
        ax.add_patch(arrow)
        hsuc += 1

    for index, row in home_cross_Unsuccessful.iterrows():
            
        arrow = patches.FancyArrowPatch((100-row['x'], 100-row['y']), (100-row['endX'], 100-row['endY']), arrowstyle='->', mutation_scale=10, color='lightgrey', linewidth=1, zorder=2, alpha=.25)
        ax.add_patch(arrow)
        hunsuc += 1

    for index, row in away_cross_successful.iterrows():
        
            arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['endX'], row['endY']), arrowstyle='->', mutation_scale=15, color=color_away, linewidth=1.5, zorder=3, alpha=1)
            ax.add_patch(arrow)
            asuc += 1
    for index, row in away_cross_Unsuccessful.iterrows():
            arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['endX'], row['endY']), arrowstyle='->', mutation_scale=10, color='lightgrey', linewidth=1, zorder=2, alpha=.25)
            ax.add_patch(arrow)
            aunsuc += 1

    home_cross = pd.concat([home_cross_successful, home_cross_Unsuccessful])
    away_cross = pd.concat([away_cross_successful, away_cross_Unsuccessful])
    # Headlines and other texts
    home_left = len(home_cross[home_cross['y']>=50])
    home_right = len(home_cross[home_cross['y']<50])
    away_left = len(away_cross[away_cross['y']>=50])
    away_right = len(away_cross[away_cross['y']<50])

    ax.text(49, 2, f"Crosses from\nLeftwing: {home_left}", color=color_home, fontsize=15, va='bottom', ha='right')
    ax.text(49, 98, f"Crosses from\nRightwing: {home_right}", color=color_home, fontsize=15, va='top', ha='right')
    ax.text(51, 98, f"Crosses from\nLeftwing: {away_left}", color=color_away, fontsize=15, va='top', ha='left')
    ax.text(51, 2, f"Crosses from\nRightwing: {away_right}", color=color_away, fontsize=15, va='bottom', ha='left')

    ax.text(0,-2, f"Successful: {hsuc}", color=color_home, fontsize=13, ha='left', va='top')
    ax.text(0,-5.5, f"Unsuccessful: {hunsuc}", color=line_color, fontsize=13, ha='left', va='top')
    ax.text(100,-2, f"Successful: {asuc}", color=color_away, fontsize=13, ha='right', va='top')
    ax.text(100,-5.5, f"Unsuccessful: {aunsuc}", color=line_color, fontsize=13, ha='right', va='top')

    ax.text(0, 103, f"<---Crosses", color=color_home, size=13, ha='left', fontweight='bold')
    ax.text(100,103, f"Crosses--->", color=color_away, size=13, ha='right', fontweight='bold')

    home_data = {
        'Team_Name': matchdict['home']['name'],
        'Total_Cross': hsuc + hunsuc,
        'Successful_Cross': hsuc,
        'Unsuccessful_Cross': hunsuc,
        'Cross_From_LeftWing': home_left,
        'Cross_From_RightWing': home_right
    }
    
    away_data = {
        'Team_Name': matchdict['away']['name'],
        'Total_Cross': asuc + aunsuc,
        'Successful_Cross': asuc,
        'Unsuccessful_Cross': aunsuc,
        'Cross_From_LeftWing': away_left,
        'Cross_From_RightWing': away_right
    }
    
    return fig, ax

#------------------------------------------------------FINAL THIRD ENTRY---------------------------------
def Final_third_entry(df, team_name, col, color_home, color_away, ax=None, show_title= False):
    path_eff = [path_effects.Stroke(linewidth=3, foreground='white'), path_effects.Normal()]

    FINAL_THIRD = 100 * (2/3)
    RIGHT_LIMIT = 100/3
    LEFT_LIMIT = 200/3
    
    dfpass = df[(df['nameTeam']==team_name) & (df['type']=='Pass') & (df['x']<FINAL_THIRD) & (df['endX']>=FINAL_THIRD) & (df['outcomeType']=='Successful') &
                (~df['qualifiers'].str.contains('Freekick', na=False))]
    dfcarry = df[(df['nameTeam']==team_name) & (df['type']=='Carry') & (df['x']<FINAL_THIRD) & (df['endX']>=70)]
    pitch = Pitch(pitch_type='opta', pitch_color='none', line_color='white', linewidth=2,
                          corner_arcs=True)
    if ax is None:
        fig, ax = pitch.draw(figsize=(10, 7))
    else:
        fig = ax.figure
        pitch.draw(ax=ax)
        
    if show_title:
        ax.set_title("Final Third Entries",  color='white', fontsize=25, fontweight='bold', path_effects=path_eff)
    
    pitch.draw(ax=ax)
 
    if team_name == team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    pass_count = len(dfpass) + len(dfcarry)

    right_entry = len(dfpass[dfpass['y'] < RIGHT_LIMIT]) + \
              len(dfcarry[dfcarry['y'] < RIGHT_LIMIT])

    mid_entry = len(dfpass[(dfpass['y'] >= RIGHT_LIMIT) &
                        (dfpass['y'] < LEFT_LIMIT)]) + \
                len(dfcarry[(dfcarry['y'] >= RIGHT_LIMIT) &
                            (dfcarry['y'] < LEFT_LIMIT)])

    left_entry = len(dfpass[dfpass['y'] >= LEFT_LIMIT]) + \
                len(dfcarry[dfcarry['y'] >= LEFT_LIMIT])


    left_percentage = round((left_entry/pass_count)*100)
    mid_percentage = round((mid_entry/pass_count)*100)
    right_percentage = round((right_entry/pass_count)*100)



    ax.hlines(33.33, xmin=0, xmax=70,colors='lightgrey', linestyle='dashed', alpha=0.45)
    ax.hlines(66.67, xmin=0, xmax=70,colors='lightgrey', linestyle='dashed', alpha=0.45)
    ax.vlines(  FINAL_THIRD,  ymin=-2,  ymax=102,  colors='lightgrey',  linestyle='dashed',  alpha=0.55)

    # showing the texts in the pitch
    bbox_props = dict(boxstyle="round,pad=0.3", edgecolor="None", facecolor='none', alpha=0.75)
    if col == col:
        ax.text(10, 18, f'{right_entry}\n({right_percentage}%)', color=color_home, fontsize=24, va='center', ha='center', bbox=bbox_props)
        ax.text(10, 50, f'{mid_entry}\n({mid_percentage}%)', color=color_home, fontsize=24, va='center', ha='center', bbox=bbox_props)
        ax.text(10, 85, f'{left_entry}\n({left_percentage}%)', color=color_home, fontsize=24, va='center', ha='center', bbox=bbox_props)
    else:
        ax.text(10, 18, f'{right_entry}\n({right_percentage}%)', color=color_away, fontsize=24, va='center', ha='center', bbox=bbox_props)
        ax.text(10, 50, f'{mid_entry}\n({mid_percentage}%)', color=color_away, fontsize=24, va='center', ha='center', bbox=bbox_props)
        ax.text(10, 85, f'{left_entry}\n({left_percentage}%)', color=color_away, fontsize=24, va='center', ha='center', bbox=bbox_props)

    # plotting the passes
    pro_pass = pitch.lines(dfpass.x, dfpass.y, dfpass.endX, dfpass.endY, lw=3.5, comet=True, color=col, ax=ax, alpha=0.5)
    # plotting some scatters at the end of each pass
    pro_pass_end = pitch.scatter(dfpass.endX, dfpass.endY, s=35, edgecolor=col, linewidth=1, color='none', zorder=2, ax=ax)
    # plotting carries
    for index, row in dfcarry.iterrows():
        arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['endX'], row['endY']), arrowstyle='->', color=col, zorder=4, mutation_scale=20, 
                                        alpha=1, linewidth=2, linestyle='--')
        ax.add_patch(arrow)

    counttext = f"Total {pass_count}"

    # Heading and other texts
    if col == color_home:
        ax.text(83, -3, '<------------ Final third ------------->', color=line_color, ha='center', va='center')
        pitch.lines(53,  103, 73, 103, lw=3, transparent=True, comet=True, color=col, ax=ax, alpha=0.5)
        ax.scatter(73,103, s=35, edgecolor=col, linewidth=1, color='none', zorder=2)
        arrow = patches.FancyArrowPatch((83, 103), (103, 103), arrowstyle='->', color=col, zorder=4, mutation_scale=20, 
                                        alpha=1, linewidth=2, linestyle='--')
        ax.add_patch(arrow)
        ax.text(63, 108, f'Entry by Pass: {len(dfpass)}', fontsize=12, color='white', ha='center', va='center')
        ax.text(93, 108, f'Entry by Carry: {len(dfcarry)}', fontsize=12, color='white', ha='center', va='center')

        ax.text( 9,2, counttext, color='black', fontsize=9, fontweight='bold', ha='left', va='top',
            bbox=dict( boxstyle='round,pad=0.4', facecolor=color_home, edgecolor='none', alpha=0.75))
        
    else:
        ax.text(83, -3, '<------------ Final third ------------->', color=line_color, ha='center', va='center')
        pitch.lines(53, 103, 73, 103, lw=3, transparent=True, comet=True, color=col, ax=ax, alpha=0.5)
        ax.scatter(73,103, s=35, edgecolor=col, linewidth=1, color='none', zorder=2)
        arrow = patches.FancyArrowPatch((83, 103), (103, 103), arrowstyle='->', color=col, zorder=4, mutation_scale=20, 
                                        alpha=1, linewidth=2, linestyle='--')
        ax.add_patch(arrow)
        ax.text(63, 108, f'Entry by Pass: {len(dfpass)}', fontsize=12, color='white', ha='center', va='center')
        ax.text(93, 108, f'Entry by Carry: {len(dfcarry)}', fontsize=12, color='white', ha='center', va='center')

        ax.text( 9,2, counttext, color='black', fontsize=9, fontweight='bold', ha='left', va='top',
            bbox=dict( boxstyle='round,pad=0.4', facecolor=color_away, edgecolor='none', alpha=0.75))

    return fig, ax

def create_match_report1_plot(referee_html,group_round, stage_selected,id_stage, id_home_fotmob,id_away_fotmob,name_home_fotmob,name_away_fotmob,homeScore,awayScore,texto_estado,
                                match_info, nombre_jugador_partido, av_players_home, av_players_away, df, passes_df,
                                home_avg_locs,away_avg_locs,home_combinations,away_combinations,   home_metrics,   away_metrics,
                            home_team_dict, away_team_dict, color_home, color_away, background_color, stats,
                            xT_grid, teams_dict_id_name_whoscored, matchdict, home_positions, home_actions, away_positions,
                            away_actions, data, team_dict_fotmob, formation_mappings, players_dict):
                                    
    fig, axs = plt.subplots( 5, 3, figsize=(35, 35), gridspec_kw={'height_ratios': [0.2, 1, 1, 1, 1]}, facecolor='black')
    fig.patch.set_facecolor('black')

    # ---------------- LOGOS ----------------
    himage = Image.open(urlopen(f"https://images.fotmob.com/image_resources/logo/teamlogo/{id_home_fotmob}.png"))
    add_image(himage, fig, left=0.23, bottom=0.94, width=0.05, height=0.05)

    aimage = Image.open(urlopen(f"https://images.fotmob.com/image_resources/logo/teamlogo/{id_away_fotmob}.png"))
    add_image(aimage, fig, left=0.75, bottom=0.94, width=0.05, height=0.05)

    # ---------------- HEADER ----------------
    axs[0, 0].axis("off")
    axs[0, 1].axis("off")
    axs[0, 2].axis("off")

    header_ax = axs[0, 1]
    header_ax.set_facecolor('black')
    header_ax.axis("off")

    highlight_text = [{'color': color_home}, {'color': color_away}]

    fig_text(0.5, 0.98,f"<{name_home_fotmob} {homeScore}> - <{awayScore} {name_away_fotmob}>",color='white', fontsize=50, fontweight='bold',
                highlight_textprops=highlight_text,ha='center', va='center',ax=header_ax)

    fig_text(0.5, 0.95, texto_estado, color='white', fontsize=40, fontweight='bold', ha='center', va='center', ax=header_ax)

    if int(id_stage) <= 3:
        title = f"{group_round} - {stage_selected}, World Cup 2026 | Post Match Report-1"
    else:
        title = f"{stage_selected}, World Cup 2026 | Post Match Report-1"

    fig_text(0.5, 0.92, title, color='white', fontsize=30, ha='center',
                    va='center', ax=header_ax)

    fig_text(0.5, 0.90, f"Venue: {match_info['venue_name']} (Attendance: {match_info['attendance']}) | {referee_html}",
            color='white', fontsize=22.5, ha='center', va='center', ax=header_ax)

    fig_text(0.5, 0.88, f"Player of the Match: {nombre_jugador_partido}",color='white', fontsize=22.5, ha='center', va='center', ax=header_ax)

    # ---------------- ROW 2 ----------------
    plot_player_position_median(av_players_home, background_color, color_home, True, ax=axs[1, 0])
    
    plot_initial_formation(df, home_team_dict['name'], away_team_dict['name'], formation_mappings, players_dict,
                        color_home, color_away,nombre_jugador_partido, ax=axs[1, 1])
    
    plot_player_position_median(av_players_away, background_color, color_away, False, ax=axs[1, 2])

    # ---------------- ROW 3 ----------------
    plot_enhanced_network( passes_df, home_avg_locs, home_combinations, home_metrics, home_team_dict['name'], color_home, True, background_color,
            ax=axs[2, 0], show_title=True)

    df_copy= preparare_df_xt(df, name_home_fotmob,name_away_fotmob)
    plot_xt_momentum(df_copy, xT_grid, teams_dict_id_name_whoscored,matchdict['home']['teamId'], matchdict['away']['teamId'],
        home_color=color_home, away_color=color_away,ax=axs[2, 1])

    plot_enhanced_network(passes_df, away_avg_locs, away_combinations, away_metrics, away_team_dict['name'], color_away, False, background_color,
        ax=axs[2, 2], show_title=True )

    # ---------------- ROW 4 ----------------
    draw_progressive_pass_map(df, matchdict['home']['teamId'], matchdict['home']['name'],color_home, False, ax=axs[3, 0], show_title=True)

    plot_match_stats_styled( stats, color_home, color_away, "Home Team", "Away Team", ax=axs[3, 1], show_title=True)

    draw_progressive_pass_map( df, matchdict['away']['teamId'], matchdict['away']['name'], color_away, True, ax=axs[3, 2], show_title=True)

    # ---------------- ROW 5 ----------------
    defensive_block(home_positions, home_actions,home_team_dict['name'], color_home,False, ax=axs[4, 0], title=True)

    shots_merged, home_stats, away_stats = prepare_dataframe_shots( df, data, team_dict_fotmob,name_home_fotmob,name_away_fotmob)

    plot_shot_map_with_stats(shots_merged, home_stats, away_stats,id_home_fotmob, id_away_fotmob,name_home_fotmob, name_away_fotmob,
        color_home, color_away, ax=axs[4, 1])

    defensive_block(away_positions, away_actions,away_team_dict['name'], color_away,True, ax=axs[4, 2], title=True)

    fig_text( 0.5, -0.01, "Data from: Opta (Whoscored/Fotmob) | coded by: @cescblanco", color='white', fontsize=22.5,
        ha='center', va='center',ax=axs[4, 1])

    # ---------------- SAVE ----------------
    fig.set_facecolor('black')

    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)

    return buffer.getvalue()
                    
def create_match_report2_plot(referee_html,group_round, stage_selected, id_stage, id_home_fotmob,id_away_fotmob,name_home_fotmob,name_away_fotmob,homeScore,awayScore,texto_estado,
                            match_info, nombre_jugador_partido, df, matchdict, color_home, color_away, home_team, away_team,
                            local_xg, visit_xg, goles_local_xg, goles_visit_xg, df_tiros_coord_home, df_tiros_coord_away, pearl_earring_cmaph,
                            pearl_earring_cmapa,IMAGEN_PELOTA,IMAGEN_PELOTA_ROJA):

        fig, axs = plt.subplots(  5, 3,  figsize=(35, 35),  gridspec_kw={'height_ratios': [0.2, 1, 1, 1, 1]},  facecolor='black')

        fig.patch.set_facecolor('black')

        # ---------------- LOGOS ----------------
        himage = Image.open(urlopen(f"https://images.fotmob.com/image_resources/logo/teamlogo/{id_home_fotmob}.png"))
        add_image(himage, fig, left=0.23, bottom=0.94, width=0.05, height=0.05)

        aimage = Image.open(urlopen(f"https://images.fotmob.com/image_resources/logo/teamlogo/{id_away_fotmob}.png"))
        add_image(aimage, fig, left=0.75, bottom=0.94, width=0.05, height=0.05)

        # ---------------- HEADER ----------------
        axs[0, 0].axis("off")
        axs[0, 1].axis("off")
        axs[0, 2].axis("off")

        header_ax = axs[0, 1]
        header_ax.set_facecolor('black')
        header_ax.axis("off")

        highlight_text = [{'color': color_home}, {'color': color_away}]

        fig_text(0.5, 0.98,f"<{name_home_fotmob} {homeScore}> - <{awayScore} {name_away_fotmob}>",color='white', fontsize=50, fontweight='bold',
                highlight_textprops=highlight_text,ha='center', va='center',ax=header_ax)

        fig_text(0.5, 0.95, texto_estado, color='white', fontsize=40, fontweight='bold', ha='center', va='center', ax=header_ax)

        if int(id_stage) <= 3:
            title = f"{group_round} - {stage_selected}, World Cup 2026 | Post Match Report-2"
        else:
            title = f"{stage_selected}, World Cup 2026 | Post Match Report-2"

        fig_text(0.5, 0.92, title,  color='white', fontsize=30, ha='center',
                    va='center', ax=header_ax)

        fig_text(0.5, 0.90, f"Venue: {match_info['venue_name']} (Attendance: {match_info['attendance']}) | {referee_html}",
                color='white', fontsize=22.5, ha='center', va='center', ax=header_ax)

        fig_text(0.5, 0.88, f"Player of the Match: {nombre_jugador_partido}",color='white', fontsize=22.5, ha='center', va='center', ax=header_ax)

        # ---------------- ROW 2 ----------------
        Pass_end_zone(df, matchdict['home']['name'], pearl_earring_cmaph, ax=axs[1, 0], show_title=True)

        plot_congestion(  df,  matchdict['home']['name'],  matchdict['away']['name'],  color_home, color_away, ax=axs[1, 1], show_title=True)

        Pass_end_zone(df, matchdict['away']['name'], pearl_earring_cmapa, ax=axs[1, 2], show_title=True)

        # ---------------- ROW 3 ----------------
        plot_heatmap_touches(df, home_team, color_home, True, ax=axs[2, 0])

        plot_xg_flow_streamlit( local_xg, visit_xg, goles_local_xg, goles_visit_xg, name_home_fotmob, name_away_fotmob,
            color_home, color_away, IMAGEN_PELOTA, IMAGEN_PELOTA_ROJA, ax=axs[2, 1])

        plot_heatmap_touches(df, away_team, color_away, False, ax=axs[2, 2])

        # ---------------- ROW 4 ----------------
        Chance_creating_zone( df, matchdict, matchdict['home']['name'], pearl_earring_cmaph,
            color_home, color_home, color_away, ax=axs[3, 0], title=True)
        axs[3, 0].text(0, -2.5, 'Attacking Direction--->',  color=color_home, fontsize=13, ha='left')

        parent_spec = axs[3, 1].get_subplotspec()
        axs[3, 1].remove()

        subgs = parent_spec.subgridspec(2, 1, hspace=0.2)

        ax_gk_home = fig.add_subplot(subgs[0])
        ax_gk_away = fig.add_subplot(subgs[1])

        ax_gk_home.set_facecolor('none')
        ax_gk_away.set_facecolor('none')

        draw_goal(df_tiros_coord_away, "HOME GK SAVES", color_home,IMAGEN_PELOTA, IMAGEN_PELOTA_ROJA, ax=ax_gk_home)
        draw_goal(df_tiros_coord_home, "AWAY GK SAVES", color_away,IMAGEN_PELOTA, IMAGEN_PELOTA_ROJA, ax=ax_gk_away)

        Chance_creating_zone( df, matchdict, matchdict['away']['name'], pearl_earring_cmapa, color_away, color_home, color_away,
            ax=axs[3, 2], title=True)

        axs[3, 2].text(0, 103, '<---Attacking Direction', color=color_away, fontsize=13, ha='right')

        # ---------------- ROW 5 ----------------
        Final_third_entry(  df, matchdict['home']['name'],  color_home, color_home, color_away,  ax=axs[4, 0],  show_title=True)
        axs[4, 0].text(0, 103, '<---Attacking Direction', color=color_home, fontsize=13, ha='right')

        Crosses(df, matchdict, color_home, color_away, ax=axs[4, 1], show_title=True)

        Final_third_entry( df, matchdict['away']['name'], color_away, color_home, color_away, ax=axs[4, 2], show_title=True)
        axs[4, 2].text(0, 103, '<---Attacking Direction',color=color_away, fontsize=13, ha='right')

        fig_text( 0.5, -0.01, "Data from: Opta (Whoscored/Fotmob) | coded by: @cescblanco", color='white', fontsize=22.5, ha='center',
                    va='center', ax=axs[4, 1])

        # ---------------- SAVE ----------------
        
        fig.patch.set_facecolor('black')

        fig.patch.set_alpha(1)
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='black', edgecolor= 'black')

        plt.close(fig)

        return buffer.getvalue()

#-----------------------------------------PLAYER OF THE MATCH---------------------------------------------------------------
def prepare_df_player_of_match(player_home,player_away, matchdict ):
    jugador_partido = player_home.loc[player_home["isManOfTheMatch"]].copy()
    if jugador_partido.empty:
        jugador_partido = player_away.loc[player_away["isManOfTheMatch"]].copy()
    jugador_partido["is_away_team"] = jugador_partido["field"] == "away"
    nombre_jugador_partido = jugador_partido["name"].iloc[0]
    position_jugador_partido = jugador_partido["position"].iloc[0]
    player_id_jugador_partido = int(jugador_partido["playerId"].iloc[0])
    is_away_team = bool(jugador_partido["is_away_team"].iloc[0])

    jugador_partido["is_goalkeeper"] = jugador_partido["position"] == "GK"
    is_goalkeeper = bool(jugador_partido["is_goalkeeper"].iloc[0])


    home_name = matchdict['home']['name']
    away_name = matchdict['away']['name']

    field_to_teamId = {
        "home": home_name,
        "away": away_name
    }

    jugador_partido["team_name"] = jugador_partido["field"].map(field_to_teamId)
    return jugador_partido, nombre_jugador_partido, position_jugador_partido, player_id_jugador_partido,is_away_team, is_goalkeeper

def prepare_datafrmae_info_teams_whoscored(matchdict, teams_dict_id_name_whoscored):
    from unidecode import unidecode
    players_home_df = pd.DataFrame(matchdict['home']['players'])
    players_home_df["teamId"] = matchdict['home']['teamId']
    players_away_df = pd.DataFrame(matchdict['away']['players'])
    players_away_df["teamId"] = matchdict['away']['teamId']
    dfp = pd.concat([players_home_df, players_away_df])
    dfp['name'] = dfp['name'].astype(str)
    dfp['name'] = dfp['name'].apply(unidecode)
    dfp['teamName']= dfp['teamId'].map(teams_dict_id_name_whoscored)
    return  dfp[['playerId', 'name', 'isFirstEleven', 'isManOfTheMatch', 'teamId',	'teamName']].copy()

def normalize_name(name):
    import unicodedata
    import re

    if pd.isna(name):
        return ""

    name = str(name).lower().strip()

    # normaliza acentos
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))

    # 🔥 IMPORTANTÍSIMO: guiones → espacios
    name = name.replace('-', ' ')

    # elimina caracteres raros pero mantiene espacios
    name = re.sub(r'[^a-z\s]', '', name)

    # limpia espacios dobles
    name = re.sub(r'\s+', ' ', name).strip()

    return name

def token_match(a, b):
    a_tokens = set(a.split())
    b_tokens = set(b.split())

    # match fuerte: subset
    if a_tokens.issubset(b_tokens):
        return True

    # match inverso (por si acaso)
    if b_tokens.issubset(a_tokens):
        return True

    # match parcial (mínimo 80% overlap)
    overlap = len(a_tokens & b_tokens) / max(len(a_tokens), len(b_tokens))
    return overlap >= 0.8

def playing_time(df, pname):
    df_player = df[df['name_norm'] == pname].copy()

    if df_player.empty:
        return 0

    df_player['isFirstEleven'] = df_player['isFirstEleven'].fillna(0).astype(int)

    max_min = df['minute'].max()

    df_sub_on = df_player[df_player['type'] == 'SubstitutionOn']
    df_sub_off = df_player[df_player['type'] == 'SubstitutionOff']

    is_starting = (df_player['isFirstEleven'].max() == 1)

    # -----------------------
    # TITULAR
    # -----------------------
    if is_starting:

        # si no fue sustituido → jugó todo el tiempo
        if df_sub_off.empty:
            return int(max_min)

        off_min = df_sub_off['minute'].min()

        return int(off_min)

    # -----------------------
    # SUPLENTE
    # -----------------------
    else:

        if df_sub_on.empty:
            return 0

        on_min = df_sub_on['minute'].min()

        return int(max_min - on_min)

def prepare_dataframe_shots_playerofmatch(df, data,team_dict_fotmob, name_home_fotmob,name_away_fotmob):
    shots_df= pd.DataFrame(data['content']['shotmap']['shots'])
    shots_df = shots_df[shots_df['period']!='PenaltyShootout']
    shots_df['teamName'] = shots_df['teamId'].map(team_dict_fotmob)

    #Dataframe eventos whoscored
    df_events_shots = df[ (df['isShot'] == True) & (df['period'] != 'PenaltyShootout')][['id', 'qualifiers', 'type', 'name','satisfiedEventsTypes']]

    shots_merged = pd.merge(shots_df, df_events_shots, left_on='id', right_on='id', how='left')

    
    # Add flags
    shots_merged['is_big_chance'] = shots_merged['qualifiers'].apply(is_big_chance)
    shots_merged['is_own_goal'] = shots_merged['qualifiers'].apply(is_own_goal)

    home= name_home_fotmob
    away = name_away_fotmob

    team_swap = {
            home: away,
            away: home
        }
    shots_merged['render_team'] = shots_merged['teamName']

    shots_merged.loc[
        shots_merged['is_own_goal'],
        'render_team'
    ] = shots_merged.loc[
        shots_merged['is_own_goal'],
        'teamName'
    ].map(team_swap)

    return shots_merged

def plot_event_timeline(df, player_name, is_goalkeeper=False, ax=None):

    path_eff = [
        path_effects.Stroke(linewidth=1, foreground='white'),
        path_effects.Normal()
    ]

    # ----------------------------
    # FILTER
    # ----------------------------
    player_df = df[df['name_norm'] == player_name].copy()
    player_df = player_df.sort_values("minute")

    # ----------------------------
    # BUILD EVENTS
    # ----------------------------
    timeline = []

    for _, row in player_df.iterrows():

        minute = int(row["minute"])
        events = row.get("satisfiedEventsTypes", []) or []

        if row["type"] == "Goal":
            timeline.append((minute, "Goal"))

        elif 100 in events:
            timeline.append((minute, "Assist"))

        elif 123 in events:
            timeline.append((minute, "Key Pass"))

        elif 203 in events:
            timeline.append((minute, "Big Chance"))

        elif row["type"] == "BallRecovery":
            timeline.append((minute, "Recovery"))

        elif row["type"] == "Interception":
            timeline.append((minute, "Interception"))

        elif row["type"] == "Tackle":
            timeline.append((minute, "Tackle"))

        elif row["type"] in ["Save", "SavedShot"] or 113 in events:
            timeline.append((minute, "Save"))

        elif 161 in events or 178 in events:
            timeline.append((minute, "Goal Conceded"))

        elif 111 in events:
            timeline.append((minute, "Penalty Save"))

        elif row["type"] == "Claim" or 104 in events or 103 in events:
            timeline.append((minute, "Claim"))

        elif 127 in events:
            timeline.append((minute, "Long Pass"))

        elif 101 in events or row["type"] == "Smother":
            timeline.append((minute, "Sweeper"))

    # ----------------------------
    # STYLE
    # ----------------------------
    if is_goalkeeper:

        colors = {
            "Save": "#00bfff",
            "Goal Conceded": "#ff4d4d",
            "Claim": "#ffffff",
            "Sweeper": "#ffd700",
            "Penalty Save": "#00ff88",
            "Long Pass": "#ff9900",
            "Error": "#ff0000"
        }

        y_map = {
            "Save": 0.35,
            "Claim": 0.23,
            "Sweeper": 0.10,
            "Long Pass": 0.01,
            "Penalty Save": -0.08,
            "Goal Conceded": -0.15,
            "Error": -0.25
        }

        sizes = {k: 140 for k in colors}  # fallback simple

    else:

        colors = {
            "Goal": "#00ff88",
            "Assist": "#00bfff",
            "Key Pass": "#b266ff",
            "Big Chance": "#ff9900",
            "Recovery": "#ffd700",
            "Interception": "#ff4d4d",
            "Tackle": "#ffffff"
        }

        sizes = {
            "Goal": 260,
            "Assist": 180,
            "Big Chance": 160,
            "Key Pass": 140,
            "Recovery": 90,
            "Interception": 90,
            "Tackle": 80
        }

        y_map = {
            "Goal": 0.12,
            "Assist": 0.8,
            "Big Chance": 0.4,
            "Key Pass": -0.001,
            "Recovery": -0.10,
            "Interception": -0.17,
            "Tackle": -0.25
        }

    # ----------------------------
    # AX SETUP
    # ----------------------------
    max_minute = player_df["minute"].max() if not player_df.empty else 90
    end_time = max(90, max_minute)

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 3.2))
    else:
        fig = ax.figure
        ax.text( 0.5, 0.95, "EVENT TIMELINE", transform=ax.transAxes, ha="center", va="center", color="white", fontsize=20, fontweight="bold", path_effects=path_eff)

    fig.patch.set_facecolor((0, 0, 0, 0))
    ax.set_facecolor((0, 0, 0, 0))

    # ----------------------------
    # BASE LINE
    # ----------------------------
    ax.hlines(-0.3, 1, end_time, color="white", alpha=0.30, linewidth=2)

    # ----------------------------
    # PLOT EVENTS (SAFE VERSION)
    # ----------------------------
    for minute, event in timeline:

        if event not in y_map or event not in colors:
            continue

        ax.scatter(
            minute,
            y_map[event],
            s=sizes.get(event, 100),
            color=colors.get(event, "gray"),
            edgecolors="white",
            linewidths=1.2,
            alpha=0.95,
            zorder=3
        )

    # ----------------------------
    # MINUTES
    # ----------------------------
    for m in range(0, end_time + 1, 15):
        ax.text(m, -0.39, str(m), ha="center", color="white", fontsize=10)

    # ----------------------------
    # LEGEND
    # ----------------------------
    legend_elements = [
        Line2D(
            [0], [0],
            marker='o',
            color='none',
            markerfacecolor=colors[k],
            markeredgecolor='white',
            markersize=8,
            label=k
        )
        for k in colors
    ]

    leg = ax.legend(
        handles=legend_elements,
        loc='upper center',
        bbox_to_anchor=(0.5, 0.20),
        ncol=4,
        frameon=False,
        fontsize=10
    )

    for text in leg.get_texts():
        text.set_color("white")

    # ----------------------------
    # AXIS CLEAN
    # ----------------------------
    ax.set_xlim(-2, end_time + 2)
    ax.set_ylim(-0.8, 0.6)
    ax.axis("off")

    return fig, ax

def prepare_dataframe_shots_playerofmatch(df, data,team_dict_fotmob, name_home_fotmob,name_away_fotmob):
    shots_df= pd.DataFrame(data['content']['shotmap']['shots'])
    shots_df = shots_df[shots_df['period']!='PenaltyShootout']
    shots_df['teamName'] = shots_df['teamId'].map(team_dict_fotmob)

    #Dataframe eventos whoscored
    df_events_shots = df[ (df['isShot'] == True) & (df['period'] != 'PenaltyShootout')][['id', 'qualifiers', 'type', 'name','satisfiedEventsTypes']]

    shots_merged = pd.merge(shots_df, df_events_shots, left_on='id', right_on='id', how='left')

    
    # Add flags
    shots_merged['is_big_chance'] = shots_merged['qualifiers'].apply(is_big_chance)
    shots_merged['is_own_goal'] = shots_merged['qualifiers'].apply(is_own_goal)

    home= name_home_fotmob
    away = name_away_fotmob

    team_swap = {
            home: away,
            away: home
        }
    shots_merged['render_team'] = shots_merged['teamName']

    shots_merged.loc[
        shots_merged['is_own_goal'],
        'render_team'
    ] = shots_merged.loc[
        shots_merged['is_own_goal'],
        'teamName'
    ].map(team_swap)

    return shots_merged

def Individual_ShotMap(shots_merged, nombre_jugador_partido, color_team,is_away_team=True, ax= None ):

    path_eff = [path_effects.Stroke(linewidth=1, foreground='white'), path_effects.Normal()]
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10,7))
    else:
        fig = ax.figure
        ax.set_title("SHOT MAP",  color='white', fontsize=20, fontweight='bold', path_effects=path_eff)

    pitch = Pitch(pitch_type='uefa',pitch_color='none',line_color='white')

    pitch.draw(ax=ax)
    
    fig.set_facecolor('none')
    ax.set_facecolor('none')

    # =========================
    # TRANSFORMACIÓN DE DATOS
    # =========================
    def transform(df):
        if is_away_team:
            return 100 - df['x'], df['y']
        return df['x'], df['y']


    # =========================
    # FILTRO DE EVENTOS
    # =========================
    op_sh = shots_merged[ (shots_merged['name_norm'] == nombre_jugador_partido) & (shots_merged['situation'] == 'RegularPlay')]

    goal = shots_merged[ (shots_merged['name_norm'] == nombre_jugador_partido) & (shots_merged['eventType'] == 'Goal')]

    miss = shots_merged[ (shots_merged['name_norm'] == nombre_jugador_partido) & (shots_merged['eventType'] == 'Miss')]

    save = shots_merged[ (shots_merged['name_norm'] == nombre_jugador_partido) & (shots_merged['eventType'] == 'AttemptSaved') & (shots_merged['isBlocked'] == 0)]

    blok = shots_merged[ (shots_merged['name_norm'] == nombre_jugador_partido) & (shots_merged['eventType'] == 'AttemptSaved') & (shots_merged['isBlocked'] == 1)]

    post = shots_merged[ (shots_merged['name_norm'] == nombre_jugador_partido) & (shots_merged['eventType'] == 'Post')]

    shots = shots_merged[ (shots_merged['name_norm'] == nombre_jugador_partido) & (shots_merged['type'].isin(['Goal', 'MissedShots', 'SavedShot', 'ShotOnPost']))].copy()

    out_box = shots[shots['isFromInsideBox'] == False]

    # =========================
    # MÉTRICAS
    # =========================
    shots['Length'] = np.sqrt((shots['x'] - 105)**2 + (shots['y'] - 34)**2)
    avg_dist = round(shots['Length'].mean(), 2)

    xG = round(shots_merged[ shots_merged['name_norm'] == nombre_jugador_partido]['expectedGoals'].sum(), 2)

    xGOT = round(shots_merged[ shots_merged['name_norm'] == nombre_jugador_partido]['expectedGoalsOnTarget'].sum(), 2)

    # =========================
    # TRANSFORMACIÓN COORDS
    # =========================
    x_g, y_g = transform(goal)
    x_p, y_p = transform(post)
    x_b, y_b = transform(blok)
    x_s, y_s = transform(save)
    x_m, y_m = transform(miss)

    # =========================
    # SHOT MAP
    # =========================
    pitch.scatter(x_g, y_g,s=goal['expectedGoals'] * 1000,marker='football',edgecolors='green',c='None',ax=ax)
    pitch.scatter(x_p, y_p,s=post['expectedGoals'] * 1000 + 100,marker='o',edgecolors=color_team,c='None',hatch='+++',ax=ax)
    pitch.scatter(x_b, y_b,s=blok['expectedGoals'] * 1000 + 100,marker='o',edgecolors=color_team,c='None',hatch='/////',ax=ax)
    pitch.scatter(x_s, y_s,s=save['expectedGoals'] * 1000 + 100,marker='o',color=color_team,edgecolors='white',ax=ax)
    pitch.scatter(x_m, y_m,s=miss['expectedGoals'] * 1000 + 100,marker='o',edgecolors=color_team,c='None',ax=ax)

    # =========================
    # PANEL DE STATS (PRO)
    # =========================
    stat_x = 0.55 if is_away_team else 0.08
    text_x = 0.60 if is_away_team else 0.10

    stats = [
        f"Total Shots: {len(shots)}",
        f"Open-play Shots: {len(op_sh)}",
        f"Goals: {len(goal)}",
        f"Shot on Post: {len(post)}",
        f"Shots on Target: {len(save)}",
        f"Shots off Target: {len(miss)}",
        f"Shots Blocked: {len(blok)}",
        f"Shots outside box: {len(out_box)}",
        f"Shots inside box: {len(shots) - len(out_box)}",
        f"Avg. Shot Distance: {avg_dist} m",
        f"xG: {xG}",
        f"xGOT: {xGOT}",
    ]

    # Título
    ax.text(stat_x, 0.85,
            "Shooting Stats",
            transform=ax.transAxes,
            color='black',
            fontsize=15,
            fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.9, edgecolor=color_team, pad=8))

    # Métricas
    for i, stat in enumerate(stats):
        ax.text(text_x,
                0.75 - i * 0.05,
                stat,
                transform=ax.transAxes,
                fontsize=10,
                ha='left',
                va='center',
                color='black',
                bbox=dict(facecolor='white', alpha=1, edgecolor=color_team, pad=4))
    return fig, ax

def individual_passMap( df1,nombre_jugador_partido,is_away_team=True, ax= None ):
    path_eff = [path_effects.Stroke(linewidth=1, foreground='white'), path_effects.Normal()]
    pitch = Pitch(pitch_type='opta', corner_arcs=True, pitch_color='black', line_color='white', linewidth=2)
    

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 7))
    else:
        fig = ax.figure
        ax.set_title("PASS MAP",  color='white', fontsize=20, fontweight='bold', path_effects=path_eff)
    pitch.draw(ax=ax)
    fig.set_facecolor('none')
    ax.set_facecolor('none')

    if is_away_team== True:

        ax.invert_xaxis()
        ax.invert_yaxis()

    dfpass = df1[(df1['type']=='Pass') & (df1['name_norm']==nombre_jugador_partido)]
    acc_pass = dfpass[dfpass['outcomeType']=='Successful']
    iac_pass = dfpass[dfpass['outcomeType']=='Unsuccessful']

    if len(dfpass) != 0:
            accurate_pass_perc = round((len(acc_pass)/len(dfpass))*100, 2)
    else:
        accurate_pass_perc = 0

    Thr_ball = dfpass[(dfpass['satisfiedEventsTypes'].apply(lambda x: 129 in x))].reset_index(drop=True)
    Thr_ball_acc = Thr_ball[Thr_ball['outcomeType']=='Successful'].reset_index(drop=True)

    Lng_ball = dfpass[(dfpass['satisfiedEventsTypes'].apply(lambda x: 127 in x))].reset_index(drop=True)
    Lng_ball_acc = Lng_ball[Lng_ball['outcomeType']=='Successful'].reset_index(drop=True)

    Crs_pass = dfpass[(dfpass['satisfiedEventsTypes'].apply(lambda x: 125 in x))].reset_index(drop=True)
    Crs_pass_acc = Crs_pass[Crs_pass['outcomeType']=='Successful'].reset_index(drop=True)

    key_pass = dfpass[dfpass['satisfiedEventsTypes'].apply(lambda x: 123 in x)].reset_index(drop=True)
    big_chnc = dfpass[dfpass['satisfiedEventsTypes'].apply(lambda x: 203 in x)].reset_index(drop=True)


    df_no_carry = df1[df1['type']!='Carry'].reset_index(drop=True)
    pre_asst = df_no_carry[(df_no_carry['satisfiedEventsTypes'].apply(lambda x: 100 in x)) & (df_no_carry['type']=='Pass') & 
                            (df_no_carry['outcomeType']=='Successful') &  (df_no_carry['name']==nombre_jugador_partido)]
    shot_buildup = df_no_carry[(df_no_carry['satisfiedEventsTypes'].apply(lambda x: 123 in x)) & (df_no_carry['type']=='Pass') & 
                            (df_no_carry['outcomeType']=='Successful') &  (df_no_carry['name']==nombre_jugador_partido)]

    g_assist = dfpass[(df_no_carry['satisfiedEventsTypes'].apply(lambda x: 100 in x))].reset_index(drop=True)

    corners = dfpass[(df_no_carry['satisfiedEventsTypes'].apply(lambda x: 31 in x))].reset_index(drop=True)
    corners_acc = corners[corners['outcomeType']=='Successful']

    freekik = dfpass[(df_no_carry['satisfiedEventsTypes'].apply(lambda x: 34 in x))].reset_index(drop=True)
    freekik_acc = freekik[freekik['outcomeType']=='Successful']

    throwins = dfpass[(df_no_carry['satisfiedEventsTypes'].apply(lambda x: 212 in x))].reset_index(drop=True)
    throwins_acc = throwins[throwins['outcomeType']=='Successful']

    fnl_thd = dfpass[(df_no_carry['satisfiedEventsTypes'].apply(lambda x: 217 in x))].reset_index(drop=True)
    midThird = dfpass[(df_no_carry['satisfiedEventsTypes'].apply(lambda x: 216 in x))].reset_index(drop=True)
    defensiveThird = dfpass[(df_no_carry['satisfiedEventsTypes'].apply(lambda x: 215 in x))].reset_index(drop=True)

    frwd_pass = dfpass[(df_no_carry['satisfiedEventsTypes'].apply(lambda x: 36 in x))].reset_index(drop=True)
    back_pass = dfpass[(df_no_carry['satisfiedEventsTypes'].apply(lambda x: 35 in x))].reset_index(drop=True)

    frwd_pass_acc = frwd_pass[frwd_pass['outcomeType']=='Successful'].reset_index(drop=True)
    back_pass_acc = back_pass[back_pass['outcomeType']=='Successful'].reset_index(drop=True)

    if len(frwd_pass) != 0:
        Forward_Pass_Accuracy = round((len(frwd_pass_acc)/len(frwd_pass))*100, 2)
    else:
        Forward_Pass_Accuracy = 0
        
    pitch.lines(iac_pass.x, iac_pass.y, iac_pass.endX, iac_pass.endY, color='red', lw=4, alpha=0.45, comet=True, zorder=4, ax=ax)
    pitch.lines(acc_pass.x, acc_pass.y, acc_pass.endX, acc_pass.endY, color='green', lw=2, alpha=0.45, comet=True, zorder=4, ax=ax)

    pitch.lines(key_pass.x, key_pass.y, key_pass.endX, key_pass.endY, color='violet',     lw=4, alpha=1,    comet=True, zorder=4, ax=ax)
    pitch.lines(g_assist.x, g_assist.y, g_assist.endX, g_assist.endY, color='blue',      lw=4, alpha=1,    comet=True, zorder=5, ax=ax)

    ax.scatter(acc_pass.endX, acc_pass.endY, s=30, color='green',    edgecolor='green', alpha=1, zorder=4)
    ax.scatter(iac_pass.endX, iac_pass.endY, s=30, color='red',    edgecolor='green', alpha=1, zorder=4)
    ax.scatter(key_pass.endX, key_pass.endY, s=50, color='black',  edgecolor='violet', alpha=1, zorder=4)
    ax.scatter(g_assist.endX, g_assist.endY, s=50, color='black',  edgecolor= 'blue', alpha=1, zorder=5)

    text = f"""    <Accurate Pass: {len(acc_pass)}>/{len(dfpass)} ({accurate_pass_perc}%)  | <Inaccurate Pass: {len(iac_pass)}> | <Chances Created: {len(key_pass)}>
    Big Chances Created: {len(big_chnc)} | <Assists: {len(g_assist)}> | Pre-Assist: {len(pre_asst)} | Build-up to Shot: {len(shot_buildup)}
    Final-Third Passes: {len(fnl_thd)} | Middle-Third Passes: {len(midThird)} | Crosses (Acc.): {len(Crs_pass)} ({len(Crs_pass_acc)})
    Longballs (Acc.): {len(Lng_ball)} ({len(Lng_ball_acc)})
    """

    if is_away_team== True:
        ax_text( 100, 102, text, color='white', highlight_textprops=[  {'color': 'green'}, {'color': 'red'}, {'color': 'violet'},  {'color': 'blue'} ], 
                fontsize=10, ha='left', va='top', ax=ax)
    
    else:
        ax_text(10, -2, text, color='white', highlight_textprops=[  {'color': 'green'},{'color': 'red'}, {'color': 'violet'},  {'color': 'blue'} ], 
                fontsize=10, ha='left', va='top', ax=ax)
        
    return fig, ax

def individual_passes_recieved(df1,nombre_jugador_partido,color_team,is_away_team=True,ax=None  ):
    path_eff = [path_effects.Stroke(linewidth=1, foreground='white'), path_effects.Normal()]
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10,7))
    else:
        fig = ax.figure
        ax.set_title("PASSES RECIEVED",  color='white', fontsize=20, fontweight='bold', path_effects=path_eff)

    pitch = Pitch(pitch_type='opta',pitch_color='none',line_color='white')

    pitch.draw(ax=ax)

    if is_away_team:
        ax.invert_xaxis()
        ax.invert_yaxis()

    fig.set_facecolor('none')
    ax.set_facecolor('none')

    dfp = df1[(df1['type']=='Pass') & (df1['outcomeType']=='Successful') & (df1['name_norm'].shift(-1)==nombre_jugador_partido)& 
            (df1['teamId']==df1['teamId'].shift(-1))]
    dfkp = df1[
        (df1['type']=='Pass') &
        (df1['outcomeType']=='Successful') &
        (df1['name_norm'].shift(-1)==nombre_jugador_partido) &
        (df1['teamId']==df1['teamId'].shift(-1)) &
        (df1['satisfiedEventsTypes'].apply(lambda x: 123 in x))
    ]

    dfas = df1[
        (df1['type'] == 'Pass') &
        (df1['outcomeType'] == 'Successful') &
        (df1['name_norm'].shift(-1) == nombre_jugador_partido) &
        (df1['teamId']==df1['teamId'].shift(-1)) &
        (df1['satisfiedEventsTypes'].apply(lambda x: 100 in x))
    ]

    dfnt = dfp[dfp['endX']>=70]
    dfpen = dfp[(dfp['endX']>=87.5) & (dfp['endY']>=13.6) & (dfp['endY']<=54.6)]

    dfcros = dfp[dfp['satisfiedEventsTypes'].apply(lambda x: 125 in x)].reset_index(drop=True)
    dflb = dfp[dfp['satisfiedEventsTypes'].apply(lambda x: 127 in x)].reset_index(drop=True)
    cutback = dfp[((dfp['x'] >= 88.54) & (dfp['x'] <= 105) & 
                    ((dfp['y'] >= 40.8) & (dfp['y'] <= 54.4) | (dfp['y'] >= 13.6) & (dfp['y'] <= 27.2)) & 
                    (dfp['endY'] >= 27.2) & (dfp['endY'] <= 40.8) & (dfp['endX'] >= 81.67))]
    next_act = df1[(df1['name']==nombre_jugador_partido) & (df1['type'].shift(1)=='Pass') & (df1['outcomeType'].shift(1)=='Successful')]
    ball_retain = next_act[(next_act['outcomeType']=='Successful') & ((next_act['type']!='Foul') | (next_act['type']!='Dispossessed'))]
    if len(next_act) != 0:
        ball_retention = round((len(ball_retain)/len(next_act))*100, 2)
    else:
        ball_retention = 0

    if len(dfp) != 0:
        name_counts = dfp['name'].value_counts()
        name_counts_df = name_counts.reset_index()
        name_counts_df.columns = ['name', 'count']
        name_counts_df = name_counts_df.sort_values(by='count', ascending=False)  
        name_counts_df = name_counts_df.reset_index()
        r_name = name_counts_df['name'][0]
        r_count = name_counts_df['count'][0]
    else:
        r_name = 'None'
        r_count = 0        

    pitch.lines(dfp.x, dfp.y, dfp.endX, dfp.endY, lw=3, transparent=True, comet=True,color=color_team, ax=ax, alpha=0.5)
    pitch.lines(dfkp.x, dfkp.y, dfkp.endX, dfkp.endY, lw=4, transparent=True, comet=True,color='violet', ax=ax, alpha=0.75)
    pitch.lines(dfas.x, dfas.y, dfas.endX, dfas.endY, lw=4, transparent=True, comet=True,color='green', ax=ax, alpha=0.75)
    pitch.scatter(dfp.endX, dfp.endY, s=30, edgecolor=color_team, linewidth=1, color=color_team, zorder=2, ax=ax)
    pitch.scatter(dfkp.endX, dfkp.endY, s=40, edgecolor='violet', linewidth=1.5, color=color_team, zorder=2, ax=ax)
    pitch.scatter(dfas.endX, dfas.endY, s=50, edgecolors='green', linewidths=1, marker='football', c=color_team, zorder=2, ax=ax)

    avg_endY = dfp['endY'].median()
    avg_endX = dfp['endX'].median()
    ax.axvline(x=avg_endX, ymin=0, ymax=68, color='gray', linestyle='--', alpha=0.6, linewidth=2)
    ax.axhline(y=avg_endY, xmin=0, xmax=105, color='gray', linestyle='--', alpha=0.6, linewidth=2)

    if is_away_team:

        ax_text(100, 105, f'''        <Passes Received: {len(dfp)}> | <Key Passes Received: {len(dfkp)}> | <Assists Received: {len(dfas)}>
        Passes Received in Final third: {len(dfnt)} | Passes Received in Opponent box: {len(dfpen)}
        Crosses Received: {len(dfcros)} | Longballs Received: {len(dflb)}
        Cutbacks Received: {len(cutback)} | Ball Retention: {ball_retention} % 
        Avg. Distance of Pass Receiving from Opponent Goal line: {round(105-dfp['endX'].median(),2)}m
        Most Passes from: {r_name} ({r_count})''', fontsize=10, ha='left', va='top', color= 'white', ax=ax,
            highlight_textprops=[{'color':color_team}, {'color':'violet'}, {'color':'green'}])
        
    else:
        ax_text(10,-2, f'''        <Passes Received: {len(dfp)}> | <Key Passes Received: {len(dfkp)}> | <Assists Received: {len(dfas)}>
        Passes Received in Final third: {len(dfnt)} | Passes Received in Opponent box: {len(dfpen)}
        Crosses Received: {len(dfcros)} | Longballs Received: {len(dflb)}
        Cutbacks Received: {len(cutback)} | Ball Retention: {ball_retention} % 
        Avg. Distance of Pass Receiving from Opponent Goal line: {round(105-dfp['endX'].median(),2)}m
        Most Passes from: {r_name} ({r_count})''', fontsize=10, ha='left', va='top', color= 'white', ax=ax,
            highlight_textprops=[{'color':color_team}, {'color':'violet'}, {'color':'green'}])
        
    return fig, ax


def heatMap(df,player,color_team,is_away_team=True,ax=None):
    path_eff = [path_effects.Stroke(linewidth=1, foreground='white'), path_effects.Normal()]
    flamingo_cmap = LinearSegmentedColormap.from_list("Team colors", ['#0C0D0E', color_team], N=500)

    if ax is None:
        fig, ax = plt.subplots(figsize=(10,7))
    else:
        fig = ax.figure
        ax.set_title("TOUCH AND HEATMAP",  color='white', fontsize=20, fontweight='bold', path_effects=path_eff)

    pitch = Pitch(
        pitch_type='opta',
        pitch_color='none',
        line_color='white'
    )

    pitch.draw(ax=ax)

    if is_away_team:
        ax.invert_xaxis()
        ax.invert_yaxis()

    player_df = df[df['name_norm'] == player].reset_index(drop=True).copy()
    player_df = player_df[~player_df['type'].str.contains('SubstitutionOff|SubstitutionOn|Card|Carry',na=False)].reset_index(drop=True)

    touches = player_df[player_df['isTouch'] ==True]

    if len(touches) == 0:
        return ax
    
    pitch.kdeplot(  touches.x,  touches.y,  ax=ax,  fill=True,  levels=250,  thresh=0.08, cut=3,  alpha=0.3, cmap=flamingo_cmap)


    pitch.scatter(touches.x,touches.y,ax=ax,color='white',s=8,alpha=0.3)

    
    final_third = touches[touches['x'] >= 66.7]
    box_touches = touches[(touches['x'] >= 83) & (touches['y'] >= 21) & (touches['y'] <= 79)]

    if is_away_team:
        ax.text( 60, 105, f"Touches: {len(touches)} | Touches in de Final-Third: {len(final_third)} | Touches in Penalty Area : {len(box_touches)}", 
                ha='center', color='white', fontsize=10)
    
    else:
        ax.text( 45, -5, f"Touches: {len(touches)} | Touches in de Final-Third: {len(final_third)} | Touches in Penalty Area : {len(box_touches)}", 
                ha='center', color='white', fontsize=10)
    
    fig.set_facecolor('none')
    ax.set_facecolor('none')
    
    return fig, ax

def individual_def_acts(df1,nombre_jugador_partido,color_team,is_away_team=True,ax=None  ):
    from matplotlib.lines import Line2D
    path_eff = [path_effects.Stroke(linewidth=1, foreground='white'), path_effects.Normal()]
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10,7))
    else:
        fig = ax.figure
        ax.set_title("DEFENSIVE ACTIONS",  color='white', fontsize=20, fontweight='bold', path_effects=path_eff)

    pitch = Pitch(pitch_type='opta',pitch_color='none',line_color='white')

    pitch.draw(ax=ax)

    if is_away_team:
        ax.invert_xaxis()
        ax.invert_yaxis()

    fig.set_facecolor('none')
    ax.set_facecolor('none')
    
    playerdf = df1[df1['name_norm'] == nombre_jugador_partido].reset_index(drop=True).copy()

    ball_wins = playerdf[(playerdf['type']=='Interception') | (playerdf['type']=='BallRecovery')]
    f_third = ball_wins[ball_wins['x']>=66.66]
    m_third = ball_wins[(ball_wins['x']>33.3) & (ball_wins['x']<66.66)]
    d_third = ball_wins[ball_wins['x']<=33.3]

    hp_tk = playerdf[(playerdf['type']=='Tackle')]
    hp_tk_u = playerdf[(playerdf['type']=='Tackle') & (playerdf['outcomeType']=='Unsuccessful')]

    hp_intc = playerdf[(playerdf['type']=='Interception')]
    hp_br = playerdf[playerdf['type']=='BallRecovery']
    hp_cl = playerdf[playerdf['type']=='Clearance']

    hp_fl_committed = playerdf[(playerdf['satisfiedEventsTypes'].apply(lambda x: 64 in x)) & (playerdf['type']=='Foul')]

    hp_ar =playerdf[(playerdf['type']=='Aerial') & (playerdf['satisfiedEventsTypes'].apply(lambda x: 197 in x)) | (playerdf['satisfiedEventsTypes'].apply(lambda x: 198 in x))]
    hp_ar_u = hp_ar[(hp_ar['outcomeType']=='Unsuccessful')]

    pass_bl = playerdf[playerdf['type']=='BlockedPass']
    shot_bl = playerdf[playerdf['type']=='Save']

    drb_pst = playerdf[playerdf['type']=='Challenge']
    drb_tkl = df1[(df1['name']==nombre_jugador_partido) & (df1['type']=='Tackle') & (df1['type'].shift(1)=='TakeOn') & (df1['outcomeType'].shift(1)=='Unsuccessful')]
    err_lat = playerdf[playerdf['satisfiedEventsTypes'].apply(lambda x: 99 in x)]
    err_lgl = playerdf[playerdf['satisfiedEventsTypes'].apply(lambda x: 98 in x)]

    dan_frk = playerdf[(playerdf['type']=='Foul') & (playerdf['x']>16.5) & (playerdf['x']<35) & (playerdf['y']>13.6) & (playerdf['y']<54.4)]

    prbr = df1[(df1['name']==nombre_jugador_partido) & ((df1['type']=='BallRecovery') | (df1['type']=='Interception')) & (df1['name'].shift(-1)==nombre_jugador_partido) & 
                (df1['outcomeType'].shift(-1)=='Successful') &
                ((df1['type'].shift(-1)!='Foul') | (df1['type'].shift(-1)!='Dispossessed'))]

    if (len(hp_br)+len(hp_intc)) != 0:
            post_rec_ball_retention = round((len(prbr)/(len(hp_br)+len(hp_intc)))*100, 2)
    else:
        post_rec_ball_retention = 0

    pitch.scatter(hp_tk.x, hp_tk.y, s=250, c=color_team, lw=2.5, edgecolor=color_team, marker='+', hatch='/////', ax=ax)
    pitch.scatter(hp_tk_u.x, hp_tk_u.y, s=250, c='gray', lw=2.5, edgecolor='gray', marker='+', hatch='/////', ax=ax)
    pitch.scatter(hp_intc.x, hp_intc.y, s=250, c='None', lw=2.5, edgecolor=color_team, marker='s', hatch='/////', ax=ax)
    pitch.scatter(hp_br.x, hp_br.y, s=250, c='None', lw=2.5, edgecolor=color_team, marker='o', hatch='/////', ax=ax)
    pitch.scatter(hp_cl.x, hp_cl.y, s=250, c='None', lw=2.5, edgecolor=color_team, marker='d', hatch='/////', ax=ax)
    pitch.scatter(hp_fl_committed.x, hp_fl_committed.y, s=250, c=color_team, lw=2.5, edgecolor=color_team, marker='x', hatch='/////', ax=ax)
    pitch.scatter(hp_ar.x, hp_ar.y, s=250, c='None', lw=2.5, edgecolor=color_team, marker='^', hatch='/////', ax=ax)
    pitch.scatter(hp_ar_u.x, hp_ar_u.y, s=250, c='None', lw=2.5, edgecolor='gray', marker='^', hatch='/////', ax=ax)
    pitch.scatter(drb_pst.x, drb_pst.y, s=250, c='None', lw=2.5, edgecolor=color_team, marker='h', hatch='|||||', ax=ax)

    if is_away_team:
        ax_text(100, 105, f'''        Tackle (Win): {len(hp_tk)} ({len(hp_tk) - len(hp_tk_u)}) | Dribblers Tackled: {len(drb_tkl)} | Dribbled past: {len(drb_pst)} | Interception: {len(hp_intc)}
        Ball Recovery: {len(hp_br)} | Post Recovery Ball Retention: {post_rec_ball_retention} %  | Pass Block: {len(pass_bl)}
        Ball Clearances: {len(hp_cl)} | Shots Blocked: {len(shot_bl)} | Aerial Duels (Win): {len(hp_ar)} ({len(hp_ar) - len(hp_ar_u)}) | Fouls: {len(hp_fl_committed)}
        Fouls infront of Penalty Box: {len(dan_frk)} | Error Led to Shot/Led to Goal: {len(err_lat)}/{len(err_lgl)}
        Possession Win in Final third/Mid third/Defensive third: {len(f_third)}/{len(m_third)}/{len(d_third)}
        ''', fontsize=10, ha='left', va='top', color= 'white', ax=ax)
    
    else:
        ax_text(10, -2, f'''        Tackle (Win): {len(hp_tk)} ({len(hp_tk) - len(hp_tk_u)}) | Dribblers Tackled: {len(drb_tkl)} | Dribbled past: {len(drb_pst)} | Interception: {len(hp_intc)}
        Ball Recovery: {len(hp_br)} | Post Recovery Ball Retention: {post_rec_ball_retention} %  | Pass Block: {len(pass_bl)}
        Ball Clearances: {len(hp_cl)} | Shots Blocked: {len(shot_bl)} | Aerial Duels (Win): {len(hp_ar)} ({len(hp_ar) - len(hp_ar_u)}) | Fouls: {len(hp_fl_committed)}
        Fouls infront of Penalty Box: {len(dan_frk)} | Error Led to Shot/Led to Goal: {len(err_lat)}/{len(err_lgl)}
        Possession Win in Final third/Mid third/Defensive third: {len(f_third)}/{len(m_third)}/{len(d_third)}
        ''', fontsize=10, ha='left', va='top', color= 'white', ax=ax)

    legend_elements = [
        Line2D([0], [0], marker='+', color=color_team, linestyle='None',  markersize=12, label='Tackle Won'),

        Line2D([0], [0], marker='+', color='gray', linestyle='None',  markersize=12, label='Tackle Lost'),

        Line2D([0], [0], marker='s', markerfacecolor='none',  markeredgecolor=color_team, linestyle='None',  markersize=10, label='Interception'),

        Line2D([0], [0], marker='o', markerfacecolor='none',  markeredgecolor=color_team, linestyle='None',  markersize=10, label='Ball Recovery'),

        Line2D([0], [0], marker='d', markerfacecolor='none',  markeredgecolor=color_team, linestyle='None',  markersize=10, label='Clearance'),

        Line2D([0], [0], marker='x', color=color_team,  linestyle='None', markersize=10,  label='Foul Committed'),

        Line2D([0], [0], marker='^', markerfacecolor='none',  markeredgecolor=color_team, linestyle='None',  markersize=10, label='Aerial Won'),

        Line2D([0], [0], marker='^', markerfacecolor='none',  markeredgecolor='gray', linestyle='None',  markersize=10, label='Aerial Lost'),

        Line2D([0], [0], marker='h', markerfacecolor='none',  markeredgecolor=color_team, linestyle='None',  markersize=10, label='Dribbled Past')
        ]

    ax.legend( handles=legend_elements, loc='lower center', bbox_to_anchor=(1.08, 0.5), ncol=1, frameon=False, fontsize=10, labelcolor='white')

    return fig, ax

def prepare_dataframe_shots_playerofmatch(df, data,team_dict_fotmob, name_home_fotmob,name_away_fotmob):
    shots_df= pd.DataFrame(data['content']['shotmap']['shots'])
    shots_df = shots_df[shots_df['period']!='PenaltyShootout']
    shots_df['teamName'] = shots_df['teamId'].map(team_dict_fotmob)

    #Dataframe eventos whoscored
    df_events_shots = df[ (df['isShot'] == True) & (df['period'] != 'PenaltyShootout')][['id', 'qualifiers', 'type', 'name','satisfiedEventsTypes']]

    shots_merged = pd.merge(shots_df, df_events_shots, left_on='id', right_on='id', how='left')

    
    # Add flags
    shots_merged['is_big_chance'] = shots_merged['qualifiers'].apply(is_big_chance)
    shots_merged['is_own_goal'] = shots_merged['qualifiers'].apply(is_own_goal)

    home= name_home_fotmob
    away = name_away_fotmob

    team_swap = {
            home: away,
            away: home
        }
    shots_merged['render_team'] = shots_merged['teamName']

    shots_merged.loc[
        shots_merged['is_own_goal'],
        'render_team'
    ] = shots_merged.loc[
        shots_merged['is_own_goal'],
        'teamName'
    ].map(team_swap)

    return shots_merged

def prepare_df_shotsgoal_pom(df, name_home , name_away):
    df['render_team'] = df['teamName']

    mask = df['isOwnGoal'].eq(True)

    home= name_home
    away = name_away
    team_swap = {
        home: away,
        away: home
    }

    df.loc[mask, 'render_team'] = (
        df.loc[mask, 'teamName'].map(team_swap)
    )
    hShotsdf = df[df['render_team']==name_home].reset_index(drop=True).copy()
    aShotsdf = df[df['render_team']==name_away].reset_index(drop=True).copy() 

    df_coords_h = hShotsdf['onGoalShot'].apply(pd.Series)

    df_coords_h = df_coords_h.rename(columns={
        'x': 'coord_x',
        'y': 'coord_y',
        'zoomRatio': 'coord_zoom'
    })
    df_tiros_coord_home = pd.concat([hShotsdf.drop(columns=['onGoalShot']), df_coords_h], axis=1)

    df_coordsa = aShotsdf['onGoalShot'].apply(pd.Series)

    df_coordsa = df_coordsa.rename(columns={
        'x': 'coord_x',
        'y': 'coord_y',
        'zoomRatio': 'coord_zoom'
    })
    df_tiros_coord_away = pd.concat([aShotsdf.drop(columns=['onGoalShot']), df_coordsa], axis=1)

    return df_tiros_coord_home, df_tiros_coord_away
    
def draw_goal_pom( df, imagen_pelota_path, imagen_pelota_red_path, ax=None):
    path_eff = [
        path_effects.Stroke(linewidth=1, foreground='white'),
        path_effects.Normal()
    ]
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 3.2), facecolor= 'none')
    else:
        fig = ax.figure
        ax.text(
            0.5, 1.54, "GK SAVES",
            transform=ax.transAxes,
            ha="center", va="center",
            color="white", fontsize=20,
            fontweight="bold",
            path_effects=path_eff
        )
    
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 0.68)
    ax.set_facecolor('none')
    ax.patch.set_alpha(0)
    ax.set_aspect("equal")
    ax.axis("off")

    # césped
    ax.fill_between([0, 2], 0, -0.06, color="green", alpha=0.3)

    # marco
    post_width = 0.03
    goal_height = 0.65
    goal_width = 1.99

    ax.add_patch(patches.Rectangle((0.01, 0), post_width, goal_height, color="white", zorder=1))
    ax.add_patch(patches.Rectangle((goal_width - post_width, 0), post_width, goal_height, color="white", zorder=1))
    ax.add_patch(patches.Rectangle((0.01, goal_height - 0.015), goal_width - 0.02, 0.015, color="white", zorder=1))

    # red
    num_lines = 6
    for i in range(1, num_lines):
        x = i * goal_width / num_lines
        ax.plot([x, x], [0, goal_height], color="lightgray", lw=0.5, zorder=0)

    for j in range(1, int(goal_height * 20)):
        y = j * goal_height / (goal_height * 20)
        ax.plot([0.01, goal_width - 0.01], [y, y], color="lightgray", lw=0.5, zorder=0)

    # tiros
    for _, row in df.iterrows():

        # ---------------------------
        # GOAL NORMAL vs OWN GOAL
        # ---------------------------
        if row["type"] == "Goal":

            # si es own goal → pelota roja
            if row.get("isOwnGoal", False):

                im = OffsetImage(imagen_pelota_red_path, zoom=0.02)

            # goal normal → pelota normal
            else:
                im = OffsetImage(imagen_pelota_path, zoom=0.03)

            ab = AnnotationBbox(
                im,
                (row["coord_x"], row["coord_y"]),
                frameon=False,
                zorder=10
            )

            ax.add_artist(ab)

        # ---------------------------
        # SAVED SHOT
        # ---------------------------
        elif row["type"] == "SavedShot" and not row["isBlocked"]:
            ax.scatter(
                row["coord_x"], row["coord_y"],
                s=350, alpha=0.6,
                color='red', edgecolors="white"
            )

        # ---------------------------
        # POST
        # ---------------------------
        elif row["type"] in ["Post", "ShotOnPost"]:
            ax.scatter(
                row["coord_x"], row["coord_y"],
                s=350, alpha=0.6,
                color='orange', edgecolors="white"
            )
    return fig, ax
