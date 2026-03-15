from nicegui import ui
import auth
from datetime import datetime, date, timedelta
from styles import inject_styles


def get_user_icon():
    """Get user's custom icon or default"""
    if auth.current_user and 'icon' in auth.current_user:
        return auth.current_user['icon']
    return '👤'


@ui.page('/dashboard')
def dashboard_page():
    inject_styles()
    
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return

    is_admin = auth.current_user.get('role') == 'admin'
    
    if is_admin:
        show_admin_dashboard()
    else:
        show_user_dashboard()


def _student_stats(user: dict) -> dict:
    today = date.today()
    total = mastered = learning = new = due = 0
    weak_cards = []
    for deck in user.get('decks', []):
        for card in deck.get('cards', []):
            total += 1
            reps = int(card.get('repetitions', 0))
            ef = float(card.get('ef', 2.5))
            if reps >= 5:
                mastered += 1
            elif reps > 0:
                learning += 1
            else:
                new += 1
            dd = card.get('due_date', '')
            if dd:
                try:
                    if datetime.fromisoformat(dd).date() <= today:
                        due += 1
                except Exception:
                    pass
            if ef < 2.0 and reps > 0:
                weak_cards.append({
                    'deck': deck.get('name', ''),
                    'front': card.get('front', ''),
                    'back': card.get('back', ''),
                    'ef': ef,
                    'reps': reps
                })
    weak_cards.sort(key=lambda c: c['ef'])
    return {
        'total': total,
        'mastered': mastered,
        'learning': learning,
        'new': new,
        'due': due,
        'weak_cards': weak_cards,
        'pct_mastered': round((mastered / total) * 100) if total else 0
    }


def _is_due_today(card: dict, today: date) -> bool:
    dd = card.get('due_date', '')
    if not dd:
        return True
    try:
        return datetime.fromisoformat(dd).date() <= today
    except Exception:
        return True


