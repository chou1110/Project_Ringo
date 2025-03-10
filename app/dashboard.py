import datetime  
import streamlit as st
import plotly.io as pio

pio.templates.default = "plotly_white"

from process import *
from plot    import *


##== Setup ==##
st.set_page_config(
     page_title="Tracking Dashboard",
     layout="centered",
)

##== Basic ==##
UPDATE_DATE         = datetime.date.today()
UPDATE_MONTH        = UPDATE_DATE.replace(day=1)

##== Runtime ==##
## Header
st.markdown("# Tracking Dashboard")
st.markdown('<br>', unsafe_allow_html=True)

##== Main Board ==##
st.markdown(f"""
    Effective strategy execution requires a clear plan and decisive action to achieve sustainable growth and adaptability. 
    By focusing on optimizing resource utilization, we can enhance efficiency and maximize operational effectiveness. 
    This dashboard serves as a tool for monitoring and optimizing our strategy, providing real-time insights that enable proactive decision-making. 
    Ensuring we make informed decisions that drive our success in this dynamic sector allows us to stay competitive, seize new opportunities, and continuously refine our approach for long-term impact.
""")

## Monthly Trend
st.markdown("## **Trend**")
st.markdown(f"""
    The following graph shows the trend of average operational strategy.
""")

#  plot1 
df_trend, df_estimate = get_month_trend(UPDATE_DATE)
fig = plot_trend(df_trend, df_estimate, UPDATE_MONTH) 
st.plotly_chart(fig, use_container_width=True)
    
# Calculate 
df_hour = get_hour_value(UPDATE_MONTH)
monthly_unit, totaldays = get_month_value(df_hour, UPDATE_MONTH)
avg_strategy = round(monthly_unit * 1000 / totaldays / 24, 1)

# Info number
col1, col2, col3 = st.columns(3)
col1.metric(label='Month', value=f'{UPDATE_MONTH.strftime("%b")} {UPDATE_MONTH.year}')
col2.metric(label='Monthly Strategy [K]',   value=f"{monthly_unit:,}", help = f'Sum of Hourly Strategy in {totaldays} Days')
col3.metric(label='Average Strategy [Unit]',   value = f"{avg_strategy:,.0f}")
st.markdown('<br>', unsafe_allow_html=True)
    
with st.expander("See hourly operational strategy of the month."):
    fig = plot_bar(df_hour)
    st.plotly_chart(fig,  use_container_width=True)
    
st.markdown('<br>', unsafe_allow_html=True)

# Tracking
st.markdown("## **Tracking**")
st.markdown(f"""
    The graph below illustrates the execution status of the strategy, highlighting instances of under- and over-action at each clock-hour. 
    The blue bars indicate real action exceeding 125% of the strategy, suggesting an opportunity to set a higher target. 
    Conversely, the orange bars represent real action falling below 75% of the strategy, which may lead to reduced profits. 
    Both scenarios may require strategy adjustments.
""")

# Plot Tracking
df_tracking = get_tracking(df_hour)
hour_count_over, hour_count_under, close_rates, tracking_stats = get_tracking_stats(df_tracking, UPDATE_DATE)

fig = plot_tracking(df_tracking, UPDATE_DATE)
st.plotly_chart(fig, use_container_width=True)

hour_over , count_over      = hour_count_over[0] , hour_count_over[1]
hour_under, count_under     = hour_count_under[0], hour_count_under[1]
close_rate, close_rate_last = close_rates[0], close_rates[1]

# Info number
col1, col2, col3 = st.columns(3)
if count_under == 0:
    col1.metric(label='Most Under Period', value=f"-")
else:
    col1.metric(label='Most Under Period', value=f"{hour_under}:00 - {hour_under+1}:00"
        ,delta=f"Occurred {count_under:,} time(s) this month", delta_color='off')        

if count_over == 0:
    col2.metric(label='Most Over Period', value=f"-")
else:
    col2.metric(label='Most Over Period', value=f"{hour_over}:00 - {hour_over+1}:00"
        ,delta=f"Occurred {count_over:,} time(s) this month", delta_color='off')     
    
col3.metric(label='Close-To-Action Rate', value=f"{close_rate:.1%}")


st.markdown('<br>', unsafe_allow_html=True)

fig1, fig2 = plot_over_under(tracking_stats)
plotly_conifg ={'displayModeBar': False}
st.plotly_chart(fig1, use_container_width=True, config=plotly_conifg)
st.plotly_chart(fig2, use_container_width=True, config=plotly_conifg)

st.markdown('<br>', unsafe_allow_html=True)