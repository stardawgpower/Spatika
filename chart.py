import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from db import*

db = ItemDatabse()
counts = db.get_counts()
years, months, amounts = db.get_monthly_amounts_for_RA_bills_raised()
a_years, a_months, a_amounts = db.get_monthly_amounts_for_total_approved_bills()
p_years, p_months, p_amounts = db.get_monthly_amounts_for_in_progress_bills()
c_years, c_months, c_amounts = db.get_monthly_amounts_for_contractor_claimed_amount()
t_years, t_months, t_amounts = db.get_monthly_amounts_for_total_amount_paid()
contractor_id, contractor_name = db.get_unique_contractor_id()

def number_to_month(months, years):
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    result = []
    for i in range(len(months)):
        if 1 <= months[i] <= 12:
            month_name = month_names[months[i] - 1]
            year_str = str(years[i])
            result.append(f"{month_name} {year_str}")
    return result

st.set_page_config(layout="wide")
fig1, fig2 = st.columns(2)

with fig1:
    # Create a function to generate a Pie Chart
    def generate_pie_chart():
        # Create a list of values and labels for the chart
        values = list(counts[0].values())
        labels = list(counts[0].keys())
        # Set custom colors for the chart
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        # Create a pie chart using Plotly
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, marker=dict(colors=colors))])
        # Set the chart title and style
        fig.update_layout(
            title='No. of days passed since submission of RA_bill',
            margin=dict(l=20, r=20, t=50, b=20)
        )
        # Add hover information to the chart
        fig.update_traces(
            hoverinfo='label+percent',
            textinfo='value',
            textfont=dict(size=16)
        )
        # Add a legend to the chart
        fig.update_layout(
            showlegend=True,
            legend=dict(
                x=1.1,
                y=0.5,
                title=None,
                font=dict(size=12),
                orientation='v'
            )
        )
        # Make the chart responsive
        fig.update_layout(
            autosize=True,
            width=600,
            height=400,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        # Display the chart in Streamlit
        st.plotly_chart(fig)

    # Create a function to generate a Bar Chart
    def generate_bar_chart():
        # Create a list of values and labels for the chart
        values = list(counts[0].values())
        labels = list(counts[0].keys())
        # Set custom colors for the chart
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        # Create a bar chart using Plotly
        fig = go.Figure(data = [go.Bar(x = labels, y = values, marker_color = colors, textposition = 'auto')])
        # Set the chart title
        fig.update_layout(title = 'No. of days passed since submission of RA_bills')
        # Set the axis titles
        fig.update_xaxes(title = 'Different Categories')
        fig.update_yaxes(title = 'Count of RA_bills')
        # Display the chart in Streamlit
        st.plotly_chart(fig)

    # Add a dropdown button to switch between the Pie and Bar Chart
    chart_type = st.selectbox('Select a chart type', ('Pie Chart', 'Bar Chart'))
    # Generate the chart based on the user's selection
    if chart_type == 'Pie Chart':
        generate_pie_chart()
    elif chart_type == 'Bar Chart':
        generate_bar_chart()

with fig2:
    # create a sample dataframe
    data = {'contractor_id': ['001', '002', '003', '004', '005'],
            'name': ['John Smith', 'Jane Doe', 'Bob Johnson', 'Sarah Lee', 'David Brown'],
            'age': [35, 28, 42, 29, 46],
            'address': ['123 Main St', '456 Elm St', '789 Oak Ave', '321 Pine Blvd', '555 Maple Ln']}
    df = pd.DataFrame(data)

    # create a select box to choose the contractor id
    contractor_id = st.selectbox('Select contractor name:', contractor_name)

    # filter the dataframe based on the selected contractor id
    filtered_df = df[df['contractor_id'] == contractor_id]

    # display the filtered dataframe
    st.write(filtered_df)

def animated_bar_chart(values, labels, title):
    # Define the colors for the bars
    colors = px.colors.qualitative.Plotly
    # Create a list of frames for the animation
    frames = []
    for i in range(len(values)):
        frame_data = go.Bar(
            x=labels[:i+1],
            y=values[:i+1],
            marker_color=colors
        )
        frame = go.Frame(data=[frame_data])
        frames.append(frame)
    # Create the animation
    fig = go.Figure(
        data=[go.Bar(x=labels, y=values, marker=dict(color=colors))],
        frames=frames
    )
    # Set the chart title
    fig.update_layout(title=title, yaxis=dict(tickformat='.1f Lakhs'))
    # Set the axis titles
    fig.update_xaxes(title='Timeline')
    fig.update_yaxes(title='Amount', tickprefix='₹')
    # Set the animation duration and loop mode
    fig.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                showactive=True,
                buttons=[
                    dict(
                        label='Play',
                        method='animate',
                        args=[
                            None,
                            {
                                'frame': {'duration': 500, 'redraw': True},
                                'fromcurrent': True,
                                'transition': {'duration': 0}
                            }
                        ]
                    )
                ],
                x=0.5, # shift the button position to the left
                y=1.3 # shift the button position above the chart
            )
        ]
    )
    return fig

