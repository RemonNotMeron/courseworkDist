from nicegui import ui
from auth import users, pwd_context, is_authenticated, login_success, login_failed
from styles import inject_styles


@ui.page('/')
def login_page():
    inject_styles()
    
    # Redirect if already logged in
    if is_authenticated():
        ui.navigate.to('/dashboard')
        return

    with ui.card().classes('auth-card w-96 mx-auto mt-20 p-8'):
        ui.label('Sign in').classes('text-3xl font-bold text-center mb-6 text-grey-8 dark:text-grey-2')

        # Username input
        username_input = ui.input(
            label='Username',
            placeholder='Enter your username'
        ).props('outlined dense').classes('w-full mb-4')

        # Password input
        password_input = ui.input(
            label='Password',
            placeholder='Enter your password',
            password=True,
            password_toggle_button=True
        ).props('outlined dense').classes('w-full mb-6')

        def try_login():
            username = username_input.value.strip().lower()
            password = password_input.value

            user = users.get(username)
            if user and pwd_context.verify(password, user["password_hash"]):
                login_success(username)
            else:
                login_failed()

        ui.button('Sign In', on_click=try_login) \
            .props('unelevated no-caps') \
            .classes('app-btn bg-indigo-600 text-white w-full')

        with ui.row().classes('justify-center text-sm gap-1 mt-4'):
            ui.label("Don't have an account?").classes('text-grey-5')
            ui.link('Create account', '/registeration').classes('text-indigo-500 hover:underline font-medium')
