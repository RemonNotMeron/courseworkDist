from nicegui import ui
import uuid
import auth
from datetime import datetime
from styles import inject_styles


@ui.page('/create_new_deck')
def create_new_deck_page():
    inject_styles()
    
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return

    # Page state
    current_cards = []
    selected = {'id': None}

    def add_card():
        card = {'id': str(uuid.uuid4()), 'front': '', 'back': ''}
        current_cards.append(card)
        selected['id'] = card['id']
        _refresh()

    def remove_card(card_id):
        nonlocal current_cards
        current_cards = [c for c in current_cards if c['id'] != card_id]
        if selected['id'] == card_id:
            selected['id'] = current_cards[-1]['id'] if current_cards else None
        _refresh()

    def select_card(card_id):
        selected['id'] = card_id
        _refresh()

    def _get_selected():
        return next((c for c in current_cards if c['id'] == selected['id']), None)

    def save_deck():
        name = deck_name_input.value.strip()
        if not name:
            ui.notify('Please enter a deck name.', type='warning')
            return
        if not current_cards:
            ui.notify('Add at least one card.', type='warning')
            return

        for c in current_cards:
            if not c['front'].strip() or not c['back'].strip():
                ui.notify('All cards must have both a front and a back.', type='warning')
                return

        username = auth.current_username
        if not username:
            ui.notify('Not logged in.', type='negative')
            return

        existing = auth.users[username].setdefault('decks', [])
        if any(d['name'].lower() == name.lower() for d in existing):
            ui.notify('A deck with that name already exists.', type='warning')
            return

        now = datetime.now().isoformat()
        saved_cards = [
            {
                'front': c['front'].strip(),
                'back': c['back'].strip(),
                'repetitions': 0,
                'interval': 0,
                'ef': 2.5,
                'due_date': now,
            }
            for c in current_cards
        ]

        existing.append({'name': name, 'description': '', 'cards': saved_cards})
        auth.save_users()
        ui.notify(f'Deck "{name}" saved!', type='positive')
        ui.navigate.to('/flashcard_library')

    def _refresh():
        _build_list()
        _build_editor()

    def _build_list():
        card_list.clear()
        with card_list:
            for i, card in enumerate(current_cards, 1):
                is_sel = card['id'] == selected['id']
                row_classes = (
                    'list-row w-full items-center gap-2 px-3 py-2 cursor-pointer '
                    + ('surface-blue border-blue-200 dark:border-blue-700' if is_sel else
                       'hover:bg-grey-2 dark:hover:bg-grey-8 border border-transparent')
                )
                with ui.row().classes(row_classes) \
                        .on('click', lambda _, cid=card['id']: select_card(cid)):
                    ui.label(str(i)).classes('text-xs text-grey-5 w-5 text-right shrink-0')
                    ui.label(card['front'] or '(empty front)') \
                        .classes('flex-1 truncate text-sm ' + ('font-medium text-indigo-700 dark:text-indigo-300' if is_sel else 'text-grey-7'))
                    ui.label('↔').classes('text-grey-4 text-xs shrink-0')
                    ui.label(card['back'] or '(empty back)') \
                        .classes('flex-1 truncate text-sm text-grey-5')
                    ui.button(icon='close') \
                        .props('flat dense round size=xs') \
                        .classes('text-grey-4 hover:text-red-500 shrink-0') \
                        .on('click', lambda _, cid=card['id']: remove_card(cid))

    def _build_editor():
        editor_area.clear()
        card = _get_selected()

        with editor_area:
            if not current_cards:
                with ui.column().classes('items-center justify-center w-full h-full py-16 gap-3'):
                    ui.icon('style', size='3rem').classes('text-grey-4')
                    ui.label('No cards yet.').classes('text-grey-5')
                    ui.label('Click "Add card" to get started.').classes('text-xs text-grey-4')
                return

            if card is None:
                ui.label('Select a card on the left to edit it.').classes('text-grey-5 italic py-10')
                return

            idx = next((i for i, c in enumerate(current_cards, 1) if c['id'] == card['id']), '?')
            with ui.row().classes('items-center gap-2 mb-3'):
                ui.label(f'Card {idx}').classes('text-base font-semibold text-grey-7')
                ui.label(f'of {len(current_cards)}').classes('text-sm text-grey-5')

            ui.label('Front').classes('micro-label mb-1')
            ui.input(placeholder='Character, word, or question…', value=card['front']) \
                .props('outlined dense').classes('w-full text-base mb-3') \
                .on('update:model-value', lambda e, c=card: (
                    c.update({'front': e.args}),
                    front_preview_label.set_text(e.args or '—'),
                    _build_list(),
                ))

            ui.label('Back').classes('micro-label mb-1')
            ui.textarea(placeholder='Reading, meaning, or answer…', value=card['back']) \
                .props('outlined autogrow dense').classes('w-full mb-3') \
                .on('update:model-value', lambda e, c=card: (
                    c.update({'back': e.args}),
                    back_preview_label.set_text(e.args or '—'),
                    _build_list(),
                ))

            ui.label('Preview').classes('micro-label mb-2')
            with ui.card().classes('w-full p-5 text-center surface-blue'):
                front_preview_label = ui.label(card['front'] or '—') \
                    .classes('text-3xl font-light text-grey-8 dark:text-grey-2 mb-3')
                ui.separator().classes('opacity-30')
                back_preview_label = ui.label(card['back'] or '—') \
                    .classes('text-lg text-grey-6 mt-3 whitespace-pre-line')

    # Header
    with ui.card().classes('w-full surface-blue mb-4'):
        with ui.row().classes('items-center w-full px-2 py-1'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/flashcard_library')) \
                .props('flat round').classes('text-grey-5')
            ui.label('Create New Deck').classes('text-2xl font-bold text-grey-8 dark:text-grey-2 flex-1')

    # Deck name
    with ui.card().classes('w-full max-w-lg p-4 mb-4'):
        with ui.row().classes('items-center gap-3'):
            ui.label('Deck name').classes('text-sm font-medium text-grey-7 w-24 shrink-0')
            deck_name_input = ui.input(placeholder='e.g. Hiragana た行') \
                .props('outlined dense').classes('flex-1')

    # Two-column body
    with ui.row().classes('w-full gap-4 items-start'):
        # LEFT - card list
        with ui.card().classes('w-5/12 p-4 gap-2 flex flex-col'):
            with ui.row().classes('w-full items-center justify-between mb-1'):
                ui.label('Cards').classes('font-semibold text-grey-7')
                ui.label(f'{len(current_cards)}').classes('text-xs text-grey-5')

            card_list = ui.column().classes('w-full gap-1 min-h-[200px] max-h-[400px] overflow-y-auto')

            ui.separator().classes('my-2')

            ui.button('Add card', icon='add') \
                .props('unelevated no-caps') \
                .classes('app-btn bg-indigo-600 text-white w-full') \
                .on('click', add_card)

        # RIGHT - editor + preview
        with ui.card().classes('flex-1 p-4 gap-0 flex flex-col'):
            editor_area = ui.column().classes('w-full gap-0')

    # Save bar
    with ui.card().classes('w-full p-4 mt-4'):
        with ui.row().classes('w-full justify-end gap-3'):
            ui.button('Cancel', on_click=lambda: ui.navigate.to('/flashcard_library')) \
                .props('flat no-caps').classes('text-grey-6')
            ui.button('Save deck', icon='save') \
                .props('unelevated no-caps') \
                .classes('app-btn bg-emerald-600 text-white px-6') \
                .on('click', save_deck)

    # Initial render
    add_card()
