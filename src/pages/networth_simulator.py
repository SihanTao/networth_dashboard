import streamlit as st
import numpy as np
import plotly.graph_objs as go
from utils.models import Pot

st.title('Net Worth Simulator')

if 'pots' not in st.session_state:
    st.session_state.pots = []

def add_pot():
    new_pot = Pot(name=f"Pot {len(st.session_state.pots) + 1}")
    st.session_state.pots.append(new_pot)

st.button('Add Pot', on_click=add_pot)

def remove_pot(index):
    del st.session_state.pots[index]
    st.rerun()

# Display pot inputs
for i, pot in enumerate(st.session_state.pots):
    st.write(f'### {pot.name}')
    pot.initial = st.number_input(f'Initial Amount ({pot.name})', min_value=0.0, value=float(pot.initial) if pot.initial is not None else 0.0, key=f"initial_{i}_{pot.name}")
    pot.monthly = st.number_input(f'Monthly Contribution ({pot.name})', min_value=0.0, value=float(pot.monthly) if pot.monthly is not None else 0.0, key=f"monthly_{i}_{pot.name}")
    pot.rate = st.number_input(f'Annual Return Rate (%) ({pot.name})', min_value=0.0, max_value=100.0, value=float(pot.rate) if pot.rate is not None else 0.0, key=f"rate_{i}_{pot.name}")
    if st.button(f'Remove {pot.name}', key=f"remove_{i}_{pot.name}"):
        remove_pot(i)

def simulate_net_worth(years=30):
    months = years * 12
    timeline = np.arange(months)
    total_networth = np.zeros(months)
    pot_breakdown = {}
    for pot_item in st.session_state.pots:
        initial = pot_item.initial if pot_item.initial is not None else 0.0
        monthly = pot_item.monthly if pot_item.monthly is not None else 0.0
        rate = (pot_item.rate / 100) if pot_item.rate is not None else 0.0
        
        growth = initial * ((1 + rate / 12) ** timeline)
        if rate == 0:
            contributions = monthly * timeline
        else:
            contributions = monthly * (((1 + rate / 12) ** timeline - 1) / (rate / 12))
        networth_for_pot = growth + contributions
        total_networth += networth_for_pot
        pot_breakdown[pot_item.name] = networth_for_pot
    return timeline, total_networth, pot_breakdown

if st.button('Simulate Net Worth'):
    if not st.session_state.pots:
        st.warning("Please add at least one pot to simulate.")
    else:
        timeline, networth_result, pot_breakdown = simulate_net_worth()
        
        # Total Net Worth Plot
        fig_total = go.Figure()
        fig_total.add_trace(go.Scatter(x=timeline / 12, y=networth_result, mode='lines', name='Total Net Worth'))
        fig_total.update_layout(title='Total Net Worth Growth Over Time', xaxis_title='Years', yaxis_title='Net Worth')
        st.plotly_chart(fig_total)

        # Pot Breakdown Plot
        fig_breakdown = go.Figure()
        for name, data in pot_breakdown.items():
            fig_breakdown.add_trace(go.Scatter(x=timeline / 12, y=data, mode='lines', name=name))
        fig_breakdown.update_layout(title='Net Worth Breakdown by Pot', xaxis_title='Years', yaxis_title='Net Worth', showlegend=True)
        st.plotly_chart(fig_breakdown)

        pot_settings_html = "<h3>Pot Settings</h3>"
        for pot_item in st.session_state.pots:
            pot_settings_html += f"""\
            <h4>{pot_item.name}</h4>
            <ul>
                <li>Initial Amount: {pot_item.initial if pot_item.initial is not None else 0.0}</li>
                <li>Monthly Contribution: {pot_item.monthly if pot_item.monthly is not None else 0.0}</li>
                <li>Annual Return Rate: {pot_item.rate if pot_item.rate is not None else 0.0}%</li>
            </ul>
            """

        html_report = f"""\
        <html>
            <head><title>Net Worth Simulation Report</title></head>
            <body>
                <h1>Net Worth Simulation Report</h1>
                {pot_settings_html}
                <h2>Total Net Worth</h2>
                {fig_total.to_html(full_html=False, include_plotlyjs='cdn')}
                <h2>Pot Breakdown</h2>
                {fig_breakdown.to_html(full_html=False, include_plotlyjs='cdn')}
            </body>
        </html>
        """
        st.download_button(
            label="Save Report as HTML",
            data=html_report,
            file_name="net_worth_report.html",
            mime="text/html"
        )
    
