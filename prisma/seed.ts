import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('Skipping data clearing so that a MongoDB replica set is not required locally.');

  console.log('Creating or retrieving Admin User...');
  const hashedPassword = await bcrypt.hash('password123', 10);
  
  // Find or Create Admin
  let admin = await prisma.user.findUnique({
    where: { email: 'admin@example.com' }
  });
  
  if (!admin) {
    admin = await prisma.user.create({
      data: {
        email: 'admin@example.com',
        name: 'Admin User',
        password: hashedPassword,
        role: 'admin',
        createdAt: new Date(),
      }
    });
  }

  const nonce = Date.now(); // We add this to unique fields so the script can be run multiple times safely

  console.log('Creating Suppliers...');
  const supplier1 = await prisma.supplier.create({
    data: {
      name: `Global Tech Suppliers ${nonce}`,
      userId: admin.id,
      createdBy: admin.id,
      description: 'Main supplier for electronics',
      status: true
    }
  });

  const supplier2 = await prisma.supplier.create({
    data: {
      name: `Office Essentials Hub ${nonce}`,
      userId: admin.id,
      createdBy: admin.id,
      description: 'Supplier for office equipment',
      status: true
    }
  });

  console.log('Creating Categories...');
  const electronics = await prisma.category.create({
    data: {
      name: `Electronics ${nonce}`,
      userId: admin.id,
      createdBy: admin.id,
      description: 'Electronic devices and accessories'
    }
  });

  const furniture = await prisma.category.create({
    data: {
      name: `Office Furniture ${nonce}`,
      userId: admin.id,
      createdBy: admin.id,
      description: 'Desks, chairs, and other office furniture'
    }
  });

  console.log('Creating Warehouse...');
  const warehouse = await prisma.warehouse.create({
    data: {
      name: `Main Distribution Center ${nonce}`,
      address: '123 Logistics Way, NY 10001',
      type: 'main',
      userId: admin.id,
      createdBy: admin.id
    }
  });

  console.log('Creating Products...');
  const product1 = await prisma.product.create({
    data: {
      name: 'Laptop Pro X15',
      sku: `LPT-PRO-X15-${nonce}`,
      price: 1299.99,
      quantity: 50n,
      status: 'active',
      categoryId: electronics.id,
      supplierId: supplier1.id,
      userId: admin.id,
      createdBy: admin.id
    }
  });

  const product2 = await prisma.product.create({
    data: {
      name: 'Ergonomic Office Chair',
      sku: `ERG-CHAIR-01-${nonce}`,
      price: 249.50,
      quantity: 120n,
      status: 'active',
      categoryId: furniture.id,
      supplierId: supplier2.id,
      userId: admin.id,
      createdBy: admin.id
    }
  });

  console.log('Allocating Stock...');
  await prisma.stockAllocation.create({
    data: {
      productId: product1.id,
      warehouseId: warehouse.id,
      quantity: 50n,
      userId: admin.id
    }
  });

  await prisma.stockAllocation.create({
    data: {
      productId: product2.id,
      warehouseId: warehouse.id,
      quantity: 120n,
      userId: admin.id
    }
  });

  console.log('Creating Orders...');
  // Note: We create the order first, and order items separately to avoid nested-writes, 
  // which also require a transaction/replica-set in MongoDB!
  const order = await prisma.order.create({
    data: {
      orderNumber: `ORD-${nonce}`,
      userId: admin.id,
      status: 'completed',
      paymentStatus: 'paid',
      subtotal: 1299.99,
      total: 1299.99,
      createdBy: admin.id
    }
  });

  await prisma.orderItem.create({
    data: {
      orderId: order.id,
      productId: product1.id,
      productName: product1.name,
      sku: product1.sku,
      quantity: 1,
      price: product1.price,
      subtotal: product1.price
    }
  });

  console.log('Creating Invoice...');
  await prisma.invoice.create({
    data: {
      invoiceNumber: `INV-${nonce}`,
      orderId: order.id,
      userId: admin.id,
      status: 'paid',
      subtotal: 1299.99,
      total: 1299.99,
      amountPaid: 1299.99,
      dueDate: new Date(),
      createdBy: admin.id
    }
  });

  console.log('Seeding completed successfully!');
  console.log(`Admin email: admin@example.com`);
  console.log(`Admin password: password123`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
