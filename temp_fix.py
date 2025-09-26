if performers_above:
                            st.markdown(f"**Top {len(performers_above)} performers ranked above you:**")
                            
                            # Create comparison table for performers above
                            above_data = []
                            for performer in performers_above:
                                score_diff = performer.get('score_difference', 0)
                                diff_color = "🟢" if score_diff > 10 else "🟡" if score_diff > 5 else "🔴"
                                above_data.append({
                                    'Rank': f"#{performer.get('rank_position', 'N/A')}",
                                    'Organization': performer['name'],
                                    'Quality Score': f"{performer['total_score']:.1f}",
                                    'Score Gap': f"{diff_color} +{score_diff:.1f}",
                                    'Country': performer.get('country', 'Unknown'),
                                    'Type': performer.get('hospital_type', 'Hospital')
                                })
                            
                            df_above = pd.DataFrame(above_data)
                            st.dataframe(df_above, use_container_width=True, hide_index=True)
                            
                            # Add visualization chart for performers above
                            if len(performers_above) > 0:
                                st.markdown("**📊 Score Distribution - Performers Above You**")
                                
                                # Create bar chart showing score comparison
                                chart_data = []
                                for performer in performers_above[-10:]:  # Show last 10 for better visualization
                                    chart_data.append({
                                        'Organization': performer['name'][:20] + '...' if len(performer['name']) > 20 else performer['name'],
                                        'Quality Score': performer['total_score'],
                                        'Rank': performer.get('rank_position', 0)
                                    })
                                
                                # Add current organization for comparison
                                chart_data.append({
                                    'Organization': f"{org_name[:15]}... (You)" if len(org_name) > 15 else f"{org_name} (You)",
                                    'Quality Score': score,
                                    'Rank': rankings_data['overall_rank']
                                })
                                
                                df_chart = pd.DataFrame(chart_data)
                                
                                # Create bar chart
                                import plotly.express as px
                                fig = px.bar(df_chart, 
                                           x='Organization', 
                                           y='Quality Score',
                                           title='Quality Score Comparison - Top Performers Above You',
                                           color='Quality Score',
                                           color_continuous_scale='RdYlGn',
                                           text='Quality Score')
                                
                                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                                fig.update_layout(
                                    xaxis_tickangle=-45,
                                    height=400,
                                    showlegend=False,
                                    xaxis_title="Organizations",
                                    yaxis_title="Quality Score"
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # Show improvement insights
                            if performers_above:
                                avg_score_above = sum(p['total_score'] for p in performers_above) / len(performers_above)
                                score_gap = avg_score_above - score
                                st.info(f"💡 **Improvement Opportunity**: Average score of top performers above you is {avg_score_above:.1f}. Bridge the {score_gap:.1f} point gap to move up in rankings.")
                        else:
                            st.success("🏆 **Congratulations!** You are among the top performers in the database.")