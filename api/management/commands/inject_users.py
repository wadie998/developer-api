from uuid import UUID

from django.core.management.base import BaseCommand
from django.db import connections, transaction

from api.models import FlouciApp, Peer
from utils.backend_client import FlouciBackendClient


class Command(BaseCommand):
    help = "Migrate users and their apps from the old database to the new database"

    def fetch_tracking_id(self, user_id, wallet):
        try:
            UUID(user_id)
            return None, None
        except Exception:
            if wallet and wallet != "Test wallet":
                result = FlouciBackendClient.fetch_associated_tracking_id(wallet)
                tracking_id = result.get("tracking_id")
                user_type = result.get("type")
            return tracking_id, user_type

    def migrate_users(self):
        """Migrate users from old_db to the new database."""
        old_cursor = connections["old_db"].cursor()
        old_cursor.execute(
            """
            SELECT id, phone_number, user_id
            FROM jhi_user
        """
        )

        users = old_cursor.fetchall()
        self.stdout.write(f"Found {len(users)} users to migrate...")

        migrated_count = 0
        skipped_count = 0

        for user in users:
            id, phone_number, user_id = user

            # Check if user already exists
            if Peer.objects.using("default").filter(id=id).exists():
                self.stdout.write(self.style.WARNING(f"Skipping existing user: {phone_number}"))
                skipped_count += 1
                continue

            # Create and save new user
            new_user = Peer(
                id=id,
                tracking_id=user_id,
                phone_number=phone_number,
            )
            new_user.save(using="default")
            migrated_count += 1

            self.stdout.write(self.style.SUCCESS(f"Migrated user {phone_number}"))

        # Update the sequence to avoid conflicts
        self.stdout.write(self.style.WARNING("Updating Peer ID sequence..."))
        update_peer_sequence()

        self.stdout.write(
            self.style.SUCCESS(f"User migration complete: {migrated_count} users migrated, {skipped_count} skipped.")
        )

    def migrate_apps(self):
        """Migrate apps and link them to migrated users."""
        old_cursor = connections["old_db"].cursor()
        old_cursor.execute(
            """
            SELECT id, name, public_token, wallet, status, active, date_created, user_id, webhook,
                   test, description, private_token, image_url, deleted, gross,
                   transaction_number, revoke_number, last_revoke_date, app_id, merchant_id
            FROM app
        """
        )

        apps = old_cursor.fetchall()
        self.stdout.write(f"Found {len(apps)} apps to migrate...")

        migrated_count = 0
        skipped_count = 0
        users_wallets = {}

        for app in apps:
            (
                id,
                name,
                public_token,
                wallet,
                status,
                active,
                date_created,
                user_id,
                webhook,
                test,
                description,
                private_token,
                image_url,
                deleted,
                gross,
                transaction_number,
                revoke_number,
                last_revoke_date,
                app_id,
                merchant_id,
            ) = app

            # Find the corresponding user in the new database
            user = None
            if user_id:
                user = Peer.objects.using("default").filter(id=user_id).first()

            # Check if app already exists
            if FlouciApp.objects.using("default").filter(id=id).exists():
                self.stdout.write(self.style.WARNING(f"Skipping existing app: {name}"))
                skipped_count += 1
                continue

            # Create and save new app
            new_app = FlouciApp(
                id=id,
                name=name,
                public_token=public_token,
                wallet=wallet,
                status=status,
                active=active,
                date_created=date_created,
                user=user,  # Preserve the ForeignKey relationship
                webhook=webhook or "",
                test=test,
                description=description or "",
                private_token=private_token,
                image_url=image_url or "",
                deleted=deleted,
                gross=gross,
                transaction_number=transaction_number,
                revoke_number=revoke_number,
                last_revoke_date=last_revoke_date,
                app_id=app_id,
                merchant_id=merchant_id,
            )
            new_app.save(using="default")
            migrated_count += 1

            if wallet != "Test wallet":
                users_wallets[user_id] = wallet

            self.stdout.write(self.style.SUCCESS(f"Migrated app {name}"))

        # Update FlouciApp sequence to avoid conflicts
        self.stdout.write(self.style.WARNING("Updating FlouciApp ID sequence..."))
        update_flouciapp_sequence()

        self.stdout.write(
            self.style.SUCCESS(f"App migration complete: {migrated_count} apps migrated, {skipped_count} skipped.")
        )
        return users_wallets

    def update_to_tracking_id(self, users_wallets):
        """Update the user_id field to tracking_id using the wallet from the App model."""

        migrated_count = 0
        skipped_count = 0

        for user_id, wallet in users_wallets.items():
            tracking_id, user_type = self.fetch_tracking_id(user_id, wallet)

            if tracking_id:
                # Update the user's user_id field to tracking_id
                Peer.objects.using("default").filter(id=user_id).update(tracking_id=tracking_id, user_type=user_type)
                migrated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Updated user {user_id} to tracking_id {tracking_id}"))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"Skipping user {user_id}: No tracking_id found"))

        self.stdout.write(
            self.style.SUCCESS(
                f"User update to tracking_id complete: {migrated_count} updated, {skipped_count} skipped."
            )
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        """Run the migration in a single transaction."""
        self.stdout.write(self.style.WARNING("Starting user migration..."))
        self.migrate_users()

        self.stdout.write(self.style.WARNING("Starting app migration..."))
        users_wallets = self.migrate_apps()

        self.stdout.write(self.style.WARNING("Starting tracking id migration calling flouci backend..."))
        self.update_to_tracking_id(users_wallets)

        self.stdout.write(self.style.SUCCESS("Migration completed successfully!"))


def update_flouciapp_sequence():
    from django.db import connection

    """Updates the sequence of FlouciApp.id to avoid conflicts."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT setval('flouciapp_id_seq', COALESCE((SELECT MAX(id) FROM FlouciApp), 1));")


def update_peer_sequence():
    from django.db import connection

    """Updates the sequence of Peer.id to avoid conflicts."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT setval('peer_id_seq', COALESCE((SELECT MAX(id) FROM peer), 1));")
