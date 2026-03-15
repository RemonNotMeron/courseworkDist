from nicegui import ui
import auth
from datetime import date, datetime
from styles import inject_styles


@ui.page('/flashcard_library')
def flashcard_library_page():
    inject_styles()
    
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return

    # Header
    with ui.card().classes('w-full surface-blue mb-4'):
        with ui.row().classes('items-center w-full px-2 py-1'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dashboard')) \
                .props('flat round').classes('text-grey-5')
            ui.label('Flashcard Library').classes('text-2xl font-bold text-grey-8 dark:text-grey-2 flex-1')

    with ui.element('div').style('display:grid; grid-template-columns:repeat(5,1fr); gap:16px; width:100%;'):
        # Create new deck button
        with ui.element('div').classes('nav-tile cursor-pointer surface-green flex flex-col items-center justify-center') \
            .style('min-height:140px; padding:24px;') \
            .on('click', lambda: ui.navigate.to('/create_new_deck')):
            ui.icon('add', size='2.5rem').classes('text-emerald-600 mb-3')
            ui.label('Create New').classes('text-base font-semibold text-grey-7')

        # Get user data
        user = None
        if hasattr(auth, 'current_username') and auth.current_username in auth.users:
            user = auth.users[auth.current_username]
        else:
            for k, v in auth.users.items():
                if v is auth.current_user:
                    user = v
                    break
        decks = user.get('decks', []) if user else []

        if decks:
            today = date.today()
            for d in decks:
                def card_is_due(card):
                    dd = card.get('due_date')
                    if not dd:
                        return True
                    try:
                        if 'T' in str(dd):
                            due_date = datetime.fromisoformat(dd).date()
                        else:
                            due_date = date.fromisoformat(dd)
                        return due_date <= today
                    except Exception:
                        return True

                def get_scheduled_breakdown(deck_cards):
                    scheduled = {}
                    for c in deck_cards:
                        dd = c.get('due_date')
                        if dd:
                            try:
                                if 'T' in str(dd):
                                    due_date = datetime.fromisoformat(dd).date()
                                else:
                                    due_date = date.fromisoformat(dd)
                                if due_date > today:
                                    scheduled[due_date] = scheduled.get(due_date, 0) + 1
                            except Exception:
                                pass
                    return scheduled

                due_count = sum(1 for c in d.get('cards', []) if card_is_due(c))
                scheduled = get_scheduled_breakdown(d.get('cards', []))
                card_count = len(d.get('cards', []))

                with ui.element('div').classes('nav-tile cursor-pointer surface-blue flex flex-col items-center justify-center') \
                    .style('min-height:140px; padding:20px;') \
                    .on('click', lambda d=d: ui.navigate.to(f'/flashcard_deck/{d.get("name", "Untitled")}')):
                    ui.label(d.get('name', 'Untitled')).classes('text-base font-semibold text-center text-grey-8 mb-2')
                    ui.label(f'{card_count} cards').classes('micro-label mb-2')
                    if due_count:
                        with ui.element('div').classes('surface-orange rounded-full px-3 py-1'):
                            ui.label(f'{due_count} due').classes('text-xs font-semibold text-orange-600')
        else:
            with ui.element('div').classes('surface-blue rounded-xl p-6 text-center col-span-4'):
                ui.label('No decks yet. Create your first deck!').classes('text-grey-5')
