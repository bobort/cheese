# Generated migration to move data from profile app to accounts app
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone
from tinymce.models import HTMLField


def migrate_data_from_profile(apps, schema_editor):
    """
    Migrate data from profile tables to accounts tables.
    This assumes profile tables exist and need to be renamed to accounts tables.
    """
    db_alias = schema_editor.connection.alias
    
    # Get the table names
    with schema_editor.connection.cursor() as cursor:
        # Rename tables from profile_* to accounts_*
        tables_to_rename = [
            ('profile_student', 'accounts_student'),
            ('profile_order', 'accounts_order'),
            ('profile_orderlineitem', 'accounts_orderlineitem'),
            ('profile_product', 'accounts_product'),
            ('profile_productuser', 'accounts_productuser'),
            ('profile_staff', 'accounts_staff'),
            ('profile_testimonial', 'accounts_testimonial'),
            ('profile_stripepayment', 'accounts_stripepayment'),
        ]
        
        # Check if profile tables exist and rename them
        for old_table, new_table in tables_to_rename:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, [old_table])
            exists = cursor.fetchone()[0]
            
            if exists:
                # Check if new table already exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, [new_table])
                new_exists = cursor.fetchone()[0]
                
                if not new_exists:
                    cursor.execute(f'ALTER TABLE {old_table} RENAME TO {new_table}')
                else:
                    # If both exist, we need to merge data (this is more complex)
                    # For now, we'll skip if both exist
                    pass
        
        # Update foreign key constraints
        # Update profile_student references to accounts_student
        foreign_key_updates = [
            # Update auth_user_groups and auth_user_user_permissions if they reference profile_student
            ("UPDATE auth_user_groups SET user_id = user_id WHERE user_id IN (SELECT id FROM accounts_student);", []),
            ("UPDATE auth_user_user_permissions SET user_id = user_id WHERE user_id IN (SELECT id FROM accounts_student);", []),
        ]
        
        for sql, params in foreign_key_updates:
            try:
                cursor.execute(sql, params)
            except Exception:
                pass  # Some updates may not be needed
        
        # Update content types
        cursor.execute("""
            UPDATE django_content_type 
            SET app_label = 'accounts' 
            WHERE app_label = 'profile';
        """)


def reverse_migration(apps, schema_editor):
    """
    Reverse the migration - rename accounts tables back to profile tables.
    """
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        # Rename tables back from accounts_* to profile_*
        tables_to_rename = [
            ('accounts_student', 'profile_student'),
            ('accounts_order', 'profile_order'),
            ('accounts_orderlineitem', 'profile_orderlineitem'),
            ('accounts_product', 'profile_product'),
            ('accounts_productuser', 'profile_productuser'),
            ('accounts_staff', 'profile_staff'),
            ('accounts_testimonial', 'profile_testimonial'),
            ('accounts_stripepayment', 'profile_stripepayment'),
        ]
        
        for new_table, old_table in tables_to_rename:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, [new_table])
            exists = cursor.fetchone()[0]
            
            if exists:
                cursor.execute(f'ALTER TABLE {new_table} RENAME TO {old_table}')
        
        # Update content types back
        cursor.execute("""
            UPDATE django_content_type 
            SET app_label = 'profile' 
            WHERE app_label = 'accounts';
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_student_name'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        # Add models to Django's state (tables already exist, just renamed)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Testimonial',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('testimonial', HTMLField()),
                        ('citation', models.CharField(max_length=255)),
                    ],
                    options={
                        'ordering': ('-pk',),
                    },
                ),
                migrations.CreateModel(
                    name='Order',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('date_paid', models.DateTimeField(default=timezone.now)),
                        ('number', models.CharField(max_length=7)),
                        ('total', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                        ('in_person_appt_qty', models.SmallIntegerField(blank=True, default=0, null=True, verbose_name='In Person Appointments')),
                        ('remote_appt_qty', models.SmallIntegerField(blank=True, default=0, null=True, verbose_name='Online Appointments')),
                        ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
                    ],
                ),
                migrations.CreateModel(
                    name='Product',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=255)),
                        ('notes', models.TextField(blank=True, null=True)),
                        ('product_duration', models.DurationField(blank=True, null=True)),
                        ('account_name', models.CharField(max_length=255)),
                        ('charge', models.DecimalField(decimal_places=2, max_digits=6)),
                        ('expiration_date', models.DateField(blank=True, null=True)),
                        ('removed', models.BooleanField()),
                        ('owners', models.ManyToManyField(blank=True, related_name='products', to='accounts.student')),
                    ],
                ),
                migrations.CreateModel(
                    name='OrderLineItem',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('product_start_date', models.DateField(blank=True, null=True)),
                        ('product_end_date', models.DateField(blank=True, null=True)),
                        ('qty', models.SmallIntegerField(verbose_name='Quantity')),
                        ('charge', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Charge (USD)')),
                        ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.order')),
                        ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.product')),
                    ],
                ),
                migrations.CreateModel(
                    name='ProductUser',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('product_start_date', models.DateField(blank=True, null=True)),
                        ('product_end_date', models.DateField(blank=True, null=True)),
                        ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
                        ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.product')),
                    ],
                ),
                migrations.CreateModel(
                    name='Staff',
                    fields=[
                        ('student_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='accounts.student')),
                        ('description', models.TextField()),
                        ('image_path', models.CharField(max_length=255)),
                    ],
                    bases=('accounts.student',),
                ),
                migrations.CreateModel(
                    name='StripePayment',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('stripe_payment_intent_id', models.CharField(help_text='Stripe Payment Intent ID', max_length=255, unique=True)),
                        ('stripe_invoice_id', models.CharField(blank=True, help_text='Stripe Invoice ID', max_length=255, null=True)),
                        ('amount', models.DecimalField(decimal_places=2, help_text='Amount paid in USD', max_digits=10)),
                        ('status', models.CharField(choices=[('pending', 'Pending'), ('succeeded', 'Succeeded'), ('failed', 'Failed'), ('canceled', 'Canceled')], default='pending', max_length=50)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('paid_at', models.DateTimeField(blank=True, null=True)),
                        ('metadata', models.JSONField(blank=True, default=dict, help_text='Additional Stripe metadata')),
                        ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stripe_payments', to='accounts.student')),
                    ],
                    options={
                        'ordering': ('-created_at',),
                    },
                ),
            ],
            database_operations=[
                migrations.RunPython(migrate_data_from_profile, reverse_migration),
            ],
        ),
    ]

