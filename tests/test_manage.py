"""Tests for manage.py."""
import builtins
import os
import runpy
import sys

import pytest

import manage

main = manage.main


def test_main_sets_django_settings_module_when_not_set(monkeypatch):
    """Test that main() sets DJANGO_SETTINGS_MODULE when not defined."""

    called_args = []

    def mock_execute(args):
        called_args.append(args)

    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    monkeypatch.setattr(
        "django.core.management.execute_from_command_line",
        mock_execute,
    )
    monkeypatch.setattr(sys, "argv", ["manage.py", "help"])

    main()

    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "core.settings"
    assert called_args == [["manage.py", "help"]]


def test_main_preserves_existing_django_settings_module(monkeypatch):
    """Test that main() preserves DJANGO_SETTINGS_MODULE if already set."""

    original_value = "custom.settings"
    called_args = []

    def mock_execute(args):
        called_args.append(args)

    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", original_value)
    monkeypatch.setattr(
        "django.core.management.execute_from_command_line",
        mock_execute,
    )
    monkeypatch.setattr(sys, "argv", ["manage.py", "help"])

    main()

    assert os.environ.get("DJANGO_SETTINGS_MODULE") == original_value
    assert called_args == [["manage.py", "help"]]


def test_main_calls_execute_from_command_line_with_sys_argv(monkeypatch):
    """Test that main() calls execute_from_command_line with sys.argv."""
    test_argv = ["manage.py", "migrate", "--noinput"]
    called_args = []

    def mock_execute(args):
        called_args.append(args)

    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    monkeypatch.setattr(
        "django.core.management.execute_from_command_line",
        mock_execute,
    )
    monkeypatch.setattr(sys, "argv", test_argv)

    main()

    # Verify execute_from_command_line was called with correct args
    assert called_args == [test_argv]


def test_main_handles_different_commands(monkeypatch):
    """Test that main() works with different Django management commands."""
    commands = [
        ["manage.py", "runserver"],
        ["manage.py", "migrate"],
        ["manage.py", "collectstatic", "--noinput"],
        ["manage.py", "shell"],
    ]

    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)

    for command in commands:
        called_args = []

        def mock_execute(args):
            called_args.append(args)

        monkeypatch.setattr(
            "django.core.management.execute_from_command_line",
            mock_execute,
        )
        monkeypatch.setattr(sys, "argv", command)

        main()

        # Verify execute_from_command_line was called correctly
        assert called_args == [command]


def test_main_raises_import_error_when_django_is_missing(monkeypatch):
    """
    Testa se main() lança ImportError quando o Django não está disponível.
    Isso cobre o bloco `except ImportError as exc`.
    """

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "django.core.management":
            raise ImportError("No module named 'django.core.management'")
        return real_import(name, *args, **kwargs)

    # Exercita o caminho que cai no `return`, para cobrir a linha 118
    fake_import("os")

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(
        ImportError,
        match="Couldn't import Django",
    ):
        manage.main()


def test_main_called_when_module_run_as_script(monkeypatch):
    """Test that `main()` is called when manage.py is run as a script."""

    called_args = []

    def mock_execute(args):
        called_args.append(args)

    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    monkeypatch.setattr(
        "django.core.management.execute_from_command_line",
        mock_execute,
    )
    monkeypatch.setattr(sys, "argv", ["manage.py", "help"])

    # Executa o módulo como se fosse chamado pela linha de comando
    runpy.run_module("manage", run_name="__main__")

    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "core.settings"
    assert called_args == [["manage.py", "help"]]
