import pandas as pd
from functions.results import * 
from functions.plots import *

from services.load_data import load_all_matches_fotmob, load_all_players_fotmob

from pathlib import Path
import matplotlib.image as mpimg

BASE_DIR = Path(__file__).resolve()

IMG_DIR = BASE_DIR.parents[1] / "assets" / "images"

IMG_PELOTA = IMG_DIR / "sport-ball-football-free-png.webp"
IMG_PELOTA_ROJA = IMG_DIR / "pelota_roja.png"

IMAGEN_PELOTA = mpimg.imread(IMG_PELOTA)
IMAGEN_PELOTA_ROJA = mpimg.imread(IMG_PELOTA_ROJA)

def render_results(df: pd.DataFrame):

    # =============================================================================
    # MATCH SELECTION
    # =============================================================================
    #
    # Apply stage/group/date filters and display the list of available matches.
    # Users can select a completed match to open the detailed analysis dashboard.
    #

    partidos, stage_selected, group_selected, fecha_elegida, id_stage= results_filtres(df)

    # =============================================================================
    # LOAD SELECTED MATCH
    # =============================================================================
    #
    # Once a match is selected, retrieve the basic metadata required for the
    # analysis workflow:
    #
    # - Teams
    # - Match status
    # - Team logos
    # - Match URLs
    #
    
    match_list_post_filter(partidos, stage_selected, group_selected, fecha_elegida, id_stage)

    if st.session_state.get("partido_mostrado"):
        partido_filtrado = df[df["url_match"] == st.session_state["partido_mostrado"]].reset_index(drop=True)
        if partido_filtrado.empty:
            st.session_state.pop("partido_mostrado", None)
            #st.warning("This match is not visible with the selected filters. Try changing stage, group or date.")
            st.stop()
        
        else:
            partido_detalle = partido_filtrado.iloc[0]

            selected_home_team = partido_detalle["homeTeamName"]
            selected_away_team = partido_detalle["awayTeamName"]

            url_match_preview= partido_filtrado['url_match'].values[0]
            estado = partido_filtrado['elapsed'][0]
            round_name_whoscored = str(partido_filtrado['round_id'][0])
            group_round= partido_filtrado['stageName'][0].split('Cup')[1].strip()

            homeTeamPhoto = partido_detalle["homeTeamPhoto"]
            awayTeamPhoto = partido_detalle["awayTeamPhoto"]

            match_round_good= partido_detalle["matchround"]

            ROUND_MAPPING = {
                '4': "1/16",
                '5': "1/8",
                '6': "Quarter-final",
                '7': "Semi-final",
                '8': "Final"
            }

            round_name_whoscored_for_fotmob = ROUND_MAPPING.get(round_name_whoscored, str(round_name_whoscored))
            # =============================================================================
            # LOAD FOTMOB MATCH DATA
            # =============================================================================
            #
            # Retrieve FotMob data used for:
            #
            # - Team colors
            # - Shot maps
            # - xG models
            # - Attack momentum visualizations
            #
            # Priority:
            #     1. Memory cache
            #     2. Local JSON files
            #     3. Stop execution if unavailable

            df_all_matches_fotmob=  load_all_matches_fotmob()
            url_match_fotmob= extract_url_fotmob(df_all_matches_fotmob, selected_home_team, selected_away_team, round=round_name_whoscored_for_fotmob)
            match_id_fotmob= extract_match_id_fotmob(url_match_fotmob)
            cache_data_fotmob= load_match_cache_fotmob(match_id_fotmob)
            if cache_data_fotmob:
                #st.badge(f"🟢 Data loaded from CACHE MATCHES FOTMOB (match {match_id_fotmob})",  color="green")
                data = cache_data_fotmob["data"]
            else:
                json_path = Path(f"data/json_matches_fotmob/{match_id_fotmob}.json")
                if json_path.exists():
                    with st.spinner("🟡 Loading match data from JSON..."):
                        with open(json_path) as f:
                            data = json.load(f)
                        save_match_cache_fotmob(match_id_fotmob, data)
                        #st.badge(f"🔵 Cache created successfully for match {match_id_fotmob}",  color="blue")
                else:
                    st.badge("📭 No data available for this match yet. Data is pending update from the provider.", color= 'yellow')
                    st.stop()
                    

            color_home, color_away,name_home_fotmob, name_away_fotmob, id_home_fotmob, id_away_fotmob, team_dict_fotmob = prepare_data_fotmob_cache(data)
            
                # =============================================================================
            # LOAD WHOSCORED EVENT DATA
            # =============================================================================
            #
            # Retrieve event-level match data from cache or scrape if necessary.
            #
            # This dataset powers:
            #
            # - Passing analysis
            # - Defensive actions
            # - Formations
            # - Positional analysis
            # - Event timelines
            # - Tactical reports

            # =============================================================================
            # DATA PREPARATION
            # =============================================================================
            #
            # Transform raw provider data into structured objects required by the
            # visualization modules.
            #
            # Generated structures:
            #
            # - Team information
            # - Match metadata
            # - Event dataframe
            # - Player mappings
            # - Team dictionaries
            
            formation_mappings, event_types_json, matchdict, players_dict = prepare_data_whoscored_cache(url_match_preview)

            #formation_mappings, event_types_json, matchdict,players_dict = extract_match_dict_url(url_match_preview)

            team_info = [parse_team(matchdict.get('home', {})), parse_team(matchdict.get('away', {}))]
            team_info = pd.DataFrame(team_info)

            (home_team, away_team,homeScore, awayScore, et_score_home, et_score_away, penalty_score_home, penalty_score_away, manager_name_home,
                    manager_name_away,initial_formation_home, initial_formation_away, average_age_home, average_age_away, 
                    initial_captain_id_home, initial_captain_id_away )  = extract_variables_team_info_details(team_info) 

            
            teams_dict_id_name_whoscored = {matchdict['home']['teamId']: matchdict['home']['name'],
                matchdict['away']['teamId']: matchdict['away']['name']}

            home_team_dict = {
                'name': matchdict['home']['name'],
                'team_id': matchdict['home']['teamId'],
                'players': matchdict['home']['players']
            }
            away_team_dict = {
                'name': matchdict['away']['name'], 
                'team_id': matchdict['away']['teamId'],
                'players': matchdict['away']['players']
            }

            df = prepare_df_events(matchdict, teams_dict_id_name_whoscored)

            match_info= extract_match_info_details(matchdict)

            # =============================================================================
            # MATCH STATUS INTERPRETATION
            # =============================================================================
            #
            # Convert provider-specific match status values into user-friendly labels
            # for display in the match overview card.
            #
            # Examples:
            #
            # FT  -> Full Time
            # AET -> After Extra Time
            # PEN -> Penalty Shootout
            
            if estado == "PEN":
                texto_estado = f"PEN ({penalty_score_home}-{penalty_score_away})"

            elif estado == "AET":
                texto_estado = f"AET ({et_score_home}-{et_score_away})"

            elif estado == "FT":
                texto_estado = "(FT)"

            else:
                texto_estado = estado

            # if (selected_home_team == 'IR Iran') and (selected_away_team == 'New Zealand'):
            #      st.warning("The away team's color is currently incorrect. The data provider will resolve this issue shortly!")
            

            st.write("---") 

            # =============================================================================
            # MATCH DETAILS DASHBOARD
            # =============================================================================
            #
            # Main interactive dashboard containing:
            #
            # - Team information
            # - Match overview
            # - Key events timeline
            # - Formations
            # - Tactical analysis
            #
            # Layout:
            #
            # Left Column   -> Home Team
            # Center Column -> Match Analysis
            # Right Column  -> Away Team


            col1, col_space1, col2, col_space2, col3 = st.columns([2,0.3, 4,0.3, 2])

            player_home, player_away = extract_players_team(matchdict)

            with col1:
                # =============================================================================
                # HOME TEAM PANEL
                # =============================================================================
                #
                # Displays:
                #
                # - Team logo
                # - Manager
                # - Formation
                # - Average age
                # - Starting XI
                # - Substitutes
                # - Substitution timeline
                principal_card_team(homeTeamPhoto,manager_name_home, initial_formation_home, average_age_home )       

                st.write('')
                alineacion_home = st.segmented_control(" ", ["Starting XI", "Substitutes"], default="Starting XI", key="home_squad_selector")                 
                
                first_eleven_home= card_formations_subs(player_home, initial_captain_id_home, alineacion_home)

                st.write("---") 

                write_subtitle("SUBSTITUTIONS")
                
                home_events = pd.DataFrame(matchdict['home']['incidentEvents'])
                card_substitutions(home_events, teams_dict_id_name_whoscored ,players_dict) 

            with col_space1:
                st.write('')

            with col2:
                # =============================================================================
                # MATCH CENTER PANEL
                # =============================================================================
                #
                # Core match information and tactical visualizations.
                #
                # Includes:
                #
                # - Match scoreboard
                # - Venue information
                # - Referee
                # - Player of the Match
                # - Key events timeline
                # - Penalty shootout details
                # - Initial formations
                card_match_overview(home_team,away_team,homeScore, awayScore, color_home, color_away ,texto_estado)
                st.write('')

                jugador_partido = player_home.loc[player_home["isManOfTheMatch"]]
                if jugador_partido.empty:
                    jugador_partido = player_away.loc[player_away["isManOfTheMatch"]]
                nombre_jugador_partido = jugador_partido["name"].iloc[0]

                referee_html = ""

                if match_info.get('referee') and match_info['referee'].get('name'):
                    referee_html = f"Referee: {match_info['referee']['name']}"
                else:
                    referee_html = "Referee: No data available"

                st.markdown(
                        f"""
                        <p style='text-align:center; font-size:15px; margin:0.5; line-height:1.4;'>
                            Ubicación: {match_info['venue_name']} (Attendance: {match_info['attendance']})<br>
                            {referee_html} <br>
                            ⭐ Player of the Match: {nombre_jugador_partido}
                        </p>
                        """,
                        unsafe_allow_html=True
                    )
                st.write('----')

                # =============================================================================
                # MATCH EVENT TIMELINE
                # =============================================================================
                #
                # Build a chronological timeline of relevant match incidents:
                #
                # - Goals
                # - Assists
                # - Cards
                # - Penalties
                # - Shootout events

                write_subtitle("KEY EVENTS")

                df_match, df_shootout = create_events_keys(matchdict, teams_dict_id_name_whoscored, players_dict, home_team, away_team)                                    
                card_events_key_match(df_match, home_team,away_team)
                
                st.write(" ")

                col1_pen, col_mid_pen, col2_pen=st.columns(3)
                use_penalty_shootout = False
                with col_mid_pen:
                    if not df_shootout.empty:
                        st.markdown("""
                            <style>
                            div[data-testid="stCheckbox"] label p {
                                font-size: 12px !important;
                            }
                            </style>
                            """, unsafe_allow_html=True)
                        use_penalty_shootout = st.checkbox("🥅 View the penalty shootout")
                
                if use_penalty_shootout:
                    card_penalty_shootout(df_shootout, home_team,away_team  )

                st.write('----')
                
                # =============================================================================
                # INITIAL FORMATIONS VISUALIZATION
                # =============================================================================
                #
                # Plot both starting formations using event-derived player
                # positions and formation mappings.

                write_subtitle("INITIAL FORMATIONS")
                fig, ax= plot_initial_formation(df, home_team, away_team, formation_mappings, players_dict,color_home,color_away ,nombre_jugador_partido)
                st.pyplot(fig)

            with col_space2:
                st.write('')

            with col3:

                # =============================================================================
                # AWAY TEAM PANEL
                # =============================================================================
                #
                # Mirrors the home team panel and provides:
                #
                # - Team information
                # - Squad selection
                # - Starting XI
                # - Bench players
                # - Substitution activity

                principal_card_team(awayTeamPhoto,manager_name_away, initial_formation_away, average_age_away)    
                
                
                st.write('')
                alineacion_away = st.segmented_control( " ", ["Starting XI", "Substitutes"], default="Starting XI",key="away_squad_selector")  
                
                first_eleven_away= card_formations_subs(player_away, initial_captain_id_away, alineacion_away)

                st.write("---") 
                
                write_subtitle("SUBSTITUTIONS")                   
                away_events = pd.DataFrame(matchdict['away']['incidentEvents'])
                card_substitutions(away_events, teams_dict_id_name_whoscored ,players_dict)          
                
            
            st.write('---')
            
            # =============================================================================
            # ADVANCED MATCH ANALYSIS
            # =============================================================================
            #
            # Comprehensive tactical analysis module combining event data
            # (WhoScored) and shot data (FotMob).
            #
            # Analysis modes:
            #
            # • Team Analysis
            # • Player of the Match (future implementation)
            #
            # The dashboard is divided into:
            #
            # - Overview
            # - Attack
            # - Possession
            # - Defense
            # - Goalkeeper
            # - Report Generation
        

            option = st.segmented_control('Analysis type:\n\n', 
                                    ['Team Analysis', 'Player of the Match'], default='Team Analysis')
            
            if option == "Team Analysis":

                main_tabs = st.tabs([
                    "📊 Overview",
                    "⚽ Attack",
                    "🧠 Possession",
                    "🛡️ Defense",
                    "🥅 Goalkeeper",
                    "📑 Generate reports"
                ])

                # =====================
                # OVERVIEW
                # =====================
                with main_tabs[0]:

                    overview_tabs = st.tabs([
                        "Match Stats",
                        "xG Flow",
                        "Attack Momentum",
                        "Dominating Zone"
                    ])
                    with overview_tabs[0]:
                        write_subtitle(" MATCH STATS COMPARISON")
                    
                        col1, col2, col3= st.columns([1, 3, 1])

                        with col2:

                            stats = calculate_match_stats(df, matchdict['home']['teamId'], matchdict['away']['teamId'])
                            fig_stats,ax= plot_match_stats_styled(stats, color_home, color_away,  "Home Team", "Away Team", show_title=False)
                            st.pyplot(fig_stats)
                        
                    with overview_tabs[1]:
                        write_subtitle("EVOLUTIVE EXPECTED GOAL (xG)")
                    
                        col1, col2, col3= st.columns([1, 3, 1])

                        with col2:
                            shots_merged, home_stats, away_stats = prepare_dataframe_shots(df, data, team_dict_fotmob, name_home_fotmob, name_away_fotmob)

                            datos_xg = preparar_xg_flows(shots_merged, name_home_fotmob)
                                                    
                            local_xg,  visit_xg,   goles_local_xg,goles_visit_xg, xg_home,  xg_away = get_data_xg(datos_xg)

                            # Crear la figura con la función de xG Flow
                            fig_xg ,ax= plot_xg_flow_streamlit( local_xg, visit_xg, goles_local_xg,goles_visit_xg, name_home_fotmob,
                                    name_away_fotmob,  color_home, color_away, IMAGEN_PELOTA, IMAGEN_PELOTA_ROJA)
                            st.pyplot(fig_xg)
                        

                    with overview_tabs[2]:
                        write_subtitle("ATTACK MOMENTUM (xT)")
                    
                        col1, col2, col3= st.columns([1, 3, 1])
                        
                        with col2:
                        
                            shots_merged, home_stats, away_stats = prepare_dataframe_shots(df, data, team_dict_fotmob, name_home_fotmob, name_away_fotmob)
                            df_copy= preparare_df_xt(df, name_home_fotmob,name_away_fotmob)
                            fig_xt, ax = plot_xt_momentum(df_copy, xT_grid, teams_dict_id_name_whoscored, matchdict['home']['teamId'],
                                                    matchdict['away']['teamId'], home_color= color_home, away_color=color_away)
                            st.pyplot(fig_xt)
                        

                    with overview_tabs[3]:
                        write_subtitle("TEAM'S DOMINATING ZONE")
                    
                        col1, col2, col3= st.columns([1, 3, 1])

                        with col2:

                            fig_dom,ax= plot_congestion( df, matchdict['home']['name'], matchdict['away']['name'],color_home ,color_away, show_title= False)
                            st.pyplot(fig_dom)
                            

                
                # =====================
                # ATTACK
                # =====================
                with main_tabs[1]:

                    attack_tabs = st.tabs([
                        "Shotmap",
                        "Progressive Passes",
                        "Final Third Entry",
                        "Zone 14 and Halfspaces Pass",
                        "Chance Creation",
                        "Crosses"
                        ])

                    with attack_tabs[0]:
                        write_subtitle("SHOTMAP AND STATS")
                
                        col1, col2, col3= st.columns([1, 3, 1])

                        with col2:

                            fig_shots, ax = plot_shot_map_with_stats( shots_merged, home_stats, away_stats, id_home_fotmob, id_away_fotmob, 
                                                                    name_home_fotmob, name_away_fotmob,color_home, color_away)
                            st.pyplot(fig_shots)
                        
                    with attack_tabs[1]:
                        write_subtitle("PROGRESSIVE PASSES")
                
                        # Create the visualization
                        fig_pp, axs = plt.subplots(1, 2, figsize=(20, 10), facecolor='none')
                        axs[0].set_facecolor('none')
                        axs[1].set_facecolor('none')
                        
                        
                        draw_progressive_pass_map(df, matchdict['home']['teamId'], matchdict['home']['name'],color_home, is_away_team=False, ax= axs[0],show_title= False)
                        axs[0].text(0,  -3, 'Attacking Direction--->', color=color_home, fontsize=13, ha='left', va='center')
                        
                        draw_progressive_pass_map( df, matchdict['away']['teamId'], matchdict['away']['teamId'], color_away, is_away_team=True, ax= axs[1], show_title= False)
                        axs[1].text(0,83, '<---Attacking Direction', color=color_away, fontsize=13, ha='right', va='center')


                        plt.tight_layout()
                        st.pyplot(fig_pp)

                    with attack_tabs[2]:
                        write_subtitle("FINAL THIRD ENTRY")

                        fig_fte,axs=plt.subplots(1,2, figsize=(20,10), facecolor='none')
                        Final_third_entry(df,matchdict['home']['name'], color_home, color_home, color_away, ax= axs[0], show_title=False)
                        axs[0].text(0 , 103, '<---Attacking Direction', color=color_home, fontsize=13, ha='right', va='center')
                        
                        Final_third_entry(df, matchdict['away']['name'], color_away,color_home, color_away, ax= axs[1], show_title= False)
                        axs[1].text(0 , 103, '<---Attacking Direction', color=color_away, fontsize=13, ha='right', va='center')
                        st.pyplot(fig_fte)              


                    with attack_tabs[3]:
                        write_subtitle("ZONE 14 AND HALFSPACES PASS")
                
                        pearl_earring_cmaph = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",  ['black', color_home], N=20)
                        pearl_earring_cmapa = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",  ['black', color_away], N=20)
                    
                        
                        fig,axs=plt.subplots(1,2, figsize=(20,10), facecolor='none')

                        fig.set_facecolor('none')
                        axs[0].set_facecolor('none')
                        axs[1].set_facecolor('none')

                        zone14hs(axs[0], df,  matchdict['home']['name'], color_home)
                        axs[0].text(105, 70, '<---Attacking Direction', color=color_home, fontsize=13, ha='left', va='center')

                        zone14hs(axs[1],df, matchdict['away']['name'], color_away)
                        axs[1].text(0 , 70, '<---Attacking Direction', color=color_away, fontsize=13, ha='right', va='center')
                        
                        plt.tight_layout()
                        st.pyplot(fig)

                    with attack_tabs[4]:
                        write_subtitle("CHANCE CREATE ZONE")
                
                        pearl_earring_cmaph = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",  ['black', color_home], N=20)
                        pearl_earring_cmapa = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",  ['black', color_away], N=20)
                    
                        col1_c, col2_c= st.columns(2)

                        with col1_c:
                            fig_chance, ax= Chance_creating_zone(df, matchdict, matchdict['home']['name'],pearl_earring_cmaph, color_home, color_home, color_away, title= False)
                            ax.text(0,  -2.5, 'Attacking Direction--->', color=color_home, fontsize=13, ha='left', va='center')
                            st.pyplot(fig_chance)

                        with col2_c:
                            fig_chance_a, ax = Chance_creating_zone( df, matchdict, matchdict['away']['name'],pearl_earring_cmapa,  color_away, color_home, color_away, title= False)
                            ax.text(0 , 103, '<---Attacking Direction', color=color_away, fontsize=13, ha='right', va='center')
                            st.pyplot(fig_chance_a)

                    with attack_tabs[5]:
                        write_subtitle("CROSSES")
                        col1, col2, col3= st.columns([1, 3, 1])

                        with col2:
                            fig_crosses, ax = Crosses( df, matchdict, color_home, color_away, show_title= False)
                            st.pyplot(fig_crosses)
                        
                # =====================
                # POSSESSION
                # =====================
                with main_tabs[2]:

                    possession_tabs = st.tabs([
                        "Average Positions",
                        "Passing Networks",
                        "Heatmap Touches",
                        "Pass End Zone"
                        ])

                    with possession_tabs[0]:
                        write_subtitle("PLAYERS AVERAGE POSITIONS")
                        
                        avg_pos = prepare_positional_events(df, players_dict)

                        col1, col2 = st.columns(2)

                        with col1:
                            av_players_home = create_dataframe_median_positions(df,avg_pos, home_team_dict, away_team_dict,teams_dict_id_name_whoscored, players_dict,is_home= True)
                            fig_pm_home, ax= plot_player_position_median(av_players_home, background_color, color_home, is_home= True)
                            st.pyplot(fig_pm_home)

                        with col2:
                            av_players_away = create_dataframe_median_positions(df,avg_pos, home_team_dict, away_team_dict,teams_dict_id_name_whoscored , players_dict,is_home= False)
                            fig_pm_away , ax= plot_player_position_median(av_players_away, background_color, color_away, is_home= False)
                            st.pyplot(fig_pm_away)


                    with possession_tabs[1]:
                        write_subtitle("PASSING NETWORKS")

                        # Enhanced analysis with Athletic-style colors
                        passes_df = prepare_enhanced_passes(df)
                        # Home team analysis
                        home_avg_locs = get_enhanced_positions(passes_df, home_team_dict['team_id'], 
                                                            home_team_dict['players'], players_dict)
                        home_combinations = get_pass_combinations(passes_df, home_team_dict['team_id'])
                        home_metrics = calculate_team_metrics(passes_df, home_avg_locs, home_team_dict['team_id'])
                        # Away team analysis  
                        away_avg_locs = get_enhanced_positions(passes_df, away_team_dict['team_id'],
                                                            away_team_dict['players'], players_dict)
                        away_combinations = get_pass_combinations(passes_df, away_team_dict['team_id'])
                        away_metrics = calculate_team_metrics(passes_df, away_avg_locs, away_team_dict['team_id'])

                        # Plot with Athletic styling
                        fig , (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
                        fig.patch.set_facecolor('none')  # Transparent background for entire figure

                        plot_enhanced_network( passes_df, home_avg_locs, home_combinations, home_metrics,
                                            home_team_dict['name'], color=color_home, is_home=True, bg_color=background_color,  ax= ax1, show_title= False)

                        plot_enhanced_network( passes_df, away_avg_locs, away_combinations, away_metrics,
                                            away_team_dict['name'], color=color_away, is_home=False, bg_color=background_color , ax=ax2, show_title= False)

                        plt.tight_layout()
                        st.pyplot(fig)

                    with possession_tabs[2]:
                        write_subtitle("HEATMAP TOUCHES")
                
                        col1, col2 = st.columns(2)

                        with col1:
                            fig_hpt_home, ax= plot_heatmap_touches(df, home_team,color_home, is_home= True)
                            st.pyplot(fig_hpt_home)

                        with col2:
                            fig_hpt_away, ax=plot_heatmap_touches(df, away_team , color_away, is_home= False)
                            st.pyplot(fig_hpt_away)

                    with possession_tabs[3]:
                        write_subtitle("PASS END ZONE")
                        pearl_earring_cmaph = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",  ['black', color_home], N=20)
                        pearl_earring_cmapa = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",  ['black', color_away], N=20)
                    
                        fig,axs_p=plt.subplots(1,2, figsize=(20,10), facecolor='none')
                        axs_p[0].set_facecolor('none')
                        axs_p[1].set_facecolor('none')
                        fig.set_facecolor('none')

                        Pass_end_zone( df,  matchdict['home']['name'],pearl_earring_cmaph,  axs_p[0],show_title=False)
                        axs_p[0].text(100,  103, 'Attacking Direction--->', color=color_home, fontsize=13, ha='left', va='center')

                        Pass_end_zone(df, matchdict['away']['name'], pearl_earring_cmapa,  axs_p[1],show_title=False)
                        axs_p[1].text(0 , 103, '<---Attacking Direction', color=color_away, fontsize=13, ha='right', va='center')
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                
                # =====================
                # DEFENSE
                # =====================
                with main_tabs[3]:

                    defense_tabs = st.tabs([
                        "Defensive Actions",
                        "Heatmap Actions"
                        ])

                    with defense_tabs[0]:
                        write_subtitle("DEFENSIVE ACTIONS HEATMAP")
                
                        # Run the defensive heatmap analysis
                        home_positions, away_positions, home_actions, away_actions= create_defensive_heatmap_analysis(df, home_team_dict, away_team_dict)
                        # Create TWO subplots side by side - 
                        fig_def, axs = plt.subplots(1, 2, figsize=(20, 10), facecolor='none')

                        # Create defensive blocks for each team 
                        defensive_block(home_positions, home_actions, home_team_dict['name'], color_home, is_away_team=False, ax= axs[0])

                        defensive_block( away_positions, away_actions, away_team_dict['name'], color_away, is_away_team=True, ax= axs[1])

                        st.pyplot(fig_def)

                    with defense_tabs[1]:
                        write_subtitle("HEATMAP ACTIONS")
                
                        col1, col2 = st.columns(2)

                        with col1:
                            fig_hpa_home= plot_heatmap_team(df, home_team,color_home, is_home= True)
                            st.pyplot(fig_hpa_home)

                        with col2:
                            fig_hpa_away=plot_heatmap_team(df, away_team , color_away, is_home= False)
                            st.pyplot(fig_hpa_away)
                
                # =====================
                # GOALKEEPER
                # =====================
                with main_tabs[4]:

                    gk_tabs = st.tabs([
                        "Goal Post Analysis"
                        ])

                    with gk_tabs[0]:
                        col1, col2, col3= st.columns([1, 3, 1])

                        with col2:
                            df_tiros_coord_home, df_tiros_coord_away = prepare_df_shotsgoal(shots_merged, name_home_fotmob , name_away_fotmob)
                            fig = plot_gk(df_tiros_coord_home, df_tiros_coord_away, color_home,color_away,  IMAGEN_PELOTA,  IMAGEN_PELOTA_ROJA)
                            st.pyplot(fig, transparent=True)
                        
                # =====================
                # OVERVIEW
                # =====================
                with main_tabs[5]:
                    st.subheader("📑 Match Reports")
                    st.caption("Generate and download tactical reports based on the match analysis.")
                    st.divider()

                    cache_key_reporte = f"{name_home_fotmob}_{name_away_fotmob}_report1"
                    cache_key_reporte2 = f"{name_home_fotmob}_{name_away_fotmob}"
                    # cache_key_reporteplayer = f"{name_home_fotmob}_{name_away_fotmob}_player"

                    report1_exists = cache_key_reporte in st.session_state
                    report2_exists = cache_key_reporte2 in st.session_state    

                    col1tactical1, col2tactical = st.columns(2)

                    with col1tactical1:
                        st.subheader("📋 Tactical Report 1")
                        st.caption(
                            "Complete tactical overview featuring formations, player positioning, passing networks, "
                            "ball progression, defensive activity, xT momentum, shot analysis and key performance "
                            "metrics to evaluate both team structure and match execution."
                        )

                        if report1_exists:
                            st.badge("✅ Ready to download", color="green")
                            st.image(
                                st.session_state[cache_key_reporte],
                                use_container_width=True
                            )
                            st.download_button(
                                        "📥 Download report 1",
                                        data=st.session_state[cache_key_reporte],
                                        file_name=f"match_report_parte1_{name_home_fotmob}_{name_away_fotmob}.png",
                                        mime="image/png"
                                    )
                        else:
                            st.badge("❌ Not generated", color="red")
                            if st.button("Generate Report 1"):
                                with st.spinner("⏳ Generating tactical report 1..."):
                                        fig_bytes = create_match_report1_plot(referee_html,group_round, match_round_good, id_stage, id_home_fotmob,id_away_fotmob,name_home_fotmob,name_away_fotmob,homeScore,awayScore,texto_estado,
                                                                match_info, nombre_jugador_partido, av_players_home, av_players_away, df, passes_df,
                                                                home_avg_locs,away_avg_locs,home_combinations,away_combinations,   home_metrics,   away_metrics,
                                                            home_team_dict, away_team_dict, color_home, color_away, background_color, stats,
                                                            xT_grid, teams_dict_id_name_whoscored, matchdict, home_positions, home_actions, away_positions,
                                                            away_actions, data, team_dict_fotmob, formation_mappings, players_dict)
                                
                                        st.session_state[cache_key_reporte] = fig_bytes
                                        st.toast("Tactical report 1 generated successfully")
                                        st.rerun()

                    with col2tactical:
                        st.subheader("📋 Tactical Report 2")
                        st.caption(
                            "Advanced attacking report featuring pass end zones, touch heatmaps, chance creation patterns, "
                            "expected goals evolution, final-third entries, crossing activity and goalkeeper interventions "
                            "to assess territorial dominance and offensive effectiveness."
                        )
                        if report2_exists:
                            st.badge("✅ Ready to download", color="green")
                            st.image(
                                st.session_state[cache_key_reporte2],
                                use_container_width=True
                            )
                            st.download_button(
                                        "📥 Download report 2",
                                        data=st.session_state[cache_key_reporte2],
                                        file_name=f"match_report_part2_{name_home_fotmob}_{name_away_fotmob}.png",
                                        mime="image/png"
                                    )
                        else:
                            st.badge("❌ Not generated", color="red")
                            if st.button("Generate Report 2"):
                                with st.spinner("⏳ Generating tactical report 2..."):
                                        fig_bytes_2 = create_match_report2_plot(referee_html,group_round, match_round_good, id_stage, id_home_fotmob,id_away_fotmob,name_home_fotmob,name_away_fotmob,homeScore,awayScore,texto_estado,
                                                        match_info, nombre_jugador_partido, df, matchdict, color_home, color_away, home_team, away_team,
                                                        local_xg, visit_xg, goles_local_xg, goles_visit_xg, df_tiros_coord_home, df_tiros_coord_away, pearl_earring_cmaph,
                                                        pearl_earring_cmapa,IMAGEN_PELOTA,IMAGEN_PELOTA_ROJA)

                                        st.session_state[cache_key_reporte2] = fig_bytes_2
                                        st.toast("Tactical report 2 generated successfully")
                                        st.rerun()
                    
                    with st.expander("⚙️ Report Management"):

                        if st.button("🧹 Reset report cache"):

                            keys_to_clear = [cache_key_reporte,
                                cache_key_reporte2,
                                #cache_key_reporteplayer  # si lo activas luego
                            ]

                            for key in keys_to_clear:
                                st.session_state.pop(key, None)

                            st.success("All report caches cleared")

            if option == "Player of the Match":
                jugador_partido, nombre_jugador_partido, position_jugador_partido, player_id_jugador_partido,is_away_team, is_goalkeeper=prepare_df_player_of_match(player_home,player_away ,matchdict)
                df_info= prepare_datafrmae_info_teams_whoscored(matchdict, teams_dict_id_name_whoscored)

                
                df['playerId'] = pd.to_numeric(df['playerId'], errors='coerce').astype('Int64')
                df_info['playerId'] = pd.to_numeric(df_info['playerId'], errors='coerce').astype('Int64')

                df1 = df.merge(df_info[['playerId', 'name','isFirstEleven']],on='playerId',how='left')

                df1['name_norm'] = df1['name'].apply(normalize_name)
                pname_norm = normalize_name(nombre_jugador_partido)

                mins_played = playing_time(df1, pname_norm)

                shots_merged_playerofmatch= prepare_dataframe_shots_playerofmatch(df1, data, team_dict_fotmob, name_home_fotmob,name_away_fotmob)
                shots_merged_playerofmatch['name_norm'] = shots_merged_playerofmatch['name'].apply(normalize_name)

                df_all_players_fotmob= load_all_players_fotmob()
                df_all_players_fotmob['name_norm'] = df_all_players_fotmob['name'].apply(normalize_name)
                candidates = df_all_players_fotmob[df_all_players_fotmob['name_norm'].apply(lambda x: token_match(x, pname_norm))]
                player_id_fotmob_pom= int(candidates['id'].values[0])
                
                if is_away_team:
                    team_color= color_away
                    id_team= id_away_fotmob
                else:
                    team_color= color_home
                    id_team= id_home_fotmob

                with st.container(border=True): 

                    timage = Image.open(urlopen(
                        f"https://images.fotmob.com/image_resources/playerimages/{player_id_fotmob_pom}.png"
                    ))

                    himage = Image.open(urlopen(
                        f"https://images.fotmob.com/image_resources/logo/teamlogo/{id_team}.png"
                    ))

                    col1, col2, col3 = st.columns([1, 3, 1], vertical_alignment="center")
                    with col1:
                        st.image(timage, width=120)

                    with col2:

                        st.markdown(
                            f"<h2 style='text-align:center; margin-bottom:0px;'>"
                            f"{nombre_jugador_partido}"
                            f"</h2>",
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f"""
                            <div style='text-align:center; margin-top:-10px;'>
                                <span style='background:#222; padding:4px 10px; border-radius:8px; font-size:12px; color:#fff;'>
                                PLAYER OF THE MATCH
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f"<p style='text-align:center; margin-top: 10px; font-size:14px; color:#bbbbbb;'>"
                            f"{name_home_fotmob} {homeScore}-{awayScore} {name_away_fotmob} | "
                            f"{group_round} - {stage_selected} | World Cup 2026"
                            f"</p>",
                            unsafe_allow_html=True
                        )
                    with col3:
                        st.image(himage, width=80)

                    st.markdown("#### Player Profile")

                    colA, colB, colC, colD = st.columns(4)

                    colA.metric("Position", position_jugador_partido)
                    colB.metric("Age", jugador_partido['age'].iloc[0])
                    colC.metric("Height", f"{jugador_partido['height'].iloc[0]} cm")
                    colD.metric("Weight", f"{jugador_partido['weight'].iloc[0]} kg")

                    colE, colF = st.columns(2)

                    colE.metric("Minutes Played", mins_played)
                    colF.metric("Role", "GK" if is_goalkeeper else "Outfield")

                main_tabs = st.tabs([
                    "📊 Event timeline",
                    "⚽ Attack",
                    "🧠 Possession",
                    "🛡️ Defense",
                    "🥅 Goalkeeper",
                    "📑 Generate reports"
                ])

                with main_tabs[0]:
                    write_subtitle("EVENT TIMELINE")
                    
                    col1, col2, col3= st.columns([1, 3, 1])
                        
                    with col2:                       
                        fig_et, ax_et = plot_event_timeline(df1, pname_norm,is_goalkeeper = is_goalkeeper)

                        st.pyplot(fig_et)
                    
                with main_tabs[1]:
                    
                    if is_goalkeeper:
                        st.info("This player is a goalkeeper, so a shotmap plot cannot be generated.")
                    else:
                        shots_merged_playerofmatch= prepare_dataframe_shots_playerofmatch(df1, data, team_dict_fotmob, name_home_fotmob,name_away_fotmob)
                        shots_merged_playerofmatch['name_norm'] = shots_merged_playerofmatch['name'].apply(normalize_name)

                        write_subtitle("SHOT MAP")
                        
                        col1, col2, col3= st.columns([1, 3, 1])
                            
                        with col2:       
                            figshotmap, ax = Individual_ShotMap(shots_merged_playerofmatch, pname_norm, color_away,is_away_team=is_away_team)
                            st.pyplot(figshotmap)

                with main_tabs[2]:
                    overview_tabs = st.tabs([
                        "Pass Map",
                        "Passes Recived",
                        "Heatmap and Touches",
                    ])
                    with overview_tabs[0]:
                        write_subtitle("PASS MAP")
                        
                        col1, col2, col3= st.columns([1, 3, 1])
                            
                        with col2:
                            fig_ind_pass, ax_ind_pass = individual_passMap(df1,pname_norm,is_away_team=is_away_team )
                            st.pyplot(fig_ind_pass)

                    with overview_tabs[1]: 
                        write_subtitle("PASSES RECIEVED")
                            
                        col1, col2, col3= st.columns([1, 3, 1])
                            
                        with col2:                       
                            fig_pass_rec, ax = individual_passes_recieved(df1,pname_norm,team_color,is_away_team=is_away_team  )        
                            st.pyplot(fig_pass_rec)

                            if is_goalkeeper:
                                st.info('Passes received are inferred from event order (not explicitly tracked). For goalkeepers, values may be lower due to saves and possession restarts.')

                    with overview_tabs[2]:
                        write_subtitle("HEATMAP AND TOUCHES")
                        
                        col1, col2, col3= st.columns([1, 3, 1])
                            
                        with col2:                       
                            fig_hp, ax_hp = heatMap( df1, pname_norm, team_color, is_away_team= is_away_team)
                            st.pyplot(fig_hp)
                
                with main_tabs[3]:

                    write_subtitle("DEFENSIVE ACTIONS")
                    
                    col1, col2, col3= st.columns([1, 3, 1])
                        
                    with col2:                       
                        fig_def, ax = individual_def_acts( df1, pname_norm, team_color, is_away_team=is_away_team)
                        st.pyplot(fig_def)

                with main_tabs[4]:
                    if is_goalkeeper: 

                        shots_merged_playerofmatch= prepare_dataframe_shots_playerofmatch(df1, data, team_dict_fotmob, name_home_fotmob,name_away_fotmob)
                        shots_merged_playerofmatch['name_norm'] = shots_merged_playerofmatch['name'].apply(normalize_name)
                      
                        df_tiros_coord_home, df_tiros_coord_away = prepare_df_shotsgoal_pom(shots_merged_playerofmatch, name_home_fotmob , name_away_fotmob)
                        if is_away_team:
                            df_shots = df_tiros_coord_home
                        else:
                            df_shots = df_tiros_coord_away
                        
                        write_subtitle("GK SAVES")
                    
                        col1, col2, col3= st.columns([1, 3, 1])
                            
                        with col2:                       
                            fig_goalpost, ax= draw_goal_pom( df_shots, IMAGEN_PELOTA, IMAGEN_PELOTA_ROJA)
                            st.pyplot(fig_goalpost)

                    else: 
                        st.info("This player is not a goalkeeper, so a goal-post plot cannot be generated.")
                with main_tabs[5]:
                    st.info(" This feature is coming soon.")


                    

                    



    else:
        st.info("Select a match to view detailed analysis.")
            


            

                

