import streamlit as st
import pandas as pd
import datetime 
import plotly.io as pio
import plotly.graph_objects as go

pio.templates.default = "plotly_white"


## Plot strategy
@st.cache_data(ttl=28800)
def plot_bar(df_hour):
    x                =  df_hour['hour']
    y_wkday          =  df_hour['value_weekday']
    y_wkend          =  df_hour['value_weekend']
    y_avg            = (df_hour['value_weekday'] * 5 / 7 + df_hour['value_weekend'] * 2 / 7).mean()

    data = [

        go.Bar(
            name          = 'Workday', 
            x             = x, 
            y             = y_wkday, 
            hovertemplate = "%{y:,d} Strategy",
            marker_line   = {'width': 0},
            marker_color  = '#007ACC',
            legendrank    = 1,  
            yaxis         = 'y' 
        ),
        
        go.Bar(
            name          = 'Holiday', 
            x             = x, 
            y             = y_wkend, 
            hovertemplate = "%{y:,d} Strategy",
            marker_line   = {'width': 0},
            marker_color  = '#FF5733',
            legendrank    = 2, 
            yaxis         = 'y' 
        ),

        go.Scatter(
            name          = 'Average', 
            x             = x, 
            y             = [y_avg]*len(x), 
            hoverinfo     = "skip", 
            line          = {'width': 2, 'color': '#D6D6D6'}, mode='lines', 
            legendrank    = 3, 
            yaxis         = 'y'
        )
    ]
    
    yrange = [0, 8000]
    if y_wkday.max()>8000:
        yrange = [0, y_wkday.max()]

    layout = go.Layout(
        title               = 'Operational Strategy',
        height              = 350,
        paper_bgcolor       = '#FFFFFF',
        plot_bgcolor        = '#FFFFFF',
        xaxis               = {'showline' : False, 'showgrid' : False, 'showticklabels' : True},
        yaxis               = {'title': 'Strategy', 'range': yrange, 'side': 'left' , 'showgrid': False, 'tickformat': ','}, 
        barmode             = 'group', bargap=0.05, bargroupgap=0,
        uniformtext_minsize = 8, 
        hovermode           = "x unified",
        margin              = {'b': 0, 'r':150},

    )
    
    fig = go.Figure(data=data, layout=layout)
    
    return fig


