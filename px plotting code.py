def px_plot_scheme_pie(df, team):
    team_data = df.loc[team]

    names = ['Cover 0','Cover 1','Cover 2','Cover 3','Cover 4','Cover 6']
    data_keys = ['cover 0 count','cover 1 count','cover 2 count','cover 3 count','cover 4 count','cover 6 count']
    chart_data = team_data[data_keys].values
    
    fig = px.pie(df, values=chart_data, names=names, title='Coverage Scheme')
    fig.show()


 def px_plot_scheme_epa_rate(df, team):
    team_data = df.loc[team]

    names = ['Overall','Cover 0','Cover 1','Cover 2','Cover 3','Cover 4','Cover 6']
    data_keys = ['overall epa rate','cover 0 epa rate','cover 1 epa rate','cover 2 epa rate','cover 3 epa rate','cover 4 epa rate','cover 6 epa rate']
    chart_data = team_data[data_keys].values
    
    fig = px.line(df, x=names, y=chart_data, title='EPA/Play')
    fig.show()