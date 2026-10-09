from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from chat.models import ChatRoom, Message
from orders.models import Order, OrderItem, OrderTracking
from reviews.models import Review
from tailor.models import ShopLocation, TailorService
from users.models import CustomerProfile, TailorProfile, User


class Command(BaseCommand):
    help = "Create repeatable demo data for the tailor application."

    @transaction.atomic
    def handle(self, *args, **options):
        customer = self._user("demo_customer", "customer@example.com", User.Role.CUSTOMER)
        CustomerProfile.objects.update_or_create(
            user=customer,
            defaults={
                "address": "Jl. Soekarno Hatta No. 10, Malang",
                "latitude": -7.983908,
                "longitude": 112.621391,
            },
        )

        tailors = []
        tailor_data = [
            ("demo_tailor_1", "Batik Lestari", "Spesialis busana batik dan kebaya custom.", 12, -7.9666204, 112.6326321),
            ("demo_tailor_2", "Jarum Rapi", "Jasa jahit harian, formal, dan reparasi pakaian.", 8, -7.979700, 112.630400),
            ("demo_tailor_3", "Sutra Mode", "Tailor premium untuk jas dan gaun acara khusus.", 15, -7.970200, 112.625100),
        ]
        for username, shop_name, bio, experience, latitude, longitude in tailor_data:
            user = self._user(username, f"{username}@example.com", User.Role.TAILOR)
            tailor, _ = TailorProfile.objects.update_or_create(
                user=user,
                defaults={
                    "shop_name": shop_name,
                    "bio": bio,
                    "is_verified": True,
                    "experience_years": experience,
                },
            )
            ShopLocation.objects.update_or_create(
                tailor=tailor,
                defaults={
                    "address": f"Jl. Malang Kreatif No. {experience}",
                    "city": "Malang",
                    "latitude": latitude,
                    "longitude": longitude,
                },
            )
            service_data = [
                ("Jahit Custom", "Pembuatan pakaian sesuai ukuran.", Decimal("250000.00"), 7),
                ("Permak Pakaian", "Perbaikan ukuran dan detail pakaian.", Decimal("75000.00"), 2),
            ]
            for name, description, price, days in service_data:
                TailorService.objects.update_or_create(
                    tailor=tailor,
                    name=name,
                    defaults={
                        "description": description,
                        "base_price": price,
                        "estimated_duration_days": days,
                        "is_active": True,
                    },
                )
            tailors.append(tailor)

        service = tailors[0].services.get(name="Jahit Custom")
        order, _ = Order.objects.update_or_create(
            customer=customer,
            tailor=tailors[0],
            snap_token="demo-order-1",
            defaults={
                "status": Order.Status.COMPLETED,
                "payment_status": Order.PaymentStatus.PAID,
                "total_price": service.base_price,
            },
        )
        OrderItem.objects.update_or_create(
            order=order,
            service=service,
            defaults={"quantity": 1, "notes": "Gunakan bahan katun warna hijau tua.", "price_at_order": service.base_price},
        )
        OrderTracking.objects.get_or_create(order=order, status=Order.Status.COMPLETED, defaults={"description": "Pesanan selesai."})
        Review.objects.update_or_create(order=order, defaults={"rating": 5, "comment": "Hasil jahitan rapi dan sesuai ukuran."})

        room, _ = ChatRoom.objects.get_or_create(customer=customer, tailor=tailors[0])
        Message.objects.get_or_create(room=room, sender=customer, text="Halo, apakah bisa konsultasi ukuran?")

        self.stdout.write(self.style.SUCCESS("Demo data berhasil dibuat/diperbarui."))

    def _user(self, username, email, role):
        user, created = User.objects.get_or_create(username=username, defaults={"email": email, "role": role})
        if created:
            user.set_password("password123")
        user.email = email
        user.role = role
        user.is_active = True
        user.save(update_fields=["email", "role", "is_active", "password"])
        return user
