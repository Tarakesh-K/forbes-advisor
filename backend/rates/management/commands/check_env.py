"""
Management command for validating .env files.
Usage: python manage.py check_env
"""

from django.core.management.base import BaseCommand, CommandError
from utils.env_validator import EnvValidator, EnvValidationError


class Command(BaseCommand):
    help = "Validate environment variables against schema"

    def add_arguments(self, parser):
        parser.add_argument(
            "--env-file", type=str, help="Path to .env file to validate", default=".env"
        )
        parser.add_argument(
            "--show-vars",
            action="store_true",
            help="Show all validated variables (except sensitive ones)",
        )

    def handle(self, *args, **options):
        env_file = options["env_file"]
        show_vars = options["show_vars"]

        try:
            self.stdout.write(self.style.SUCCESS(f"Validating {env_file}..."))
            validated = EnvValidator.validate(env_file)

            self.stdout.write(
                self.style.SUCCESS("✓ All environment variables are valid!\n")
            )

            if show_vars:
                # Hide sensitive variables
                sensitive_keywords = ["password", "secret", "key", "token"]
                self.stdout.write(self.style.WARNING("Validated Variables:"))
                for var_name, value in sorted(validated.items()):
                    is_sensitive = any(
                        kw in var_name.lower() for kw in sensitive_keywords
                    )
                    display_value = "***HIDDEN***" if is_sensitive else value
                    self.stdout.write(f"  {var_name}: {display_value}")

        except EnvValidationError as e:
            raise CommandError(str(e))
