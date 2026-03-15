from nicegui import ui, app
import auth
import base64
from styles import inject_styles


EMOJI_OPTIONS = ['👤', '🎓', '📚', '🧠', '⭐', '🎯', '✨', '🚀', '💡', '🎨', '📝', '🏆']
IMAGE_FILE_TYPES = ('Image Files (*.png;*.jpg;*.jpeg;*.webp;*.gif)', 'All Files (*.*)')


def get_user_icon():
    if auth.current_user and 'icon' in auth.current_user:
        return auth.current_user['icon']
    return '👤'


def set_user_icon(icon: str):
    if auth.current_user:
        auth.current_user['icon'] = icon
        auth.save_users()
        ui.notify(f"Icon changed to {icon}", type='positive')


def change_full_name(new_name: str):
    if not new_name or not new_name.strip():
        ui.notify('Name cannot be empty', type='negative')
        return False
    if auth.current_user:
        auth.current_user['full_name'] = new_name.strip()
        auth.save_users()
        ui.notify('Name updated successfully', type='positive')
        return True
    return False


def change_username(new_username: str):
    new_username = new_username.strip().lower()
    if not new_username:
        ui.notify('Username cannot be empty', type='negative')
        return False
    if new_username in auth.users and new_username != auth.current_username:
        ui.notify('Username already taken', type='negative')
        return False
    if auth.current_user and auth.current_username:
        user_data = auth.users[auth.current_username]
        del auth.users[auth.current_username]
        auth.users[new_username] = user_data
        auth.current_username = new_username
        auth.current_user = auth.users[new_username]
        auth.save_users()
        ui.notify('Username updated successfully', type='positive')
        return True
    return False


def change_password(current_password: str, new_password: str, confirm_password: str):
    if not current_password or not new_password or not confirm_password:
        ui.notify('Please fill in all password fields', type='negative')
        return False
    if new_password != confirm_password:
        ui.notify('New passwords do not match', type='negative')
        return False
    if len(new_password) < 6:
        ui.notify('Password must be at least 6 characters', type='negative')
        return False
    if auth.current_user and auth.current_username:
        if not auth.pwd_context.verify(current_password, auth.current_user['password_hash']):
            ui.notify('Current password is incorrect', type='negative')
            return False
        auth.current_user['password_hash'] = auth.pwd_context.hash(new_password)
        auth.save_users()
        ui.notify('Password updated successfully', type='positive')
        return True
    return False