@st.cache_data(ttl=28800)
def plot_tracking(df_tracking, theDate):

    df_plot_over  = df_tracking[df_tracking['over'].fillna(False)]
    df_plot_under = df_tracking[df_tracking['under'].fillna(False)]

    x_bar         = df_tracking['date_hour']
    strategy      = df_tracking['strategy']
    strategy_low  = df_tracking['strategy'] - df_tracking['buffer']

    x_smaller     = df_plot_over['date_hour']
    y_smaller     = df_plot_over['strategy'] - df_plot_over['buffer']

    x_scatter     = df_tracking['date_hour']
    action        = df_tracking['action']

    x_bigger      = df_plot_under['date_hour']
    y_bigger      = df_plot_under['strategy'] + df_plot_under['buffer']
    
    y_buffer      = df_tracking['buffer']

    ## Plotting
    data = [
            # first layer : Bar
            go.Bar(
                name            = 'Strategy', 
                x               = x_bar, 
                y               = strategy, 
                hovertemplate   = "%{y:,d}",
                marker_line     = {'width': 0},
                marker_color    = 'rgb(232, 232, 232)',
                legendrank      = 1, 
                yaxis           = 'y'
            ),

            go.Bar(
                x               = x_bar , 
                y               = strategy_low, 
                hoverinfo       = 'skip', 
                marker_line     = {'width': 0},
                marker_color    = 'rgba(232, 232, 232, 0.0)', 
                legendrank      = 2, 
                yaxis           = 'y2', 
                showlegend      = False
            ),

            go.Bar(
                x               = x_bar, 
                y               = y_buffer - 0.25, 
                hoverinfo       = 'skip', 
                marker_line     = {'width': 0},
                marker_color    = 'rgb(211, 211, 211)', 
                legendrank      = 3, 
                yaxis           = 'y2',
                showlegend      = False
            ),

            go.Bar(
                x               = x_bar, 
                y               = [0.5]*len(x_bar), 
                hoverinfo       = 'skip', 
                marker_line     = {'width': 0},
                marker_color    = 'rgb(255,255,255)', 
                legendrank      = 4, 
                yaxis           = 'y2',
                showlegend      = False
            ),

            go.Bar(
                x               = x_bar, 
                y               = y_buffer-0.25, 
                hoverinfo       = 'skip', 
                marker_line     = {'width': 0},
                marker_color    = 'rgb(211, 211, 211)',
                legendrank      = 5,
                yaxis           = 'y2',
                showlegend      = False
            ),

            ## 2nd layer: over bar
            go.Bar(
                name            = 'Over', 
                x               = x_smaller, 
                y               = y_smaller, 
                hoverinfo     = "skip", 
                marker_line     = {'width': 0},
                marker_color    = 'rgba(255, 165, 0, 0.5)', 
                legendrank      = 6, 
                yaxis           = 'y3'
            ),

            ## 5th layer: under bar
            go.Bar(
                name            = 'Under', 
                x               = x_bigger, 
                y               = y_bigger, 
                hoverinfo       = "skip", 
                marker_line     = {'width': 0},
                marker_color    = 'rgba(0, 102, 255, 0.5)',
                legendrank      = 7, 
                yaxis           = 'y3'
                ),

            ## 3rd layer: Scatter
            go.Scatter(
                name            = 'Action', 
                x               = x_scatter, 
                y               = action, 
                hovertemplate   = "%{y:,d}",
                mode            = 'lines+markers',
                marker_color    = 'rgba(0, 180, 130, 0.8)', 
                marker_size     = 6,
                legendrank      = 8, 
                yaxis           ='y4'
            ),

    ]

    x_max = theDate + datetime.timedelta(days = 1)
    x_min = theDate - datetime.timedelta(days = 3)
    y_max = strategy.max()*1.3
    xrange = [x_min, x_max]
    yrange = [0,     y_max]

    layout = go.Layout(
                    title='Strategy vs Action',
                    height=400,
                    paper_bgcolor='#FFFFFF',
                    plot_bgcolor='#FFFFFF',
                    yaxis ={'title': 'Strategy',  'side': 'left', 'range': yrange,  'showgrid': False, 'tickformat': ','},
                    yaxis2={                 'side': 'left', 'range': yrange,  'showgrid': False, 'tickformat': ',', 'anchor': 'x', 'overlaying': 'y'},
                    yaxis3={                 'side': 'left', 'range': yrange,  'showgrid': False, 'tickformat': ',', 'anchor': 'x', 'overlaying': 'y'},
                    yaxis4={                 'side': 'left', 'range': yrange,  'showgrid': False, 'tickformat': ',', 'anchor': 'x', 'overlaying': 'y'},
                    xaxis={'tickangle': -30, 'range': xrange}, 
                    barmode='stack', bargap = 0.1, bargroupgap = 0,
                    uniformtext_minsize = 8, 
                    hovermode="x unified",
                    margin = dict(b=50),
)

    fig = go.Figure(data=data, layout=layout)
    
    return fig