def show_admin_dashboard():
    """Show teacher dashboard for admins"""
    selected = {'username': None}

    # Header card
    with ui.card().classes('w-full surface-blue mb-4'):
        with ui.row().classes('items-center w-full px-3 py-2'):
            with ui.avatar(size='lg', color='primary'):
                ui.label(get_user_icon()).classes('text-2xl')
            with ui.column().classes('gap-0 ml-2'):
                ui.label(f'Welcome, {auth.current_user["full_name"]}!') \
                    .classes('text-2xl font-bold text-grey-9 dark:text-grey-1')
                ui.badge('Teacher').classes('bg-purple-600 text-white text-xs px-2 py-0.5 rounded-full')
            with ui.row().classes('ml-auto items-center gap-3'):
                with ui.column().classes('items-end gap-0'):
                    ui.label(datetime.now().strftime('%A, %d %B %Y')) \
                        .classes('opacity-70 text-sm font-medium text-grey-7')
                    clock = ui.label('').classes('text-2xl font-light text-grey-8 dark:text-grey-2')
                    ui.timer(1.0, lambda: clock.set_text(datetime.now().strftime('%H:%M')))
                ui.button(icon='settings', on_click=lambda: ui.navigate.to('/preference_settings')) \
                    .props('flat round').classes('text-grey-5')

    with ui.row().classes('w-full gap-4 items-start'):
        # LEFT - student roster
        with ui.card().classes('w-5/12 p-4'):
            with ui.row().classes('items-center gap-2 mb-3'):
                ui.icon('group', size='sm').classes('text-grey-5')
                ui.label('Students').classes('font-bold text-grey-8 dark:text-grey-2')
            
            students = {u: d for u, d in auth.users.items() if d.get('role') != 'admin'}
            if not students:
                with ui.element('div').classes('surface-blue rounded-xl p-6 text-center'):
                    ui.label('No student accounts yet.').classes('text-grey-5 text-sm')
            else:
                for uname, udata in students.items():
                    stats = _student_stats(udata)
                    is_sel = uname == selected['username']
                    row_cls = (
                        'list-row w-full items-center gap-3 px-3 py-3 cursor-pointer '
                        + ('surface-blue border-blue-200 dark:border-blue-700' if is_sel else
                           'hover:bg-grey-2 dark:hover:bg-grey-8 border border-transparent')
                    )
                    def _select(u=uname):
                        selected['username'] = u
                        _rebuild_detail()
                    with ui.row().classes(row_cls).on('click', _select):
                        with ui.avatar(size='md', color='primary' if is_sel else 'grey-4'):
                            ui.label(udata.get('icon', '👤')).classes('text-lg')
                        with ui.column().classes('flex-1 gap-0'):
                            ui.label(udata.get('full_name', uname)) \
                                .classes('font-semibold text-sm text-grey-8')
                            ui.label(f'@{uname}').classes('text-xs text-grey-5')
                        with ui.column().classes('items-end gap-0.5'):
                            pct = stats['pct_mastered']
                            col = ('text-emerald-600' if pct >= 50
                                   else 'text-orange-500' if pct >= 20
                                   else 'text-red-500')
                            ui.label(f'{pct}% mastered') \
                                .classes(f'text-xs font-semibold {col}')
                            if stats['weak_cards']:
                                ui.label(f'⚠ {len(stats["weak_cards"])} weak') \
                                    .classes('text-xs text-red-400')
                            if stats['due']:
                                ui.label(f'{stats["due"]} due') \
                                    .classes('text-xs text-orange-500')

        # RIGHT - detail panel
        detail_panel = ui.column().classes('flex-1 gap-3')

        def _rebuild_detail():
            detail_panel.clear()
            with detail_panel:
                uname = selected['username']
                if not uname:
                    with ui.card().classes('w-full p-10 items-center text-center surface-blue'):
                        ui.icon('person_search', size='3rem').classes('text-indigo-300 mx-auto')
                        ui.label('Select a student to view their profile.') \
                            .classes('text-grey-5 mt-3')
                    return

                udata = auth.users.get(uname, {})
                stats = _student_stats(udata)

                # Summary stats
                with ui.card().classes('w-full p-4 surface-blue'):
                    with ui.row().classes('items-center gap-2 mb-3'):
                        with ui.avatar(size='md', color='primary'):
                            ui.label(udata.get('icon', '👤')).classes('text-lg')
                        with ui.column().classes('gap-0'):
                            ui.label(udata.get('full_name', uname)) \
                                .classes('font-bold text-grey-8')
                            ui.label(f'@{uname}').classes('text-sm text-grey-5')
                    with ui.grid(columns=4).classes('w-full gap-3'):
                        for label, value, surface, col in [
                            ('Total', stats['total'], 'surface-indigo', 'text-indigo-600'),
                            ('Mastered', stats['mastered'], 'surface-green', 'text-emerald-600'),
                            ('Learning', stats['learning'], 'surface-orange', 'text-amber-600'),
                            ('Due today', stats['due'], 'surface-red', 'text-red-500'),
                        ]:
                            with ui.card().classes(f'stat-chip p-3 text-center {surface}'):
                                ui.label(str(value)).classes(f'text-2xl font-bold {col}')
                                ui.label(label).classes('micro-label mt-1')

                # Weak cards
                with ui.card().classes('w-full p-4'):
                    with ui.row().classes('items-center gap-2 mb-3'):
                        ui.icon('warning', color='orange')
                        ui.label('Weak Cards').classes('font-bold text-grey-8')
                        ui.label('EF < 2.0').classes('micro-label ml-1')
                    if not stats['weak_cards']:
                        with ui.element('div').classes('surface-green rounded-xl p-4 text-center'):
                            ui.label('✓ No weak cards.').classes('text-emerald-700 text-sm font-medium')
                    else:
                        by_deck: dict = {}
                        for wc in stats['weak_cards']:
                            by_deck.setdefault(wc['deck'], []).append(wc)
                        for dname, cards in by_deck.items():
                            ui.label(dname).classes('micro-label mt-3 mb-1')
                            for wc in cards:
                                ef_pct = round(((wc['ef'] - 1.3) / (2.5 - 1.3)) * 100)
                                bar_col = ('bg-red-400' if ef_pct < 30
                                           else 'bg-orange-400' if ef_pct < 60
                                           else 'bg-yellow-400')
                                with ui.row().classes('w-full items-center gap-3 py-1.5'):
                                    ui.label(wc['front']).classes(
                                        'text-xl font-light w-12 text-center shrink-0'
                                    )
                                    with ui.column().classes('flex-1 gap-0'):
                                        ui.label(wc['back']).classes('text-xs text-grey-6 truncate')
                                        with ui.element('div').classes('w-full bg-grey-3 rounded-full h-1.5 mt-1'):
                                            ui.element('div').classes(f'{bar_col} h-1.5 rounded-full').style(f'width:{ef_pct}%')
                                    ui.label(f'EF {wc["ef"]:.2f}').classes('text-xs text-grey-5 shrink-0')

                # Deck overview
                with ui.card().classes('w-full p-4'):
                    with ui.row().classes('items-center gap-2 mb-3'):
                        ui.icon('library_books').classes('text-grey-5')
                        ui.label('Deck Overview').classes('font-bold text-grey-8')
                    today = date.today()
                    for deck in udata.get('decks', []):
                        cards = deck.get('cards', [])
                        dm = sum(1 for c in cards if int(c.get('repetitions', 0)) >= 5)
                        dn = sum(1 for c in cards if int(c.get('repetitions', 0)) == 0)
                        dd = sum(1 for c in cards if _is_due_today(c, today))
                        dw = sum(1 for c in cards
                                 if float(c.get('ef', 2.5)) < 2.0
                                 and int(c.get('repetitions', 0)) > 0)
                        with ui.row().classes(
                            'list-row w-full items-center gap-2 px-2 py-2 '
                            'border-b border-grey-2 dark:border-grey-8'
                        ):
                            ui.label(deck.get('name', 'Untitled')).classes(
                                'flex-1 text-sm font-medium text-grey-7'
                            )
                            for txt, col in [
                                (f'{dm}/{len(cards)}', 'text-emerald-600'),
                                (f'{dd} due', 'text-orange-500'),
                                (f'{dn} new', 'text-blue-500'),
                                (f'{dw} weak', 'text-red-400' if dw else 'text-grey-4'),
                            ]:
                                ui.label(txt).classes(f'text-xs font-semibold {col} shrink-0')

                # Add card
                with ui.card().classes('w-full p-4 surface-indigo'):
                    with ui.row().classes('items-center gap-2 mb-3'):
                        ui.icon('add_card').classes('text-indigo-500')
                        ui.label('Add a Card').classes('font-bold text-grey-8')
                    deck_names = [d.get('name', '') for d in udata.get('decks', [])]
                    deck_select = ui.select(
                        options=deck_names, label='Select deck',
                        value=deck_names[0] if deck_names else None
                    ).props('outlined dense').classes('w-full mb-3')
                    front_in = ui.input(placeholder='Front (character / question)') \
                        .props('outlined dense').classes('w-full mb-2')
                    back_in = ui.textarea(placeholder='Back (reading / answer)') \
                        .props('outlined autogrow dense').classes('w-full mb-3')

                    def _add_card(u=uname):
                        dname = deck_select.value
                        front = front_in.value.strip()
                        back = back_in.value.strip()
                        if not dname or not front or not back:
                            ui.notify('Please fill in all fields.', type='warning')
                            return
                        student = auth.users.get(u)
                        if not student:
                            return
                        target = next(
                            (d for d in student.get('decks', []) if d.get('name') == dname),
                            None
                        )
                        if not target:
                            ui.notify('Deck not found.', type='negative')
                            return
                        target['cards'].append({
                            'front': front, 'back': back,
                            'repetitions': 0, 'interval': 0, 'ef': 2.5,
                            'due_date': datetime.now().isoformat(),
                        })
                        auth.save_users()
                        ui.notify(f'Card added to "{dname}".', type='positive')
                        front_in.set_value('')
                        back_in.set_value('')
                        _rebuild_detail()

                    ui.button('Add card', icon='add') \
                        .props('unelevated no-caps') \
                        .classes('app-btn bg-indigo-600 text-white w-full') \
                        .on('click', _add_card)

        _rebuild_detail()