@ui.page('/preference_settings')
def preference_settings():
    inject_styles()
    
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return

    user = auth.current_user

    # Header
    with ui.card().classes('w-full surface-blue mb-4'):
        with ui.row().classes('items-center w-full px-2 py-1'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dashboard')) \
                .props('flat round').classes('text-grey-5')
            ui.label('Preferences').classes('text-2xl font-bold text-grey-8 dark:text-grey-2 flex-1')

    # 3-column layout
    with ui.element('div').style('display:grid; grid-template-columns:repeat(3,1fr); gap:16px; width:100%;'):

        # LEFT: Avatar + Account
        with ui.column().style('gap:12px;'):
            with ui.card().classes('w-full p-4'):
                with ui.row().classes('items-center gap-2 mb-3'):
                    ui.icon('account_circle', size='sm').classes('text-grey-5')
                    ui.label('Avatar').classes('font-bold text-grey-7 text-sm')
                with ui.row().classes('items-center gap-3 mb-3'):
                    with ui.avatar(size='lg', color='primary'):
                        current_icon_label = ui.label(get_user_icon()).classes('text-2xl')
                    with ui.column().classes('gap-0'):
                        ui.label(user.get('full_name', '')).classes('font-medium text-grey-8 text-sm')
                        ui.label(f'@{auth.current_username}').classes('text-xs text-grey-5')
                with ui.row().classes('gap-1 flex-wrap'):
                    for emoji in EMOJI_OPTIONS:
                        is_sel = emoji == get_user_icon()
                        ui.button(emoji) \
                            .props('unelevated' if is_sel else 'flat') \
                            .classes('text-lg w-10 h-10 rounded-lg ' +
                                     ('bg-indigo-600 text-white' if is_sel else 'hover:bg-grey-2')) \
                            .on('click', lambda e=emoji: (set_user_icon(e), current_icon_label.set_text(e)))

            with ui.card().classes('w-full p-4'):
                with ui.row().classes('items-center gap-2 mb-3'):
                    ui.icon('badge', size='sm').classes('text-grey-5')
                    ui.label('Account Details').classes('font-bold text-grey-7 text-sm')
                ui.label('Full name').classes('micro-label mb-1')
                name_input = ui.input(placeholder='Your display name', value=user.get('full_name', '')) \
                    .props('outlined dense').classes('w-full mb-3')
                ui.label('Username').classes('micro-label mb-1')
                username_input = ui.input(placeholder='your_username', value=auth.current_username) \
                    .props('outlined dense').classes('w-full mb-3')

                def save_account():
                    changed = False
                    if name_input.value.strip() != user.get('full_name', ''):
                        if not change_full_name(name_input.value):
                            name_input.set_value(user.get('full_name', ''))
                            return
                        changed = True
                    if username_input.value.strip().lower() != auth.current_username:
                        if not change_username(username_input.value):
                            username_input.set_value(auth.current_username)
                            return
                        changed = True
                    if changed:
                        ui.navigate.to('/preference_settings')

                ui.button('Save changes', icon='save').props('unelevated no-caps') \
                    .classes('app-btn bg-indigo-600 text-white w-full').on('click', save_account)

        # MIDDLE: Security + Session
        with ui.column().style('gap:12px;'):
            with ui.card().classes('w-full p-4'):
                with ui.row().classes('items-center gap-2 mb-3'):
                    ui.icon('lock', size='sm').classes('text-grey-5')
                    ui.label('Security').classes('font-bold text-grey-7 text-sm')
                ui.label('Current password').classes('micro-label mb-1')
                current_pwd = ui.input(placeholder='Enter current password', password=True, password_toggle_button=True) \
                    .props('outlined dense').classes('w-full mb-3')
                ui.label('New password').classes('micro-label mb-1')
                new_pwd = ui.input(placeholder='At least 6 characters', password=True, password_toggle_button=True) \
                    .props('outlined dense').classes('w-full mb-3')
                ui.label('Confirm new password').classes('micro-label mb-1')
                confirm_pwd = ui.input(placeholder='Repeat new password', password=True, password_toggle_button=True) \
                    .props('outlined dense').classes('w-full mb-3')

                def update_password():
                    if change_password(current_pwd.value, new_pwd.value, confirm_pwd.value):
                        current_pwd.set_value('')
                        new_pwd.set_value('')
                        confirm_pwd.set_value('')

                ui.button('Update password', icon='lock_reset').props('unelevated no-caps') \
                    .classes('app-btn bg-blue-600 text-white w-full').on('click', update_password)

            with ui.card().classes('w-full p-4'):
                with ui.row().classes('items-center gap-2 mb-3'):
                    ui.icon('logout', size='sm').classes('text-grey-5')
                    ui.label('Session').classes('font-bold text-grey-7 text-sm')
                ui.label(f'Signed in as {user.get("full_name", auth.current_username)}') \
                    .classes('text-xs text-grey-6 mb-3')

                def sign_out():
                    ui.notify('Signing out…', type='info')
                    auth.logout()

                ui.button('Sign out', icon='logout').props('unelevated no-caps color=red') \
                    .classes('app-btn bg-red-500 text-white w-full').on('click', sign_out)

        # RIGHT: Dashboard Background
        with ui.column().style('gap:12px;'):
            with ui.card().classes('w-full p-4'):
                with ui.row().classes('items-center gap-2 mb-3'):
                    ui.icon('wallpaper', size='sm').classes('text-grey-5')
                    ui.label('Dashboard Background').classes('font-bold text-grey-7 text-sm')
                ui.label('Set a custom image as your dashboard background.').classes('text-xs text-grey-5 mb-3')

                stored_url = user.get('bg_image', '')

                preview_img = ui.image(stored_url if stored_url else '') \
                    .classes('w-full rounded-lg border-2 border-indigo-400') \
                    .style('height: 80px; object-fit: cover;')
                preview_img.set_visibility(bool(stored_url))

                active_badge = ui.label('✓ Custom image active') \
                    .classes('text-xs text-indigo-500 font-medium mt-1 mb-2')
                active_badge.set_visibility(bool(stored_url))

                async def _pick_image():
                    result = await app.native.main_window.create_file_dialog(
                        dialog_type=10, allow_multiple=False, file_types=IMAGE_FILE_TYPES,
                    )
                    if not result:
                        return
                    path = result[0]
                    try:
                        raw = open(path, 'rb').read()
                    except OSError as exc:
                        ui.notify(f'Could not read file: {exc}', type='negative')
                        return
                    if len(raw) > auth.MAX_IMAGE_BYTES:
                        mb = len(raw) / (1024 * 1024)
                        ui.notify(f'Image is {mb:.1f} MB — maximum allowed is 5 MB.', type='negative')
                        return

                    ext = path.lower().rsplit('.', 1)[-1]
                    mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                                'png': 'image/png', 'webp': 'image/webp', 'gif': 'image/gif'}
                    mime = mime_map.get(ext, 'image/jpeg')
                    encoded = base64.b64encode(raw).decode('ascii')
                    data_url = f'data:{mime};base64,{encoded}'

                    auth.set_bg_image(data_url)
                    preview_img.set_source(data_url)
                    preview_img.set_visibility(True)
                    active_badge.set_visibility(True)
                    brightness_row.set_visibility(True)
                    brightness_pct.set_text('100%')
                    remove_btn.set_visibility(True)

                    size_str = f'{len(raw) / 1024:.0f} KB' if len(raw) < 1024 * 1024 else f'{len(raw) / (1024*1024):.1f} MB'
                    ui.notify(f'🖼 Background set ({size_str}) — visible on next dashboard visit.', type='positive')

                def _remove_image():
                    auth.clear_bg_image()
                    preview_img.set_visibility(False)
                    active_badge.set_visibility(False)
                    brightness_row.set_visibility(False)
                    remove_btn.set_visibility(False)
                    ui.notify('Background image removed.', type='info')

                ui.button('Choose image…', icon='upload') \
                    .props('unelevated no-caps') \
                    .classes('app-btn bg-indigo-600 text-white w-full mb-3') \
                    .on('click', _pick_image)

                with ui.column().classes('w-full gap-1 mb-2') as brightness_row:
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label('Brightness').classes('micro-label')
                        brightness_pct = ui.label(f'{int(auth.get_bg_brightness() * 100)}%').classes('text-xs text-grey-5')
                    ui.slider(min=0, max=100, value=int(auth.get_bg_brightness() * 100)) \
                        .props('dense').classes('w-full').on(
                            'update:model-value',
                            lambda e: (auth.set_bg_brightness(e.args / 100), brightness_pct.set_text(f'{int(e.args)}%')),
                        )
                brightness_row.set_visibility(bool(stored_url))

                remove_btn = ui.button('Remove image', icon='delete_outline') \
                    .props('flat no-caps') \
                    .classes('text-red-500 w-full') \
                    .on('click', _remove_image)
                remove_btn.set_visibility(bool(stored_url))
