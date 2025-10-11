"""Login and registration screens with optional data encryption prompt."""

from collections.abc import Callable
from typing import Protocol

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Container, Grid
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static


class AuthProvider(Protocol):
    app_name: str

    def create_user(self, username: str, password: str, encrypt_data: bool = False) -> None: ...
    def verify_user(self, username: str, password: str) -> bool: ...
    def user_exists(self, username: str) -> bool: ...


class EncryptionPromptScreen(ModalScreen[bool]):
    CSS = """
    EncryptionPromptScreen { align: center middle; }
    #encrypt-dialog {
        width: 70;
        height: auto;
        padding: 2 3;
        border: thick $accent;
        background: $panel;
    }
    #encrypt-title { content-align: center middle; text-style: bold; margin-bottom: 1; }
    #encrypt-message { margin-bottom: 2; }
    #encrypt-btns { width: 100%; grid-size: 2 1; grid-gutter: 1 2; grid-columns: 1fr 1fr; }
    #encrypt-btns Button { width: 100%; }
    Button.-primary { background: $accent; color: $text; }
    """

    DEFAULT_HELP_TEXT = (
        "Would you like to encrypt your data?\n\n"
        "• YES: Your data will be encrypted with your password.\n"
        "         More secure, but you cannot recover data if you forget your password.\n\n"
        "• NO: Your data will be stored in plain text.\n"
        "        Less secure, but easier to access."
    )

    def __init__(self, help_text: str | None = None):
        super().__init__()
        self.help_text = help_text or self.DEFAULT_HELP_TEXT

    def compose(self) -> ComposeResult:
        with Container(id="encrypt-dialog"):
            yield Label("Data Encryption", id="encrypt-title")
            yield Static(self.help_text, id="encrypt-message")
            with Grid(id="encrypt-btns"):
                yield Button("Yes, Encrypt", id="btn-yes", classes="-primary")
                yield Button("No, Plain Text", id="btn-no")

    @on(Button.Pressed, "#btn-yes")
    def _btn_yes(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#btn-no")
    def _btn_no(self) -> None:
        self.dismiss(False)


class LoginScreen(Screen[None]):
    BINDINGS = [
        Binding("enter", "login", "Login", show=True),
        Binding("ctrl+l", "login", "Login", show=True),
        Binding("escape", "quit", "Quit", show=True),
        Binding("ctrl+q", "quit", "Quit", show=False),
        Binding("ctrl+r", "register", "Register", show=True),
    ]

    CSS = """
    #login-card {
        width: 70;
        max-width: 90%;
        margin: 2 0;
        padding: 2 3;
        border: round $accent;
        background: $panel;
    }
    #title { content-align: center middle; margin-bottom: 1; }
    Input { width: 100%; margin: 1 0; }
    #btns { width: 100%; grid-size: 3 1; grid-gutter: 1 2; grid-columns: 1fr 1fr 1fr; }
    #btns Button { width: 100%; }
    Button.-primary { background: $accent; color: $text; }
    """

    def __init__(
        self,
        title: str,
        auth: AuthProvider,
        next_screen: Callable[[str, str], Screen[None]],
        encryption_help: str | None = None,
    ):
        super().__init__()
        self._title = title
        self._auth = auth
        self._next = next_screen
        self._encryption_help = encryption_help

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(), Container(id="login-card"):
            yield Label(self._title, id="title")
            yield Input(placeholder="Username", id="username")
            yield Input(password=True, placeholder="Password", id="password")
            with Grid(id="btns"):
                yield Button("Login", id="btn-login", variant="primary")
                yield Button("Register", id="btn-register")
                yield Button("Quit", id="btn-quit")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#username", Input).focus()

    @on(Button.Pressed, "#btn-quit")
    def _btn_quit(self) -> None:
        self.action_quit()

    @on(Button.Pressed, "#btn-register")
    def _btn_register(self) -> None:
        self.action_register()

    @on(Button.Pressed, "#btn-login")
    def _btn_login(self) -> None:
        self.action_login()

    def action_quit(self) -> None:
        self.app.exit()

    def action_register(self) -> None:
        user = self.query_one("#username", Input).value.strip()
        pwd = self.query_one("#password", Input).value
        if not user or not pwd:
            self.app.notify("Enter a username & password to register.", severity="warning")
            return
        if self._auth.user_exists(user):
            self.app.notify(
                f"Username '{user}' is already taken. Please choose a different username.",
                severity="error",
            )
            return
        self.app.push_screen(
            EncryptionPromptScreen(self._encryption_help), self._on_encryption_choice
        )

    def _on_encryption_choice(self, encrypt_data: bool | None) -> None:
        if encrypt_data is None:
            return
        user = self.query_one("#username", Input).value.strip()
        pwd = self.query_one("#password", Input).value
        try:
            self._auth.create_user(user, pwd, encrypt_data)
            encryption_msg = " with encryption" if encrypt_data else ""
            self.app.notify(f"User '{user}' created{encryption_msg}. You can log in now.")
            self.query_one("#password", Input).value = ""
        except Exception as e:
            error_msg = str(e)
            if "user exists" in error_msg.lower():
                self.app.notify(
                    f"Username '{user}' is already taken. Please choose a different username.",
                    severity="error",
                )
            else:
                self.app.notify(f"Register failed: {error_msg}", severity="error")

    def action_login(self) -> None:
        user = self.query_one("#username", Input).value.strip()
        pwd = self.query_one("#password", Input).value
        if not user or not pwd:
            self.app.notify("Username and password required.", severity="warning")
            return
        if self._auth.verify_user(user, pwd):
            self.query_one("#password", Input).value = ""
            self.query_one("#username", Input).value = ""
            self.app.push_screen(self._next(user, pwd))
        else:
            self.app.notify("Invalid credentials.", severity="error")