def show_user_dashboard():
    """Show normal user dashboard - compact layout"""
    inject_styles()
    
    # Header
    with ui.card().classes('w-full max-w-5xl mx-auto surface-blue mb-4'):
        with ui.row().classes('items-center w-full px-3 py-2'):
            with ui.avatar(size='lg', color='primary'):
                ui.label(get_user_icon()).classes('text-2xl')
            with ui.column().classes('gap-0 ml-2'):
                ui.label(f'Welcome back, {auth.current_user["full_name"]}!') \
                    .classes('text-2xl font-bold text-grey-9 dark:text-grey-1')
            with ui.row().classes('ml-auto items-center gap-3'):
                with ui.column().classes('items-end gap-0'):
                    ui.label(datetime.now().strftime('%A, %d %B %Y')) \
                        .classes('opacity-70 text-sm font-medium text-grey-7')
                    clock = ui.label('').classes('text-2xl font-light text-grey-8 dark:text-grey-2')
                    ui.timer(1.0, lambda: clock.set_text(datetime.now().strftime('%H:%M')))
                ui.button(icon='settings', on_click=lambda: ui.navigate.to('/preference_settings')) \
                    .props('flat round').classes('text-grey-5')

    # Due today section
    with ui.card().classes('w-full max-w-5xl mx-auto p-4 mb-4'):
        with ui.row().classes('items-center gap-2 mb-3'):
            ui.icon('assignment_late', size='sm').classes('text-orange-500')
            ui.label('Due Today').classes('font-bold text-grey-8 dark:text-grey-2')

        has_due = False
        with ui.column().classes('w-full gap-1').style('max-height: 140px; overflow-y: auto;'):
            for deck in auth.current_user.get('decks', []):
                due_cards = [
                    c for c in deck.get('cards', [])
                    if 'due_date' in c
                    and datetime.fromisoformat(c['due_date']) <= datetime.now()
                ]
                if due_cards:
                    has_due = True
                    with ui.row().classes(
                        'list-row items-center gap-3 px-3 py-2 cursor-pointer'
                    ).on('click', lambda d=deck: ui.navigate.to(f'/flashcard_deck/{d["name"]}')):
                        with ui.element('div').classes('surface-orange rounded-lg px-3 py-1 shrink-0'):
                            ui.label(str(len(due_cards))).classes('text-lg font-bold text-orange-600')
                        ui.label(deck['name']).classes('flex-1 text-sm font-medium text-grey-7')
                        ui.icon('chevron_right', size='sm').classes('text-grey-4')

        if not has_due:
            with ui.element('div').classes('surface-green rounded-xl p-4 text-center'):
                ui.label('🎉').classes('text-2xl mb-1')
                ui.label('You\'re all caught up!').classes('text-emerald-700 font-semibold text-sm')

    # Navigation tiles - compact 3-column grid
    with ui.card().classes('w-full max-w-5xl mx-auto p-5'):
        ui.label('Navigate').classes('micro-label mb-4')
        with ui.element('div').style('display:grid; grid-template-columns:repeat(3,1fr); gap:20px; width:100%;'):
            for title, icon_name, route, surface, icon_bg, icon_col in [
                ('Flashcard Library', 'library_books', '/flashcard_library', 'surface-blue', '#ccfbf1', '#0f766e'),
                ('Progress', 'trending_up', '/progress_visualiser', 'surface-purple', '#f3e8ff', '#7c3aed'),
                ('Settings', 'settings', '/preference_settings', 'surface-orange', '#ffedd5', '#c2410c'),
            ]:
                with ui.element('div').classes(f'nav-tile cursor-pointer {surface}').style(
                    'display:flex; flex-direction:column; align-items:center; '
                    'justify-content:center; padding:32px 16px; box-sizing:border-box;'
                ).on('click', lambda r=route: ui.navigate.to(r)):
                    with ui.element('div').style(
                        f'width:52px; height:52px; border-radius:16px; '
                        f'background:{icon_bg}; display:flex; align-items:center; '
                        f'justify-content:center; margin-bottom:12px; flex-shrink:0;'
                    ):
                        ui.icon(icon_name, size='1.75rem').style(f'color:{icon_col};')
                    ui.label(title).style(
                        'font-size:0.95rem; font-weight:600; text-align:center; color:#1f2937;'
                    )