# def bar_chart(values, labels, title):
#     # Define the colors for the bars
#     colors = px.colors.qualitative.Plotly
#     # Create the bar chart
#     fig = go.Figure(data=[go.Bar(x=labels, y=values, marker=dict(color=colors))])
#     # Set the chart title
#     fig.update_layout(title=title, yaxis=dict(tickformat='.1f Lakhs'))
#     # Set the axis titles
#     fig.update_xaxes(title='Timeline')
#     fig.update_yaxes(title='Amount', tickprefix='₹')
#     return fig

fig3, fig4 = st.columns(2)

with fig3:
    # Create selectbox
    selected_option = st.selectbox('Select Chart', ('RA_bills amount raised monthly', 'Approved RA_bills amount monthly', 'Pending RA_bills amount monthly'))

    if selected_option == 'RA_bills amount raised monthly':
        values = amounts
        labels = number_to_month(months, years)
    elif selected_option == 'Approved RA_bills amount monthly':
        values = a_amounts
        labels = number_to_month(a_months, a_years)
    elif selected_option == 'Pending RA_bills amount monthly':
        values = p_amounts
        labels = number_to_month(p_months, p_years)

    fig = animated_bar_chart(values, labels, selected_option)
    st.plotly_chart(fig)

with fig4:
    # BAR CHART
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x = number_to_month(months, years),
        y = amounts,
        name = 'RA_bills raised',
        marker_color = 'blue'
    ))
    fig.add_trace(go.Bar(
        x = number_to_month(a_months, a_years),
        y = a_amounts,
        name = 'approved RA_bills',
        marker_color = 'red'
    ))
    fig.add_trace(go.Bar(
        x = number_to_month(p_months, p_years),
        y = p_amounts,
        name = 'pending RA_bills',
        marker_color = 'green'
    ))
    # Here we modify the tick format of the y-axis, resulting in amounts displayed in Lakhs.
    fig.update_layout(title = 'Comparison of RA bills raised, approved, and pending monthly',
                    barmode = 'group',
                    yaxis = dict(tickformat = '.1f Lakhs', title = 'Amount'),
                    xaxis = dict(title = 'Timeline'),
                    legend = dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
                    )
    # Set the axis titles
    fig.update_yaxes(title='Amount', tickprefix='₹')
    st.plotly_chart(fig)

fig5, fig6 = st.columns(2)

with fig5:
    # Create selectbox for choosing the chart
    chart_options = ['Contractor claimed amount monthly', 'Total amount paid monthly']
    selected_chart = st.selectbox('Select a chart', chart_options)

    if selected_chart == 'Contractor claimed amount monthly':
        # BAR CHART 1
        values = c_amounts
        labels = number_to_month(c_months, c_years)
        fig = animated_bar_chart(values, labels, 'Contractor claimed amount monthly')
        st.plotly_chart(fig)

    elif selected_chart == 'Total amount paid monthly':
        # BAR CHART 2
        values = t_amounts
        labels = number_to_month(t_months, t_years)
        fig = animated_bar_chart(values, labels, 'Total amount paid monthly')
        st.plotly_chart(fig)

with fig6:
    # BAR CHART
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=number_to_month(c_months, c_years),
        y=amounts,
        name='Contractor claimed amount',
        marker_color='blue'
    ))
    fig.add_trace(go.Bar(
        x=number_to_month(t_months, t_years),
        y=t_amounts,
        name='Total amount paid',
        marker_color='red'
    ))
    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(title='Comparison of contractor claimed amount and total amount paid monthly',
                    barmode='group',
                    yaxis=dict(tickformat='.1f Lakhs'),
                    xaxis=dict(title='Timeline'),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                    )
    # Set the axis titles
    fig.update_yaxes(title='Amount', tickprefix='₹')
    st.plotly_chart(fig)
