from django.core.management.base import BaseCommand

from api.models import App, FlouciApp  # if needed


class Command(BaseCommand):
    help = "Link real FlouciApp entries to existing test apps using JhiUser relation"

    def handle(self, *args, **options):
        self.stdout.write("🔍 Scanning existing FlouciApp entries...")
        seen_wallets = set()
        # Get all real apps (test=False) from default DB
        real_apps = FlouciApp.objects.using("default").filter(test=False)
        count = 0
        for real_app in real_apps:
            wallet_id = real_app.wallet
            if not wallet_id:
                continue
            if wallet_id in seen_wallets:
                continue

            seen_wallets.add(wallet_id)
            try:
                # Step 1: Find real App in old_db with this wallet
                real_old_app = App.objects.using("old_db").filter(wallet=wallet_id).first()
            except App.DoesNotExist:
                self.stdout.write(f"⚠️ No matching real App found in old_db for wallet: {wallet_id}")
                continue

            try:
                # Step 2: Get the JhiUser related to this real_old_app
                jhi_user = real_old_app.user
                # Step 3: Find the test App for this user
                test_old_app = App.objects.using("old_db").get(user=jhi_user, test=True)
            except (App.DoesNotExist, AttributeError):
                self.stdout.write(f"⚠️ No test App found for user {jhi_user.id} (wallet: {wallet_id})")
                continue
            # Step 4: Link real_app with test_old_app
            real_test_app = FlouciApp.objects.get(id=test_old_app.id)
            real_test_app.tracking_id = real_app.tracking_id
            real_app.save(using="default")
            count += 1
            self.stdout.write(
                f"✅ Linked real app wallet {wallet_id} to test app ID {real_test_app.id} for id {real_app.tracking_id}"
            )
        self.stdout.write(f"🎉 Finished linking all real apps to their test apps. len{count}")