@st.cache_data(ttl=28800)
def plot_trend(df_trend, df_estimate, UPDATE_MONTH):
    UPDATE_MONTH = str(UPDATE_MONTH)
    df_connect  = pd.concat([df_trend.sort_values('date').tail(1), df_estimate.sort_values('date').head(1)])
    
    x_suggest           =  df_trend['date']
    y_suggest           =  df_trend['avg_value']

    x_estimate          =  df_estimate['date']
    y_estimate          =  df_estimate['avg_value']

    x_today             = [UPDATE_MONTH]
    y_today             = [df_trend.set_index('date').loc[UPDATE_MONTH]['avg_value']]
    
    data = [
            # Plot Dashline
            go.Scatter(
                x               = df_connect['date'], 
                y               = df_connect['avg_value'], 
                hoverinfo       = 'skip', 
                mode            = 'lines',
                legendrank      = 1, 
                yaxis           ='y',
                line_dash       ='dash',
                line_color      = '#C8C8C8',
                showlegend      = False, 
            ),

            # Plot suggest
            go.Scatter(
                name            = 'Operational Strategy', 
                x               = x_suggest, 
                y               = y_suggest, 
                hovertemplate   = "%{y:.1f} U",
                mode            = 'lines+markers',
                marker_color    = '#969696', 
                marker_size     = 11,
                marker_symbol   = 'circle',
                legendrank      = 2, 
                yaxis           ='y'
            ),


            # Plot Estimate
            go.Scatter(
                name            = 'Estimated Strategy', 
                x               = x_estimate, 
                y               = y_estimate, 
                hovertemplate   = "%{y:.1f} U",
                mode            = 'lines+markers',
                marker_color    = '#C8C8C8', 
                marker_size     = 12,
                marker_symbol   = 'circle-open',

                legendrank      = 3, 
                yaxis           ='y',
                line_dash       ='dash'
            ),

            # Plot Today
            go.Scatter(
                name            = 'This Month', 
                x               = x_today, 
                y               = y_today, 
                hoverinfo       = 'skip',
                mode            = 'markers',
                marker_color    = '#4285F4', 
                marker_size     = 13,
                marker_symbol   = 'circle',

                legendrank      = 4, 
                yaxis           ='y',
            ),


    ]

    yrange = [0,max(y_estimate.max(), y_suggest.max())+1000]
    layout = go.Layout(
                title               = 'Trend Plot',
                height              = 400,
                paper_bgcolor       = '#FFFFFF',
                plot_bgcolor        = '#FFFFFF',
                yaxis               = {'title': 'Strategy', 'range': yrange,  'showgrid': False},
                xaxis               = {'tickangle': -30, 'showgrid': False}, 
                uniformtext_minsize = 8, 
                hovermode           = "x unified",
                margin              = dict(r=0, l=0, b=100),
            )

    fig = go.Figure(data=data, layout=layout)

    return fig


## Plot under over freqency
@st.cache_data(ttl=28800)
def plot_over_under(tracking_stats):
    df = tracking_stats.copy()
    df['min'] = 0
    colorscale1 =[[False, '#eeeeee'], [True, '#0066FF']]
    colorscale2 =[[False, '#eeeeee'], [True, '#FFA500']]

    data1 = [
        go.Heatmap(
            name  = 'Under',
            x     = df['hour'],
            y     = df['min'],
            z     = df['under'],
            xgap  = 3, 
            ygap  = 3,
            showscale     = False,
            colorscale    = colorscale1,
            hovertemplate = "[%{x}:00] Count : %{z:,d} ",
            zmin = 0, 
            zmax = 10
        )
    ]

    layout1 = go.Layout(
        height       = 24,
        xaxis        = dict(  
            nticks = 48, 
            showline = False, showgrid = False, zeroline = False,
            showticklabels = False
            ),
        yaxis        = dict(
            showline = False, showgrid = False, zeroline = False,
            tickmode = 'array',
            ticktext = ['Under [#]'],
            tickvals = [0],
        ),

        font         = {'size':10, 'color':'#9e9e9e'},
        plot_bgcolor = ('#fff'),
        margin       = dict(t=0, b=0, r=107),
    )
    fig1 = go.Figure(data=data1, layout=layout1)

    data2 = [
        go.Heatmap(
            name  = 'Over',
            x     = df['hour'],
            y     = df['min'],
            z     = df['over'],
            xgap  = 3, 
            ygap  = 3,
            showscale     = False,
            colorscale    = colorscale2,
            hovertemplate = "[%{x}:00] Count : %{z:,d} ",
            zmin = 0, 
            zmax = 10
        )
    ]

    layout2 = go.Layout(
        height       = 84,
        xaxis        = dict( title = 'Clock', nticks = 48, showline = False, showgrid = False, zeroline = False),
        yaxis        = dict(
            showline = False, showgrid = False, zeroline = False,
            tickmode = 'array',
            ticktext = ['   Over [#]'],
            tickvals = [0],
        ),

        font         = {'size':10, 'color':'#9e9e9e'},
        plot_bgcolor = ('#fff'),
        margin       = dict(t=0, b=60, r=107),
    )

    fig2 = go.Figure(data=data2, layout=layout2)

    return fig1, fig2

