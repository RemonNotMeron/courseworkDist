from nicegui import ui
import auth
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
from collections import defaultdict
from styles import inject_styles


def get_user_data():
    user = None
    if hasattr(auth, 'current_username') and auth.current_username in auth.users:
        user = auth.users[auth.current_username]
    else:
        for k, v in auth.users.items():
            if v is auth.current_user:
                user = v
                break
    return user


def calculate_card_stats(user):
    if not user or 'decks' not in user:
        return {
            'total_cards': 0,
            'mastered_cards': 0,
            'learning_cards': 0,
            'new_cards': 0,
            'due_today': 0,
            'total_reviews': 0,
            'study_hours': 0
        }

    total_cards = 0
    mastered_cards = 0
    learning_cards = 0
    new_cards = 0
    due_today = 0
    total_reviews = 0
    today = date.today()

    for deck in user.get('decks', []):
        for card in deck.get('cards', []):
            total_cards += 1
            reps = int(card.get('repetitions', 0))
            total_reviews += reps

            if reps >= 5:
                mastered_cards += 1
            elif reps > 0:
                learning_cards += 1
            else:
                new_cards += 1

            due_date = card.get('due_date', '')
            if due_date:
                try:
                    card_due = datetime.fromisoformat(due_date).date()
                    if card_due <= today:
                        due_today += 1
                except Exception:
                    pass

    study_hours = round(total_reviews / 60, 1)

    return {
        'total_cards': total_cards,
        'mastered_cards': mastered_cards,
        'learning_cards': learning_cards,
        'new_cards': new_cards,
        'due_today': due_today,
        'total_reviews': total_reviews,
        'study_hours': study_hours
    }


def get_mastery_timeline(user):
    if not user or 'decks' not in user:
        return [], []

    mastery_data = defaultdict(int)

    for deck in user.get('decks', []):
        for card in deck.get('cards', []):
            reps = int(card.get('repetitions', 0))
            if reps >= 5:
                mastery_str = card.get('mastered_date')
                if mastery_str:
                    try:
                        m_date = datetime.fromisoformat(mastery_str).date()
                        mastery_data[m_date] += 1
                        continue
                    except Exception:
                        pass
                mastery_data[date.today()] += 1

    timeline_dates = []
    timeline_mastered = []
    cumulative = 0
    start_date = date.today() - timedelta(days=30)
    total_before_window = sum(count for d, count in mastery_data.items() if d < start_date)
    cumulative = total_before_window

    current = start_date
    while current <= date.today():
        cumulative += mastery_data.get(current, 0)
        timeline_dates.append(current.strftime('%Y-%m-%d'))
        timeline_mastered.append(cumulative)
        current += timedelta(days=1)

    return timeline_dates, timeline_mastered


def get_card_state_breakdown(user):
    if not user or 'decks' not in user:
        return [], []

    states = {'New': 0, 'Learning': 0, 'Mastered': 0}

    for deck in user.get('decks', []):
        for card in deck.get('cards', []):
            reps = int(card.get('repetitions', 0))
            if reps >= 5:
                states['Mastered'] += 1
            elif reps > 0:
                states['Learning'] += 1
            else:
                states['New'] += 1

    return list(states.keys()), list(states.values())


def create_mastery_graph():
    user = get_user_data()
    dates, mastered_count = get_mastery_timeline(user)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=mastered_count,
        mode='lines+markers',
        name='Cumulative Mastered',
        line=dict(color='#10b981', width=3),
        marker=dict(size=6)
    ))
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Cards Mastered',
        hovermode='x unified',
        plot_bgcolor='#f9fafb',
        height=320,
        margin=dict(l=40, r=20, t=30, b=40)
    )
    return fig


def create_state_breakdown_graph():
    user = get_user_data()
    labels, values = get_card_state_breakdown(user)

    colors = ['#6366f1', '#f59e0b', '#10b981']
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hoverinfo='label+value+percent'
    )])
    fig.update_layout(
        height=288,
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.1)
    )
    return fig


@ui.page('/progress_visualiser')
def progress_visualiser():
    inject_styles()
    
    user = get_user_data()

    if not user:
        ui.label('Please log in to view progress').classes('text-red-600')
        return

    # Header
    with ui.card().classes('w-full surface-blue mb-4'):
        with ui.row().classes('items-center w-full px-2 py-1'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dashboard')) \
                .props('flat round').classes('text-grey-5')
            ui.label('Progress Visualiser').classes('text-2xl font-bold text-grey-8 dark:text-grey-2 flex-1')

    stats = calculate_card_stats(user)

    # Tabs
    with ui.tabs().classes('w-full') as tabs:
        overview_tab = ui.tab('Overview', icon='dashboard')
        charts_tab = ui.tab('Charts', icon='insert_chart')

    with ui.tab_panels(tabs, value=overview_tab).classes('w-full'):
        
        # Overview Tab - Bigger stats tiles
        with ui.tab_panel(overview_tab):
            # Main stats - bigger
            with ui.element('div').style('display:grid; grid-template-columns:repeat(4,1fr); gap:20px; width:100%; margin-bottom:20px;'):
                for label, value, surface, col in [
                    ('Study Hours', f"{stats['study_hours']}h", 'surface-indigo', 'text-indigo-600'),
                    ('Total Cards', stats['total_cards'], 'surface-purple', 'text-purple-600'),
                    ('Mastered', stats['mastered_cards'], 'surface-green', 'text-emerald-600'),
                    ('Due Today', stats['due_today'], 'surface-orange', 'text-orange-600'),
                ]:
                    with ui.card().classes(f'stat-chip p-6 text-center {surface}'):
                        ui.label(str(value)).classes(f'text-4xl font-bold {col}')
                        ui.label(label).classes('micro-label mt-2')

            # Secondary stats - bigger too
            with ui.element('div').style('display:grid; grid-template-columns:repeat(3,1fr); gap:20px; width:100%;'):
                for label, value, surface, col in [
                    ('New Cards', stats['new_cards'], 'surface-blue', 'text-blue-600'),
                    ('Learning', stats['learning_cards'], 'surface-orange', 'text-amber-600'),
                    ('Total Reviews', stats['total_reviews'], 'surface-indigo', 'text-indigo-600'),
                ]:
                    with ui.card().classes(f'stat-chip p-5 text-center {surface}'):
                        ui.label(str(value)).classes(f'text-3xl font-bold {col}')
                        ui.label(label).classes('micro-label mt-2')

        # Charts Tab - Side by side, no scroll
        with ui.tab_panel(charts_tab):
            with ui.element('div').style('display:grid; grid-template-columns:repeat(2,1fr); gap:20px; width:100%;'):
                with ui.card().classes('p-4'):
                    ui.label('Cards Mastered Over Time').classes('micro-label mb-3')
                    ui.plotly(create_mastery_graph()).classes('w-full')

                with ui.card().classes('p-4'):
                    ui.label('Card States Distribution').classes('micro-label mb-3')
                    ui.plotly(create_state_breakdown_graph()).classes('w-full')
