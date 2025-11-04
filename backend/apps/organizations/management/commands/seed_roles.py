from django.core.management.base import BaseCommand
from apps.organizations.models import Role, Permission, RolePermission


class Command(BaseCommand):
    help = 'Seed initial roles and permissions'

    def handle(self, *args, **options):
        self.stdout.write('Seeding roles and permissions...')
        
        # Define permissions
        permissions_data = [
            # Products
            {'code': 'products.view', 'name': 'View Products', 'category': 'products'},
            {'code': 'products.create', 'name': 'Create Products', 'category': 'products'},
            {'code': 'products.update', 'name': 'Update Products', 'category': 'products'},
            {'code': 'products.delete', 'name': 'Delete Products', 'category': 'products'},
            
            # Inventory
            {'code': 'inventory.view', 'name': 'View Inventory', 'category': 'inventory'},
            {'code': 'inventory.update', 'name': 'Update Inventory', 'category': 'inventory'},
            
            # Invoices
            {'code': 'invoices.view', 'name': 'View Invoices', 'category': 'invoices'},
            {'code': 'invoices.create', 'name': 'Create Invoices', 'category': 'invoices'},
            {'code': 'invoices.update', 'name': 'Update Invoices', 'category': 'invoices'},
            {'code': 'invoices.delete', 'name': 'Delete Invoices', 'category': 'invoices'},
            {'code': 'invoices.approve', 'name': 'Approve Invoices', 'category': 'invoices'},
            
            # Payments
            {'code': 'payments.view', 'name': 'View Payments', 'category': 'payments'},
            {'code': 'payments.create', 'name': 'Create Payments', 'category': 'payments'},
            
            # Reports
            {'code': 'reports.view', 'name': 'View Reports', 'category': 'reports'},
            {'code': 'reports.export', 'name': 'Export Reports', 'category': 'reports'},
            
            # Users & Settings
            {'code': 'users.view', 'name': 'View Users', 'category': 'users'},
            {'code': 'users.invite', 'name': 'Invite Users', 'category': 'users'},
            {'code': 'users.manage', 'name': 'Manage Users', 'category': 'users'},
            {'code': 'settings.view', 'name': 'View Settings', 'category': 'settings'},
            {'code': 'settings.manage', 'name': 'Manage Settings', 'category': 'settings'},
        ]
        
        # Create permissions
        permissions = {}
        for perm_data in permissions_data:
            permission, created = Permission.objects.get_or_create(
                code=perm_data['code'],
                defaults={
                    'name': perm_data['name'],
                    'category': perm_data['category']
                }
            )
            permissions[perm_data['code']] = permission
            if created:
                self.stdout.write(f'  ✓ Created permission: {perm_data["code"]}')
        
        # Define roles with permissions
        roles_data = [
            {
                'name': 'Owner',
                'description': 'Full access to everything including organization deletion',
                'level': 100,
                'permissions': [p.code for p in permissions.values()]  # All permissions
            },
            {
                'name': 'Admin',
                'description': 'Manage users, settings, and all resources',
                'level': 90,
                'permissions': [
                    'products.view', 'products.create', 'products.update', 'products.delete',
                    'inventory.view', 'inventory.update',
                    'invoices.view', 'invoices.create', 'invoices.update', 'invoices.delete', 'invoices.approve',
                    'payments.view', 'payments.create',
                    'reports.view', 'reports.export',
                    'users.view', 'users.invite', 'users.manage',
                    'settings.view', 'settings.manage',
                ]
            },
            {
                'name': 'Manager',
                'description': 'Approve invoices and manage inventory',
                'level': 70,
                'permissions': [
                    'products.view', 'products.create', 'products.update',
                    'inventory.view', 'inventory.update',
                    'invoices.view', 'invoices.create', 'invoices.update', 'invoices.approve',
                    'payments.view', 'payments.create',
                    'reports.view', 'reports.export',
                    'users.view',
                    'settings.view',
                ]
            },
            {
                'name': 'Accountant',
                'description': 'Manage invoices, payments, and view reports',
                'level': 60,
                'permissions': [
                    'products.view',
                    'inventory.view',
                    'invoices.view', 'invoices.create', 'invoices.update', 'invoices.delete',
                    'payments.view', 'payments.create',
                    'reports.view', 'reports.export',
                    'settings.view',
                ]
            },
            {
                'name': 'Staff',
                'description': 'Create invoices and update inventory',
                'level': 40,
                'permissions': [
                    'products.view', 'products.create',
                    'inventory.view', 'inventory.update',
                    'invoices.view', 'invoices.create', 'invoices.update',
                    'payments.view',
                    'reports.view',
                ]
            },
            {
                'name': 'Viewer',
                'description': 'Read-only access to all resources',
                'level': 10,
                'permissions': [
                    'products.view',
                    'inventory.view',
                    'invoices.view',
                    'payments.view',
                    'reports.view',
                ]
            },
        ]
        
        # Create roles and assign permissions
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'level': role_data['level']
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ Created role: {role_data["name"]}')
            
            # Clear existing permissions
            RolePermission.objects.filter(role=role).delete()
            
            # Assign permissions
            for perm_code in role_data['permissions']:
                if perm_code in permissions:
                    RolePermission.objects.get_or_create(
                        role=role,
                        permission=permissions[perm_code]
                    )
            
            perm_count = role.permissions.count()
            self.stdout.write(f'    → Assigned {perm_count} permissions')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Successfully seeded roles and permissions!'))